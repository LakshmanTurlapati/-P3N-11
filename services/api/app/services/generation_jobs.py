from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from services.api.app.schemas.generation import (
    GenerationAttempt,
    GenerationJobRecord,
    GenerationJobStatus,
    GenerationRequest,
    GenerationRightsCheck,
    GenerationTiming,
    ProviderTraceEntry,
)
from services.api.app.schemas.voice_profile import VoiceProfile


def _now() -> datetime:
    return datetime.now(UTC)


def _milliseconds(delta: timedelta) -> int:
    return max(int(delta.total_seconds() * 1000), 0)


def _job_id() -> str:
    return f"job-{uuid4().hex[:12]}"


def _build_rights_check(profile: VoiceProfile) -> GenerationRightsCheck:
    return GenerationRightsCheck(
        status="approved",
        approved_for_generation=True,
        message="Rights gate approved the bundled voice profile.",
    )


def _build_provider_trace(profile: VoiceProfile) -> list[ProviderTraceEntry]:
    return [
        ProviderTraceEntry(
            stage="rights-gate",
            provider="server-registry",
            detail=f"Bundled {profile.display_name} profile passed the approval check.",
        ),
        ProviderTraceEntry(
            stage="job-queue",
            provider="api-control-plane",
            detail="Queued a generation job with the submitted text and tone preset.",
        ),
        ProviderTraceEntry(
            stage="provider-boundary",
            provider="job-service",
            detail="Speech-worker contracts stay swappable behind the job-backed generation route.",
        ),
    ]


def _build_retry_trace(previous_trace: list[ProviderTraceEntry]) -> list[ProviderTraceEntry]:
    return [
        *previous_trace,
        ProviderTraceEntry(
            stage="retry",
            provider="api-control-plane",
            detail="Retry created a brand new job from the cached text, voice, and tone inputs.",
        ),
    ]


class LocalObjectStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.audio_root = self.root / "audio"
        self.audio_root.mkdir(parents=True, exist_ok=True)
        self._audio_root_resolved = self.audio_root.resolve()

    def _path_for_job(self, job_id: str) -> Path:
        if Path(job_id).name != job_id:
            raise ValueError("job_id must not contain path separators")

        candidate = (self.audio_root / f"{job_id}.wav").resolve()
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


class GenerationJobService:
    def __init__(
        self,
        object_store: LocalObjectStore | None = None,
        *,
        storage_root: Path | str | None = None,
        db_path: Path | str | None = None,
    ) -> None:
        if object_store is None:
            root = Path(storage_root) if storage_root is not None else self._default_storage_root()
            object_store = LocalObjectStore(root)

        self.object_store = object_store
        self.storage_root = object_store.root
        self.db_path = Path(db_path) if db_path is not None else self.storage_root / "generation-jobs.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @classmethod
    def from_env(cls) -> "GenerationJobService":
        storage_root = os.environ.get("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT")
        if storage_root:
            return cls(storage_root=Path(storage_root))
        return cls(storage_root=cls._default_storage_root())

    @staticmethod
    def _default_storage_root() -> Path:
        return Path(tempfile.gettempdir()) / "theatrical-voice-studio" / "generation-jobs"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS generation_jobs (
                    job_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL
                )
                """,
            )

    def _save_record(self, record: GenerationJobRecord) -> GenerationJobRecord:
        validated_record = GenerationJobRecord.model_validate(record.model_dump(mode="python"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO generation_jobs (job_id, record_json)
                VALUES (?, ?)
                ON CONFLICT(job_id) DO UPDATE SET record_json = excluded.record_json
                """,
                (validated_record.job_id, validated_record.model_dump_json()),
            )
        return validated_record

    def _load_record(self, job_id: str) -> GenerationJobRecord:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM generation_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()

        if row is None:
            raise KeyError(job_id)

        return GenerationJobRecord.model_validate_json(row["record_json"])

    def create_job(
        self,
        request: GenerationRequest,
        profile: VoiceProfile,
        *,
        retry_of_job_id: str | None = None,
    ) -> GenerationJobRecord:
        now = _now()
        record = GenerationJobRecord(
            job_id=_job_id(),
            retry_of_job_id=retry_of_job_id,
            status=GenerationJobStatus.QUEUED,
            voice_id=request.voice_id,
            text=request.text,
            tone_preset=request.tone_preset,
            provider_type=None,
            provider_name=None,
            rights_check=_build_rights_check(profile),
            provider_trace=_build_provider_trace(profile),
            timing=GenerationTiming(started_at=now, ended_at=now, duration_ms=0),
            attempt=GenerationAttempt(started_at=now, ended_at=now, duration_ms=0),
            playback_url=None,
            audio_duration_ms=None,
        )
        return self._save_record(record)

    def get_job(self, job_id: str) -> GenerationJobRecord:
        return self._load_record(job_id)

    def mark_running(self, job_id: str) -> GenerationJobRecord:
        record = self.get_job(job_id)
        if record.status != GenerationJobStatus.QUEUED:
            raise ValueError("Only queued jobs can transition to running")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = GenerationJobStatus.RUNNING
        record.attempt.status = GenerationJobStatus.RUNNING
        record.attempt.ended_at = now
        record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        record.provider_trace = [
            *record.provider_trace,
            ProviderTraceEntry(
                stage="job-state",
                provider="api-control-plane",
                detail="Generation job marked running.",
            ),
        ]
        record.playback_url = None
        record.audio_duration_ms = None
        return self._save_record(record)

    def mark_succeeded(
        self,
        job_id: str,
        *,
        audio_bytes: bytes,
        mime_type: str,
        provider_name: str,
        audio_duration_ms: int,
    ) -> GenerationJobRecord:
        record = self.get_job(job_id)
        if record.status not in {GenerationJobStatus.QUEUED, GenerationJobStatus.RUNNING}:
            raise ValueError("Only queued or running jobs can transition to succeeded")

        self.object_store.write_audio(job_id, audio_bytes)
        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = GenerationJobStatus.SUCCEEDED
        record.provider_type = provider_name
        record.provider_name = provider_name
        record.attempt.status = GenerationJobStatus.SUCCEEDED
        record.attempt.provider_name = provider_name
        record.attempt.mime_type = mime_type
        record.attempt.audio_duration_ms = audio_duration_ms
        record.attempt.ended_at = now
        record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        record.playback_url = f"/generations/{job_id}/audio"
        record.audio_duration_ms = audio_duration_ms
        record.provider_trace = [
            *record.provider_trace,
            ProviderTraceEntry(
                stage="audio-store",
                provider=provider_name,
                detail="Normalized audio stored for controlled playback.",
            ),
        ]
        return self._save_record(record)

    def mark_failed(self, job_id: str, *, error_message: str) -> GenerationJobRecord:
        record = self.get_job(job_id)
        if record.status == GenerationJobStatus.SUCCEEDED:
            raise ValueError("Succeeded jobs cannot transition to failed")

        now = _now()
        elapsed_ms = _milliseconds(now - record.timing.started_at)
        record.status = GenerationJobStatus.FAILED
        record.attempt.status = GenerationJobStatus.FAILED
        record.attempt.error_message = error_message
        record.attempt.ended_at = now
        record.attempt.duration_ms = elapsed_ms
        record.timing.ended_at = now
        record.timing.duration_ms = elapsed_ms
        record.provider_trace = [
            *record.provider_trace,
            ProviderTraceEntry(
                stage="generation-failed",
                provider=record.provider_name or record.provider_type or "generation-worker",
                detail=error_message,
            ),
        ]
        record.playback_url = None
        record.audio_duration_ms = None
        return self._save_record(record)

    def retry_job(self, job_id: str) -> GenerationJobRecord:
        previous_job = self.get_job(job_id)
        if previous_job.status != GenerationJobStatus.FAILED:
            raise ValueError("Only failed jobs can be retried")

        now = _now()
        retry_record = GenerationJobRecord(
            job_id=_job_id(),
            retry_of_job_id=previous_job.job_id,
            status=GenerationJobStatus.QUEUED,
            voice_id=previous_job.voice_id,
            text=previous_job.text,
            tone_preset=previous_job.tone_preset,
            provider_type=None,
            provider_name=None,
            rights_check=previous_job.rights_check.model_copy(deep=True),
            provider_trace=_build_retry_trace(previous_job.provider_trace),
            timing=GenerationTiming(started_at=now, ended_at=now, duration_ms=0),
            attempt=GenerationAttempt(started_at=now, ended_at=now, duration_ms=0),
            playback_url=None,
            audio_duration_ms=None,
        )
        return self._save_record(retry_record)

    def get_audio_path(self, job_id: str) -> Path:
        record = self.get_job(job_id)
        if record.status != GenerationJobStatus.SUCCEEDED or record.playback_url is None:
            raise KeyError(job_id)

        audio_path = self.object_store.path_for_job(job_id)
        if not audio_path.exists():
            raise KeyError(job_id)

        return audio_path
