from __future__ import annotations

import io
import subprocess
import wave

from audio.normalization import normalize_audio
from providers.contracts import SpeechArtifact


def _wav_bytes(sample_rate_hz: int = 24_000, frame_count: int = 2_400) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


def test_normalize_audio_invokes_ffmpeg_and_returns_playable_wav(monkeypatch) -> None:
    normalized_wav = _wav_bytes()
    recorded: dict[str, object] = {}

    def fake_run(cmd, **kwargs):
        recorded["cmd"] = cmd
        recorded["kwargs"] = kwargs
        return subprocess.CompletedProcess(cmd, 0, stdout=normalized_wav, stderr=b"")

    monkeypatch.setattr("audio.normalization.subprocess.run", fake_run)

    artifact = SpeechArtifact(
        audio_bytes=b"raw input bytes",
        sample_rate_hz=48_000,
        mime_type="audio/mpeg",
        provider_name="cosyvoice",
    )

    normalized = normalize_audio(artifact, target_sample_rate_hz=24_000)

    assert recorded["cmd"][0] == "ffmpeg"
    assert "-ac" in recorded["cmd"]
    assert "1" in recorded["cmd"]
    assert "-ar" in recorded["cmd"]
    assert "24000" in recorded["cmd"]
    assert recorded["kwargs"]["input"] == b"raw input bytes"
    assert recorded["kwargs"]["capture_output"] is True
    assert recorded["kwargs"]["check"] is True

    assert normalized.audio_bytes == normalized_wav
    assert normalized.sample_rate_hz == 24_000
    assert normalized.mime_type == "audio/wav"
    assert normalized.provider_name == "cosyvoice"
    assert normalized.duration_ms == 100
