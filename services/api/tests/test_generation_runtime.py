from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any

from services.api.app.schemas.generation import GenerationJobStatus, GenerationRequest, GenerationTonePreset
from services.api.app.services.generation_runtime import get_generation_tts_provider, process_generation_job
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE


class RecordingProvider:
    provider_name = "fake-cosyvoice"

    def __init__(
        self,
        *,
        audio_bytes: bytes = b"fake-audio-bytes",
        duration_ms: int = 987,
        expected_job_service: Any | None = None,
        expected_job_id: str | None = None,
        raise_on_call: Exception | None = None,
    ) -> None:
        self.audio_bytes = audio_bytes
        self.duration_ms = duration_ms
        self.expected_job_service = expected_job_service
        self.expected_job_id = expected_job_id
        self.raise_on_call = raise_on_call
        self.calls: list[tuple[str, str, str | None]] = []

    def synthesize(self, text: str, voice_id: str, *, tone: str | None = None) -> SimpleNamespace:
        self.calls.append((text, voice_id, tone))
        if self.expected_job_service is not None and self.expected_job_id is not None:
            assert self.expected_job_service.get_job(self.expected_job_id).status == GenerationJobStatus.RUNNING
        if self.raise_on_call is not None:
            raise self.raise_on_call
        return SimpleNamespace(
            audio_bytes=self.audio_bytes,
            sample_rate_hz=24_000,
            mime_type="audio/wav",
            provider_name=self.provider_name,
            duration_ms=self.duration_ms,
        )


def _build_request(text: str = "Deliver one measured, theatrical line.") -> GenerationRequest:
    return GenerationRequest(
        voice_id=VESPER_GLASS_PROFILE.id,
        text=text,
        tone_preset=GenerationTonePreset.MEASURED,
    )


def test_generation_runtime_exports_default_provider_helper() -> None:
    assert get_generation_tts_provider.__name__ == "get_generation_tts_provider"


def test_process_generation_job_advances_a_queued_job_to_succeeded(
    generation_job_service,
    generation_request,
) -> None:
    created_job = generation_job_service.create_job(
        generation_request,
        VESPER_GLASS_PROFILE,
    )
    provider = RecordingProvider(
        expected_job_service=generation_job_service,
        expected_job_id=created_job.job_id,
    )

    updated_job = process_generation_job(
        created_job.job_id,
        job_service=generation_job_service,
        provider=provider,
    )

    assert provider.calls == [
        (generation_request.text, generation_request.voice_id, generation_request.tone_preset.value)
    ]
    assert updated_job.job_id == created_job.job_id
    assert updated_job.status == GenerationJobStatus.SUCCEEDED
    assert updated_job.provider_name == provider.provider_name
    assert updated_job.playback_url == f"/generations/{created_job.job_id}/audio"
    assert updated_job.attempt.status == GenerationJobStatus.SUCCEEDED
    assert updated_job.attempt.provider_name == provider.provider_name
    assert updated_job.attempt.mime_type == "audio/wav"
    assert updated_job.audio_duration_ms == provider.duration_ms
    assert generation_job_service.object_store.read_audio(created_job.job_id) == provider.audio_bytes


def test_process_generation_job_marks_provider_errors_as_failed(
    generation_job_service,
) -> None:
    request = _build_request()
    created_job = generation_job_service.create_job(
        request,
        VESPER_GLASS_PROFILE,
    )
    provider = RecordingProvider(
        raise_on_call=RuntimeError("synthetic synthesis failure"),
    )

    updated_job = process_generation_job(
        created_job.job_id,
        job_service=generation_job_service,
        provider=provider,
    )

    assert provider.calls == [(request.text, request.voice_id, request.tone_preset.value)]
    assert updated_job.status == GenerationJobStatus.FAILED
    assert updated_job.playback_url is None
    assert updated_job.audio_duration_ms is None
    assert updated_job.attempt.status == GenerationJobStatus.FAILED
    assert updated_job.attempt.error_message == "synthetic synthesis failure"
    assert generation_job_service.get_job(created_job.job_id).status == GenerationJobStatus.FAILED


def test_process_generation_job_consumes_the_playwright_fail_once_marker(
    generation_job_service,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_TEST_FAILURE_MARKER", "playwright-fail-once")

    runtime_module = importlib.import_module("services.api.app.services.generation_runtime")
    monkeypatch.setattr(runtime_module, "_playwright_failure_consumed", False, raising=False)

    marked_text = "Deliver one measured, theatrical line. playwright-fail-once"
    cleaned_text = "Deliver one measured, theatrical line."
    request = _build_request(marked_text)
    created_job = generation_job_service.create_job(
        request,
        VESPER_GLASS_PROFILE,
    )
    provider = RecordingProvider(
        expected_job_service=generation_job_service,
        expected_job_id=created_job.job_id,
    )

    failed_job = process_generation_job(
        created_job.job_id,
        job_service=generation_job_service,
        provider=provider,
    )

    assert provider.calls == []
    assert failed_job.status == GenerationJobStatus.FAILED
    assert failed_job.attempt.error_message is not None
    assert "playwright-fail-once" in failed_job.attempt.error_message

    retried_job = generation_job_service.retry_job(failed_job.job_id)

    rerun_provider = RecordingProvider(
        expected_job_service=generation_job_service,
        expected_job_id=retried_job.job_id,
    )
    retried_result = process_generation_job(
        retried_job.job_id,
        job_service=generation_job_service,
        provider=rerun_provider,
    )

    assert rerun_provider.calls == [(cleaned_text, request.voice_id, request.tone_preset.value)]
    assert retried_result.status == GenerationJobStatus.SUCCEEDED
    assert retried_result.playback_url == f"/generations/{retried_job.job_id}/audio"
