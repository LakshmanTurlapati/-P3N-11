from __future__ import annotations

from services.api.app.schemas.conversation import (
    ConversationResponsePrompt,
    ConversationTurnRecord,
    ConversationTurnStatus,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.services.conversation_runtime import buildConversationResponsePrompt
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE


def _recent_turn() -> ConversationTurnRecord:
    return ConversationTurnRecord(
        turn_id="conversation-turn-001",
        status=ConversationTurnStatus.SUCCEEDED,
        input_audio_url="/conversation-turns/conversation-turn-001/input.wav",
        user_transcript_text="You sound amused.",
        response_text="Naturally.",
        playback_url="/conversation-turns/conversation-turn-001/audio",
        latency_ms=1280,
    )


def test_build_conversation_response_prompt_keeps_the_original_voice_boundary_and_memory() -> None:
    recent_turn = _recent_turn()

    prompt: ConversationResponsePrompt = buildConversationResponsePrompt(
        voice_profile=VESPER_GLASS_PROFILE,
        user_transcript_text="Give me the next line.",
        tone_preset=GenerationTonePreset.CUTTING,
        recent_turns=[recent_turn],
    )

    assert prompt.voice_id == VESPER_GLASS_PROFILE.id
    assert prompt.voice_display_name == VESPER_GLASS_PROFILE.display_name
    assert prompt.boundary_note == VESPER_GLASS_PROFILE.boundary_note
    assert prompt.prohibited_associations == VESPER_GLASS_PROFILE.style.prohibited_associations
    assert prompt.tone_preset == GenerationTonePreset.CUTTING
    assert prompt.user_transcript_text == "Give me the next line."
    assert prompt.recent_turns == [recent_turn]
    assert "theatrical" in prompt.persona_instructions.lower()
    assert "dryly witty" in prompt.persona_instructions.lower()
