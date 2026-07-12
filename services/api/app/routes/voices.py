from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from services.api.app.schemas.voice_profile import VoiceProfile
from services.api.app.services.rights_gate import ensure_voice_allowed
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE, VOICE_REGISTRY

router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("", response_model=list[VoiceProfile])
def list_voices() -> list[VoiceProfile]:
    return [ensure_voice_allowed(profile) for profile in VOICE_REGISTRY.values()]


@router.get("/{voice_id}", response_model=VoiceProfile)
def get_voice(voice_id: str) -> VoiceProfile:
    profile = VOICE_REGISTRY.get(voice_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found.",
        )

    return ensure_voice_allowed(profile if profile.id == VESPER_GLASS_PROFILE.id else profile)

