from __future__ import annotations

import pytest
from fastapi import HTTPException

from services.api.app.main import app
from services.api.app.routes.voices import get_voice, list_voices
from services.api.app.schemas.voice_profile import VoiceProfile, VoiceRights, VoiceStyle
from services.api.app.services.rights_gate import (
    BLOCKED_RIGHTS_MESSAGE,
    ensure_voice_allowed,
    has_required_rights_metadata,
)
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE


def test_voice_registry_route_returns_the_bundled_profile() -> None:
    assert app.url_path_for("get_voice", voice_id="vesper-glass") == "/voices/vesper-glass"

    payload = get_voice("vesper-glass")

    assert payload.id == "vesper-glass"
    assert payload.display_name == "Vesper Glass"
    assert payload.rights.approved_for_generation is True


def test_voice_registry_list_returns_the_bundled_profile() -> None:
    payloads = list_voices()

    assert [payload.id for payload in payloads] == ["vesper-glass"]
    assert payloads[0].display_name == "Vesper Glass"


def test_rights_gate_allows_the_server_owned_bundled_profile() -> None:
    assert has_required_rights_metadata(VESPER_GLASS_PROFILE) is True
    assert ensure_voice_allowed(VESPER_GLASS_PROFILE) is VESPER_GLASS_PROFILE


def test_rights_gate_blocks_unapproved_profiles_with_the_phase_message() -> None:
    profile = VoiceProfile.model_construct(
        id="blocked-voice",
        display_name="Blocked Voice",
        boundary_note="Original voice profile with a theatrical edge.",
        rights=VoiceRights.model_construct(
            rights_status="original",
            approved_for_generation=False,
            source_notes="Original internal seed",
            consent_notes="Documented but not approved",
            intended_use="Internal testing",
        ),
        style=VoiceStyle.model_construct(
            summary="Measured theatrical delivery",
            style_traits=["Measured theatrical delivery"],
            prohibited_associations=["Any protected character voice"],
        ),
    )

    with pytest.raises(HTTPException) as excinfo:
        ensure_voice_allowed(profile)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == BLOCKED_RIGHTS_MESSAGE


def test_rights_gate_blocks_incomplete_metadata_with_the_phase_message() -> None:
    profile = VoiceProfile.model_construct(
        id="incomplete-voice",
        display_name="Incomplete Voice",
        boundary_note="Original voice profile with a theatrical edge.",
        rights=VoiceRights.model_construct(
            rights_status="original",
            approved_for_generation=True,
            source_notes="Original internal seed",
            consent_notes="",
            intended_use="Internal testing",
        ),
        style=VoiceStyle.model_construct(
            summary="Measured theatrical delivery",
            style_traits=["Measured theatrical delivery"],
            prohibited_associations=["Any protected character voice"],
        ),
    )

    with pytest.raises(HTTPException) as excinfo:
        ensure_voice_allowed(profile)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == BLOCKED_RIGHTS_MESSAGE
