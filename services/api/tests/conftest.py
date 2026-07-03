from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.routes import generate as generate_route
from services.api.app.schemas.generation import GenerationRequest, GenerationTonePreset
from services.api.app.voice_registry.bundled_voice import VESPER_GLASS_PROFILE


@pytest.fixture
def generation_storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "generation-store"
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT", str(root))
    return root


@pytest.fixture
def generation_object_store(generation_storage_root: Path):
    from services.api.app.services.generation_jobs import LocalObjectStore

    return LocalObjectStore(generation_storage_root)


@pytest.fixture
def generation_job_service(generation_object_store):
    from services.api.app.services.generation_jobs import GenerationJobService

    return GenerationJobService(object_store=generation_object_store)


@pytest.fixture
def generation_request() -> GenerationRequest:
    return GenerationRequest(
        voice_id=VESPER_GLASS_PROFILE.id,
        text="Deliver one measured, theatrical line.",
        tone_preset=GenerationTonePreset.MEASURED,
    )


@pytest.fixture
def generation_audio_bytes() -> bytes:
    return b"RIFFphase2-audio"


@pytest.fixture
def client(generation_job_service, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(
        generate_route,
        "get_generation_job_service",
        lambda: generation_job_service,
        raising=False,
    )
    return TestClient(app)


@pytest.fixture(autouse=True)
def disable_background_generation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generate_route,
        "process_generation_job",
        lambda *args, **kwargs: None,
        raising=False,
    )
