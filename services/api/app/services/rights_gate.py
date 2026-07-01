from __future__ import annotations

from fastapi import HTTPException, status

from services.api.app.schemas.voice_profile import VoiceProfile

BLOCKED_RIGHTS_MESSAGE = "Generation blocked: this voice profile is missing approved rights metadata."


def _text_value(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _text_items(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def has_required_rights_metadata(profile: VoiceProfile) -> bool:
    rights = getattr(profile, "rights", None)
    style = getattr(profile, "style", None)
    if rights is None or style is None:
        return False

    rights_status = _text_value(getattr(rights, "rights_status", ""))
    approved = bool(getattr(rights, "approved_for_generation", False))
    source_notes = _text_value(getattr(rights, "source_notes", ""))
    consent_notes = _text_value(getattr(rights, "consent_notes", ""))
    intended_use = _text_value(getattr(rights, "intended_use", ""))
    boundary_note = _text_value(getattr(profile, "boundary_note", ""))
    style_summary = _text_value(getattr(style, "summary", ""))
    style_traits = _text_items(getattr(style, "style_traits", []))
    prohibited_associations = _text_items(getattr(style, "prohibited_associations", []))

    return all(
        [
            rights_status in {"original", "licensed", "consented"},
            approved,
            source_notes,
            consent_notes,
            intended_use,
            boundary_note,
            style_summary,
            bool(style_traits),
            bool(prohibited_associations),
        ],
    )


def ensure_voice_allowed(profile: VoiceProfile) -> VoiceProfile:
    if not has_required_rights_metadata(profile):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=BLOCKED_RIGHTS_MESSAGE,
        )

    return profile

