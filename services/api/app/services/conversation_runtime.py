from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

from services.api.app.schemas.conversation import (
    ConversationResponsePrompt,
    ConversationResponseResult,
    ConversationTurnRecord,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.schemas.voice_profile import VoiceProfile

WORKER_ROOT_ENV = "THEATRICAL_VOICE_STUDIO_WORKER_ROOT"
MAX_RECENT_TURNS = 4


def _worker_root() -> Path:
    configured_root = os.environ.get(WORKER_ROOT_ENV)
    if configured_root:
        worker_root = Path(configured_root)
    else:
        worker_root = Path(__file__).resolve().parents[4] / "services" / "speech-worker"

    if not worker_root.exists():
        raise RuntimeError(
            "Approved speech-worker root not found. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory.",
        )

    providers_dir = worker_root / "providers"
    if not providers_dir.exists():
        raise RuntimeError(
            "Approved speech-worker root is missing the providers package. "
            f"Set {WORKER_ROOT_ENV} to the checked-out services/speech-worker directory.",
        )

    return worker_root


def _ensure_worker_root_on_path() -> Path:
    worker_root = _worker_root()
    worker_root_str = str(worker_root)
    if worker_root_str not in sys.path:
        sys.path.insert(0, worker_root_str)
    return worker_root


@lru_cache(maxsize=1)
def _load_conversation_provider_class() -> Any:
    _ensure_worker_root_on_path()
    try:
        from providers import VesperConversationResponder
    except ImportError as exc:  # pragma: no cover - only exercised when worker checkout is missing
        raise RuntimeError(
            "Conversation responder could not be imported from the approved worker root.",
        ) from exc

    return VesperConversationResponder


@lru_cache(maxsize=1)
def get_conversation_response_provider() -> Any:
    provider_class = _load_conversation_provider_class()
    return provider_class()


def _build_persona_instructions(
    *,
    voice_profile: VoiceProfile,
    tone_preset: GenerationTonePreset,
    recent_turn_count: int,
) -> str:
    memory_clause = (
        "Use the recent conversation turns only for short session memory, and do not "
        "persist memory after refresh."
        if recent_turn_count
        else "No prior turns are available, so keep the reply self-contained."
    )

    return (
        f"{voice_profile.style.summary} Stay inside this original voice boundary: "
        f"{voice_profile.boundary_note} Avoid any claim to be Loki, Tom Hiddleston, "
        f"Marvel, or any other protected or unlicensed identity. Tone preset: "
        f"{tone_preset.value}. Keep the response concise, theatrical, cool, and dryly "
        f"witty. {memory_clause}"
    )


def buildConversationResponsePrompt(
    *,
    voice_profile: VoiceProfile,
    user_transcript_text: str,
    tone_preset: GenerationTonePreset,
    recent_turns: Sequence[ConversationTurnRecord] | None = None,
) -> ConversationResponsePrompt:
    memory_turns = list(recent_turns or [])[-MAX_RECENT_TURNS:]
    return ConversationResponsePrompt(
        voice_id=voice_profile.id,
        voice_display_name=voice_profile.display_name,
        boundary_note=voice_profile.boundary_note,
        prohibited_associations=list(voice_profile.style.prohibited_associations),
        tone_preset=tone_preset,
        user_transcript_text=user_transcript_text.strip(),
        recent_turns=memory_turns,
        persona_instructions=_build_persona_instructions(
            voice_profile=voice_profile,
            tone_preset=tone_preset,
            recent_turn_count=len(memory_turns),
        ),
    )


def generateConversationReply(
    prompt: ConversationResponsePrompt,
    provider: Any | None = None,
) -> ConversationResponseResult:
    conversation_provider = provider or get_conversation_response_provider()
    result = conversation_provider.generate_reply(prompt)
    return ConversationResponseResult.model_validate(result)
