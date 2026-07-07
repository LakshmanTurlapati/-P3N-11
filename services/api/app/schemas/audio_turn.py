from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AudioTurnCaptureSource = Literal["recording", "upload"]


def _now() -> datetime:
    return datetime.now(UTC)


def _default_timing() -> "AudioTurnTiming":
    now = _now()
    return AudioTurnTiming(started_at=now, ended_at=now, duration_ms=0)


class AudioTurnJobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class AudioTurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    capture_source: AudioTurnCaptureSource = "upload"
    audio_filename: str = Field(min_length=1)
    audio_mime_type: str = Field(min_length=1)

    @field_validator("audio_filename", "audio_mime_type")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


class AudioTurnTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def _require_end_after_start(self) -> "AudioTurnTiming":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self


class AudioTurnAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: AudioTurnJobStatus = AudioTurnJobStatus.QUEUED
    provider_name: str | None = None
    mime_type: str | None = None
    error_message: str | None = None
    transcript_text: str | None = None
    vad_provider_name: str | None = None
    vad_confidence: float | None = None
    audio_duration_ms: int | None = None
    started_at: datetime = Field(default_factory=_now)
    ended_at: datetime = Field(default_factory=_now)
    duration_ms: int = Field(default=0, ge=0)

    @field_validator(
        "provider_name",
        "mime_type",
        "error_message",
        "transcript_text",
        "vad_provider_name",
    )
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value


class AudioTurnJobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider_type: str | None = None
    provider_name: str | None = None
    job_id: str = Field(min_length=1)
    status: AudioTurnJobStatus
    capture_source: AudioTurnCaptureSource
    audio_filename: str = Field(min_length=1)
    audio_mime_type: str = Field(min_length=1)
    playback_url: str | None = None
    transcript_text: str | None = None
    vad_provider_name: str | None = None
    vad_confidence: float | None = None
    audio_duration_ms: int | None = None
    timing: AudioTurnTiming = Field(default_factory=_default_timing)
    attempt: AudioTurnAttempt = Field(default_factory=AudioTurnAttempt)

    @field_validator("job_id", "audio_filename", "audio_mime_type")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator(
        "provider_type",
        "provider_name",
        "playback_url",
        "transcript_text",
        "vad_provider_name",
    )
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @model_validator(mode="after")
    def _validate_status_and_attempt(self) -> "AudioTurnJobRecord":
        if self.attempt.status != self.status:
            raise ValueError("attempt status must match the job status")

        if self.status == AudioTurnJobStatus.FAILED and not self.attempt.error_message:
            raise ValueError("failed jobs must preserve the error message")

        return self
