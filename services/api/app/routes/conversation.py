from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import FileResponse

from services.api.app.schemas.conversation import ConversationSessionRecord, ConversationTurnRecord
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.services.conversation_jobs import (
    create_conversation_session,
    get_conversation_session_service,
    get_conversation_turn_service,
    stop_conversation_session,
)
from services.api.app.services.conversation_runtime import synthesizeConversationTurn
from services.api.app.services.rights_gate import ensure_voice_allowed
from services.api.app.voice_registry.bundled_voice import VOICE_REGISTRY

router = APIRouter(tags=["conversation"])
MAX_CONVERSATION_AUDIO_BYTES = 25 * 1024 * 1024


def _normalize_session_id(session_id: str) -> str:
    cleaned_session_id = session_id.strip()
    if not cleaned_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation session id is required.",
        )

    if Path(cleaned_session_id).name != cleaned_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation session id is invalid.",
        )

    return cleaned_session_id


def _normalize_turn_id(turn_id: str) -> str:
    cleaned_turn_id = turn_id.strip()
    if not cleaned_turn_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation turn id is required.",
        )

    if Path(cleaned_turn_id).name != cleaned_turn_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation turn id is invalid.",
        )

    return cleaned_turn_id


def _capture_source_from_headers(request: Request) -> str:
    raw_capture_source = request.headers.get("x-audio-capture-source", "upload")
    capture_source = raw_capture_source.strip().lower()
    if capture_source not in {"recording", "upload"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation audio capture source must be recording or upload.",
        )
    return capture_source


def _filename_from_headers(request: Request) -> str:
    raw_filename = request.headers.get("x-audio-filename", "spoken-turn.wav")
    filename = Path(raw_filename).name.strip()
    return filename or "spoken-turn.wav"


def _content_type_from_headers(request: Request) -> str:
    return request.headers.get("content-type", "").split(";", 1)[0].strip().lower()


def _voice_profile_from_headers(request: Request):
    raw_voice_id = request.headers.get("x-voice-id", "").strip()
    if not raw_voice_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation voice id is required.",
        )

    profile = VOICE_REGISTRY.get(raw_voice_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found.",
        )

    return ensure_voice_allowed(profile)


def _tone_preset_from_headers(request: Request) -> GenerationTonePreset:
    raw_tone_preset = request.headers.get("x-tone-preset", "measured").strip().lower()
    try:
        return GenerationTonePreset(raw_tone_preset)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation tone preset must be measured, cutting, or grandiose.",
        ) from exc


@router.post("/conversation-sessions", response_model=ConversationSessionRecord)
def start_conversation_session() -> ConversationSessionRecord:
    return create_conversation_session()


@router.get("/conversation-sessions/{session_id}", response_model=ConversationSessionRecord)
def get_conversation_session(session_id: str) -> ConversationSessionRecord:
    normalized_session_id = _normalize_session_id(session_id)
    service = get_conversation_session_service()

    try:
        return service.get_session(normalized_session_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found.",
        ) from exc


@router.post("/conversation-sessions/{session_id}/stop", response_model=ConversationSessionRecord)
def stop_conversation_session_route(session_id: str) -> ConversationSessionRecord:
    normalized_session_id = _normalize_session_id(session_id)

    try:
        return stop_conversation_session(normalized_session_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found.",
        ) from exc


@router.post("/conversation-turns", response_model=ConversationTurnRecord)
async def create_conversation_turn(
    request: Request,
    background_tasks: BackgroundTasks,
) -> ConversationTurnRecord:
    audio_bytes = await request.body()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation audio upload is required.",
        )

    if len(audio_bytes) > MAX_CONVERSATION_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Conversation audio upload is too large.",
        )

    content_type = _content_type_from_headers(request)
    if not content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Conversation audio upload must use an audio content type.",
        )

    session_id = _normalize_session_id(request.headers.get("x-conversation-session-id", ""))
    capture_source = _capture_source_from_headers(request)
    _ = capture_source
    voice_profile = _voice_profile_from_headers(request)
    tone_preset = _tone_preset_from_headers(request)
    audio_filename = _filename_from_headers(request)

    turn_service = get_conversation_turn_service()
    try:
        queued_turn = turn_service.create_turn(
            session_id,
            audio_bytes=audio_bytes,
            audio_mime_type=content_type,
            tone_preset=tone_preset,
            audio_filename=audio_filename,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found.",
        ) from exc

    background_tasks.add_task(
        synthesizeConversationTurn,
        queued_turn.turn_id,
        turn_service=turn_service,
        voice_profile=voice_profile,
    )
    return queued_turn


@router.get("/conversation-turns/{turn_id}", response_model=ConversationTurnRecord)
def get_conversation_turn(turn_id: str) -> ConversationTurnRecord:
    normalized_turn_id = _normalize_turn_id(turn_id)

    try:
        return get_conversation_turn_service().get_turn(normalized_turn_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation turn not found.",
        ) from exc


@router.get("/conversation-turns/{turn_id}/input.wav")
def get_conversation_turn_input(turn_id: str) -> FileResponse:
    normalized_turn_id = _normalize_turn_id(turn_id)
    service = get_conversation_turn_service()
    try:
        record = service.get_turn(normalized_turn_id)
        audio_path = service.get_input_audio_path(normalized_turn_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation turn input audio not found.",
        ) from exc

    return FileResponse(
        path=audio_path,
        media_type=record.attempt.mime_type or "audio/wav",
        filename=f"{normalized_turn_id}.wav",
    )


@router.get("/conversation-turns/{turn_id}/audio")
def get_conversation_turn_audio(turn_id: str) -> FileResponse:
    normalized_turn_id = _normalize_turn_id(turn_id)
    service = get_conversation_turn_service()
    try:
        record = service.get_turn(normalized_turn_id)
        audio_path = service.get_audio_path(normalized_turn_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation turn audio not found.",
        ) from exc

    return FileResponse(
        path=audio_path,
        media_type=record.attempt.mime_type or "audio/wav",
        filename=f"{normalized_turn_id}.wav",
    )
