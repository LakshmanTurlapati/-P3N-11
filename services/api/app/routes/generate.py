from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from services.api.app.schemas.generation import GenerationJobRecord, GenerationRequest
from services.api.app.services.generation_jobs import GenerationJobService
from services.api.app.services.generation_runtime import process_generation_job
from services.api.app.services.rights_gate import ensure_voice_allowed
from services.api.app.voice_registry.bundled_voice import VOICE_REGISTRY

router = APIRouter(tags=["generation"])


@lru_cache(maxsize=1)
def get_generation_job_service() -> GenerationJobService:
    return GenerationJobService.from_env()


@router.post("/generate", response_model=GenerationJobRecord)
def generate(request: GenerationRequest, background_tasks: BackgroundTasks) -> GenerationJobRecord:
    profile = VOICE_REGISTRY.get(request.voice_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found.",
        )

    allowed_profile = ensure_voice_allowed(profile)
    job_service = get_generation_job_service()
    queued_job = job_service.create_job(request, allowed_profile)
    background_tasks.add_task(
        process_generation_job,
        queued_job.job_id,
        job_service=job_service,
    )
    return queued_job


@router.get("/generations/{job_id}", response_model=GenerationJobRecord)
def get_generation(job_id: str) -> GenerationJobRecord:
    try:
        return get_generation_job_service().get_job(job_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found.",
        ) from exc


@router.get("/generations/{job_id}/audio")
def get_generation_audio(job_id: str) -> FileResponse:
    service = get_generation_job_service()
    try:
        record = service.get_job(job_id)
        audio_path = service.get_audio_path(job_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job audio not found.",
        ) from exc

    return FileResponse(
        path=audio_path,
        media_type=record.attempt.mime_type or "audio/wav",
        filename=f"{job_id}.wav",
    )
