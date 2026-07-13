from __future__ import annotations

import os
import sys
from functools import lru_cache
import io
import wave
from pathlib import Path
from typing import Any, Sequence

from services.api.app.schemas.conversation import (
    ConversationResponsePrompt,
    ConversationResponseResult,
    ConversationTurnRecord,
    ConversationTurnStatus,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.schemas.voice_profile import VoiceProfile
from services.api.app.services.audio_turn_runtime import (
    _audio_buffer_for_turn,
    _audio_duration_ms,
    _speech_window_audio_buffer,
    _summarize_segments,
    get_audio_turn_stt_provider,
    get_audio_turn_vad_provider,
)
from services.api.app.services.generation_runtime import get_generation_tts_provider
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE

WORKER_ROOT_ENV = "THEATRICAL_VOICE_STUDIO_WORKER_ROOT"
MAX_RECENT_TURNS = 4


def _worker_root() -> Path:
    configured_root = os.environ.get(WORKER_ROOT_ENV)
    if configured_root:
        worker_root = Path(configured_root)
    else:
        worker_root = Path(__file__).resolve().parents[4] / "services" / "speech-worker"

    if not worker_root.exists():
        raise RuntimeError(
            "Approved speech-worker root not found. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory.",
        )

    providers_dir = worker_root / "providers"
    if not providers_dir.exists():
        raise RuntimeError(
            "Approved speech-worker root is missing the providers package. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory.",
        )

    return worker_root


def _ensure_worker_root_on_path() -> Path:
    worker_root = _worker_root()
    worker_root_str = str(worker_root)
    if worker_root_str not in sys.path:
        sys.path.insert(0, worker_root_str)
    return worker_root


@lru_cache(maxsize=1)
def _load_conversation_provider_class() -> Any:
    _ensure_worker_root_on_path()
    try:
        from providers import VesperConversationResponder
    except ImportError as exc:  # pragma: no cover - only exercised when worker checkout is missing
        raise RuntimeError(
            "Conversation responder could not be imported from the approved worker root.",
        ) from exc

    return VesperConversationResponder


@lru_cache(maxsize=1)
def get_conversation_response_provider() -> Any:
    provider_class = _load_conversation_provider_class()
    return provider_class()


def _build_persona_instructions(
    *,
    voice_profile: VoiceProfile,
    tone_preset: GenerationTonePreset,
    recent_turn_count: int,
) -> str:
    memory_clause = (
        "Use the recent conversation turns only for short session memory, and do not "
        "persist memory after refresh."
        if recent_turn_count
        else "No prior turns are available, so keep the reply self-contained."
    )

    return (
        f"{voice_profile.style.summary} Stay inside this original voice boundary: "
        f"{voice_profile.boundary_note} Avoid any claim to be Loki, Tom Hiddleston, "
        f"Marvel, or any other protected or unlicensed identity. Tone preset: "
        f"{tone_preset.value}. Keep the response concise, theatrical, cool, and dryly "
        f"witty. {memory_clause}"
    )


def buildConversationResponsePrompt(
    *,
    voice_profile: VoiceProfile,
    user_transcript_text: str,
    tone_preset: GenerationTonePreset,
    recent_turns: Sequence[ConversationTurnRecord] | None = None,
) -> ConversationResponsePrompt:
    memory_turns = list(recent_turns or [])[:MAX_RECENT_TURNS]
    return ConversationResponsePrompt(
        voice_id=voice_profile.id,
        voice_display_name=voice_profile.display_name,
        boundary_note=voice_profile.boundary_note,
        prohibited_associations=list(voice_profile.style.prohibited_associations),
        tone_preset=tone_preset,
        user_transcript_text=user_transcript_text.strip(),
        recent_turns=memory_turns,
        persona_instructions=_build_persona_instructions(
            voice_profile=voice_profile,
            tone_preset=tone_preset,
            recent_turn_count=len(memory_turns),
        ),
    )


def generateConversationReply(
    prompt: ConversationResponsePrompt,
    provider: Any | None = None,
) -> ConversationResponseResult:
    conversation_provider = provider or get_conversation_response_provider()
    result = conversation_provider.generate_reply(prompt)
    return ConversationResponseResult.model_validate(result)


def _artifact_duration_ms(artifact: Any) -> int:
    duration_ms = getattr(artifact, "duration_ms", None)
    if duration_ms is not None:
        return int(duration_ms)

    audio_bytes = getattr(artifact, "audio_bytes", b"")
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate_hz = wav_file.getframerate()
            if sample_rate_hz > 0:
                return int(round(frame_count / sample_rate_hz * 1000))
    except (wave.Error, EOFError):
        pass

    return 0


def synthesizeConversationTurn(
    turn_id: str,
    *,
    turn_service: Any | None = None,
    voice_profile: VoiceProfile | None = None,
    vad_provider: Any | None = None,
    stt_provider: Any | None = None,
    response_provider: Any | None = None,
    tts_provider: Any | None = None,
) -> ConversationTurnRecord:
    from services.api.app.services.conversation_jobs import get_conversation_turn_service

    conversation_turn_service = turn_service or get_conversation_turn_service()
    voice_profile = voice_profile or VESPER_GLASS_PROFILE
    running_record = conversation_turn_service.mark_running(turn_id)
    session_id = conversation_turn_service.get_turn_session_id(turn_id)

    try:
        audio_bytes = conversation_turn_service.get_input_audio_path(turn_id).read_bytes()
        audio_buffer = _audio_buffer_for_turn(
            audio_bytes,
            running_record.attempt.mime_type or "audio/wav",
        )
        vad_provider = vad_provider or get_audio_turn_vad_provider()
        speech_segments = vad_provider.detect_speech_segments(audio_buffer)
        if not speech_segments:
            raise RuntimeError("No meaningful speech was detected in the conversation turn.")

        vad_metadata = _summarize_segments(
            speech_segments,
            provider_name=vad_provider.provider_name,
        )
        stt_provider = stt_provider or get_audio_turn_stt_provider()
        speech_window_audio = _speech_window_audio_buffer(
            audio_buffer,
            start_ms=vad_metadata.speech_start_ms,
            end_ms=vad_metadata.speech_end_ms,
        )
        transcript = stt_provider.transcribe(speech_window_audio)
        transcript_text = getattr(transcript, "text", "").strip()
        if not transcript_text:
            raise RuntimeError("The STT provider returned an empty transcript for the conversation turn.")

        session_turns = conversation_turn_service.session_service.list_turns(session_id)
        recent_turns = [
            turn
            for turn in session_turns
            if turn.turn_id != turn_id and turn.status == ConversationTurnStatus.SUCCEEDED
        ]
        prompt = buildConversationResponsePrompt(
            voice_profile=voice_profile,
            user_transcript_text=transcript_text,
            tone_preset=running_record.tone_preset or GenerationTonePreset.MEASURED,
            recent_turns=recent_turns,
        )
        response = generateConversationReply(prompt, provider=response_provider)
        tts_provider = tts_provider or get_generation_tts_provider()
        artifact = tts_provider.synthesize(
            response.text,
            voice_profile.id,
            tone=response.tone_preset.value,
        )
        response_audio_bytes = getattr(artifact, "audio_bytes")
        mime_type = getattr(artifact, "mime_type", None) or "audio/wav"
        provider_name = getattr(artifact, "provider_name", None) or getattr(
            tts_provider,
            "provider_name",
            "tts-provider",
        )
        return conversation_turn_service.mark_succeeded(
            turn_id,
            response_audio_bytes=response_audio_bytes,
            user_transcript_text=transcript_text,
            response_provider_name=response.provider_name,
            tts_provider_name=provider_name,
            response_text=response.text,
            mime_type=mime_type,
            audio_duration_ms=_artifact_duration_ms(artifact),
            tone_preset=response.tone_preset,
        )
    except Exception as exc:
        return conversation_turn_service.mark_failed(turn_id, error_message=str(exc))
