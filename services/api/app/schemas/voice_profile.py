from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VoiceRightsStatus = Literal["original", "licensed", "consented"]


class VoiceRights(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    rights_status: VoiceRightsStatus
    approved_for_generation: bool
    source_notes: str = Field(min_length=1)
    consent_notes: str = Field(min_length=1)
    intended_use: str = Field(min_length=1)

    @field_validator("source_notes", "consent_notes", "intended_use")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


class VoiceStyle(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    summary: str = Field(min_length=1)
    style_traits: list[str] = Field(min_length=1)
    prohibited_associations: list[str] = Field(min_length=1)

    @field_validator("summary")
    @classmethod
    def _require_summary(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("style_traits", "prohibited_associations")
    @classmethod
    def _require_text_items(cls, values: list[str]) -> list[str]:
        cleaned_values = [item.strip() for item in values if item and item.strip()]
        if not cleaned_values:
            raise ValueError("must not be empty")
        return cleaned_values


class VoiceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    boundary_note: str = Field(min_length=1)
    rights: VoiceRights
    style: VoiceStyle

    @field_validator("id", "display_name", "boundary_note")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

