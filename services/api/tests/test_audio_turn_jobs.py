from __future__ import annotations

import io
import wave
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.schemas.audio_turn import AudioTurnJobStatus, AudioTurnRequest
from services.api.app.services.audio_turn_jobs import AudioTurnJobService
from services.api.app.services.audio_turn_runtime import process_audio_turn_job


@pytest.fixture
def audio_turn_storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "audio-turn-store"
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT", str(root))
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_VAD_FIXTURE", "1")
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STT_FIXTURE", "1")
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
    assert detail["provider_name"] == "faster-whisper"
    assert detail["vad_metadata"]["provider_name"] == "silero-vad"
    assert detail["vad_metadata"]["speech_start_ms"] < detail["vad_metadata"]["speech_end_ms"]
    assert detail["vad_metadata"]["speech_duration_ms"] > 0
    assert detail["vad_metadata"]["confidence"] is not None
    assert detail["transcript_text"] == "fixture transcript"
    assert detail["transcript_language"] == "en"
    assert detail["transcript_confidence"] == pytest.approx(0.83)
    assert detail["attempt"]["vad_metadata"]["provider_name"] == "silero-vad"
    assert detail["attempt"]["vad_metadata"]["speech_duration_ms"] > 0
    assert detail["attempt"]["transcript_text"] == "fixture transcript"
    assert detail["attempt"]["transcript_language"] == "en"
    assert detail["attempt"]["transcript_confidence"] == pytest.approx(0.83)

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
    assert detail["transcript_text"] == "fixture transcript"
    assert detail["transcript_language"] == "en"
    assert detail["transcript_confidence"] == pytest.approx(0.83)


@dataclass
class FakeSpeechSegment:
    start_ms: int
    end_ms: int
    confidence: float | None = None


class FakeAudioTurnVADProvider:
    provider_name = "fake-vad"

    def __init__(self) -> None:
        self.calls: list[object] = []

    def detect_speech_segments(self, audio):
        self.calls.append(audio)
        return [
            FakeSpeechSegment(start_ms=150, end_ms=320, confidence=0.82),
            FakeSpeechSegment(start_ms=390, end_ms=700, confidence=0.76),
        ]


class FakeAudioTurnSTTProvider:
    provider_name = "fake-stt"

    def __init__(self) -> None:
        self.calls: list[object] = []

    def transcribe(self, audio):
        self.calls.append(audio)
        return type(
            "TranscriptResult",
            (),
            {
                "text": "edited transcript from the turn",
                "language": "en",
                "confidence": 0.88,
            },
        )()


def test_audio_turn_runtime_transcribes_the_vad_span_and_persists_transcript_metadata(
    audio_turn_storage_root: Path,
) -> None:
    job_service = AudioTurnJobService(storage_root=audio_turn_storage_root)
    request = AudioTurnRequest(
        capture_source="upload",
        audio_filename="spoken-turn.wav",
        audio_mime_type="audio/wav",
    )
    created_job = job_service.create_job(request, _wav_bytes())
    vad_provider = FakeAudioTurnVADProvider()
    stt_provider = FakeAudioTurnSTTProvider()

    updated_job = process_audio_turn_job(
        created_job.job_id,
        job_service=job_service,
        vad_provider=vad_provider,
        stt_provider=stt_provider,
    )

    assert updated_job.status == AudioTurnJobStatus.SUCCEEDED
    assert updated_job.vad_provider_name == "fake-vad"
    assert updated_job.provider_name == "fake-stt"
    assert updated_job.transcript_text == "edited transcript from the turn"
    assert updated_job.transcript_language == "en"
    assert updated_job.transcript_confidence == pytest.approx(0.88)
    assert updated_job.attempt.transcript_text == "edited transcript from the turn"
    assert updated_job.attempt.transcript_language == "en"
    assert updated_job.attempt.transcript_confidence == pytest.approx(0.88)
    assert len(vad_provider.calls) == 1
    assert len(stt_provider.calls) == 1
    assert stt_provider.calls[0].sample_rate_hz == 16_000
    assert len(stt_provider.calls[0].pcm16) == 17_600

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
