from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from services.api.app.schemas.conversation import (
    ConversationTurnAttempt,
    ConversationTurnCancelState,
    ConversationSessionRecord,
    ConversationSessionStatus,
    ConversationTurnRecord,
    ConversationTurnStatus,
    ConversationSessionTiming,
    ConversationTurnTiming,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.services.conversation_runtime import recordConversationLatency


def _now() -> datetime:
    return datetime.now(UTC)


def _milliseconds(delta: timedelta) -> int:
    return max(int(delta.total_seconds() * 1000), 0)


def _session_id() -> str:
    return f"conversation-session-{uuid4().hex[:12]}"


def _turn_id() -> str:
    return f"conversation-turn-{uuid4().hex[:12]}"


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

    def upsert_turn(self, session_id: str, turn: ConversationTurnRecord) -> ConversationSessionRecord:
        record = self.get_session(session_id)
        turns = list(record.turns)
        existing_index = next(
            (index for index, existing_turn in enumerate(turns) if existing_turn.turn_id == turn.turn_id),
            -1,
        )

        if existing_index == -1:
            turns.insert(0, turn)
        else:
            turns[existing_index] = turn

        record.turns = turns
        return self._save_record(record)


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


class ConversationTurnObjectStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.input_audio_root = self.root / "input-audio"
        self.response_audio_root = self.root / "response-audio"
        self.input_audio_root.mkdir(parents=True, exist_ok=True)
        self.response_audio_root.mkdir(parents=True, exist_ok=True)
        self._input_audio_root_resolved = self.input_audio_root.resolve()
        self._response_audio_root_resolved = self.response_audio_root.resolve()

    def _input_path_for_turn(self, turn_id: str) -> Path:
        if Path(turn_id).name != turn_id:
            raise ValueError("turn_id must not contain path separators")

        candidate = (self.input_audio_root / f"{turn_id}.wav").resolve()
        if not candidate.is_relative_to(self._input_audio_root_resolved):
            raise ValueError("turn_id escaped the input object store root")
        return candidate

    def _response_path_for_turn(self, turn_id: str) -> Path:
        if Path(turn_id).name != turn_id:
            raise ValueError("turn_id must not contain path separators")

        candidate = (self.response_audio_root / f"{turn_id}.wav").resolve()
        if not candidate.is_relative_to(self._response_audio_root_resolved):
            raise ValueError("turn_id escaped the response object store root")
        return candidate

    def write_input_audio(self, turn_id: str, audio_bytes: bytes) -> Path:
        path = self._input_path_for_turn(turn_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio_bytes)
        return path

    def write_response_audio(self, turn_id: str, audio_bytes: bytes) -> Path:
        path = self._response_path_for_turn(turn_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio_bytes)
        return path

    def read_input_audio(self, turn_id: str) -> bytes:
        return self._input_path_for_turn(turn_id).read_bytes()

    def path_for_input_audio(self, turn_id: str) -> Path:
        return self._input_path_for_turn(turn_id)

    def path_for_response_audio(self, turn_id: str) -> Path:
        return self._response_path_for_turn(turn_id)


class ConversationTurnService:
    def __init__(
        self,
        object_store: ConversationTurnObjectStore | None = None,
        *,
        session_service: ConversationSessionService | None = None,
        storage_root: Path | str | None = None,
        db_path: Path | str | None = None,
    ) -> None:
        if object_store is None:
            root = Path(storage_root) if storage_root is not None else self._default_storage_root()
            object_store = ConversationTurnObjectStore(root)

        self.object_store = object_store
        self.session_service = session_service or get_conversation_session_service()
        self.storage_root = object_store.root
        self.db_path = Path(db_path) if db_path is not None else self.storage_root / "conversation-turns.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @classmethod
    def from_env(cls) -> "ConversationTurnService":
        storage_root = os.environ.get("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT")
        if storage_root:
            return cls(storage_root=Path(storage_root) / "conversation-turns")
        return cls(storage_root=cls._default_storage_root())

    @staticmethod
    def _default_storage_root() -> Path:
        return Path(tempfile.gettempdir()) / "theatrical-voice-studio" / "conversation-turns"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    turn_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    record_json TEXT NOT NULL
                )
                """,
            )

    def _save_record(self, session_id: str, record: ConversationTurnRecord) -> ConversationTurnRecord:
        validated_record = ConversationTurnRecord.model_validate(record.model_dump(mode="python"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversation_turns (turn_id, session_id, record_json)
                VALUES (?, ?, ?)
                ON CONFLICT(turn_id) DO UPDATE SET
                    session_id = excluded.session_id,
                    record_json = excluded.record_json
                """,
                (validated_record.turn_id, session_id, validated_record.model_dump_json()),
            )
        self.session_service.upsert_turn(session_id, validated_record)
        return validated_record

    def _load_record(self, turn_id: str) -> tuple[str, ConversationTurnRecord]:
        normalized_turn_id = turn_id.strip()
        if not normalized_turn_id:
            raise ValueError("turn_id must not be empty")

        with self._connect() as connection:
            row = connection.execute(
                "SELECT session_id, record_json FROM conversation_turns WHERE turn_id = ?",
                (normalized_turn_id,),
            ).fetchone()

        if row is None:
            raise KeyError(normalized_turn_id)

        return row["session_id"], ConversationTurnRecord.model_validate_json(row["record_json"])

    def create_turn(
        self,
        session_id: str,
        *,
        audio_bytes: bytes,
        audio_mime_type: str,
        tone_preset: GenerationTonePreset,
        audio_filename: str,
    ) -> ConversationTurnRecord:
        if not audio_bytes:
            raise ValueError("audio bytes are required")

        self.session_service.get_session(session_id)
        now = _now()
        turn_id = _turn_id()
        self.object_store.write_input_audio(turn_id, audio_bytes)
        record = ConversationTurnRecord(
            turn_id=turn_id,
            status=ConversationTurnStatus.QUEUED,
            input_audio_url=f"/conversation-turns/{turn_id}/input.wav",
            user_transcript_text=None,
            response_text=None,
            playback_url=None,
            tone_preset=tone_preset,
            latency_ms=None,
            attempt=ConversationTurnAttempt(
                status=ConversationTurnStatus.QUEUED,
                mime_type=audio_mime_type,
                input_audio_url=f"/conversation-turns/{turn_id}/input.wav",
                tone_preset=tone_preset,
                started_at=now,
                ended_at=now,
                duration_ms=0,
            ),
            timing=ConversationTurnTiming(started_at=now, ended_at=now, duration_ms=0),
        )
        return self._save_record(session_id, record)

    def get_turn_session_id(self, turn_id: str) -> str:
        session_id, _ = self._load_record(turn_id)
        return session_id

    def get_turn(self, turn_id: str) -> ConversationTurnRecord:
        _, record = self._load_record(turn_id)
        return record

    def mark_running(self, turn_id: str) -> ConversationTurnRecord:
        session_id, record = self._load_record(turn_id)
        if record.status != ConversationTurnStatus.QUEUED:
            raise ValueError("Only queued turns can transition to running")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = ConversationTurnStatus.RUNNING
        if record.attempt is not None:
            record.attempt.status = ConversationTurnStatus.RUNNING
            record.attempt.ended_at = now
            record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        return self._save_record(session_id, record)

    def mark_interrupted(
        self,
        turn_id: str,
        *,
        reason: str | None = None,
    ) -> ConversationTurnRecord:
        session_id, record = self._load_record(turn_id)
        if record.status in {
            ConversationTurnStatus.INTERRUPTED,
            ConversationTurnStatus.CANCELED,
        }:
            return record

        if record.status == ConversationTurnStatus.FAILED:
            return record

        was_succeeded = record.status == ConversationTurnStatus.SUCCEEDED
        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = ConversationTurnStatus.INTERRUPTED
        record.cancel_state = ConversationTurnCancelState(
            requested_at=now,
            interrupted_at=now,
            reason=reason or "manual interrupt",
        )

        if record.attempt is not None:
            record.attempt.status = ConversationTurnStatus.INTERRUPTED
            if not was_succeeded:
                record.attempt.ended_at = now
                record.attempt.duration_ms = elapsed_ms
            if record.attempt.error_message is None and not was_succeeded:
                record.attempt.error_message = "Conversation turn interrupted."

        if not was_succeeded:
            record.timing.ended_at = now
            record.timing.duration_ms = elapsed_ms
            record = recordConversationLatency(
                record,
                speech_end_to_transcript_ms=(
                    record.timing.speech_end_to_transcript_ms
                    if record.timing.speech_end_to_transcript_ms is not None
                    else elapsed_ms
                ),
                response_text_ms=(
                    record.timing.response_text_ms
                    if record.timing.response_text_ms is not None
                    else elapsed_ms
                ),
                tts_complete_ms=(
                    record.timing.tts_complete_ms
                    if record.timing.tts_complete_ms is not None
                    else elapsed_ms
                ),
                playback_start_ms=(
                    record.timing.playback_start_ms
                    if record.timing.playback_start_ms is not None
                    else elapsed_ms
                ),
            )
        else:
            record = recordConversationLatency(record)

        return self._save_record(session_id, record)

    def mark_succeeded(
        self,
        turn_id: str,
        *,
        response_audio_bytes: bytes,
        user_transcript_text: str,
        response_provider_name: str,
        tts_provider_name: str,
        response_text: str,
        mime_type: str,
        audio_duration_ms: int,
        tone_preset: GenerationTonePreset | None = None,
        speech_end_to_transcript_ms: int | None = None,
        response_text_ms: int | None = None,
        tts_complete_ms: int | None = None,
        playback_start_ms: int | None = None,
    ) -> ConversationTurnRecord:
        session_id, record = self._load_record(turn_id)
        if record.status in {
            ConversationTurnStatus.INTERRUPTED,
            ConversationTurnStatus.CANCELED,
        }:
            return record

        if record.status not in {ConversationTurnStatus.QUEUED, ConversationTurnStatus.RUNNING}:
            raise ValueError("Only queued or running turns can transition to succeeded")

        self.object_store.write_response_audio(turn_id, response_audio_bytes)
        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = ConversationTurnStatus.SUCCEEDED
        record.user_transcript_text = user_transcript_text
        record.response_text = response_text
        record.playback_url = f"/conversation-turns/{turn_id}/audio"
        record.latency_ms = elapsed_ms
        record.tone_preset = tone_preset or record.tone_preset
        if record.attempt is not None:
            record.attempt.status = ConversationTurnStatus.SUCCEEDED
            record.attempt.provider_name = tts_provider_name
            record.attempt.response_provider_name = response_provider_name
            record.attempt.tts_provider_name = tts_provider_name
            record.attempt.mime_type = mime_type
            record.attempt.input_audio_url = record.input_audio_url
            record.attempt.user_transcript_text = user_transcript_text
            record.attempt.response_text = response_text
            record.attempt.playback_url = record.playback_url
            record.attempt.tone_preset = record.tone_preset
            record.attempt.audio_duration_ms = audio_duration_ms
            record.attempt.ended_at = now
            record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        record = recordConversationLatency(
            record,
            speech_end_to_transcript_ms=speech_end_to_transcript_ms,
            response_text_ms=response_text_ms,
            tts_complete_ms=tts_complete_ms,
            playback_start_ms=playback_start_ms,
        )
        return self._save_record(session_id, record)

    def mark_failed(self, turn_id: str, *, error_message: str) -> ConversationTurnRecord:
        session_id, record = self._load_record(turn_id)
        if record.status in {
            ConversationTurnStatus.INTERRUPTED,
            ConversationTurnStatus.CANCELED,
        }:
            return record

        if record.status == ConversationTurnStatus.SUCCEEDED:
            raise ValueError("Succeeded turns cannot transition to failed")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = ConversationTurnStatus.FAILED
        if record.attempt is not None:
            record.attempt.status = ConversationTurnStatus.FAILED
            record.attempt.error_message = error_message
            record.attempt.ended_at = now
            record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        return self._save_record(session_id, record)

    def get_input_audio_path(self, turn_id: str) -> Path:
        session_id, record = self._load_record(turn_id)
        if record.input_audio_url is None:
            raise KeyError(turn_id)

        audio_path = self.object_store.path_for_input_audio(turn_id)
        if not audio_path.exists():
            raise KeyError(turn_id)

        _ = session_id
        return audio_path

    def get_audio_path(self, turn_id: str) -> Path:
        session_id, record = self._load_record(turn_id)
        if record.status != ConversationTurnStatus.SUCCEEDED or record.playback_url is None:
            raise KeyError(turn_id)

        audio_path = self.object_store.path_for_response_audio(turn_id)
        if not audio_path.exists():
            raise KeyError(turn_id)

        _ = session_id
        return audio_path


def get_conversation_turn_service() -> ConversationTurnService:
    return _get_conversation_turn_service()


@lru_cache(maxsize=1)
def _get_conversation_turn_service() -> ConversationTurnService:
    return ConversationTurnService.from_env()
