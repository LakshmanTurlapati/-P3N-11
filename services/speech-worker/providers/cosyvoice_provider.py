from __future__ import annotations

import io
import os
import struct
import sys
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from audio.normalization import normalize_audio
from providers.contracts import SpeechArtifact, TTSProvider

DEFAULT_CHECKPOINT_NAME = "Fun-CosyVoice3-0.5B-2512"
DEFAULT_MODEL_DIR = Path("pretrained_models/Fun-CosyVoice3-0.5B")
DEFAULT_PROMPT_AUDIO = Path("asset/zero_shot_prompt.wav")
DEFAULT_PROMPT_TEXT = (
    "You are a helpful assistant delivering an original theatrical voice "
    "without imitating any real performer or protected character.<|endofprompt|>"
)

TONE_PROMPTS: dict[str, str] = {
    "measured": "Deliver the line with measured, theatrical restraint.",
    "cutting": "Deliver the line with a cutting, icy, honeyed-sarcasm edge.",
    "grandiose": "Deliver the line with grandiose, theatrical presence.",
}


@dataclass(frozen=True, slots=True)
class VoicePromptConfig:
    prompt_text: str
    prompt_audio_path: Path


def _resolve_path(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _flatten_samples(payload: Any) -> list[float]:
    if payload is None:
        return []
    if hasattr(payload, "detach"):
        payload = payload.detach()
    if hasattr(payload, "cpu"):
        payload = payload.cpu()
    if hasattr(payload, "tolist"):
        payload = payload.tolist()
    if isinstance(payload, (list, tuple)):
        samples: list[float] = []
        for item in payload:
            samples.extend(_flatten_samples(item))
        return samples
    if isinstance(payload, (int, float)):
        return [float(payload)]
    raise TypeError(f"Unsupported CosyVoice audio payload: {type(payload)!r}")


def _samples_to_pcm16_bytes(samples: list[float]) -> bytes:
    frames = bytearray()
    for sample in samples:
        clipped = max(-1.0, min(1.0, float(sample)))
        frame = int(round(clipped * 32767.0))
        frame = max(-32768, min(32767, frame))
        frames.extend(struct.pack("<h", frame))
    return bytes(frames)


def _samples_to_wav_bytes(samples: list[float], sample_rate_hz: int) -> bytes:
    if not samples:
        raise RuntimeError("CosyVoice returned no audio samples")

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(_samples_to_pcm16_bytes(samples))
    return buffer.getvalue()


def _extract_tts_speech(segment: Any) -> Any:
    if isinstance(segment, dict):
        if "tts_speech" not in segment:
            raise KeyError("CosyVoice segment missing 'tts_speech'")
        return segment["tts_speech"]
    if hasattr(segment, "tts_speech"):
        return getattr(segment, "tts_speech")
    raise TypeError(f"Unsupported CosyVoice segment type: {type(segment)!r}")


class CosyVoiceTTSProvider(TTSProvider):
    provider_name = "cosyvoice"

    def __init__(
        self,
        *,
        repo_root: str | Path | None = None,
        model_dir: str | Path | None = None,
        prompt_audio_path: str | Path | None = None,
        prompt_text: str = DEFAULT_PROMPT_TEXT,
        checkpoint_name: str = DEFAULT_CHECKPOINT_NAME,
        backend: Any | None = None,
    ) -> None:
        self.repo_root = _resolve_path(repo_root or os.environ.get("COSYVOICE_REPO_DIR", "third_party/CosyVoice"))
        self.checkpoint_name = checkpoint_name
        self.model_dir = _resolve_path(model_dir or self.repo_root / DEFAULT_MODEL_DIR)
        self.prompt_audio_path = _resolve_path(prompt_audio_path or self.repo_root / DEFAULT_PROMPT_AUDIO)
        self.prompt_text = prompt_text
        self._backend = backend
        self._voice_profiles = {
            "vesper-glass": VoicePromptConfig(
                prompt_text=self.prompt_text,
                prompt_audio_path=self.prompt_audio_path,
            )
        }

    def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        voice_profile = self._voice_profiles.get(voice_id)
        if voice_profile is None:
            raise ValueError(f"Unknown CosyVoice baseline voice_id: {voice_id}")

        backend = self._backend or self._load_backend()
        sample_rate_hz = self._backend_sample_rate_hz(backend)
        tone_instruction = self._tone_instruction(tone)
        prompt_text = " ".join(
            part
            for part in (
                voice_profile.prompt_text.strip(),
                tone_instruction,
            )
            if part
        )
        segments = list(
            backend.inference_zero_shot(
                text,
                prompt_text,
                str(voice_profile.prompt_audio_path),
                stream=False,
            )
        )
        if not segments:
            raise RuntimeError("CosyVoice returned no generation segments")

        collected_samples: list[float] = []
        for segment in segments:
            collected_samples.extend(_flatten_samples(_extract_tts_speech(segment)))

        source_artifact = SpeechArtifact(
            audio_bytes=_samples_to_wav_bytes(collected_samples, sample_rate_hz),
            sample_rate_hz=sample_rate_hz,
            mime_type="audio/wav",
            provider_name=self.provider_name,
        )
        return normalize_audio(source_artifact, target_sample_rate_hz=sample_rate_hz)

    def _backend_sample_rate_hz(self, backend: Any) -> int:
        sample_rate = getattr(backend, "sample_rate", None)
        if sample_rate is None:
            sample_rate = getattr(backend, "sample_rate_hz", None)
        if sample_rate is None:
            sample_rate = 24_000
        return int(sample_rate)

    def _tone_instruction(self, tone: str | None) -> str:
        if tone is None:
            return ""
        normalized_tone = tone.strip().lower()
        if normalized_tone not in TONE_PROMPTS:
            raise ValueError(f"Unsupported CosyVoice tone preset: {tone}")
        return TONE_PROMPTS[normalized_tone]

    def _load_backend(self) -> Any:
        self._ensure_repo_on_path()
        try:
            from cosyvoice.cli.cosyvoice import AutoModel
        except ImportError as exc:
            raise RuntimeError(
                "CosyVoice repo checkout is not available on the worker path. "
                "Point COSYVOICE_REPO_DIR at the approved FunAudioLLM/CosyVoice checkout "
                "before attempting synthesis."
            ) from exc

        return AutoModel(model_dir=str(self.model_dir))

    def _ensure_repo_on_path(self) -> None:
        for path in (
            self.repo_root,
            self.repo_root / "third_party" / "Matcha-TTS",
        ):
            path_str = str(path)
            if path.exists() and path_str not in sys.path:
                sys.path.insert(0, path_str)
