from __future__ import annotations

import io
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.routes import conversation as conversation_route
from services.api.app.schemas.conversation import (
    ConversationResponseResult,
    ConversationTurnStatus,
)
from services.api.app.schemas.generation import GenerationTonePreset
from services.api.app.services.conversation_jobs import (
    ConversationSessionService,
    ConversationTurnService,
)
from services.api.app.services.conversation_runtime import synthesizeConversationTurn
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE

CONVERSATION_SESSION_STATUS_LISTENING = "listening"
CONVERSATION_SESSION_STATUS_STOPPED = "stopped"


@pytest.fixture
def conversation_storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "conversation-store"
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT", str(root))
    return root


@pytest.fixture
def client(conversation_storage_root: Path) -> TestClient:
    return TestClient(app)


def _wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16_000)
        wav_file.writeframes((1200).to_bytes(2, byteorder="little", signed=True) * 16_000)
    return buffer.getvalue()


class _SpeechyVADProvider:
    provider_name = "fixture-vad"

    def detect_speech_segments(self, audio):
        _ = audio
        return [
            type(
                "SpeechSegment",
                (),
                {"start_ms": 0, "end_ms": 480, "confidence": 0.91},
            )(),
        ]


class _TranscriptProvider:
    provider_name = "fixture-stt"

    def transcribe(self, audio):
        _ = audio
        return type(
            "Transcript",
            (),
            {"text": "Give me the next line.", "language": "en", "confidence": 0.97},
        )()


class _ResponseProvider:
    provider_name = "fixture-response"

    def generate_reply(self, prompt):
        assert prompt.tone_preset == GenerationTonePreset.CUTTING
        return ConversationResponseResult(
            provider_name=self.provider_name,
            tone_preset=prompt.tone_preset,
            text="Naturally. I will keep this sharp. No borrowed masks.",
        )


class _TTSProvider:
    provider_name = "fixture-tts"

    def synthesize(self, text: str, voice_id: str, *, tone: str):
        assert text == "Naturally. I will keep this sharp. No borrowed masks."
        assert voice_id == VESPER_GLASS_PROFILE.id
        assert tone == "cutting"
        return type(
            "SpeechArtifact",
            (),
            {
                "provider_name": self.provider_name,
                "mime_type": "audio/wav",
                "audio_bytes": b"RIFFconversation-audio",
                "duration_ms": 432,
            },
        )()


def assert_session_record(
    record: dict[str, object],
    *,
    expected_status: str,
    expected_session_id: str | None = None,
) -> None:
    session_id = record["session_id"]
    assert isinstance(session_id, str)
    assert session_id.startswith("conversation-session-")
    if expected_session_id is not None:
        assert session_id == expected_session_id

    assert record["status"] == expected_status
    assert record["turns"] == []


def test_conversation_session_route_starts_an_inline_session(client: TestClient) -> None:
    response = client.post("/conversation-sessions")

    assert response.status_code == 200

    session_record = response.json()
    assert_session_record(
        session_record,
        expected_status=CONVERSATION_SESSION_STATUS_LISTENING,
    )

    session_id = session_record["session_id"]
    detail_response = client.get(f"/conversation-sessions/{session_id}")

    assert detail_response.status_code == 200
    assert_session_record(
        detail_response.json(),
        expected_status=CONVERSATION_SESSION_STATUS_LISTENING,
        expected_session_id=session_id,
    )


def test_conversation_session_stop_route_preserves_the_session_record(
    client: TestClient,
) -> None:
    start_response = client.post("/conversation-sessions")

    assert start_response.status_code == 200

    session_id = start_response.json()["session_id"]

    stop_response = client.post(f"/conversation-sessions/{session_id}/stop")

    assert stop_response.status_code == 200

    stopped_record = stop_response.json()
    assert_session_record(
        stopped_record,
        expected_status=CONVERSATION_SESSION_STATUS_STOPPED,
        expected_session_id=session_id,
    )

    detail_response = client.get(f"/conversation-sessions/{session_id}")

    assert detail_response.status_code == 200
    assert_session_record(
        detail_response.json(),
        expected_status=CONVERSATION_SESSION_STATUS_STOPPED,
        expected_session_id=session_id,
    )


def test_conversation_turn_interrupt_route_records_cancel_state_and_stage_timings(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    session_service = ConversationSessionService(storage_root=tmp_path / "sessions")
    turn_service = ConversationTurnService(
        storage_root=tmp_path / "turns",
        session_service=session_service,
    )
    session = session_service.create_session()
    queued_turn = turn_service.create_turn(
        session.session_id,
        audio_bytes=_wav_bytes(),
        audio_mime_type="audio/wav",
        tone_preset=GenerationTonePreset.MEASURED,
        audio_filename="spoken-turn.wav",
    )

    monkeypatch.setattr(
        conversation_route,
        "get_conversation_session_service",
        lambda: session_service,
        raising=False,
    )
    monkeypatch.setattr(
        conversation_route,
        "get_conversation_turn_service",
        lambda: turn_service,
        raising=False,
    )

    response = client.post(f"/conversation-turns/{queued_turn.turn_id}/interrupt")

    assert response.status_code == 200

    interrupted_turn = response.json()
    assert interrupted_turn["turn_id"] == queued_turn.turn_id
    assert interrupted_turn["status"] in {
        ConversationTurnStatus.INTERRUPTED.value,
        ConversationTurnStatus.CANCELED.value,
    }
    assert interrupted_turn["cancel_state"]["requested_at"]
    assert (
        interrupted_turn["cancel_state"]["interrupted_at"]
        or interrupted_turn["cancel_state"]["canceled_at"]
    )
    assert interrupted_turn["timing"]["speech_end_to_transcript_ms"] is not None
    assert interrupted_turn["timing"]["response_text_ms"] is not None
    assert interrupted_turn["timing"]["tts_complete_ms"] is not None
    assert interrupted_turn["timing"]["playback_start_ms"] is not None
    assert interrupted_turn["timing"]["duration_ms"] >= 0
    assert session_service.get_session(session.session_id).turns[0].turn_id == queued_turn.turn_id

    detail_response = client.get(f"/conversation-turns/{queued_turn.turn_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == interrupted_turn["status"]


def test_synthesize_conversation_turn_persists_stage_timing_metadata(
    tmp_path: Path,
) -> None:
    session_service = ConversationSessionService(storage_root=tmp_path / "sessions")
    turn_service = ConversationTurnService(
        storage_root=tmp_path / "turns",
        session_service=session_service,
    )
    session = session_service.create_session()
    queued_turn = turn_service.create_turn(
        session.session_id,
        audio_bytes=_wav_bytes(),
        audio_mime_type="audio/wav",
        tone_preset=GenerationTonePreset.CUTTING,
        audio_filename="spoken-turn.wav",
    )

    updated_turn = synthesizeConversationTurn(
        queued_turn.turn_id,
        turn_service=turn_service,
        voice_profile=VESPER_GLASS_PROFILE,
        vad_provider=_SpeechyVADProvider(),
        stt_provider=_TranscriptProvider(),
        response_provider=_ResponseProvider(),
        tts_provider=_TTSProvider(),
    )

    assert updated_turn.status == ConversationTurnStatus.SUCCEEDED
    assert updated_turn.response_text == "Naturally. I will keep this sharp. No borrowed masks."
    assert updated_turn.playback_url == f"/conversation-turns/{queued_turn.turn_id}/audio"
    assert updated_turn.tone_preset == GenerationTonePreset.CUTTING
    assert updated_turn.timing.speech_end_to_transcript_ms is not None
    assert updated_turn.timing.response_text_ms is not None
    assert updated_turn.timing.tts_complete_ms is not None
    assert updated_turn.timing.playback_start_ms is not None
    persisted_turn = turn_service.get_turn(queued_turn.turn_id)
    assert persisted_turn.timing.speech_end_to_transcript_ms is not None
    assert persisted_turn.timing.playback_start_ms is not None
    assert persisted_turn.latency_ms == persisted_turn.timing.duration_ms
    assert turn_service.get_audio_path(queued_turn.turn_id).read_bytes() == b"RIFFconversation-audio"


def test_synthesize_conversation_turn_leaves_an_interrupted_turn_recoverable(
    tmp_path: Path,
) -> None:
    session_service = ConversationSessionService(storage_root=tmp_path / "sessions")
    turn_service = ConversationTurnService(
        storage_root=tmp_path / "turns",
        session_service=session_service,
    )
    session = session_service.create_session()
    queued_turn = turn_service.create_turn(
        session.session_id,
        audio_bytes=_wav_bytes(),
        audio_mime_type="audio/wav",
        tone_preset=GenerationTonePreset.CUTTING,
        audio_filename="spoken-turn.wav",
    )

    interrupted_turn = turn_service.mark_interrupted(queued_turn.turn_id)

    assert interrupted_turn.status in {
        ConversationTurnStatus.INTERRUPTED,
        ConversationTurnStatus.CANCELED,
    }
    assert interrupted_turn.cancel_state is not None

    late_turn = synthesizeConversationTurn(
        queued_turn.turn_id,
        turn_service=turn_service,
        voice_profile=VESPER_GLASS_PROFILE,
        vad_provider=_SpeechyVADProvider(),
        stt_provider=_TranscriptProvider(),
        response_provider=_ResponseProvider(),
        tts_provider=_TTSProvider(),
    )

    assert late_turn.status == interrupted_turn.status
    assert late_turn.cancel_state is not None
    assert turn_service.get_turn(queued_turn.turn_id).status == interrupted_turn.status
