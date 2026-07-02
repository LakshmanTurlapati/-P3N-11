from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.schemas.voice_profile import VoiceProfile, VoiceRights, VoiceStyle
from services.api.app.voice_registry.bundled_voice import VOICE_REGISTRY


client = TestClient(app)


def test_generate_stub_returns_queued_prototype_job() -> None:
    response = client.post(
        "/generate",
        json={
            "voice_id": "vesper-glass",
            "text": "Deliver one measured, theatrical line.",
            "tone_preset": "measured",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["provider_type"] == "prototype-baseline-stub"
    assert payload["job_id"].startswith("job-")
    assert payload["status"] == "queued"
    assert payload["voice_id"] == "vesper-glass"
    assert payload["text"] == "Deliver one measured, theatrical line."
    assert payload["tone_preset"] == "measured"
    assert payload["rights_check"] == {
        "status": "approved",
        "approved_for_generation": True,
        "message": "Rights gate approved the bundled voice profile.",
    }
    assert payload["provider_trace"] == [
        {
            "stage": "rights-gate",
            "provider": "server-registry",
            "detail": "Bundled Vesper Glass profile passed the approval check.",
        },
        {
            "stage": "job-queue",
            "provider": "api-control-plane",
            "detail": "Queued a prototype baseline job with the submitted text and tone preset.",
        },
        {
            "stage": "provider-boundary",
            "provider": "prototype-baseline-stub",
            "detail": "Speech-worker contracts stay swappable behind the prototype baseline stub.",
        },
    ]
    assert "result_metadata" not in payload
    assert "audio" not in payload
    assert "playback_url" not in payload

    started_at = datetime.fromisoformat(payload["timing"]["started_at"].replace("Z", "+00:00"))
    ended_at = datetime.fromisoformat(payload["timing"]["ended_at"].replace("Z", "+00:00"))
    assert started_at.tzinfo is not None
    assert ended_at.tzinfo is not None
    assert ended_at >= started_at
    assert payload["timing"]["duration_ms"] == 18


def test_generate_stub_blocks_unapproved_profiles_with_exact_message() -> None:
    blocked_profile = VoiceProfile.model_construct(
        id="vesper-glass",
        display_name="Vesper Glass",
        boundary_note="Original voice profile with a theatrical edge.",
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

    original_profile = VOICE_REGISTRY["vesper-glass"]
    VOICE_REGISTRY["vesper-glass"] = blocked_profile
    try:
        response = client.post(
            "/generate",
            json={
                "voice_id": "vesper-glass",
                "text": "Deliver one measured, theatrical line.",
                "tone_preset": "measured",
            },
        )
    finally:
        VOICE_REGISTRY["vesper-glass"] = original_profile

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Generation blocked: this voice profile is missing approved rights metadata."
    }
