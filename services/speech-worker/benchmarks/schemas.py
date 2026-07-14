from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BenchmarkModality = Literal["text", "audio"]
BenchmarkTonePreset = Literal["measured", "cutting", "grandiose"]


class BenchmarkCorpusItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    modality: BenchmarkModality
    text: str = Field(min_length=1)
    tone: BenchmarkTonePreset
    voice_id: str = Field(min_length=1)
    fixture_path: Path | None = None
    transcript: str | None = None
    speech_window_start_ms: int | None = Field(default=None, ge=0)
    speech_window_end_ms: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)
    condition_tags: list[str] = Field(default_factory=list)
    expected_failure: str | None = None
    safety_notes: str = Field(min_length=1)

    @field_validator("id", "text", "voice_id", "safety_notes", "transcript", "expected_failure")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @field_validator("condition_tags")
    @classmethod
    def _normalize_condition_tags(cls, value: list[str]) -> list[str]:
        normalized_tags = [tag.strip() for tag in value if tag and tag.strip()]
        return normalized_tags

    @model_validator(mode="after")
    def _validate_modality_specific_fields(self) -> "BenchmarkCorpusItem":
        if self.modality == "text":
            if self.fixture_path is not None:
                raise ValueError("text benchmark items must not include a fixture_path")
            if self.transcript is not None:
                raise ValueError("text benchmark items must not include a transcript")
            if self.speech_window_start_ms is not None or self.speech_window_end_ms is not None:
                raise ValueError("text benchmark items must not include speech-window metadata")
            if self.duration_ms is not None:
                raise ValueError("text benchmark items must not include duration metadata")
        elif self.modality == "audio":
            missing_fields = [
                field_name
                for field_name, field_value in (
                    ("fixture_path", self.fixture_path),
                    ("transcript", self.transcript),
                    ("speech_window_start_ms", self.speech_window_start_ms),
                    ("speech_window_end_ms", self.speech_window_end_ms),
                    ("duration_ms", self.duration_ms),
                )
                if field_value is None
            ]
            if missing_fields:
                raise ValueError(
                    "audio benchmark items must include fixture, transcript, timing, and duration metadata",
                )
            if self.condition_tags == []:
                raise ValueError("audio benchmark items must include condition tags")
            if self.speech_window_start_ms is not None and self.speech_window_end_ms is not None:
                if self.speech_window_start_ms >= self.speech_window_end_ms:
                    raise ValueError("speech_window_start_ms must be less than speech_window_end_ms")
        return self


class BenchmarkCorpus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[BenchmarkCorpusItem]

    @model_validator(mode="after")
    def _validate_items(self) -> "BenchmarkCorpus":
        if not self.items:
            raise ValueError("benchmark corpus must include at least one item")

        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("benchmark corpus item ids must be unique")

        return self


class BenchmarkStageTimings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vad_ms: int = Field(ge=0)
    stt_ms: int = Field(ge=0)
    response_text_ms: int = Field(ge=0)
    tts_ms: int = Field(ge=0)
    playback_ready_ms: int = Field(ge=0)
    total_wall_ms: int = Field(ge=0)


class BenchmarkGateResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: Literal["pass", "fail", "blocked"]
    reason: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    blocked: bool

    @field_validator("reason", "evidence")
    @classmethod
    def _normalize_text(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("must not be empty")
        return cleaned_value

    @model_validator(mode="after")
    def _validate_blocked_consistency(self) -> "BenchmarkGateResult":
        if self.status == "blocked" and not self.blocked:
            raise ValueError("blocked gate results must mark blocked=true")
        if self.status != "blocked" and self.blocked:
            raise ValueError("non-blocked gate results must mark blocked=false")
        return self


class BenchmarkQualityScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intelligibility: int = Field(ge=1, le=5)
    persona_tone_fit: int = Field(ge=1, le=5)
    naturalness: int = Field(ge=1, le=5)
    artifact_level: int = Field(ge=1, le=5)
    safety_boundary_adherence: int = Field(ge=1, le=5)


class BenchmarkCandidateResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    candidate_id: str = Field(min_length=1)
    provider_type: str = Field(min_length=1)
    provider_name: str = Field(min_length=1)
    corpus_item_id: str = Field(min_length=1)
    status: Literal["passed", "blocked", "failed"]
    stage_timings_ms: BenchmarkStageTimings
    total_duration_ms: int = Field(ge=0)
    quality_scores: BenchmarkQualityScores
    license_gate: BenchmarkGateResult
    safety_gate: BenchmarkGateResult
    integration_gate: BenchmarkGateResult
    runtime_cost: str = Field(min_length=1)
    integration_risk: str = Field(min_length=1)
    failure_blocker: str | None = None
    artifact_references: list[str] = Field(default_factory=list)

    @field_validator(
        "candidate_id",
        "provider_type",
        "provider_name",
        "corpus_item_id",
        "runtime_cost",
        "integration_risk",
        "failure_blocker",
    )
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @field_validator("artifact_references")
    @classmethod
    def _normalize_artifact_references(cls, value: list[str]) -> list[str]:
        return [reference.strip() for reference in value if reference and reference.strip()]


class BenchmarkRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    studio_default_recommendation: str = Field(min_length=1)
    live_conversation_recommendation: str = Field(min_length=1)
    notes: str | None = None

    @field_validator(
        "studio_default_recommendation",
        "live_conversation_recommendation",
        "notes",
    )
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value
