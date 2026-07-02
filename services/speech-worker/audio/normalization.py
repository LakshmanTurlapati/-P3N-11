from __future__ import annotations

import io
import subprocess
import wave
from dataclasses import replace

from providers.contracts import SpeechArtifact


def _duration_ms_from_wav_bytes(wav_bytes: bytes) -> int | None:
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        frame_count = wav_file.getnframes()
        sample_rate_hz = wav_file.getframerate()
        if sample_rate_hz <= 0:
            return None
        return int(round(frame_count / sample_rate_hz * 1000))


def normalize_audio(
    artifact: SpeechArtifact,
    *,
    target_sample_rate_hz: int | None = None,
) -> SpeechArtifact:
    sample_rate_hz = target_sample_rate_hz or artifact.sample_rate_hz
    if sample_rate_hz <= 0:
        raise ValueError("target_sample_rate_hz must be a positive integer")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
        "-i",
        "pipe:0",
        "-ac",
        "1",
        "-ar",
        str(sample_rate_hz),
        "-sample_fmt",
        "s16",
        "-f",
        "wav",
        "pipe:1",
    ]
    try:
        completed = subprocess.run(
            command,
            input=artifact.audio_bytes,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg is required to normalize CosyVoice audio. "
            "Install ffmpeg in the worker runtime before synthesis."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
        raise RuntimeError(
            f"FFmpeg normalization failed for CosyVoice audio: {stderr or exc}"
        ) from exc
    normalized_bytes = completed.stdout
    duration_ms = _duration_ms_from_wav_bytes(normalized_bytes)

    return replace(
        artifact,
        audio_bytes=normalized_bytes,
        sample_rate_hz=sample_rate_hz,
        mime_type="audio/wav",
        duration_ms=duration_ms,
    )
