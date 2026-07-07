from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app


@pytest.fixture
def audio_turn_storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "audio-turn-store"
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT", str(root))
    return root


@pytest.fixture
def client(audio_turn_storage_root: Path) -> TestClient:
    return TestClient(app)


def test_audio_turn_route_creates_a_queued_job_and_serves_controlled_audio(client) -> None:
    response = client.post(
        "/audio-turns",
        content=b"recorded-audio-bytes",
        headers={
            "Content-Type": "audio/webm",
            "X-Audio-Filename": "spoken-turn.webm",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["job_id"]
    assert payload["status"] == "queued"

    job_id = payload["job_id"]

    detail_response = client.get(f"/audio-turns/{job_id}")
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["job_id"] == job_id
    assert detail["status"] == "queued"

    audio_response = client.get(f"/audio-turns/{job_id}/audio")
    assert audio_response.status_code == 200
    assert audio_response.headers["content-type"].startswith("audio/")
    assert audio_response.content == b"recorded-audio-bytes"


def test_audio_turn_route_rejects_invalid_audio_uploads(client) -> None:
    response = client.post(
        "/audio-turns",
        content=b"not-audio",
        headers={
            "Content-Type": "text/plain",
            "X-Audio-Filename": "spoken-turn.txt",
        },
    )

    assert response.status_code in {400, 415, 422}
