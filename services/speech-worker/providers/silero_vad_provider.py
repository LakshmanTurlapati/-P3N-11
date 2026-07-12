from __future__ import annotations

import array
import os
import sys
from typing import Any

from providers.contracts import AudioBuffer, SpeechSegment, VADProvider

FORCE_FIXTURE_ENV = "THEATRICAL_VOICE_STUDIO_VAD_FIXTURE"
DEFAULT_SAMPLE_RATE_HZ = 16_000
FRAME_WINDOW_MS = 20
MIN_SEGMENT_MS = 80


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _pcm16_samples(audio: AudioBuffer) -> array.array[int]:
    if audio.channels != 1:
        raise ValueError("Silero VAD expects mono audio")
    if audio.sample_rate_hz <= 0:
        raise ValueError("Silero VAD expects a positive sample rate")
    if len(audio.pcm16) % 2 != 0:
        raise ValueError("AudioBuffer.pcm16 must contain whole 16-bit samples")

    samples = array.array("h")
    samples.frombytes(audio.pcm16)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def _frame_size(audio: AudioBuffer) -> int:
    return max(int(round(audio.sample_rate_hz * FRAME_WINDOW_MS / 1000)), 1)


def _segment_confidence(segment_peak: int) -> float:
    return round(min(0.99, segment_peak / 8_000.0), 3)


def _fixture_segments(audio: AudioBuffer) -> list[SpeechSegment]:
    samples = _pcm16_samples(audio)
    if len(samples) == 0:
        return []

    frame_size = _frame_size(audio)
    peak_amplitude = max(abs(sample) for sample in samples)
    speech_threshold = max(80, int(round(peak_amplitude * 0.12)))
    min_segment_samples = max(int(round(audio.sample_rate_hz * MIN_SEGMENT_MS / 1000)), 1)

    segments: list[SpeechSegment] = []
    segment_start_sample: int | None = None
    segment_peak = 0

    for frame_start in range(0, len(samples), frame_size):
        frame = samples[frame_start : frame_start + frame_size]
        frame_peak = max(abs(sample) for sample in frame) if frame else 0

        if frame_peak >= speech_threshold:
            if segment_start_sample is None:
                segment_start_sample = frame_start
            segment_peak = max(segment_peak, frame_peak)
            continue

        if segment_start_sample is None:
            continue

        segment_end_sample = frame_start
        if segment_end_sample - segment_start_sample >= min_segment_samples:
            segments.append(
                SpeechSegment(
                    start_ms=int(round(segment_start_sample / audio.sample_rate_hz * 1000)),
                    end_ms=int(round(segment_end_sample / audio.sample_rate_hz * 1000)),
                    confidence=_segment_confidence(segment_peak),
                )
            )
        segment_start_sample = None
        segment_peak = 0

    if segment_start_sample is not None:
        segment_end_sample = len(samples)
        if segment_end_sample - segment_start_sample >= min_segment_samples:
            segments.append(
                SpeechSegment(
                    start_ms=int(round(segment_start_sample / audio.sample_rate_hz * 1000)),
                    end_ms=int(round(segment_end_sample / audio.sample_rate_hz * 1000)),
                    confidence=_segment_confidence(segment_peak),
                )
            )

    return segments


class _FixtureSileroBackend:
    provider_name = "silero-vad"

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        return _fixture_segments(audio)


class _TorchSileroBackend:
    provider_name = "silero-vad"

    def __init__(self, sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ) -> None:
        self.sample_rate_hz = sample_rate_hz
        self._model: Any | None = None
        self._get_speech_timestamps: Any | None = None

    def _load_model(self) -> None:
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - exercised only on hosts without torch
            raise RuntimeError("torch is unavailable in the worker runtime.") from exc

        try:
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
            )
        except Exception as exc:  # pragma: no cover - requires the real Silero package
            raise RuntimeError("Silero VAD could not be loaded from torch.hub.") from exc

        try:
            get_speech_timestamps = utils[0]
        except Exception as exc:  # pragma: no cover - defensive around hub return shape
            raise RuntimeError("Silero VAD utility bundle is not in the expected shape.") from exc

        self._model = model
        self._get_speech_timestamps = get_speech_timestamps

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        if audio.sample_rate_hz != self.sample_rate_hz:
            raise ValueError(
                f"Silero VAD expects {self.sample_rate_hz} Hz audio, got {audio.sample_rate_hz} Hz."
            )

        if self._model is None or self._get_speech_timestamps is None:
            self._load_model()

        try:
            import torch
        except ImportError as exc:  # pragma: no cover - exercised only on hosts without torch
            raise RuntimeError("torch is unavailable in the worker runtime.") from exc

        samples = torch.tensor(_pcm16_samples(audio).tolist(), dtype=torch.float32) / 32_768.0
        timestamps = self._get_speech_timestamps(
            samples,
            self._model,
            sampling_rate=audio.sample_rate_hz,
        )

        return [
            SpeechSegment(
                start_ms=int(round(timestamp["start"] / audio.sample_rate_hz * 1000)),
                end_ms=int(round(timestamp["end"] / audio.sample_rate_hz * 1000)),
                confidence=None,
            )
            for timestamp in timestamps
        ]


class SileroVADProvider(VADProvider):
    provider_name = "silero-vad"

    def __init__(
        self,
        *,
        backend: Any | None = None,
        force_fixture_fallback: bool | None = None,
        sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ,
    ) -> None:
        self._backend = backend
        self._force_fixture_fallback = (
            force_fixture_fallback
            if force_fixture_fallback is not None
            else _is_truthy(os.environ.get(FORCE_FIXTURE_ENV))
        )
        self.sample_rate_hz = sample_rate_hz

    def _load_backend(self) -> Any:
        if self._force_fixture_fallback:
            return _FixtureSileroBackend()

        try:
            return _TorchSileroBackend(sample_rate_hz=self.sample_rate_hz)
        except Exception:  # pragma: no cover - fallback is the common local path
            return _FixtureSileroBackend()

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        backend = self._backend or self._load_backend()
        try:
            return backend.detect_speech_segments(audio)
        except (ImportError, RuntimeError, OSError):
            if self._backend is not None or self._force_fixture_fallback:
                raise
            return _FixtureSileroBackend().detect_speech_segments(audio)
