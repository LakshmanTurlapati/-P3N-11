from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from services.api.app.schemas.generation import GenerationTonePreset


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


class ConversationTurnAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: ConversationTurnStatus = ConversationTurnStatus.QUEUED
    provider_name: str | None = None
    response_provider_name: str | None = None
    tts_provider_name: str | None = None
    mime_type: str | None = None
    error_message: str | None = None
    input_audio_url: str | None = None
    user_transcript_text: str | None = None
    response_text: str | None = None
    playback_url: str | None = None
    tone_preset: GenerationTonePreset | None = None
    audio_duration_ms: int | None = None
    started_at: datetime = Field(default_factory=_now)
    ended_at: datetime = Field(default_factory=_now)
    duration_ms: int = Field(default=0, ge=0)

    @field_validator(
        "provider_name",
        "response_provider_name",
        "tts_provider_name",
        "mime_type",
        "error_message",
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
    tone_preset: GenerationTonePreset | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    attempt: ConversationTurnAttempt | None = None
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

    @model_validator(mode="after")
    def _require_succeeded_turn_fields(self) -> "ConversationTurnRecord":
        if self.status == ConversationTurnStatus.SUCCEEDED:
            if self.attempt is None:
                raise ValueError("succeeded conversation turns must include an attempt record")

            missing_fields = [
                field_name
                for field_name, field_value in (
                    ("input_audio_url", self.input_audio_url),
                    ("user_transcript_text", self.user_transcript_text),
                    ("response_text", self.response_text),
                    ("playback_url", self.playback_url),
                    ("tone_preset", self.tone_preset),
                    ("latency_ms", self.latency_ms),
                    ("attempt.provider_name", self.attempt.provider_name),
                    ("attempt.response_provider_name", self.attempt.response_provider_name),
                    ("attempt.tts_provider_name", self.attempt.tts_provider_name),
                    ("attempt.mime_type", self.attempt.mime_type),
                    ("attempt.input_audio_url", self.attempt.input_audio_url),
                    ("attempt.user_transcript_text", self.attempt.user_transcript_text),
                    ("attempt.response_text", self.attempt.response_text),
                    ("attempt.playback_url", self.attempt.playback_url),
                    ("attempt.tone_preset", self.attempt.tone_preset),
                    ("attempt.audio_duration_ms", self.attempt.audio_duration_ms),
                )
                if field_value is None
            ]
            if missing_fields:
                raise ValueError(
                    "succeeded conversation turns must include input audio, transcript, "
                    "response, playback, and latency metadata",
                )
        return self


class ConversationResponsePrompt(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    voice_id: str = Field(min_length=1)
    voice_display_name: str = Field(min_length=1)
    boundary_note: str = Field(min_length=1)
    prohibited_associations: list[str] = Field(min_length=1)
    tone_preset: GenerationTonePreset
    user_transcript_text: str = Field(min_length=1)
    recent_turns: list[ConversationTurnRecord] = Field(default_factory=list)
    persona_instructions: str = Field(min_length=1)

    @field_validator("voice_id", "voice_display_name", "boundary_note", "user_transcript_text")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("prohibited_associations")
    @classmethod
    def _normalize_associations(cls, values: list[str]) -> list[str]:
        cleaned_values = [item.strip() for item in values if isinstance(item, str) and item.strip()]
        if not cleaned_values:
            raise ValueError("must not be empty")
        return cleaned_values


class ConversationResponseResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider_name: str = Field(min_length=1)
    tone_preset: GenerationTonePreset
    text: str = Field(min_length=1)

    @field_validator("provider_name", "text")
    @classmethod
    def _require_text(cls, value: str) -> str:
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
