from .contracts import (
    AudioBuffer,
    SpeechArtifact,
    SpeechSegment,
    SpeechToSpeechProvider,
    STTProvider,
    TTSProvider,
    VADProvider,
    TranscriptResult,
)

__all__ = [
    "AudioBuffer",
    "CosyVoiceTTSProvider",
    "SpeechArtifact",
    "SpeechSegment",
    "SpeechToSpeechProvider",
    "STTProvider",
    "TTSProvider",
    "VADProvider",
    "TranscriptResult",
]


def __getattr__(name: str):
    if name == "CosyVoiceTTSProvider":
        from .cosyvoice_provider import CosyVoiceTTSProvider

        return CosyVoiceTTSProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
