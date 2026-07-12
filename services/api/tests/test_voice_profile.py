from __future__ import annotations

import pytest
from pydantic import ValidationError

from services.api.app.schemas.voice_profile import VoiceProfile, VoiceRights
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE


def test_bundled_voice_profile_includes_required_rights_and_style_fields() -> None:
    profile = VESPER_GLASS_PROFILE

    assert profile.id == "vesper-glass"
    assert profile.display_name == "Vesper Glass"
    assert "original voice profile" in profile.boundary_note.lower()
    assert "protected character" in profile.boundary_note.lower()

    assert profile.rights.rights_status == "original"
    assert profile.rights.approved_for_generation is True
    assert profile.rights.source_notes
    assert profile.rights.consent_notes
    assert profile.rights.intended_use

    assert profile.style.summary
    assert profile.style.style_traits == [
        "Measured theatrical delivery",
        "Cool charm",
        "Philosophical cynicism",
        "Honey-edged sarcasm",
    ]
    assert profile.style.prohibited_associations == [
        "Any protected character voice",
        "Any unlicensed performer likeness",
    ]


def test_bundled_voice_profile_round_trips_through_the_schema() -> None:
    round_tripped = VoiceProfile.model_validate(VESPER_GLASS_PROFILE.model_dump())

    assert round_tripped == VESPER_GLASS_PROFILE


def test_voice_rights_rejects_incomplete_metadata() -> None:
    with pytest.raises(ValidationError):
        VoiceRights.model_validate(
            {
                "rights_status": "original",
                "approved_for_generation": True,
                "source_notes": "Original studio voice seed",
                "intended_use": "Internal testing only",
            },
        )

