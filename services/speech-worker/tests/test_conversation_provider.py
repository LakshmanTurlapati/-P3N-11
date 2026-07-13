from __future__ import annotations

from services.api.app.schemas.conversation import (
    ConversationResponsePrompt,
    ConversationResponseResult,
    ConversationTurnRecord,
    ConversationTurnStatus,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.services.conversation_runtime import buildConversationResponsePrompt
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE
from providers import ConversationResponseProvider, VesperConversationResponder


def _build_prompt(tone_preset: GenerationTonePreset) -> ConversationResponsePrompt:
    recent_turn = ConversationTurnRecord(
        turn_id="conversation-turn-001",
        status=ConversationTurnStatus.SUCCEEDED,
        input_audio_url="/conversation-turns/conversation-turn-001/input.wav",
        user_transcript_text="You sound amused.",
        response_text="Naturally.",
        playback_url="/conversation-turns/conversation-turn-001/audio",
        latency_ms=1280,
    )

    return buildConversationResponsePrompt(
        voice_profile=VESPER_GLASS_PROFILE,
        user_transcript_text="Offer a reply with a dry edge.",
        tone_preset=tone_preset,
        recent_turns=[recent_turn],
    )


def test_vesper_conversation_responder_stays_inside_the_original_voice_boundary() -> None:
    responder = VesperConversationResponder()
    prompt = _build_prompt(GenerationTonePreset.MEASURED)

    assert isinstance(responder, ConversationResponseProvider)

    result: ConversationResponseResult = responder.generate_reply(prompt)
    lower_text = result.text.lower()

    assert result.provider_name == responder.provider_name
    assert result.text.strip()
    assert len(result.text) <= 240
    assert "loki" not in lower_text
    assert "tom hiddleston" not in lower_text
    assert "marvel" not in lower_text
    assert "protected" not in lower_text
    assert "unlicensed" not in lower_text


def test_vesper_conversation_responder_steers_tone_without_changing_the_boundary() -> None:
    responder = VesperConversationResponder()

    measured_result = responder.generate_reply(_build_prompt(GenerationTonePreset.MEASURED))
    cutting_result = responder.generate_reply(_build_prompt(GenerationTonePreset.CUTTING))
    grandiose_result = responder.generate_reply(_build_prompt(GenerationTonePreset.GRANDIOSE))

    assert measured_result.text != cutting_result.text
    assert cutting_result.text != grandiose_result.text
    assert measured_result.provider_name == responder.provider_name
    assert cutting_result.provider_name == responder.provider_name
    assert grandiose_result.provider_name == responder.provider_name

    for result in (measured_result, cutting_result, grandiose_result):
        lower_text = result.text.lower()
        assert "loki" not in lower_text
        assert "tom hiddleston" not in lower_text
        assert "marvel" not in lower_text
        assert "protected" not in lower_text
