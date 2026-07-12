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
    "SileroVADProvider",
    "STTProvider",
    "TTSProvider",
    "VADProvider",
    "TranscriptResult",
]


def __getattr__(name: str):
    if name == "CosyVoiceTTSProvider":
        from .cosyvoice_provider import CosyVoiceTTSProvider

        return CosyVoiceTTSProvider
    if name == "SileroVADProvider":
        from .silero_vad_provider import SileroVADProvider

        return SileroVADProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
