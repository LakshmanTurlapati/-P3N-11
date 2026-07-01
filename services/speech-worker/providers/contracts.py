from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class AudioBuffer:
    pcm16: bytes
    sample_rate_hz: int
    channels: int = 1
    mime_type: str = "audio/wav"


@dataclass(frozen=True, slots=True)
class SpeechSegment:
    start_ms: int
    end_ms: int
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class TranscriptResult:
    text: str
    language: str | None = None
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class SpeechArtifact:
    audio_bytes: bytes
    sample_rate_hz: int
    mime_type: str
    provider_name: str
    duration_ms: int | None = None


@runtime_checkable
class VADProvider(Protocol):
    provider_name: str

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        """Return the ordered speech segments found in the audio buffer."""


@runtime_checkable
class STTProvider(Protocol):
    provider_name: str

    def transcribe(self, audio: AudioBuffer) -> TranscriptResult:
        """Return the best transcript for the provided audio buffer."""


@runtime_checkable
class TTSProvider(Protocol):
    provider_name: str

    def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        """Synthesize spoken audio for the requested voice."""


@runtime_checkable
class SpeechToSpeechProvider(Protocol):
    provider_name: str

    def transform(
        self,
        audio: AudioBuffer,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        """Transform input speech into the requested voice style."""
