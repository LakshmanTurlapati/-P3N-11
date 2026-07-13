from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app

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
