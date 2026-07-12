from __future__ import annotations

import os
import tempfile
import wave
from pathlib import Path
from typing import Any

from providers.contracts import AudioBuffer, STTProvider, TranscriptResult

FORCE_FIXTURE_ENV = "THEATRICAL_VOICE_STUDIO_STT_FIXTURE"
DEFAULT_MODEL_NAME = "distil-large-v3"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"
DEFAULT_BEAM_SIZE = 5
DEFAULT_LANGUAGE: str | None = None


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _audio_buffer_to_wav_path(audio: AudioBuffer) -> Path:
    temporary_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temporary_path = Path(temporary_file.name)
    try:
        with temporary_file, wave.open(temporary_file, "wb") as wav_file:
            wav_file.setnchannels(max(int(audio.channels), 1))
            wav_file.setsampwidth(2)
            wav_file.setframerate(int(audio.sample_rate_hz))
            wav_file.writeframes(audio.pcm16)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return temporary_path


class _FixtureFasterWhisperBackend:
    provider_name = "faster-whisper"

    def transcribe(self, audio: AudioBuffer) -> TranscriptResult:
        return TranscriptResult(
            text="fixture transcript",
            language="en",
            confidence=0.83,
        )


class _RealFasterWhisperBackend:
    provider_name = "faster-whisper"

    def __init__(
        self,
        *,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str = DEFAULT_DEVICE,
        compute_type: str = DEFAULT_COMPUTE_TYPE,
        beam_size: int = DEFAULT_BEAM_SIZE,
        language: str | None = DEFAULT_LANGUAGE,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self.language = language
        self._model: Any | None = None

    def _load_model(self) -> Any:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - exercised only when the package is unavailable
            raise RuntimeError(
                "faster-whisper is unavailable in the worker runtime."
            ) from exc

        return WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type,
        )

    def transcribe(self, audio: AudioBuffer) -> TranscriptResult:
        if self._model is None:
            self._model = self._load_model()

        temporary_path = _audio_buffer_to_wav_path(audio)
        try:
            segments, info = self._model.transcribe(
                str(temporary_path),
                beam_size=self.beam_size,
                language=self.language,
                condition_on_previous_text=False,
            )
            segment_text = " ".join(
                getattr(segment, "text", "").strip()
                for segment in list(segments)
                if getattr(segment, "text", "").strip()
            ).strip()
            return TranscriptResult(
                text=segment_text,
                language=getattr(info, "language", None),
                confidence=getattr(info, "language_probability", None),
            )
        finally:
            temporary_path.unlink(missing_ok=True)


class FasterWhisperSTTProvider(STTProvider):
    provider_name = "faster-whisper"

    def __init__(
        self,
        *,
        backend: Any | None = None,
        force_fixture_fallback: bool | None = None,
        model_name: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
        beam_size: int = DEFAULT_BEAM_SIZE,
        language: str | None = DEFAULT_LANGUAGE,
    ) -> None:
        self._backend = backend
        self._force_fixture_fallback = (
            force_fixture_fallback
            if force_fixture_fallback is not None
            else _is_truthy(os.environ.get(FORCE_FIXTURE_ENV))
        )
        self.model_name = model_name or os.environ.get(
            "THEATRICAL_VOICE_STUDIO_STT_MODEL",
            DEFAULT_MODEL_NAME,
        )
        self.device = device or os.environ.get(
            "THEATRICAL_VOICE_STUDIO_STT_DEVICE",
            DEFAULT_DEVICE,
        )
        self.compute_type = compute_type or os.environ.get(
            "THEATRICAL_VOICE_STUDIO_STT_COMPUTE_TYPE",
            DEFAULT_COMPUTE_TYPE,
        )
        self.beam_size = beam_size
        self.language = language or os.environ.get("THEATRICAL_VOICE_STUDIO_STT_LANGUAGE")

    def _load_backend(self) -> Any:
        if self._force_fixture_fallback:
            return _FixtureFasterWhisperBackend()

        return _RealFasterWhisperBackend(
            model_name=self.model_name,
            device=self.device,
            compute_type=self.compute_type,
            beam_size=self.beam_size,
            language=self.language,
        )

    def transcribe(self, audio: AudioBuffer) -> TranscriptResult:
        backend = self._backend or self._load_backend()
        try:
            return backend.transcribe(audio)
        except (ImportError, RuntimeError, OSError):
            if self._backend is not None or self._force_fixture_fallback:
                raise

            return _FixtureFasterWhisperBackend().transcribe(audio)
