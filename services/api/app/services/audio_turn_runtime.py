from __future__ import annotations

import io
import os
import sys
import wave
from functools import lru_cache
from pathlib import Path
from typing import Any

from services.api.app.schemas.audio_turn import (
    AudioTurnJobRecord,
    AudioTurnVADMetadata,
    AudioTurnVADSegment,
)
from services.api.app.services.audio_turn_jobs import AudioTurnJobService

WORKER_ROOT_ENV = "THEATRICAL_VOICE_STUDIO_WORKER_ROOT"
DEFAULT_VAD_SAMPLE_RATE_HZ = 16_000
THIN_TURN_DURATION_MS = 500
THIN_TURN_CONFIDENCE = 0.45


def _worker_root() -> Path:
    configured_root = os.environ.get(WORKER_ROOT_ENV)
    if configured_root:
        worker_root = Path(configured_root)
    else:
        worker_root = Path(__file__).resolve().parents[4] / "services" / "speech-worker"

    if not worker_root.exists():
        raise RuntimeError(
            "Approved speech-worker root not found. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory."
        )

    providers_dir = worker_root / "providers"
    if not providers_dir.exists():
        raise RuntimeError(
            "Approved speech-worker root is missing the providers package. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory."
        )

    return worker_root


def _ensure_worker_root_on_path() -> Path:
    worker_root = _worker_root()
    worker_root_str = str(worker_root)
    if worker_root_str not in sys.path:
        sys.path.insert(0, worker_root_str)
    return worker_root


@lru_cache(maxsize=1)
def _load_worker_dependencies() -> tuple[Any, Any, Any, Any]:
    _ensure_worker_root_on_path()
    try:
        from audio.normalization import normalize_audio
        from providers import AudioBuffer, SileroVADProvider, SpeechArtifact
    except ImportError as exc:  # pragma: no cover - only when the approved worker root is missing
        raise RuntimeError(
            "Approved speech-worker dependencies could not be imported."
        ) from exc

    return normalize_audio, AudioBuffer, SpeechArtifact, SileroVADProvider


@lru_cache(maxsize=1)
def get_audio_turn_vad_provider() -> Any:
    _, _, _, vad_provider_class = _load_worker_dependencies()
    return vad_provider_class()


def _audio_duration_ms(audio_buffer: Any) -> int:
    sample_count = len(getattr(audio_buffer, "pcm16", b"")) // 2
    sample_rate_hz = int(getattr(audio_buffer, "sample_rate_hz", 0))
    if sample_count <= 0 or sample_rate_hz <= 0:
        return 0
    return int(round(sample_count / sample_rate_hz * 1000))


def _wav_bytes_to_audio_buffer(wav_bytes: bytes) -> Any:
    _, audio_buffer_class, _, _ = _load_worker_dependencies()
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        sample_width = wav_file.getsampwidth()
        if sample_width != 2:
            raise RuntimeError("Audio turn runtime expects 16-bit PCM WAV input.")

        return audio_buffer_class(
            pcm16=wav_file.readframes(wav_file.getnframes()),
            sample_rate_hz=wav_file.getframerate(),
            channels=wav_file.getnchannels(),
            mime_type="audio/wav",
        )


def _audio_buffer_for_turn(audio_bytes: bytes, mime_type: str) -> Any:
    normalize_audio, _, speech_artifact_class, _ = _load_worker_dependencies()
    if mime_type == "audio/wav" or audio_bytes.startswith(b"RIFF"):
        try:
            return _wav_bytes_to_audio_buffer(audio_bytes)
        except (EOFError, wave.Error) as exc:
            if mime_type == "audio/wav":
                raise RuntimeError("Audio turn payload is not a valid WAV file.") from exc

    normalized_artifact = normalize_audio(
        speech_artifact_class(
            audio_bytes=audio_bytes,
            sample_rate_hz=DEFAULT_VAD_SAMPLE_RATE_HZ,
            mime_type=mime_type,
            provider_name="audio-turn-input",
        ),
        target_sample_rate_hz=DEFAULT_VAD_SAMPLE_RATE_HZ,
    )
    return _wav_bytes_to_audio_buffer(normalized_artifact.audio_bytes)


def _summarize_segments(
    segments: list[Any],
    *,
    provider_name: str,
) -> AudioTurnVADMetadata:
    vad_segments = [
        AudioTurnVADSegment(
            start_ms=int(segment.start_ms),
            end_ms=int(segment.end_ms),
            confidence=segment.confidence,
        )
        for segment in segments
    ]
    speech_start_ms = min(segment.start_ms for segment in vad_segments)
    speech_end_ms = max(segment.end_ms for segment in vad_segments)
    speech_duration_ms = sum(segment.end_ms - segment.start_ms for segment in vad_segments)
    confidence_values = [segment.confidence for segment in vad_segments if segment.confidence is not None]
    confidence = round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else None

    warning_message = None
    if speech_duration_ms < THIN_TURN_DURATION_MS or (
        confidence is not None and confidence < THIN_TURN_CONFIDENCE
    ):
        warning_message = (
            "Audio was captured, but the turn is thin or low-confidence. "
            "Review before transcription."
        )

    return AudioTurnVADMetadata(
        provider_name=provider_name,
        segments=vad_segments,
        speech_start_ms=speech_start_ms,
        speech_end_ms=speech_end_ms,
        speech_duration_ms=speech_duration_ms,
        confidence=confidence,
        warning_message=warning_message,
    )


def process_audio_turn_job(
    job_id: str,
    *,
    job_service: AudioTurnJobService | None = None,
    provider: Any | None = None,
) -> AudioTurnJobRecord:
    job_service = job_service or AudioTurnJobService.from_env()
    running_record = job_service.mark_running(job_id)

    try:
        audio_bytes = job_service.get_audio_path(job_id).read_bytes()
        audio_buffer = _audio_buffer_for_turn(audio_bytes, running_record.audio_mime_type)
        vad_provider = provider or get_audio_turn_vad_provider()
        segments = vad_provider.detect_speech_segments(audio_buffer)
        if not segments:
            raise RuntimeError("No meaningful speech was detected in the captured turn.")

        vad_metadata = _summarize_segments(segments, provider_name=vad_provider.provider_name)
        audio_duration_ms = _audio_duration_ms(audio_buffer)
        return job_service.mark_succeeded(
            job_id,
            vad_metadata=vad_metadata,
            audio_duration_ms=audio_duration_ms,
        )
    except Exception as exc:
        return job_service.mark_failed(job_id, error_message=str(exc))
