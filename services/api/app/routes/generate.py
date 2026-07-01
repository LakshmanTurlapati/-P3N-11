from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from services.api.app.schemas.generation import GenerationRequest, GenerationResult
from services.api.app.services.rights_gate import ensure_voice_allowed
from services.api.app.services.stub_generation import build_stub_generation_result
from services.api.app.voice_registry.bundled_voice import VOICE_REGISTRY

router = APIRouter(tags=["generation"])


@router.post("/generate", response_model=GenerationResult)
def generate(request: GenerationRequest) -> GenerationResult:
    profile = VOICE_REGISTRY.get(request.voice_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found.",
        )

    allowed_profile = ensure_voice_allowed(profile)
    return build_stub_generation_result(allowed_profile)
