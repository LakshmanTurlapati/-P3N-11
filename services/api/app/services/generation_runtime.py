from __future__ import annotations

import io
import os
import sys
import threading
import wave
from functools import lru_cache
from pathlib import Path
from typing import Any

from services.api.app.schemas.generation import GenerationJobRecord
from services.api.app.services.generation_jobs import GenerationJobService

TEST_FAILURE_MARKER_ENV = "THEATRICAL_VOICE_STUDIO_TEST_FAILURE_MARKER"
TEST_FAILURE_MARKER = "playwright-fail-once"
WORKER_ROOT_ENV = "THEATRICAL_VOICE_STUDIO_WORKER_ROOT"
PLAYWRIGHT_GATES = ("CI", "THEATRICAL_VOICE_STUDIO_PLAYWRIGHT")

_PLAYWRIGHT_FAILURE_LOCK = threading.Lock()
_playwright_failure_consumed = False


def disable_background_generation(*args: Any, **kwargs: Any) -> None:
    """No-op background task used by tests that need to suppress dispatch."""


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _playwright_failure_gate_active() -> bool:
    return any(_is_truthy(os.environ.get(env_name)) for env_name in PLAYWRIGHT_GATES)


def _worker_root() -> Path:
    configured_root = os.environ.get(WORKER_ROOT_ENV)
    if configured_root:
        worker_root = Path(configured_root)
    else:
        worker_root = Path(__file__).resolve().parents[4] / "services" / "speech-worker"

    if not worker_root.exists():
        raise RuntimeError(
            "Approved speech-worker root not found. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory."
        )

    providers_dir = worker_root / "providers"
    if not providers_dir.exists():
        raise RuntimeError(
            "Approved speech-worker root is missing the providers package. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory."
        )

    return worker_root


def _ensure_worker_root_on_path() -> Path:
    worker_root = _worker_root()
    worker_root_str = str(worker_root)
    if worker_root_str not in sys.path:
        sys.path.insert(0, worker_root_str)
    return worker_root


def _load_cosyvoice_provider_class():
    _ensure_worker_root_on_path()
    try:
        from providers import CosyVoiceTTSProvider
    except ImportError as exc:  # pragma: no cover - exercised only when worker checkout is missing
        raise RuntimeError(
            "CosyVoice provider could not be imported from the approved worker root."
        ) from exc

    return CosyVoiceTTSProvider


@lru_cache(maxsize=1)
def get_generation_tts_provider():
    provider_class = _load_cosyvoice_provider_class()
    return provider_class()


def _cleanup_test_failure_marker(text: str) -> str:
    cleaned_text = text.replace(TEST_FAILURE_MARKER, "")
    return " ".join(cleaned_text.split()).strip()


def _consume_playwright_failure_marker(text: str) -> tuple[bool, str]:
    if TEST_FAILURE_MARKER not in text or not _playwright_failure_gate_active():
        return False, text

    global _playwright_failure_consumed
    with _PLAYWRIGHT_FAILURE_LOCK:
        if _playwright_failure_consumed:
            return False, _cleanup_test_failure_marker(text)

        _playwright_failure_consumed = True

    os.environ.pop(TEST_FAILURE_MARKER_ENV, None)
    return True, _cleanup_test_failure_marker(text)


def _artifact_duration_ms(artifact: Any) -> int:
    duration_ms = getattr(artifact, "duration_ms", None)
    if duration_ms is not None:
        return int(duration_ms)

    audio_bytes = getattr(artifact, "audio_bytes", b"")
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate_hz = wav_file.getframerate()
            if sample_rate_hz > 0:
                return int(round(frame_count / sample_rate_hz * 1000))
    except (wave.Error, EOFError):
        pass

    return 0


def process_generation_job(
    job_id: str,
    *,
    job_service: GenerationJobService | None = None,
    provider: Any | None = None,
) -> GenerationJobRecord:
    job_service = job_service or GenerationJobService.from_env()

    running_record = job_service.mark_running(job_id)

    should_fail, text_for_provider = _consume_playwright_failure_marker(running_record.text)
    if should_fail:
        return job_service.mark_failed(
            job_id,
            error_message="playwright-fail-once marker triggered before synthesis.",
        )

    try:
        tts_provider = provider or get_generation_tts_provider()
        artifact = tts_provider.synthesize(
            text_for_provider,
            running_record.voice_id,
            tone=running_record.tone_preset.value,
        )
        provider_name = getattr(artifact, "provider_name", None) or getattr(tts_provider, "provider_name")
        return job_service.mark_succeeded(
            job_id,
            audio_bytes=getattr(artifact, "audio_bytes"),
            mime_type=getattr(artifact, "mime_type"),
            provider_name=provider_name,
            audio_duration_ms=_artifact_duration_ms(artifact),
        )
    except Exception as exc:
        return job_service.mark_failed(job_id, error_message=str(exc))
