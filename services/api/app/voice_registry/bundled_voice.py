from __future__ import annotations

from services.api.app.schemas.voice_profile import VoiceProfile, VoiceRights, VoiceStyle

VESPER_GLASS_PROFILE = VoiceProfile(
    id="vesper-glass",
    display_name="Vesper Glass",
    boundary_note=(
        "Original voice profile with a theatrical trickster edge; not a clone of any "
        "actor or protected character."
    ),
    rights=VoiceRights(
        rights_status="original",
        approved_for_generation=True,
        source_notes=(
            "Server-owned original voice seed for the no-login studio; no third-party "
            "performance reference is embedded in the registry record."
        ),
        consent_notes=(
            "Consent and rights notes are stored with the registry record so the backend "
            "can enforce generation policy directly."
        ),
        intended_use=(
            "Internal studio testing and rights-gated generation experiments during "
            "Phase 1."
        ),
    ),
    style=VoiceStyle(
        summary=(
            "Measured theatrical delivery with cool charm, philosophical cynicism, and "
            "honey-edged sarcasm."
        ),
        style_traits=[
            "Measured theatrical delivery",
            "Cool charm",
            "Philosophical cynicism",
            "Honey-edged sarcasm",
        ],
        prohibited_associations=[
            "Any protected character voice",
            "Any unlicensed performer likeness",
        ],
    ),
)

VOICE_REGISTRY = {VESPER_GLASS_PROFILE.id: VESPER_GLASS_PROFILE}

