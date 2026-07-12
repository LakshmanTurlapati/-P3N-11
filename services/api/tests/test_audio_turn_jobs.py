from __future__ import annotations

import io
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.schemas.audio_turn import AudioTurnJobStatus


@pytest.fixture
def audio_turn_storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "audio-turn-store"
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT", str(root))
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_VAD_FIXTURE", "1")
    return root


@pytest.fixture
def client(audio_turn_storage_root: Path) -> TestClient:
    return TestClient(app)


def _wav_bytes(
    *,
    sample_rate_hz: int = 16_000,
    lead_silence_ms: int = 120,
    speech_ms: int = 720,
    trail_silence_ms: int = 120,
    amplitude: int = 16_000,
) -> bytes:
    samples: list[int] = []
    for duration_ms, value in (
        (lead_silence_ms, 0),
        (speech_ms, amplitude),
        (trail_silence_ms, 0),
    ):
        sample_count = int(sample_rate_hz * duration_ms / 1000)
        samples.extend([value] * sample_count)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(b"".join(int(sample).to_bytes(2, "little", signed=True) for sample in samples))
    return buffer.getvalue()


def test_audio_turn_route_creates_a_queued_job_and_processes_vad_metadata(client) -> None:
    response = client.post(
        "/audio-turns",
        content=_wav_bytes(),
        headers={
            "Content-Type": "audio/wav",
            "X-Audio-Filename": "spoken-turn.wav",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["job_id"]
    assert payload["status"] == AudioTurnJobStatus.QUEUED.value

    job_id = payload["job_id"]

    detail_response = client.get(f"/audio-turns/{job_id}")
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["job_id"] == job_id
    assert detail["status"] == AudioTurnJobStatus.SUCCEEDED.value
    assert detail["vad_metadata"]["provider_name"] == "silero-vad"
    assert detail["vad_metadata"]["speech_start_ms"] < detail["vad_metadata"]["speech_end_ms"]
    assert detail["vad_metadata"]["speech_duration_ms"] > 0
    assert detail["vad_metadata"]["confidence"] is not None
    assert detail["attempt"]["vad_metadata"]["provider_name"] == "silero-vad"
    assert detail["attempt"]["vad_metadata"]["speech_duration_ms"] > 0

    audio_response = client.get(f"/audio-turns/{job_id}/audio")
    assert audio_response.status_code == 200
    assert audio_response.headers["content-type"].startswith("audio/wav")


def test_audio_turn_route_keeps_thin_turns_reviewable_with_a_warning(client) -> None:
    response = client.post(
        "/audio-turns",
        content=_wav_bytes(amplitude=900, speech_ms=160),
        headers={
            "Content-Type": "audio/wav",
            "X-Audio-Filename": "thin-turn.wav",
        },
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]
    detail_response = client.get(f"/audio-turns/{job_id}")
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["status"] == AudioTurnJobStatus.SUCCEEDED.value
    assert detail["vad_metadata"]["warning_message"] is not None
    assert "thin" in detail["vad_metadata"]["warning_message"].lower()
    assert detail["vad_metadata"]["segments"]


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
