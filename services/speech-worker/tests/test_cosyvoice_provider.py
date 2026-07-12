from __future__ import annotations

import io
import wave

from providers.contracts import SpeechArtifact, TTSProvider
from providers.cosyvoice_provider import CosyVoiceTTSProvider


def _wav_bytes(sample_rate_hz: int = 24_000, frame_count: int = 2_400) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


class FakeCosyVoiceBackend:
    def __init__(self, sample_rate_hz: int = 24_000) -> None:
        self.sample_rate = sample_rate_hz
        self.calls: list[dict[str, object]] = []

    def inference_zero_shot(
        self,
        text: str,
        prompt_text: str,
        prompt_audio_path: str,
        *,
        stream: bool = False,
    ):
        self.calls.append(
            {
                "text": text,
                "prompt_text": prompt_text,
                "prompt_audio_path": prompt_audio_path,
                "stream": stream,
            }
        )
        yield {"tts_speech": [0.0, 0.4, -0.4, 0.0]}


def test_cosyvoice_provider_synthesizes_a_playable_baseline_and_steers_tone(
    monkeypatch,
    tmp_path,
) -> None:
    repo_root = tmp_path / "CosyVoice"
    model_dir = repo_root / "pretrained_models" / "Fun-CosyVoice3-0.5B"
    prompt_audio_path = repo_root / "asset" / "zero_shot_prompt.wav"
    backend = FakeCosyVoiceBackend()
    normalized_artifact = SpeechArtifact(
        audio_bytes=_wav_bytes(),
        sample_rate_hz=backend.sample_rate,
        mime_type="audio/wav",
        provider_name="cosyvoice",
        duration_ms=100,
    )
    captured_inputs: list[tuple[SpeechArtifact, int | None]] = []

    def fake_normalize_audio(
        artifact: SpeechArtifact,
        *,
        target_sample_rate_hz: int | None = None,
    ) -> SpeechArtifact:
        captured_inputs.append((artifact, target_sample_rate_hz))
        return normalized_artifact

    monkeypatch.setattr("providers.cosyvoice_provider.normalize_audio", fake_normalize_audio)

    provider = CosyVoiceTTSProvider(
        repo_root=repo_root,
        model_dir=model_dir,
        prompt_audio_path=prompt_audio_path,
        backend=backend,
    )

    artifact = provider.synthesize("The stage is mine.", "vesper-glass", tone="cutting")

    assert isinstance(provider, TTSProvider)
    assert provider.provider_name == "cosyvoice"
    assert provider.repo_root == repo_root
    assert provider.model_dir == model_dir
    assert provider.prompt_audio_path == prompt_audio_path
    assert artifact == normalized_artifact

    raw_artifact, target_sample_rate_hz = captured_inputs[0]
    assert raw_artifact.provider_name == "cosyvoice"
    assert raw_artifact.mime_type == "audio/wav"
    assert raw_artifact.audio_bytes.startswith(b"RIFF")
    assert target_sample_rate_hz == backend.sample_rate

    call = backend.calls[0]
    assert call["text"] == "The stage is mine."
    assert call["prompt_audio_path"] == str(prompt_audio_path)
    assert call["stream"] is False
    assert "cutting" in str(call["prompt_text"]).lower()
