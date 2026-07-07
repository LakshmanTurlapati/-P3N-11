from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from services.api.app.schemas.audio_turn import (
    AudioTurnAttempt,
    AudioTurnJobRecord,
    AudioTurnJobStatus,
    AudioTurnRequest,
    AudioTurnTiming,
)


def _now() -> datetime:
    return datetime.now(UTC)


def _milliseconds(delta: timedelta) -> int:
    return max(int(delta.total_seconds() * 1000), 0)


def _job_id() -> str:
    return f"turn-{uuid4().hex[:12]}"


def _sanitize_filename(filename: str | None) -> str:
    cleaned_filename = Path(filename or "").name.strip()
    return cleaned_filename or "spoken-turn.audio"


class AudioTurnObjectStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.audio_root = self.root / "audio"
        self.audio_root.mkdir(parents=True, exist_ok=True)
        self._audio_root_resolved = self.audio_root.resolve()

    def _path_for_job(self, job_id: str) -> Path:
        if Path(job_id).name != job_id:
            raise ValueError("job_id must not contain path separators")

        candidate = (self.audio_root / f"{job_id}.audio").resolve()
        if not candidate.is_relative_to(self._audio_root_resolved):
            raise ValueError("job_id escaped the object store root")
        return candidate

    def write_audio(self, job_id: str, audio_bytes: bytes) -> Path:
        path = self._path_for_job(job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio_bytes)
        return path

    def read_audio(self, job_id: str) -> bytes:
        return self._path_for_job(job_id).read_bytes()

    def path_for_job(self, job_id: str) -> Path:
        return self._path_for_job(job_id)


class AudioTurnJobService:
    def __init__(
        self,
        object_store: AudioTurnObjectStore | None = None,
        *,
        storage_root: Path | str | None = None,
        db_path: Path | str | None = None,
    ) -> None:
        if object_store is None:
            root = Path(storage_root) if storage_root is not None else self._default_storage_root()
            object_store = AudioTurnObjectStore(root)

        self.object_store = object_store
        self.storage_root = object_store.root
        self.db_path = Path(db_path) if db_path is not None else self.storage_root / "audio-turn-jobs.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @classmethod
    def from_env(cls) -> "AudioTurnJobService":
        storage_root = os.environ.get("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT")
        if storage_root:
            return cls(storage_root=Path(storage_root) / "audio-turns")
        return cls(storage_root=cls._default_storage_root())

    @staticmethod
    def _default_storage_root() -> Path:
        return Path(tempfile.gettempdir()) / "theatrical-voice-studio" / "audio-turns"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audio_turn_jobs (
                    job_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL
                )
                """,
            )

    def _save_record(self, record: AudioTurnJobRecord) -> AudioTurnJobRecord:
        validated_record = AudioTurnJobRecord.model_validate(record.model_dump(mode="python"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audio_turn_jobs (job_id, record_json)
                VALUES (?, ?)
                ON CONFLICT(job_id) DO UPDATE SET record_json = excluded.record_json
                """,
                (validated_record.job_id, validated_record.model_dump_json()),
            )
        return validated_record

    def _load_record(self, job_id: str) -> AudioTurnJobRecord:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audio_turn_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()

        if row is None:
            raise KeyError(job_id)

        return AudioTurnJobRecord.model_validate_json(row["record_json"])

    def create_job(
        self,
        request: AudioTurnRequest,
        audio_bytes: bytes,
    ) -> AudioTurnJobRecord:
        if not audio_bytes:
            raise ValueError("audio bytes are required")

        now = _now()
        job_id = _job_id()
        self.object_store.write_audio(job_id, audio_bytes)

        record = AudioTurnJobRecord(
            job_id=job_id,
            status=AudioTurnJobStatus.QUEUED,
            capture_source=request.capture_source,
            audio_filename=_sanitize_filename(request.audio_filename),
            audio_mime_type=request.audio_mime_type,
            provider_type=None,
            provider_name=None,
            playback_url=f"/audio-turns/{job_id}/audio",
            transcript_text=None,
            vad_provider_name=None,
            vad_confidence=None,
            audio_duration_ms=None,
            timing=AudioTurnTiming(started_at=now, ended_at=now, duration_ms=0),
            attempt=AudioTurnAttempt(
                status=AudioTurnJobStatus.QUEUED,
                provider_name=None,
                mime_type=request.audio_mime_type,
                error_message=None,
                transcript_text=None,
                vad_provider_name=None,
                vad_confidence=None,
                audio_duration_ms=None,
                started_at=now,
                ended_at=now,
                duration_ms=0,
            ),
        )
        return self._save_record(record)

    def get_job(self, job_id: str) -> AudioTurnJobRecord:
        return self._load_record(job_id)

    def mark_running(self, job_id: str) -> AudioTurnJobRecord:
        record = self.get_job(job_id)
        if record.status != AudioTurnJobStatus.QUEUED:
            raise ValueError("Only queued jobs can transition to running")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = AudioTurnJobStatus.RUNNING
        record.attempt.status = AudioTurnJobStatus.RUNNING
        record.attempt.ended_at = now
        record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        return self._save_record(record)

    def mark_succeeded(
        self,
        job_id: str,
        *,
        provider_name: str | None = None,
        transcript_text: str | None = None,
        vad_provider_name: str | None = None,
        vad_confidence: float | None = None,
        audio_duration_ms: int | None = None,
    ) -> AudioTurnJobRecord:
        record = self.get_job(job_id)
        if record.status not in {AudioTurnJobStatus.QUEUED, AudioTurnJobStatus.RUNNING}:
            raise ValueError("Only queued or running jobs can transition to succeeded")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = AudioTurnJobStatus.SUCCEEDED
        record.provider_type = provider_name
        record.provider_name = provider_name
        record.transcript_text = transcript_text
        record.vad_provider_name = vad_provider_name
        record.vad_confidence = vad_confidence
        record.audio_duration_ms = audio_duration_ms
        record.attempt.status = AudioTurnJobStatus.SUCCEEDED
        record.attempt.provider_name = provider_name
        record.attempt.transcript_text = transcript_text
        record.attempt.vad_provider_name = vad_provider_name
        record.attempt.vad_confidence = vad_confidence
        record.attempt.audio_duration_ms = audio_duration_ms
        record.attempt.ended_at = now
        record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        return self._save_record(record)

    def mark_failed(self, job_id: str, *, error_message: str) -> AudioTurnJobRecord:
        record = self.get_job(job_id)
        if record.status == AudioTurnJobStatus.SUCCEEDED:
            raise ValueError("Succeeded jobs cannot transition to failed")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = AudioTurnJobStatus.FAILED
        record.attempt.status = AudioTurnJobStatus.FAILED
        record.attempt.error_message = error_message
        record.attempt.ended_at = now
        record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        return self._save_record(record)

    def get_audio_path(self, job_id: str) -> Path:
        self.get_job(job_id)
        audio_path = self.object_store.path_for_job(job_id)
        if not audio_path.exists():
            raise KeyError(job_id)

        return audio_path
