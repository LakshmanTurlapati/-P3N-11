from __future__ import annotations

import io
import wave

from providers import AudioBuffer, SpeechSegment, SileroVADProvider


def _wav_bytes(
    *,
    sample_rate_hz: int = 16_000,
    lead_silence_ms: int = 120,
    speech_ms: int = 720,
    trail_silence_ms: int = 120,
    amplitude: int = 16_000,
) -> bytes:
    samples: list[int] = []
    for duration_ms, value in (
        (lead_silence_ms, 0),
        (speech_ms, amplitude),
        (trail_silence_ms, 0),
    ):
        sample_count = int(sample_rate_hz * duration_ms / 1000)
        samples.extend([value] * sample_count)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(b"".join(int(sample).to_bytes(2, "little", signed=True) for sample in samples))
    return buffer.getvalue()


def _audio_buffer_from_wav_bytes(wav_bytes: bytes) -> AudioBuffer:
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        return AudioBuffer(
            pcm16=wav_file.readframes(wav_file.getnframes()),
            sample_rate_hz=wav_file.getframerate(),
            channels=wav_file.getnchannels(),
            mime_type="audio/wav",
        )


def test_silero_vad_provider_uses_a_backend_and_returns_ordered_segments() -> None:
    class Backend:
        def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
            assert audio.sample_rate_hz == 16_000
            return [
                SpeechSegment(start_ms=100, end_ms=420, confidence=0.84),
                SpeechSegment(start_ms=560, end_ms=920, confidence=0.76),
            ]

    provider = SileroVADProvider(backend=Backend())
    audio = _audio_buffer_from_wav_bytes(_wav_bytes())

    segments = provider.detect_speech_segments(audio)

    assert provider.provider_name == "silero-vad"
    assert segments == [
        SpeechSegment(start_ms=100, end_ms=420, confidence=0.84),
        SpeechSegment(start_ms=560, end_ms=920, confidence=0.76),
    ]


def test_silero_vad_provider_fixture_fallback_detects_speech_from_wav_only_audio() -> None:
    provider = SileroVADProvider(force_fixture_fallback=True)
    audio = _audio_buffer_from_wav_bytes(_wav_bytes(amplitude=900))

    segments = provider.detect_speech_segments(audio)

    assert provider.provider_name == "silero-vad"
    assert segments
    assert segments[0].start_ms < segments[0].end_ms
    assert segments[0].confidence is not None
