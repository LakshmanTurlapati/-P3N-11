from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _now() -> datetime:
    return datetime.now(UTC)


def _default_session_timing() -> "ConversationSessionTiming":
    now = _now()
    return ConversationSessionTiming(started_at=now, ended_at=now, duration_ms=0)


def _default_turn_timing() -> "ConversationTurnTiming":
    now = _now()
    return ConversationTurnTiming(started_at=now, ended_at=now, duration_ms=0)


class ConversationSessionStatus(str, Enum):
    LISTENING = "listening"
    STOPPED = "stopped"


class ConversationTurnStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    CANCELED = "canceled"


class ConversationSessionTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def _require_end_after_start(self) -> "ConversationSessionTiming":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self


class ConversationTurnTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def _require_end_after_start(self) -> "ConversationTurnTiming":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self


class ConversationTurnRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    turn_id: str = Field(min_length=1)
    status: ConversationTurnStatus
    input_audio_url: str | None = None
    user_transcript_text: str | None = None
    response_text: str | None = None
    playback_url: str | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    timing: ConversationTurnTiming = Field(default_factory=_default_turn_timing)

    @field_validator(
        "input_audio_url",
        "user_transcript_text",
        "response_text",
        "playback_url",
    )
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @field_validator("turn_id")
    @classmethod
    def _require_turn_id(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


class ConversationSessionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    session_id: str = Field(min_length=1)
    status: ConversationSessionStatus
    turns: list[ConversationTurnRecord] = Field(default_factory=list)
    timing: ConversationSessionTiming = Field(default_factory=_default_session_timing)

    @field_validator("session_id")
    @classmethod
    def _require_session_id(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value
