# Phase 3: Audio Input and Turn Detection - Pattern Map

**Mapped:** 2026-07-03
**Files analyzed:** 16
**Analogs found:** 16 / 16

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `apps/web/components/studio-shell.tsx` | component | request-response | `apps/web/components/studio-shell.tsx` | exact |
| `apps/web/app/globals.css` | config | transform | `apps/web/app/globals.css` | exact |
| `apps/web/next.config.ts` | config | request-response | `apps/web/next.config.ts` | exact |
| `apps/web/tests/root-route.spec.ts` | test | request-response | `apps/web/tests/root-route.spec.ts` | exact |
| `apps/web/tests/audio-input.spec.ts` | test | request-response | `apps/web/tests/studio-generation.spec.ts` | role-match |
| `services/api/app/main.py` | config | request-response | `services/api/app/main.py` | exact |
| `services/api/app/routes/audio_turns.py` | route | request-response | `services/api/app/routes/generate.py` | role-match |
| `services/api/app/services/audio_turn_jobs.py` | service | CRUD | `services/api/app/services/generation_jobs.py` | role-match |
| `services/api/app/services/audio_turn_runtime.py` | service | event-driven | `services/api/app/services/generation_runtime.py` | role-match |
| `services/api/app/schemas/audio_turn.py` | model | transform | `services/api/app/schemas/generation.py` | role-match |
| `services/api/tests/conftest.py` | utility | file-I/O | `services/api/tests/conftest.py` | exact |
| `services/api/tests/test_audio_turn_jobs.py` | test | request-response | `services/api/tests/test_generation_jobs.py` | role-match |
| `services/speech-worker/providers/__init__.py` | config | transform | `services/speech-worker/providers/__init__.py` | exact |
| `services/speech-worker/providers/silero_vad_provider.py` | service | transform | `services/speech-worker/providers/cosyvoice_provider.py` | role-match |
| `services/speech-worker/providers/faster_whisper_stt_provider.py` | service | transform | `services/speech-worker/providers/cosyvoice_provider.py` | role-match |
| `services/speech-worker/tests/test_audio_turn_providers.py` | test | transform | `services/speech-worker/tests/test_cosyvoice_provider.py` | role-match |

## Pattern Assignments

### `apps/web/components/studio-shell.tsx` (component, request-response)

**Analog:** `apps/web/components/studio-shell.tsx`

**State + polling pattern** (lines 316-487):
```tsx
export function StudioShell() {
  const [generationText, setGenerationText] = useState("");
  const [selectedTonePreset, setSelectedTonePreset] =
    useState<GenerationTonePreset>("measured");
  const [attempts, setAttempts] = useState<GenerationJobRecord[]>([]);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const pollTimerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!activeJobId) {
      return undefined;
    }

    ...
    pollTimerRef.current = window.setTimeout(() => {
      void pollGeneration();
    }, POLL_INTERVAL_MS);
  }, [activeJobId]);
}
```

**Attempt list pattern** (lines 232-312):
```tsx
function RecentAttemptList({
  attempts,
  onRetryCurrentGeneration,
}: {
  attempts: GenerationJobRecord[];
  onRetryCurrentGeneration: () => void;
}) {
  return (
    <section className="recent-attempts" aria-labelledby="recent-attempts-title">
      ...
      <ol className="attempt-list" aria-label="Recent attempts">
        ...
      </ol>
    </section>
  );
}
```

Copy the same state ownership, polling cleanup, and session-scoped list rendering for spoken turns. Keep generation and audio-turn histories separate; add mic/upload state beside the composer instead of replacing the current form.

---

### `apps/web/app/globals.css` (config, transform)

**Analog:** `apps/web/app/globals.css`

**Form + card language** (lines 325-501):
```css
.generation-form {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 24px;
  border: 1px solid rgba(214, 160, 106, 0.18);
  background:
    linear-gradient(180deg, rgba(31, 24, 21, 0.92), rgba(18, 13, 11, 0.94));
}

.generation-form__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.current-clip-card,
.recent-attempts {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1.25rem;
  border-radius: 24px;
  border: 1px solid rgba(214, 160, 106, 0.22);
  background:
    linear-gradient(180deg, rgba(34, 27, 24, 0.95), rgba(17, 13, 11, 0.96)),
    rgba(20, 15, 13, 0.96);
}
```

**Attempt card + responsive pattern** (lines 593-821):
```css
.attempt-list {
  display: grid;
  gap: 0.9rem;
  padding: 0;
  margin: 0;
  list-style: none;
}

.attempt-card {
  display: grid;
  gap: 0.95rem;
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(250, 227, 198, 0.12);
  background: rgba(255, 255, 255, 0.025);
}

@media (max-width: 640px) {
  .generation-form {
    padding: 1rem;
    border-radius: 20px;
  }

  .generation-form__footer {
    flex-direction: column;
    align-items: stretch;
  }
}
```

Re-use the same dark theatrical card language for mic/upload controls, transcript review, and spoken-turn cards. Keep the mobile collapse behavior and action-button styling consistent with the existing studio surface.

---

### `apps/web/next.config.ts` (config, request-response)

**Analog:** `apps/web/next.config.ts`

**Rewrite bridge pattern** (lines 1-19):
```ts
const apiBaseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/generate",
        destination: `${apiBaseUrl}/generate`,
      },
      {
        source: "/generations/:path*",
        destination: `${apiBaseUrl}/generations/:path*`,
      },
      {
        source: "/voices/:path*",
        destination: `${apiBaseUrl}/voices/:path*`,
      },
    ];
  },
};
```

Add the audio-turn route family to the same rewrite array so the browser can call the backend on-origin for capture, polling, and controlled artifact access.

---

### `apps/web/tests/root-route.spec.ts` (test, request-response)

**Analog:** `apps/web/tests/root-route.spec.ts`

**Current smoke assertions** (lines 3-20):
```ts
test("root route opens the studio directly", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(page.getByRole("heading", { name: "Theatrical Voice Studio" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vesper Glass" })).toBeVisible();
  await expect(page.getByRole("status", { name: "Voice rights status" })).toContainText(
    "Approved for generation",
  );
  await expect(page.getByRole("textbox", { name: "Generation text" })).toBeVisible();
  await expect(page.getByRole("group", { name: "Tone preset" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Generate voice" })).toBeVisible();

  await expect(page.getByRole("button", { name: /retry/i })).toHaveCount(0);
  await expect(page.getByLabel(/mic/i)).toHaveCount(0);
  await expect(page.getByLabel(/upload/i)).toHaveCount(0);
  await expect(page.getByLabel(/live conversation/i)).toHaveCount(0);
  await expect(page.getByRole("button", { name: /playback/i })).toHaveCount(0);
});
```

Keep the direct-root and rights-gate smoke checks, but update the mic/upload expectations once the spoken-input controls are visible beside the composer.

---

### `apps/web/tests/audio-input.spec.ts` (test, request-response)

**Analog:** `apps/web/tests/studio-generation.spec.ts`

**Live backend polling pattern** (lines 50-157):
```ts
async function submitLiveGeneration(
  page: Page,
  text: string,
  tonePreset: GenerationTonePreset,
) {
  const generateResponsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().endsWith("/generate") &&
      response.status() === 200,
  );

  await page.getByRole("button", { name: "Generate voice" }).click();
  ...
}

async function waitForGenerationRecord(
  page: Page,
  jobId: string,
  expectedStatus: GenerationJobStatus,
) {
  await expect
    .poll(async () => {
      const response = await page.request.get(generationUrl);
      ...
      return latestRecord.status;
    })
    .toBe(expectedStatus);
}
```

Copy the same `waitForResponse` + `expect.poll` structure, but add browser audio capture mocks (`getUserMedia` / `MediaRecorder`) or upload fixtures so the spec can assert queued/running/succeeded/failed audio-turn states, editable transcript text, and the explicit `Use as generation text` handoff.

---

### `services/api/app/main.py` (config, request-response)

**Analog:** `services/api/app/main.py`

**Router inclusion pattern** (lines 3-10):
```py
from fastapi import FastAPI

from services.api.app.routes.generate import router as generate_router
from services.api.app.routes.voices import router as voices_router

app = FastAPI(title="Theatrical Voice Studio API")
app.include_router(generate_router)
app.include_router(voices_router)
```

Add the audio-turn router here so the backend actually serves the new capture/status endpoints.

---

### `services/api/app/routes/audio_turns.py` (route, request-response)

**Analog:** `services/api/app/routes/generate.py`

**Queued job + FileResponse pattern** (lines 5-69):
```py
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from services.api.app.schemas.generation import GenerationJobRecord, GenerationRequest
from services.api.app.services.generation_jobs import GenerationJobService
from services.api.app.services.generation_runtime import process_generation_job
from services.api.app.services.rights_gate import ensure_voice_allowed

router = APIRouter(tags=["generation"])


@router.post("/generate", response_model=GenerationJobRecord)
def generate(request: GenerationRequest, background_tasks: BackgroundTasks) -> GenerationJobRecord:
    ...


@router.get("/generations/{job_id}/audio")
def get_generation_audio(job_id: str) -> FileResponse:
    ...
```

**404 handling pattern** (lines 17-26, 42-61):
```py
if profile is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Voice profile not found.",
    )
```

Mirror the same route shape for audio turns: create the queued job, dispatch background processing, expose job status, and serve the controlled artifact URL. Add FastAPI upload primitives around it, but keep the job/404/error handling conventions identical.

---

### `services/api/app/services/audio_turn_jobs.py` (service, CRUD)

**Analog:** `services/api/app/services/generation_jobs.py`

**Object store + SQLite pattern** (lines 73-170):
```py
class LocalObjectStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.audio_root = self.root / "audio"
        self.audio_root.mkdir(parents=True, exist_ok=True)
        self._audio_root_resolved = self.audio_root.resolve()

    def write_audio(self, job_id: str, audio_bytes: bytes) -> Path:
        path = self._path_for_job(job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio_bytes)
        return path


class GenerationJobService:
    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS generation_jobs (
                    job_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL
                )
                """,
            )
```

**State transition pattern** (lines 172-324):
```py
def create_job(...):
    record = GenerationJobRecord(
        job_id=_job_id(),
        status=GenerationJobStatus.QUEUED,
        ...
    )
    return self._save_record(record)

def mark_running(self, job_id: str) -> GenerationJobRecord:
    ...

def mark_succeeded(...):
    self.object_store.write_audio(job_id, audio_bytes)
    ...

def mark_failed(self, job_id: str, *, error_message: str) -> GenerationJobRecord:
    ...
```

Copy the storage-root validation, persisted JSON record flow, and queued/running/succeeded/failed transitions. Do not copy `retry_job` for audio turns; D-17 prefers re-record/re-upload over mutating the same captured artifact.

---

### `services/api/app/services/audio_turn_runtime.py` (service, event-driven)

**Analog:** `services/api/app/services/generation_runtime.py`

**Provider loading + process pattern** (lines 69-158):
```py
@lru_cache(maxsize=1)
def get_generation_tts_provider():
    provider_class = _load_cosyvoice_provider_class()
    return provider_class()


def process_generation_job(
    job_id: str,
    *,
    job_service: GenerationJobService | None = None,
    provider: Any | None = None,
) -> GenerationJobRecord:
    job_service = job_service or GenerationJobService.from_env()

    running_record = job_service.mark_running(job_id)
    ...
    try:
        tts_provider = provider or get_generation_tts_provider()
        artifact = tts_provider.synthesize(...)
        return job_service.mark_succeeded(...)
    except Exception as exc:
        return job_service.mark_failed(job_id, error_message=str(exc))
```

**Audio normalization helper** (lines 32-96):
```py
def normalize_audio(
    artifact: SpeechArtifact,
    *,
    target_sample_rate_hz: int | None = None,
) -> SpeechArtifact:
    ...
    completed = subprocess.run(
        command,
        input=artifact.audio_bytes,
        capture_output=True,
        check=True,
    )
```

Copy the worker-root import guard, cached provider factory pattern, and exception-to-failed-job flow. Normalize captured/uploaded audio to mono WAV before VAD/STT, then persist transcript and compact VAD metadata back into the job record.

---

### `services/api/app/schemas/audio_turn.py` (model, transform)

**Analog:** `services/api/app/schemas/generation.py`

**Strict validation pattern** (lines 63-205):
```py
class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    voice_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    tone_preset: GenerationTonePreset
    ...

class GenerationTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def _require_end_after_start(self) -> "GenerationTiming":
        ...
```

**Nested record pattern** (lines 129-205):
```py
class GenerationAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: GenerationJobStatus = GenerationJobStatus.QUEUED
    provider_name: str | None = None
    mime_type: str | None = None
    error_message: str | None = None
    ...

class GenerationJobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ...
```

**Secondary analog:** `services/api/app/schemas/voice_profile.py` (lines 10-65) for `extra="forbid"` + `field_validator` style:
```py
class VoiceRights(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ...

class VoiceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ...
```

Keep audio-turn schema fields explicit, nested, and validated the same way. Add transcript/VAD/provider metadata as first-class record data, and keep job/status/timing coherence enforced in a model validator.

---

### `services/api/tests/conftest.py` (utility, file-I/O)

**Analog:** `services/api/tests/conftest.py`

**Existing generation fixtures** (lines 14-67):
```py
@pytest.fixture
def generation_storage_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "generation-store"
    monkeypatch.setenv("THEATRICAL_VOICE_STUDIO_STORAGE_ROOT", str(root))
    return root


@pytest.fixture
def client(generation_job_service, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(
        generate_route,
        "get_generation_job_service",
        lambda: generation_job_service,
        raising=False,
    )
    return TestClient(app)
```

Add the same temp-storage/object-store fixture shape for audio turns, then patch the audio-turn route/runtime module the same way the generation tests patch `generate_route` and `process_generation_job`.

---

### `services/api/tests/test_audio_turn_jobs.py` (test, request-response)

**Analog:** `services/api/tests/test_generation_jobs.py`

**Queue/status/storage pattern** (lines 28-137):
```py
response = client.post("/generate", json=generation_request.model_dump(mode="json"))

assert response.status_code == 200
assert payload["status"] == GenerationJobStatus.QUEUED.value
...
running_job = generation_job_service.mark_running(job_id)
assert running_job.status == GenerationJobStatus.RUNNING

succeeded_job = generation_job_service.mark_succeeded(
    job_id,
    audio_bytes=generation_audio_bytes,
    mime_type="audio/wav",
    provider_name="prototype-baseline-stub",
    audio_duration_ms=1536,
)
```

**Runtime/provider pattern** (lines 58-165 of `services/api/tests/test_generation_runtime.py`):
```py
updated_job = process_generation_job(
    created_job.job_id,
    job_service=generation_job_service,
    provider=provider,
)

assert provider.calls == [...]
assert updated_job.status == GenerationJobStatus.SUCCEEDED
assert generation_job_service.object_store.read_audio(created_job.job_id) == provider.audio_bytes
```

Copy the same queue/running/succeeded/failed assertions, artifact-path checks, and deterministic provider injection. Add upload validation and transcript/VAD metadata assertions, and keep weak/failed turns on the re-record/re-upload path instead of same-artifact retry.

---

### `services/speech-worker/providers/__init__.py` (config, transform)

**Analog:** `services/speech-worker/providers/__init__.py`

**Lazy export pattern** (lines 1-30):
```py
from .contracts import (
    AudioBuffer,
    SpeechArtifact,
    SpeechSegment,
    SpeechToSpeechProvider,
    STTProvider,
    TTSProvider,
    VADProvider,
    TranscriptResult,
)

__all__ = [
    "AudioBuffer",
    "CosyVoiceTTSProvider",
    "SpeechArtifact",
    "SpeechSegment",
    "SpeechToSpeechProvider",
    "STTProvider",
    "TTSProvider",
    "VADProvider",
    "TranscriptResult",
]


def __getattr__(name: str):
    if name == "CosyVoiceTTSProvider":
        from .cosyvoice_provider import CosyVoiceTTSProvider

        return CosyVoiceTTSProvider
    raise AttributeError(...)
```

Extend the same lazy-import export table for the Silero VAD and faster-whisper STT adapters so the API runtime can import them from the worker package root.

---

### `services/speech-worker/providers/silero_vad_provider.py` (service, transform)

**Analog:** `services/speech-worker/providers/cosyvoice_provider.py`

**Provider + backend loading pattern** (lines 92-199):
```py
class CosyVoiceTTSProvider(TTSProvider):
    provider_name = "cosyvoice"

    def __init__(..., backend: Any | None = None) -> None:
        ...
        self._backend = backend

    def synthesize(...):
        backend = self._backend or self._load_backend()
        ...

    def _load_backend(self) -> Any:
        self._ensure_repo_on_path()
        try:
            from cosyvoice.cli.cosyvoice import AutoModel
        except ImportError as exc:
            raise RuntimeError(...) from exc
```

**Contract shape** (lines 7-52 of `services/speech-worker/providers/contracts.py`):
```py
@runtime_checkable
class VADProvider(Protocol):
    provider_name: str

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        ...
```

Mirror the `provider_name` attr, constructor injection for tests, import-guarded backend loading, and runtime error messaging. Return `list[SpeechSegment]` with start/end/confidence, and keep the implementation swappable behind `VADProvider`.

---

### `services/speech-worker/providers/faster_whisper_stt_provider.py` (service, transform)

**Analog:** `services/speech-worker/providers/cosyvoice_provider.py`

**Provider + backend loading pattern** (lines 92-199):
```py
class CosyVoiceTTSProvider(TTSProvider):
    provider_name = "cosyvoice"
    ...
    def _load_backend(self) -> Any:
        self._ensure_repo_on_path()
        try:
            from cosyvoice.cli.cosyvoice import AutoModel
        except ImportError as exc:
            raise RuntimeError(...) from exc
```

**Transcript contract** (lines 22-52 of `services/speech-worker/providers/contracts.py`):
```py
@runtime_checkable
class STTProvider(Protocol):
    provider_name: str

    def transcribe(self, audio: AudioBuffer) -> TranscriptResult:
        ...
```

Use the same backend injection and dependency-guard style as the TTS provider, but return `TranscriptResult` with editable text plus language/confidence metadata. Keep optional package failures explicit so the tests can swap in deterministic fixtures.

---

### `services/speech-worker/tests/test_audio_turn_providers.py` (test, transform)

**Analog:** `services/speech-worker/tests/test_cosyvoice_provider.py`

**Backend injection pattern** (lines 20-97):
```py
class FakeCosyVoiceBackend:
    def inference_zero_shot(...):
        ...
        yield {"tts_speech": [0.0, 0.4, -0.4, 0.0]}


def test_cosyvoice_provider_synthesizes_a_playable_baseline_and_steers_tone(
    monkeypatch,
    tmp_path,
) -> None:
    ...
    monkeypatch.setattr("providers.cosyvoice_provider.normalize_audio", fake_normalize_audio)
    provider = CosyVoiceTTSProvider(...)
    artifact = provider.synthesize("The stage is mine.", "vesper-glass", tone="cutting")
```

**Protocol swappability pattern** (lines 15-88 of `services/speech-worker/tests/test_provider_contracts.py`):
```py
vad = DummyVAD()
stt = DummySTT()

assert isinstance(vad, VADProvider)
assert isinstance(stt, STTProvider)
assert vad.detect_speech_segments(audio)[0].start_ms == 0
assert stt.transcribe(audio).text == "transcribed:4"
```

Mirror the fake-backend injection style and assert the adapter still satisfies the protocol contracts. Include deterministic fallback coverage for missing optional speech packages so the tests remain runnable in this workspace.

## Shared Patterns

### Same-origin rewrites
**Source:** `apps/web/next.config.ts`
**Apply to:** `apps/web/next.config.ts`
```ts
{
  source: "/generations/:path*",
  destination: `${apiBaseUrl}/generations/:path*`,
}
```

### Job state machine
**Source:** `services/api/app/services/generation_jobs.py`
**Apply to:** `services/api/app/services/audio_turn_jobs.py`, `services/api/app/routes/audio_turns.py`, `services/api/tests/test_audio_turn_jobs.py`
```py
record.status = GenerationJobStatus.RUNNING
record.attempt.status = GenerationJobStatus.RUNNING
...
record.status = GenerationJobStatus.SUCCEEDED
record.playback_url = f"/generations/{job_id}/audio"
```

### Strict model validation
**Source:** `services/api/app/schemas/generation.py`
**Apply to:** `services/api/app/schemas/audio_turn.py`
```py
model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

### Provider boundary
**Source:** `services/speech-worker/providers/contracts.py` and `services/speech-worker/providers/__init__.py`
**Apply to:** `services/speech-worker/providers/silero_vad_provider.py`, `services/speech-worker/providers/faster_whisper_stt_provider.py`, `services/api/app/services/audio_turn_runtime.py`
```py
@runtime_checkable
class VADProvider(Protocol):
    ...
```

### Worker-path loading + error wrapping
**Source:** `services/api/app/services/generation_runtime.py`
**Apply to:** `services/api/app/services/audio_turn_runtime.py`
```py
try:
    from cosyvoice.cli.cosyvoice import AutoModel
except ImportError as exc:
    raise RuntimeError(...) from exc
```

### Audio normalization
**Source:** `services/speech-worker/audio/normalization.py`
**Apply to:** `services/api/app/services/audio_turn_runtime.py`
```py
completed = subprocess.run(
    command,
    input=artifact.audio_bytes,
    capture_output=True,
    check=True,
)
```

### Playwright polling
**Source:** `apps/web/tests/studio-generation.spec.ts`
**Apply to:** `apps/web/tests/audio-input.spec.ts`
```ts
await expect
  .poll(async () => {
    const response = await page.request.get(generationUrl);
    ...
  })
  .toBe(expectedStatus);
```

### Test fixtures
**Source:** `services/api/tests/conftest.py`
**Apply to:** `services/api/tests/conftest.py`
```py
monkeypatch.setattr(
    generate_route,
    "get_generation_job_service",
    lambda: generation_job_service,
    raising=False,
)
```

## No Analog Found

None.

## Metadata

**Analog search scope:** `apps/web`, `services/api`, `services/speech-worker`, `.planning/phases/02-consented-studio-generation`
**Pattern extraction date:** 2026-07-03
