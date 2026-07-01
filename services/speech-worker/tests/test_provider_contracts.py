from __future__ import annotations

from providers.contracts import (
    AudioBuffer,
    SpeechArtifact,
    SpeechSegment,
    SpeechToSpeechProvider,
    STTProvider,
    TTSProvider,
    TranscriptResult,
    VADProvider,
)


class DummyVAD:
    provider_name = "dummy-vad"

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        return [SpeechSegment(start_ms=0, end_ms=len(audio.pcm16), confidence=0.9)]


class DummySTT:
    provider_name = "dummy-stt"

    def transcribe(self, audio: AudioBuffer) -> TranscriptResult:
        return TranscriptResult(text=f"transcribed:{len(audio.pcm16)}", language="en")


class DummyTTS:
    provider_name = "dummy-tts"

    def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        payload = f"{voice_id}:{tone or 'neutral'}:{text}".encode("utf-8")
        return SpeechArtifact(
            audio_bytes=payload,
            sample_rate_hz=22_050,
            mime_type="audio/wav",
            provider_name=self.provider_name,
            duration_ms=25,
        )


class DummySpeechToSpeech:
    provider_name = "dummy-s2s"

    def transform(
        self,
        audio: AudioBuffer,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        payload = f"{voice_id}:{tone or 'neutral'}:{len(audio.pcm16)}".encode("utf-8")
        return SpeechArtifact(
            audio_bytes=payload,
            sample_rate_hz=audio.sample_rate_hz,
            mime_type=audio.mime_type,
            provider_name=self.provider_name,
            duration_ms=33,
        )


def test_provider_contracts_are_swappable_and_audio_shape_driven() -> None:
    audio = AudioBuffer(pcm16=b"\x00\x01\x02\x03", sample_rate_hz=16_000)

    vad = DummyVAD()
    stt = DummySTT()
    tts = DummyTTS()
    s2s = DummySpeechToSpeech()

    assert isinstance(vad, VADProvider)
    assert isinstance(stt, STTProvider)
    assert isinstance(tts, TTSProvider)
    assert isinstance(s2s, SpeechToSpeechProvider)

    assert vad.detect_speech_segments(audio)[0].start_ms == 0
    assert stt.transcribe(audio).text == "transcribed:4"
    assert tts.synthesize("hello", "vesper-glass").provider_name == "dummy-tts"
    assert s2s.transform(audio, "vesper-glass").provider_name == "dummy-s2s"

    assert audio.channels == 1
    assert audio.mime_type == "audio/wav"
