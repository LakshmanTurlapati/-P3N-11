from __future__ import annotations

import io
import wave

from services.api.app.schemas.conversation import (
    ConversationTurnAttempt,
    ConversationResponsePrompt,
    ConversationTurnRecord,
    ConversationTurnStatus,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.services.conversation_jobs import ConversationSessionService, ConversationTurnService
from services.api.app.services.conversation_runtime import (
    buildConversationResponsePrompt,
    synthesizeConversationTurn,
)
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE


def _wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16_000)
        wav_file.writeframes((1200).to_bytes(2, byteorder="little", signed=True) * 16_000)
    return buffer.getvalue()


def _recent_turn() -> ConversationTurnRecord:
    return ConversationTurnRecord(
        turn_id="conversation-turn-001",
        status=ConversationTurnStatus.SUCCEEDED,
        input_audio_url="/conversation-turns/conversation-turn-001/input.wav",
        user_transcript_text="You sound amused.",
        response_text="Naturally.",
        playback_url="/conversation-turns/conversation-turn-001/audio",
        tone_preset=GenerationTonePreset.MEASURED,
        latency_ms=1280,
        attempt=ConversationTurnAttempt(
            status=ConversationTurnStatus.SUCCEEDED,
            provider_name="fixture-tts",
            response_provider_name="fixture-responder",
            tts_provider_name="fixture-tts",
            mime_type="audio/wav",
            input_audio_url="/conversation-turns/conversation-turn-001/input.wav",
            user_transcript_text="You sound amused.",
            response_text="Naturally.",
            playback_url="/conversation-turns/conversation-turn-001/audio",
            tone_preset=GenerationTonePreset.MEASURED,
            audio_duration_ms=128,
        ),
    )


def test_build_conversation_response_prompt_keeps_the_original_voice_boundary_and_memory() -> None:
    recent_turn = _recent_turn()

    prompt: ConversationResponsePrompt = buildConversationResponsePrompt(
        voice_profile=VESPER_GLASS_PROFILE,
        user_transcript_text="Give me the next line.",
        tone_preset=GenerationTonePreset.CUTTING,
        recent_turns=[recent_turn],
    )

    assert prompt.voice_id == VESPER_GLASS_PROFILE.id
    assert prompt.voice_display_name == VESPER_GLASS_PROFILE.display_name
    assert prompt.boundary_note == VESPER_GLASS_PROFILE.boundary_note
    assert prompt.prohibited_associations == VESPER_GLASS_PROFILE.style.prohibited_associations
    assert prompt.tone_preset == GenerationTonePreset.CUTTING
    assert prompt.user_transcript_text == "Give me the next line."
    assert prompt.recent_turns == [recent_turn]
    assert "theatrical" in prompt.persona_instructions.lower()
    assert "dryly witty" in prompt.persona_instructions.lower()


class _SpeechyVADProvider:
    provider_name = "fixture-vad"

    def detect_speech_segments(self, audio):
        _ = audio
        return [
            type(
                "SpeechSegment",
                (),
                {"start_ms": 0, "end_ms": 480, "confidence": 0.91},
            )(),
        ]


class _TranscriptProvider:
    provider_name = "fixture-stt"

    def transcribe(self, audio):
        _ = audio
        return type(
            "Transcript",
            (),
            {"text": "Give me the next line.", "language": "en", "confidence": 0.97},
        )()


class _ResponseProvider:
    provider_name = "fixture-response"

    def generate_reply(self, prompt):
        assert prompt.tone_preset == GenerationTonePreset.CUTTING
        from services.api.app.schemas.conversation import ConversationResponseResult

        return ConversationResponseResult(
            provider_name=self.provider_name,
            tone_preset=prompt.tone_preset,
            text="Naturally. I will keep this sharp. No borrowed masks.",
        )


class _TTSProvider:
    provider_name = "fixture-tts"

    def synthesize(self, text: str, voice_id: str, *, tone: str):
        assert text == "Naturally. I will keep this sharp. No borrowed masks."
        assert voice_id == VESPER_GLASS_PROFILE.id
        assert tone == "cutting"
        return type(
            "SpeechArtifact",
            (),
            {
                "provider_name": self.provider_name,
                "mime_type": "audio/wav",
                "audio_bytes": b"RIFFconversation-audio",
                "duration_ms": 432,
            },
        )()


def test_synthesize_conversation_turn_persists_response_and_playback_metadata(tmp_path) -> None:
    session_service = ConversationSessionService(storage_root=tmp_path / "sessions")
    turn_service = ConversationTurnService(
        storage_root=tmp_path / "turns",
        session_service=session_service,
    )
    session = session_service.create_session()
    queued_turn = turn_service.create_turn(
        session.session_id,
        audio_bytes=_wav_bytes(),
        audio_mime_type="audio/wav",
        tone_preset=GenerationTonePreset.CUTTING,
        audio_filename="spoken-turn.wav",
    )

    updated_turn = synthesizeConversationTurn(
        queued_turn.turn_id,
        turn_service=turn_service,
        voice_profile=VESPER_GLASS_PROFILE,
        vad_provider=_SpeechyVADProvider(),
        stt_provider=_TranscriptProvider(),
        response_provider=_ResponseProvider(),
        tts_provider=_TTSProvider(),
    )

    assert updated_turn.status == ConversationTurnStatus.SUCCEEDED
    assert updated_turn.user_transcript_text == "Give me the next line."
    assert updated_turn.response_text == "Naturally. I will keep this sharp. No borrowed masks."
    assert updated_turn.playback_url == f"/conversation-turns/{queued_turn.turn_id}/audio"
    assert updated_turn.tone_preset == GenerationTonePreset.CUTTING
    assert updated_turn.attempt is not None
    assert updated_turn.attempt.response_provider_name == "fixture-response"
    assert updated_turn.attempt.tts_provider_name == "fixture-tts"
    assert updated_turn.attempt.audio_duration_ms == 432
    assert turn_service.get_audio_path(queued_turn.turn_id).read_bytes() == b"RIFFconversation-audio"
