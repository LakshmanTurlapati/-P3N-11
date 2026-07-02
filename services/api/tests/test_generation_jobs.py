from __future__ import annotations

from services.api.app.schemas.generation import GenerationJobStatus, GenerationTonePreset
from services.api.app.schemas.voice_profile import VoiceProfile, VoiceRights, VoiceStyle
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE, VOICE_REGISTRY


def _blocked_voice_profile() -> VoiceProfile:
    return VoiceProfile.model_construct(
        id=VESPER_GLASS_PROFILE.id,
        display_name=VESPER_GLASS_PROFILE.display_name,
        boundary_note=VESPER_GLASS_PROFILE.boundary_note,
        rights=VoiceRights.model_construct(
            rights_status="original",
            approved_for_generation=False,
            source_notes="Bundled internal seed",
            consent_notes="Documented but not approved",
            intended_use="Internal testing",
        ),
        style=VoiceStyle.model_construct(
            summary="Measured theatrical delivery",
            style_traits=["Measured theatrical delivery"],
            prohibited_associations=["Any protected character voice"],
        ),
    )


def test_generation_route_tracks_queued_running_and_succeeded_states(
    client,
    generation_job_service,
    generation_request,
    generation_audio_bytes,
) -> None:
    response = client.post("/generate", json=generation_request.model_dump(mode="json"))

    assert response.status_code == 200

    payload = response.json()
    assert payload["job_id"].startswith("job-")
    assert payload["status"] == GenerationJobStatus.QUEUED.value
    assert payload["voice_id"] == VESPER_GLASS_PROFILE.id
    assert payload["text"] == generation_request.text
    assert payload["tone_preset"] == GenerationTonePreset.MEASURED.value
    assert payload["playback_url"] is None
    assert payload["audio_duration_ms"] is None
    assert payload["retry_of_job_id"] is None
    assert payload["attempt"]["status"] == GenerationJobStatus.QUEUED.value

    job_id = payload["job_id"]
    running_job = generation_job_service.mark_running(job_id)
    assert running_job.status == GenerationJobStatus.RUNNING
    assert running_job.attempt.status == GenerationJobStatus.RUNNING

    succeeded_job = generation_job_service.mark_succeeded(
        job_id,
        audio_bytes=generation_audio_bytes,
        mime_type="audio/wav",
        provider_name="prototype-baseline-stub",
        audio_duration_ms=1536,
    )

    assert succeeded_job.status == GenerationJobStatus.SUCCEEDED
    assert succeeded_job.playback_url == f"/generations/{job_id}/audio"
    assert succeeded_job.audio_duration_ms == 1536
    assert succeeded_job.attempt.status == GenerationJobStatus.SUCCEEDED

    detail_response = client.get(f"/generations/{job_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["status"] == GenerationJobStatus.SUCCEEDED.value
    assert detail["playback_url"] == f"/generations/{job_id}/audio"
    assert detail["audio_duration_ms"] == 1536
    assert detail["attempt"]["status"] == GenerationJobStatus.SUCCEEDED.value
    assert detail["attempt"]["provider_name"] == "prototype-baseline-stub"
    assert detail["attempt"]["mime_type"] == "audio/wav"

    audio_response = client.get(f"/generations/{job_id}/audio")

    assert audio_response.status_code == 200
    assert audio_response.headers["content-type"].startswith("audio/wav")
    assert audio_response.content == generation_audio_bytes


def test_generation_retry_reuses_cached_inputs_and_keeps_failed_job_visible(
    generation_job_service,
    generation_request,
) -> None:
    created_job = generation_job_service.create_job(
        generation_request,
        VESPER_GLASS_PROFILE,
    )
    failed_job = generation_job_service.mark_failed(
        created_job.job_id,
        error_message="cosyvoice timed out",
    )

    assert failed_job.status == GenerationJobStatus.FAILED
    assert failed_job.attempt.status == GenerationJobStatus.FAILED
    assert failed_job.attempt.error_message == "cosyvoice timed out"

    retried_job = generation_job_service.retry_job(failed_job.job_id)

    assert retried_job.job_id != failed_job.job_id
    assert retried_job.retry_of_job_id == failed_job.job_id
    assert retried_job.voice_id == failed_job.voice_id
    assert retried_job.text == failed_job.text
    assert retried_job.tone_preset == failed_job.tone_preset
    assert retried_job.status == GenerationJobStatus.QUEUED
    assert retried_job.attempt.status == GenerationJobStatus.QUEUED

    preserved_failed_job = generation_job_service.get_job(failed_job.job_id)

    assert preserved_failed_job.status == GenerationJobStatus.FAILED
    assert preserved_failed_job.attempt.error_message == "cosyvoice timed out"


def test_generation_route_blocks_unapproved_voices_before_job_creation(client) -> None:
    blocked_profile = _blocked_voice_profile()
    original_profile = VOICE_REGISTRY[VESPER_GLASS_PROFILE.id]
    VOICE_REGISTRY[VESPER_GLASS_PROFILE.id] = blocked_profile
    try:
        response = client.post(
            "/generate",
            json={
                "voice_id": VESPER_GLASS_PROFILE.id,
                "text": "Deliver one measured, theatrical line.",
                "tone_preset": GenerationTonePreset.MEASURED.value,
            },
        )
    finally:
        VOICE_REGISTRY[VESPER_GLASS_PROFILE.id] = original_profile

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Generation blocked: this voice profile is missing approved rights metadata."
    }
