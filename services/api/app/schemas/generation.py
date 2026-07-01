from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GenerationProviderType = Literal["metadata-only-stub"]
GenerationResultStatus = Literal["metadata-only"]
GenerationRightsCheckStatus = Literal["approved"]


class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    voice_id: str = Field(min_length=1)

    @field_validator("voice_id")
    @classmethod
    def _require_voice_id(cls, value: str) -> str:
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


class GenerationResultMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: GenerationResultStatus
    summary: str = Field(min_length=1)
    artifact_label: str = Field(min_length=1)
    provider_note: str = Field(min_length=1)

    @field_validator("summary", "artifact_label", "provider_note")
    @classmethod
    def _require_text(cls, value: str) -> str:
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

    @field_validator("ended_at")
    @classmethod
    def _require_end_after_start(cls, value: datetime, info: object) -> datetime:
        started_at = getattr(getattr(info, "data", {}), "get", lambda _key, _default=None: None)(
            "started_at",
            None,
        )
        if isinstance(started_at, datetime) and value < started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return value


class GenerationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider_type: GenerationProviderType
    voice_id: str = Field(min_length=1)
    rights_check: GenerationRightsCheck
    result_metadata: GenerationResultMetadata
    provider_trace: list[ProviderTraceEntry] = Field(min_length=1)
    timing: GenerationTiming

    @field_validator("voice_id")
    @classmethod
    def _require_voice_id(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value
