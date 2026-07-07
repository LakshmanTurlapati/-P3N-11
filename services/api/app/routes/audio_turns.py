from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

from services.api.app.schemas.audio_turn import AudioTurnJobRecord, AudioTurnRequest
from services.api.app.services.audio_turn_jobs import AudioTurnJobService

router = APIRouter(tags=["audio-turns"])

MAX_AUDIO_BYTES = 25 * 1024 * 1024


@lru_cache(maxsize=1)
def get_audio_turn_job_service() -> AudioTurnJobService:
    return AudioTurnJobService.from_env()


def _capture_source_from_headers(request: Request) -> str:
    raw_capture_source = request.headers.get("x-audio-capture-source", "upload")
    capture_source = raw_capture_source.strip().lower()
    if capture_source not in {"recording", "upload"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio capture source must be recording or upload.",
        )
    return capture_source


def _filename_from_headers(request: Request) -> str:
    raw_filename = request.headers.get("x-audio-filename", "spoken-turn.audio")
    filename = Path(raw_filename).name.strip()
    return filename or "spoken-turn.audio"


def _content_type_from_headers(request: Request) -> str:
    raw_content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    return raw_content_type


@router.post("/audio-turns", response_model=AudioTurnJobRecord)
async def create_audio_turn(request: Request) -> AudioTurnJobRecord:
    audio_bytes = await request.body()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio upload is required.",
        )

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio upload is too large.",
        )

    content_type = _content_type_from_headers(request)
    if not content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Audio upload must use an audio content type.",
        )

    audio_request = AudioTurnRequest(
        capture_source=_capture_source_from_headers(request),
        audio_filename=_filename_from_headers(request),
        audio_mime_type=content_type,
    )
    return get_audio_turn_job_service().create_job(audio_request, audio_bytes)


@router.get("/audio-turns/{job_id}", response_model=AudioTurnJobRecord)
def get_audio_turn(job_id: str) -> AudioTurnJobRecord:
    try:
        return get_audio_turn_job_service().get_job(job_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio turn job not found.",
        ) from exc


@router.get("/audio-turns/{job_id}/audio")
def get_audio_turn_audio(job_id: str) -> FileResponse:
    service = get_audio_turn_job_service()
    try:
        record = service.get_job(job_id)
        audio_path = service.get_audio_path(job_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio turn job audio not found.",
        ) from exc

    return FileResponse(
        path=audio_path,
        media_type=record.attempt.mime_type or record.audio_mime_type or "audio/wav",
        filename=record.audio_filename,
    )
