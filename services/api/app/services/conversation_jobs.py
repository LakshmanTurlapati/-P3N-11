from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from services.api.app.schemas.conversation import (
    ConversationSessionRecord,
    ConversationSessionStatus,
    ConversationTurnRecord,
    ConversationSessionTiming,
)


def _now() -> datetime:
    return datetime.now(UTC)


def _milliseconds(delta: timedelta) -> int:
    return max(int(delta.total_seconds() * 1000), 0)


def _session_id() -> str:
    return f"conversation-session-{uuid4().hex[:12]}"


def _validate_session_id(session_id: str) -> str:
    cleaned_session_id = session_id.strip()
    if not cleaned_session_id:
        raise ValueError("session_id must not be empty")

    if Path(cleaned_session_id).name != cleaned_session_id:
        raise ValueError("session_id must not contain path separators")

    return cleaned_session_id


class ConversationSessionService:
    def __init__(
        self,
        *,
        storage_root: Path | str | None = None,
        db_path: Path | str | None = None,
    ) -> None:
        root = Path(storage_root) if storage_root is not None else self._default_storage_root()
        self.storage_root = root
        self.db_path = Path(db_path) if db_path is not None else self.storage_root / "conversation-sessions.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @classmethod
    def from_env(cls) -> "ConversationSessionService":
        storage_root = os.environ.get("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT")
        if storage_root:
            return cls(storage_root=Path(storage_root) / "conversation-sessions")
        return cls(storage_root=cls._default_storage_root())

    @staticmethod
    def _default_storage_root() -> Path:
        return Path(tempfile.gettempdir()) / "theatrical-voice-studio" / "conversation-sessions"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL
                )
                """,
            )

    def _save_record(self, record: ConversationSessionRecord) -> ConversationSessionRecord:
        validated_record = ConversationSessionRecord.model_validate(record.model_dump(mode="python"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversation_sessions (session_id, record_json)
                VALUES (?, ?)
                ON CONFLICT(session_id) DO UPDATE SET record_json = excluded.record_json
                """,
                (validated_record.session_id, validated_record.model_dump_json()),
            )
        return validated_record

    def _load_record(self, session_id: str) -> ConversationSessionRecord:
        normalized_session_id = _validate_session_id(session_id)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM conversation_sessions WHERE session_id = ?",
                (normalized_session_id,),
            ).fetchone()

        if row is None:
            raise KeyError(normalized_session_id)

        return ConversationSessionRecord.model_validate_json(row["record_json"])

    def create_session(self) -> ConversationSessionRecord:
        now = _now()
        record = ConversationSessionRecord(
            session_id=_session_id(),
            status=ConversationSessionStatus.LISTENING,
            turns=[],
            timing=ConversationSessionTiming(started_at=now, ended_at=now, duration_ms=0),
        )
        return self._save_record(record)

    def get_session(self, session_id: str) -> ConversationSessionRecord:
        return self._load_record(session_id)

    def stop_session(self, session_id: str) -> ConversationSessionRecord:
        record = self.get_session(session_id)
        if record.status == ConversationSessionStatus.STOPPED:
            return record

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = ConversationSessionStatus.STOPPED
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        return self._save_record(record)

    def list_turns(self, session_id: str) -> list[ConversationTurnRecord]:
        return self.get_session(session_id).turns


def create_conversation_session(
    service: ConversationSessionService | None = None,
) -> ConversationSessionRecord:
    return (service or get_conversation_session_service()).create_session()


def stop_conversation_session(
    session_id: str,
    service: ConversationSessionService | None = None,
) -> ConversationSessionRecord:
    return (service or get_conversation_session_service()).stop_session(session_id)


def list_conversation_turns(
    session_id: str,
    service: ConversationSessionService | None = None,
) -> list[ConversationTurnRecord]:
    return (service or get_conversation_session_service()).list_turns(session_id)


from functools import lru_cache


@lru_cache(maxsize=1)
def get_conversation_session_service() -> ConversationSessionService:
    return ConversationSessionService.from_env()

