from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

GenerationProviderType = str
GenerationRightsCheckStatus = Literal["approved"]


def _now() -> datetime:
    return datetime.now(UTC)


def _default_rights_check() -> "GenerationRightsCheck":
    return GenerationRightsCheck(
        status="approved",
        approved_for_generation=True,
        message="Rights gate approved the bundled voice profile.",
    )


def _default_provider_trace() -> list["ProviderTraceEntry"]:
    return [
        ProviderTraceEntry(
            stage="rights-gate",
            provider="server-registry",
            detail="Bundled Vesper Glass profile passed the approval check.",
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


def _default_timing() -> "GenerationTiming":
    now = _now()
    return GenerationTiming(started_at=now, ended_at=now, duration_ms=0)


class GenerationTonePreset(str, Enum):
    MEASURED = "measured"
    CUTTING = "cutting"
    GRANDIOSE = "grandiose"


class GenerationJobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    voice_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    tone_preset: GenerationTonePreset

    @field_validator("voice_id")
    @classmethod
    def _require_voice_id(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("text")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


class GenerationRightsCheck(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: GenerationRightsCheckStatus
    approved_for_generation: bool
    message: str = Field(min_length=1)

    @field_validator("message")
    @classmethod
    def _require_message(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


class ProviderTraceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    stage: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    detail: str = Field(min_length=1)

    @field_validator("stage", "provider", "detail")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


class GenerationTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def _require_end_after_start(self) -> "GenerationTiming":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self


class GenerationAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: GenerationJobStatus = GenerationJobStatus.QUEUED
    provider_name: str | None = None
    mime_type: str | None = None
    error_message: str | None = None
    audio_duration_ms: int | None = None
    started_at: datetime = Field(default_factory=_now)
    ended_at: datetime = Field(default_factory=_now)
    duration_ms: int = Field(default=0, ge=0)

    @field_validator("provider_name", "mime_type", "error_message")
    @classmethod
    def _allow_blank_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value


class GenerationJobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider_type: GenerationProviderType | None = None
    provider_name: str | None = None
    job_id: str = Field(min_length=1)
    retry_of_job_id: str | None = None
    status: GenerationJobStatus
    voice_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    tone_preset: GenerationTonePreset
    rights_check: GenerationRightsCheck = Field(default_factory=_default_rights_check)
    provider_trace: list[ProviderTraceEntry] = Field(default_factory=_default_provider_trace)
    timing: GenerationTiming = Field(default_factory=_default_timing)
    attempt: GenerationAttempt = Field(default_factory=GenerationAttempt)
    playback_url: str | None = None
    audio_duration_ms: int | None = None

    @field_validator("job_id", "voice_id", "text")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("provider_type", "provider_name", "retry_of_job_id", "playback_url")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @model_validator(mode="after")
    def _validate_status_and_playback_fields(self) -> "GenerationJobRecord":
        if self.attempt.status != self.status:
            raise ValueError("attempt status must match the job status")

        if self.status == GenerationJobStatus.SUCCEEDED:
            if self.playback_url is None or self.audio_duration_ms is None:
                raise ValueError("succeeded jobs must include playback_url and audio_duration_ms")
            if self.provider_name is None or self.attempt.provider_name is None:
                raise ValueError("succeeded jobs must include provider metadata")
            if self.attempt.mime_type is None:
                raise ValueError("succeeded jobs must include mime type metadata")
        else:
            if self.playback_url is not None or self.audio_duration_ms is not None:
                raise ValueError("only succeeded jobs may expose playback metadata")
            if self.status == GenerationJobStatus.FAILED and not self.attempt.error_message:
                raise ValueError("failed jobs must preserve the error message")

        return self


class GenerationResult(GenerationJobRecord):
    pass
