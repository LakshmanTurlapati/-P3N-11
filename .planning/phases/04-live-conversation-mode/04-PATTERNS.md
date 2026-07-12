# Phase 4: Live Conversation Mode - Pattern Map

**Mapped:** 2026-07-12
**Files analyzed:** 17
**Analogs found:** 17 / 17

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `apps/web/components/studio-shell.tsx` | component | event-driven | `apps/web/components/studio-shell.tsx` | exact |
| `apps/web/app/globals.css` | config | transform | `apps/web/app/globals.css` | exact |
| `apps/web/next.config.ts` | config | request-response | `apps/web/next.config.ts` | exact |
| `apps/web/tests/root-route.spec.ts` | test | event-driven | `apps/web/tests/root-route.spec.ts` | exact |
| `apps/web/tests/conversation-mode.spec.ts` | test | event-driven | `apps/web/tests/audio-input.spec.ts` | role-match |
| `services/api/app/main.py` | config | request-response | `services/api/app/main.py` | exact |
| `services/api/app/routes/conversation.py` | route | request-response | `services/api/app/routes/audio_turns.py` | role-match |
| `services/api/app/schemas/conversation.py` | model | transform | `services/api/app/schemas/generation.py` | role-match |
| `services/api/app/services/conversation_jobs.py` | service | CRUD | `services/api/app/services/generation_jobs.py` | role-match |
| `services/api/app/services/conversation_runtime.py` | service | event-driven | `services/api/app/services/audio_turn_runtime.py` | role-match |
| `services/api/tests/conftest.py` | utility | file-I/O | `services/api/tests/conftest.py` | exact |
| `services/api/tests/test_conversation_jobs.py` | test | CRUD | `services/api/tests/test_audio_turn_jobs.py` | role-match |
| `services/api/tests/test_conversation_provider.py` | test | transform | `services/api/tests/test_generate_stub.py` | role-match |
| `services/speech-worker/providers/contracts.py` | provider | transform | `services/speech-worker/providers/contracts.py` | exact |
| `services/speech-worker/providers/conversation_provider.py` | provider | transform | `services/speech-worker/providers/cosyvoice_provider.py` | role-match |
| `services/speech-worker/providers/__init__.py` | config | transform | `services/speech-worker/providers/__init__.py` | exact |
| `services/speech-worker/tests/test_conversation_provider.py` | test | transform | `services/speech-worker/tests/test_provider_contracts.py` | role-match |

## Pattern Assignments

### `apps/web/components/studio-shell.tsx` (component, event-driven)

**Analog:** [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx)

**Session state + polling** (lines 630-659, 933-1090):
```tsx
const [spokenTurns, setSpokenTurns] = useState<AudioTurnJobRecord[]>([]);
const [activeAudioTurnId, setActiveAudioTurnId] = useState<string | null>(null);
const mediaRecorderRef = useRef<MediaRecorder | null>(null);
const audioTurnPollTimerRef = useRef<number | null>(null);

useEffect(() => {
  if (!activeAudioTurnId) {
    return undefined;
  }

  let cancelled = false;
  ...
}, [activeAudioTurnId]);
```

**Capture control pattern** (lines 772-855):
```tsx
async function startRecording() {
  const recorder = new MediaRecorder(stream, { mimeType: preferredMimeType });
  recorder.onstop = () => {
    ...
    void submitAudioTurn(recordingBlob, "recording", "spoken-turn.wav").catch(
      () => undefined,
    );
  };
}

function stopRecording() { ... }
function handleAudioButtonClick() { ... }
```

**Session-scoped turn cards** (lines 485-627, 1318-1332):
```tsx
function SpokenTurnList({ ... }) {
  return (
    <section className="recent-attempts" aria-labelledby="spoken-turns-title">
      <ol className="attempt-list" aria-label="Spoken turns">
        ...
      </ol>
    </section>
  );
}
```

Copy the same session-owned state, timer cleanup, and upsert-on-poll flow for live conversation. If the shell grows too large, extract the live panel into a `conversation-panel.tsx` subcomponent and keep this same card/list pattern.

---

### `apps/web/app/globals.css` (config, transform)

**Analog:** [apps/web/app/globals.css](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/globals.css)

**Card + chip language** (lines 489-649):
```css
.current-clip-card,
.recent-attempts {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1.25rem;
  border-radius: 24px;
  border: 1px solid rgba(214, 160, 106, 0.22);
}

.attempt-card {
  display: grid;
  gap: 0.95rem;
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(250, 227, 198, 0.12);
  background: rgba(255, 255, 255, 0.025);
}
```

**Status + responsive pattern** (lines 410-474, 765-829):
```css
.generation-status {
  display: inline-flex;
  align-items: center;
  min-height: 3.4rem;
  padding: 0.85rem 1rem;
  border-radius: 16px;
}

@media (max-width: 640px) {
  .generation-form__footer {
    flex-direction: column;
    align-items: stretch;
  }

  .generation-status,
  .studio-action {
    width: 100%;
    justify-content: center;
  }
}
```

Reuse the same theatrical dark cards, compact chips, and mobile collapse behavior for live turn cards, the interrupt button, and the latency chip. The existing `attempt-card--queued|running|succeeded|failed` states are the right visual language for live turn phases too.

---

### `apps/web/next.config.ts` (config, request-response)

**Analog:** [apps/web/next.config.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts)

**Rewrite bridge** (lines 1-32):
```ts
const apiBaseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/generate", destination: `${apiBaseUrl}/generate` },
      { source: "/generations/:path*", destination: `${apiBaseUrl}/generations/:path*` },
      { source: "/audio-turns", destination: `${apiBaseUrl}/audio-turns` },
      { source: "/audio-turns/:path*", destination: `${apiBaseUrl}/audio-turns/:path*` },
    ];
  },
};
```

Add the conversation session/turn routes to the same array so the browser stays on the app origin for capture, polling, interrupt, and controlled audio playback.

---

### `apps/web/tests/root-route.spec.ts` (test, event-driven)

**Analog:** [apps/web/tests/root-route.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/root-route.spec.ts)

**Current smoke shape** (lines 3-24):
```ts
test("root route opens the studio directly", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(page.getByRole("heading", { name: "Theatrical Voice Studio" })).toBeVisible();
  await expect(page.getByRole("button", { name: /playback/i })).toHaveCount(0);
  await expect(page.getByLabel(/live conversation/i)).toHaveCount(0);
});
```

Keep the direct-root and rights-gate smoke checks, but invert the live-conversation assertions once the inline panel lands. This file should prove the root route still opens the studio, not that live controls are absent forever.

---

### `apps/web/tests/conversation-mode.spec.ts` (test, event-driven)

**Analog:** [apps/web/tests/audio-input.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/audio-input.spec.ts) and [apps/web/tests/studio-generation.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/studio-generation.spec.ts)

**MediaRecorder mock pattern** (audio-input lines 63-140):
```ts
await page.addInitScript(
  ({ wavBytesBase64 }) => {
    class FakeMediaRecorder {
      start(): void { ... }
      stop(): void { ... }
    }
    ...
  },
  { wavBytesBase64: wavBytes.toString("base64") },
);
```

**Polling + response waiting pattern** (studio-generation lines 50-157):
```ts
const generateResponsePromise = page.waitForResponse(
  (response) =>
    response.request().method() === "POST" &&
    response.url().endsWith("/generate") &&
    response.status() === 200,
);

await expect.poll(async () => {
  const response = await page.request.get(generationUrl);
  const payload = (await response.json()) as { status?: string };
  return payload.status;
}).toBe(expectedStatus);
```

Use the MediaRecorder mock to prove Start/Stop and VAD-driven turn submission, then reuse the polling pattern to assert response playback, interrupt/cancel, and the compact total-latency chip. The browser spec should combine the spoken-input capture flow with the generation playback assertions, not re-implement both from scratch.

---

### `services/api/app/main.py` (config, request-response)

**Analog:** [services/api/app/main.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py)

**Router registration** (lines 3-12):
```py
from services.api.app.routes.audio_turns import router as audio_turns_router
from services.api.app.routes.generate import router as generate_router
from services.api.app.routes.voices import router as voices_router

app.include_router(audio_turns_router)
app.include_router(generate_router)
app.include_router(voices_router)
```

Register the conversation router here alongside the existing root routes so the FastAPI control plane exposes the new session/turn endpoints without changing the app entrypoint shape.

---

### `services/api/app/routes/conversation.py` (route, request-response)

**Analog:** [services/api/app/routes/audio_turns.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py) and [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py)

**Import + handler pattern** (audio_turns lines 1-112, generate lines 1-69):
```py
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import FileResponse

@router.post("/conversation-turns", response_model=ConversationTurnRecord)
async def create_conversation_turn(
    request: Request,
    background_tasks: BackgroundTasks,
) -> ConversationTurnRecord:
    audio_bytes = await request.body()
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio upload is required.")
    ...
```

**Controlled audio serving** (audio_turns/generate `FileResponse` pattern):
```py
return FileResponse(
    path=audio_path,
    media_type=record.attempt.mime_type or "audio/wav",
    filename=f"{turn_id}.wav",
)
```

Copy the same request-body checks, MIME validation, `BackgroundTasks` handoff, `404` handling, and same-origin file serving. Add interrupt/cancel endpoints as cooperative state transitions, not as hard-kill process controls.

---

### `services/api/app/schemas/conversation.py` (model, transform)

**Analog:** [services/api/app/schemas/generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py), [services/api/app/schemas/audio_turn.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/audio_turn.py), and [services/api/app/schemas/voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py)

**Strict nested validation** (generation/audio_turn lines 1-205):
```py
class GenerationJobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ...
    @model_validator(mode="after")
    def _validate_status_and_playback_fields(self) -> "GenerationJobRecord":
        ...
        return self
```

**Boundary vocabulary** (voice_profile lines 10-57):
```py
class VoiceStyle(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    summary: str = Field(min_length=1)
    style_traits: list[str] = Field(min_length=1)
    prohibited_associations: list[str] = Field(min_length=1)
```

Conversation schemas should include the first-class turn record, session record, timing/attempt nesting, and the response-provider input that carries `boundary_note`, `prohibited_associations`, tone instructions, and a small recent-turn memory window. Keep `extra="forbid"` and explicit validators so a turn cannot become "succeeded" without the required timing/audio fields.

---

### `services/api/app/services/conversation_jobs.py` (service, CRUD)

**Analog:** [services/api/app/services/generation_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py) and [services/api/app/services/audio_turn_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py)

**SQLite + object-store pattern** (audio_turn_jobs/generation_jobs lines 37-182, 73-196):
```py
class AudioTurnObjectStore:
    def _path_for_job(self, job_id: str) -> Path:
        if Path(job_id).name != job_id:
            raise ValueError("job_id must not contain path separators")
        ...

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

**State transition pattern** (generation_jobs lines 201-289, audio_turn_jobs lines 187-258):
```py
def mark_failed(self, job_id: str, *, error_message: str) -> GenerationJobRecord:
    record = self.get_job(job_id)
    ...
    record.attempt.error_message = error_message
    record.timing.duration_ms = elapsed_ms
    return self._save_record(record)
```

Copy the same `_now()`, `_milliseconds()`, `_job_id()`, `_save_record()`, and `_load_record()` structure. If conversation audio needs both input and response artifacts, keep the same path-safety checks and add explicit `mark_interrupted` / `mark_canceled` transitions that preserve the failed stage and timing just like `mark_failed`.

---

### `services/api/app/services/conversation_runtime.py` (service, event-driven)

**Analog:** [services/api/app/services/audio_turn_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py) and [services/api/app/services/generation_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py)

**Worker-root + dependency loading** (audio_turn_runtime lines 1-71):
```py
WORKER_ROOT_ENV = "THEATRICAL_VOICE_STUDIO_WORKER_ROOT"

@lru_cache(maxsize=1)
def _load_worker_dependencies() -> tuple[Any, Any, Any, Any, Any]:
    _ensure_worker_root_on_path()
    from audio.normalization import normalize_audio
    from providers import AudioBuffer, FasterWhisperSTTProvider, SileroVADProvider, SpeechArtifact
```

**Process / fail-safe orchestration** (generation_runtime lines 125-158):
```py
def process_generation_job(
    job_id: str,
    *,
    job_service: GenerationJobService | None = None,
    provider: Any | None = None,
) -> GenerationJobRecord:
    running_record = job_service.mark_running(job_id)
    try:
        ...
        return job_service.mark_succeeded(...)
    except Exception as exc:
        return job_service.mark_failed(job_id, error_message=str(exc))
```

The conversation runtime should insert response generation between STT and TTS, record stage timings for transcript/response/TTS/playback, and check cancel state between stages. Build the short session-memory window from recent turn records only, and let refresh wipe it.

---

### `services/api/tests/conftest.py` (utility, file-I/O)

**Analog:** [services/api/tests/conftest.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/conftest.py)

**Fixture + monkeypatch pattern** (lines 14-67):
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

Conversation tests can copy this exact fixture shape for a conversation storage root, a patched job service, and a patched runtime/provider hook. If it gets crowded, split the conversation fixtures into a sibling module, but keep the same monkeypatch + TestClient approach.

---

### `services/api/tests/test_conversation_jobs.py` (test, CRUD)

**Analog:** [services/api/tests/test_audio_turn_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_audio_turn_jobs.py), [services/api/tests/test_generation_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generation_jobs.py), and [services/api/tests/test_generation_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generation_runtime.py)

**State-transition assertions** (generation/audio_turn tests lines 57-123, 166-199):
```py
response = client.post("/audio-turns", content=_wav_bytes(), headers={...})
assert response.status_code == 200
payload = response.json()
assert payload["status"] == AudioTurnJobStatus.QUEUED.value

running_job = generation_job_service.mark_running(job_id)
assert running_job.status == GenerationJobStatus.RUNNING

succeeded_job = generation_job_service.mark_succeeded(...)
assert succeeded_job.status == GenerationJobStatus.SUCCEEDED
```

Conversation job tests should verify queued/running/speaking/succeeded/failed/interrupted transitions, preserved timing metadata, and controlled playback URLs. Add one cancel/interrupt assertion so a partially processed turn remains recoverable and the next user turn still works.

---

### `services/api/tests/test_conversation_provider.py` (test, transform)

**Analog:** [services/api/tests/test_generate_stub.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generate_stub.py), [services/api/tests/test_rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_rights_gate.py), and [services/api/tests/test_voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_voice_profile.py)

**Boundary + exact-message pattern** (rights_gate/voice_profile/test_generate_stub lines 10-111):
```py
profile = VoiceProfile.model_construct(
    id="blocked-voice",
    display_name="Blocked Voice",
    boundary_note="Original voice profile with a theatrical edge.",
    rights=VoiceRights.model_construct(...),
    style=VoiceStyle.model_construct(
        summary="Measured theatrical delivery",
        style_traits=["Measured theatrical delivery"],
        prohibited_associations=["Any protected character voice"],
    ),
)

with pytest.raises(HTTPException) as excinfo:
    ensure_voice_allowed(profile)

assert excinfo.value.detail == BLOCKED_RIGHTS_MESSAGE
```

Use the same style to assert the conversation response schema/provider keeps the original-voice boundary, the prohibited associations, and the short-memory window explicit. Add a regression for names like Loki and Tom Hiddleston so the provider can only return an original Vesper-safe persona.

---

### `services/speech-worker/providers/contracts.py` (provider, transform)

**Analog:** [services/speech-worker/providers/contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py)

**Protocol boundary** (lines 7-79):
```py
@dataclass(frozen=True, slots=True)
class SpeechArtifact:
    audio_bytes: bytes
    sample_rate_hz: int
    mime_type: str
    provider_name: str

@runtime_checkable
class TTSProvider(Protocol):
    provider_name: str
    def synthesize(...): ...
```

Add the conversation-response dataclasses and protocol here with the same frozen `@dataclass(slots=True)` and `@runtime_checkable` style. Keep the provider boundary narrow: explicit input, explicit output, no browser dependencies, and no hidden global state.

---

### `services/speech-worker/providers/conversation_provider.py` (provider, transform)

**Analog:** [services/speech-worker/providers/cosyvoice_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/cosyvoice_provider.py) and [services/api/app/services/stub_generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py)

**Tone steering + provider identity** (cosyvoice lines 23-177):
```py
TONE_PROMPTS: dict[str, str] = {
    "measured": "Deliver the line with measured, theatrical restraint.",
    "cutting": "Deliver the line with a cutting, icy, honeyed-sarcasm edge.",
    "grandiose": "Deliver the line with grandiose, theatrical presence.",
}

class CosyVoiceTTSProvider(TTSProvider):
    provider_name = "cosyvoice"
```

**Deterministic default pattern** (stub_generation lines 19-60):
```py
def build_stub_generation_result(profile: VoiceProfile, request: GenerationRequest) -> GenerationResult:
    return GenerationResult(
        provider_type=STUB_PROVIDER_TYPE,
        job_id=f"job-{uuid4().hex[:12]}",
        status=GenerationJobStatus.QUEUED,
        ...
    )
```

Copy the explicit `provider_name`, constructor injection, and tone validation pattern, but return response text instead of audio. The default implementation should be deterministic, concise, and easy to regression-test for banned identities and protected-character drift.

---

### `services/speech-worker/providers/__init__.py` (config, transform)

**Analog:** [services/speech-worker/providers/__init__.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/__init__.py)

**Package export pattern** (lines 1-40):
```py
__all__ = [
    "AudioBuffer",
    "CosyVoiceTTSProvider",
    "FasterWhisperSTTProvider",
    "SileroVADProvider",
    ...
]

def __getattr__(name: str):
    if name == "CosyVoiceTTSProvider":
        from .cosyvoice_provider import CosyVoiceTTSProvider
        return CosyVoiceTTSProvider
```

Export the new conversation provider through the same lazy-import surface so API/runtime code can import it from `providers` without paying the worker import cost up front.

---

### `services/speech-worker/tests/test_conversation_provider.py` (test, transform)

**Analog:** [services/speech-worker/tests/test_provider_contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/tests/test_provider_contracts.py) and [services/speech-worker/tests/test_cosyvoice_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/tests/test_cosyvoice_provider.py)

**Protocol + backend injection pattern** (provider_contracts / cosyvoice lines 69-97):
```py
assert isinstance(vad, VADProvider)
assert isinstance(stt, STTProvider)
assert isinstance(tts, TTSProvider)

provider = CosyVoiceTTSProvider(repo_root=repo_root, model_dir=model_dir, prompt_audio_path=prompt_audio_path, backend=backend)
artifact = provider.synthesize("The stage is mine.", "vesper-glass", tone="cutting")
```

Copy the same fake-backend and protocol-compliance style for the deterministic responder. Assert the tone presets steer the reply, and assert the returned text never claims to be Loki, Tom Hiddleston, or any other protected or unlicensed identity.

## Shared Patterns

### Session-Scoped Records
**Source:** [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx), [services/api/app/services/generation_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py), [services/api/app/services/audio_turn_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py)

```py
def mark_failed(self, job_id: str, *, error_message: str) -> GenerationJobRecord:
    record = self.get_job(job_id)
    ...
    record.timing.duration_ms = elapsed_ms
    return self._save_record(record)
```

Use the same nested `timing` + `attempt` shape for conversation turns, and keep browser state as a pollable view of the server record rather than the source of truth.

### Boundary Enforcement
**Source:** [services/api/app/schemas/voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py), [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py), [services/api/app/voice_registry/bundled_voice.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py)

```py
class VoiceStyle(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    prohibited_associations: list[str] = Field(min_length=1)
```

The conversation provider schema should carry the original-voice boundary and prohibited associations explicitly; do not rely on prompt text alone.

### Cooperative Interrupt
**Source:** [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx), [services/api/app/services/audio_turn_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py), [services/api/app/services/generation_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py)

```tsx
function stopRecording() {
  const recorder = mediaRecorderRef.current;
  if (!recorder || recorder.state === "inactive") {
    return;
  }
  recorder.stop();
}
```

Stop playback immediately in the browser, abort pending fetches/polling where possible, and mark the turn interrupted or canceled in the backend record. Do not assume background tasks can be hard-killed.

### Controlled Audio Serving
**Source:** [services/api/app/routes/audio_turns.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py), [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py)

```py
return FileResponse(
    path=audio_path,
    media_type=record.attempt.mime_type or "audio/wav",
    filename=record.audio_filename,
)
```

Keep all generated audio behind same-origin routes and object-store path safety. No raw filesystem paths in the browser.

### Browser Test Shape
**Source:** [apps/web/tests/audio-input.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/audio-input.spec.ts), [apps/web/tests/studio-generation.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/studio-generation.spec.ts)

```ts
await page.addInitScript(({ wavBytesBase64 }) => { ... }, { wavBytesBase64: ... });
await expect.poll(async () => { ... }).toBe(expectedStatus);
```

Conversation browser tests should combine microphone mocking, backend polling, response playback, and interrupt assertions in one flow.
Treat `MediaRecorder` as capture transport, not the clock; keep stage timings in backend metadata and API responses.

## Metadata

**Search scope:** `apps/web`, `services/api`, `services/speech-worker`, `.planning/phases/04-live-conversation-mode`

**Pattern extraction date:** 2026-07-12
