from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

GenerationProviderType = Literal["prototype-baseline-stub"]
GenerationRightsCheckStatus = Literal["approved"]


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


class GenerationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider_type: GenerationProviderType
    job_id: str = Field(min_length=1)
    status: GenerationJobStatus
    voice_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    tone_preset: GenerationTonePreset
    rights_check: GenerationRightsCheck
    provider_trace: list[ProviderTraceEntry] = Field(min_length=1)
    timing: GenerationTiming

    @field_validator("job_id", "voice_id", "text")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value
