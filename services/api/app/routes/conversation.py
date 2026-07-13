from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from services.api.app.schemas.conversation import ConversationSessionRecord
from services.api.app.services.conversation_jobs import (
    create_conversation_session,
    get_conversation_session_service,
    stop_conversation_session,
)

router = APIRouter(tags=["conversation"])


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
