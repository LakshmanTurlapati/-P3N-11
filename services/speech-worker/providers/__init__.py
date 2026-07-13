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
    "ConversationResponseProvider",
    "CosyVoiceTTSProvider",
    "FasterWhisperSTTProvider",
    "SpeechArtifact",
    "SpeechSegment",
    "SpeechToSpeechProvider",
    "SileroVADProvider",
    "VesperConversationResponder",
    "STTProvider",
    "TTSProvider",
    "VADProvider",
    "TranscriptResult",
]


def __getattr__(name: str):
    if name == "ConversationResponseProvider":
        from .conversation_provider import ConversationResponseProvider

        return ConversationResponseProvider
    if name == "CosyVoiceTTSProvider":
        from .cosyvoice_provider import CosyVoiceTTSProvider

        return CosyVoiceTTSProvider
    if name == "FasterWhisperSTTProvider":
        from .faster_whisper_stt_provider import FasterWhisperSTTProvider

        return FasterWhisperSTTProvider
    if name == "SileroVADProvider":
        from .silero_vad_provider import SileroVADProvider

        return SileroVADProvider
    if name == "VesperConversationResponder":
        from .conversation_provider import VesperConversationResponder

        return VesperConversationResponder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
