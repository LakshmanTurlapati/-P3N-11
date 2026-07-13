from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from services.api.app.schemas.conversation import (
    ConversationResponsePrompt,
    ConversationResponseResult,
)
from services.api.app.schemas.generation import GenerationTonePreset


@runtime_checkable
class ConversationResponseProvider(Protocol):
    provider_name: str

    def generate_reply(self, prompt: ConversationResponsePrompt) -> ConversationResponseResult:
        """Return a persona-safe reply for the provided conversation prompt."""


def _tone_opening(tone_preset: GenerationTonePreset) -> str:
    if tone_preset == GenerationTonePreset.MEASURED:
        return "Very well."
    if tone_preset == GenerationTonePreset.CUTTING:
        return "Naturally."
    return "Let us proceed."


def _tone_body(tone_preset: GenerationTonePreset) -> str:
    if tone_preset == GenerationTonePreset.MEASURED:
        return "I will keep this precise."
    if tone_preset == GenerationTonePreset.CUTTING:
        return "I will keep this sharp."
    return "I will keep this grand without losing the thread."


def _tone_closing(tone_preset: GenerationTonePreset, has_memory: bool) -> str:
    memory_clause = (
        "The last exchange remains in view."
        if has_memory
        else "We begin cleanly."
    )
    _ = tone_preset
    return f"No borrowed masks. {memory_clause}"


@dataclass(frozen=True, slots=True)
class VesperConversationResponder:
    provider_name: str = "vesper-conversation-responder"

    def generate_reply(self, prompt: ConversationResponsePrompt) -> ConversationResponseResult:
        opening = _tone_opening(prompt.tone_preset)
        body = _tone_body(prompt.tone_preset)
        closing = _tone_closing(prompt.tone_preset, bool(prompt.recent_turns))
        text = f"{opening} {body} {closing}"

        return ConversationResponseResult(
            provider_name=self.provider_name,
            tone_preset=prompt.tone_preset,
            text=text.strip(),
        )
