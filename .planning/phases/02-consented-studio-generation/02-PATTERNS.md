# Phase 2: Consented Studio Generation - Pattern Map

**Mapped:** 2026-07-01
**Files analyzed:** 17
**Analogs found:** 15 / 17

**Note:** `README.md` is stale relative to the planning artifacts and current code. Treat it as docs drift only; the pattern map below uses the current codebase and `.planning/` docs as the source of truth.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `apps/web/components/studio-shell.tsx` | component | request-response | `apps/web/components/studio-shell.tsx` | exact |
| `apps/web/app/globals.css` | config | transform | `apps/web/app/globals.css` | exact |
| `apps/web/next.config.ts` | config | request-response | `apps/web/next.config.ts` | exact |
| `apps/web/tests/root-route.spec.ts` | test | request-response | `apps/web/tests/root-route.spec.ts` | exact |
| `apps/web/tests/studio-generation.spec.ts` | test | request-response | `apps/web/tests/studio-generation.spec.ts` | exact |
| `services/api/app/schemas/generation.py` | model | transform | `services/api/app/schemas/generation.py` | exact |
| `services/api/app/routes/generate.py` | route | request-response | `services/api/app/routes/generate.py` | exact |
| `services/api/app/services/stub_generation.py` | service | request-response | `services/api/app/services/stub_generation.py` | exact |
| `services/api/app/services/generation_jobs.py` | service | CRUD | `services/api/app/services/stub_generation.py` | role-match |
| `services/api/app/services/object_store.py` | store | file-I/O | none | none |
| `services/api/tests/test_generate_stub.py` | test | request-response | `services/api/tests/test_generate_stub.py` | exact |
| `services/api/tests/test_generation_jobs.py` | test | request-response | `services/api/tests/test_generate_stub.py` | role-match |
| `services/api/tests/conftest.py` | utility | file-I/O | `services/speech-worker/tests/conftest.py` | role-match |
| `services/speech-worker/providers/cosyvoice_provider.py` | provider | request-response | `services/speech-worker/providers/contracts.py` | role-match |
| `services/speech-worker/audio/normalization.py` | utility | file-I/O | none | none |
| `services/speech-worker/tests/test_cosyvoice_provider.py` | test | request-response | `services/speech-worker/tests/test_provider_contracts.py` | role-match |
| `services/speech-worker/tests/test_audio_normalization.py` | test | file-I/O | `services/speech-worker/tests/test_provider_contracts.py` | partial |

## Pattern Assignments

### `apps/web/components/studio-shell.tsx` (component, request-response)

**Analog:** `apps/web/components/studio-shell.tsx`

**State + submit flow** (lines 35-83):
```tsx
export function StudioShell() {
  const [selectedVoiceId, setSelectedVoiceId] = useState(
    voiceDisplaySeeds[0]?.id ?? "",
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);
  ...
  const response = await fetch("/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      voice_id: selectedVoiceId,
    }),
  });
```

**Result card pattern** (lines 178-237):
```tsx
{generationResult ? (
  <article className="generation-card" aria-labelledby="generation-card-title">
    ...
    <section className="generation-card__trace" aria-label="Provider trace">
      <ul>
        {generationResult.provider_trace.map((entry) => (
          <li key={`${entry.stage}-${entry.provider}`}>
            <strong>{entry.stage}</strong>
            <span>{entry.provider}</span>
            <p>{entry.detail}</p>
          </li>
        ))}
      </ul>
    </section>
  </article>
) : null}
```

**Use for Phase 2:** keep the same stateful client component, but extend it with text input, tone preset state, job polling, retry, and an actual audio element instead of the stub result card.

### `apps/web/app/globals.css` (config, transform)

**Analog:** `apps/web/app/globals.css`

**Current control and card styles** (lines 312-476):
```css
.studio-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 3.4rem;
  padding: 0.95rem 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(214, 160, 106, 0.42);
  ...
}

.generation-state {
  margin: 1rem 0 0;
  min-height: 1.5rem;
  color: var(--muted);
}

.generation-card {
  margin-top: 1rem;
  padding: 1.25rem;
  border-radius: 24px;
  border: 1px solid rgba(214, 160, 106, 0.22);
  ...
}
```

**Use for Phase 2:** add styles for the text field, tone preset chips, job-state badges, retry affordance, audio player, and recent-attempts list while keeping the existing dark theatrical palette and responsive breakpoints.

### `apps/web/next.config.ts` (config, request-response)

**Analog:** `apps/web/next.config.ts`

**Rewrite bridge pattern** (lines 3-17):
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
        source: "/voices/:path*",
        destination: `${apiBaseUrl}/voices/:path*`,
      },
    ];
  },
};
```

**Use for Phase 2:** keep the same rewrite shape and add any new job/status or playback paths that the browser needs to reach on the FastAPI control plane.

### `apps/web/tests/root-route.spec.ts` (test, request-response)

**Analog:** `apps/web/tests/root-route.spec.ts`

**Current smoke assertions** (lines 3-20):
```ts
test("root route opens the studio directly", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(page.getByRole("heading", { name: "Theatrical Voice Studio" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vesper Glass" })).toBeVisible();
  await expect(page.getByRole("status")).toContainText("Approved for generation");
  await expect(page.getByRole("button", { name: "Generate stub reading" })).toBeVisible();

  await expect(page.getByRole("textbox")).toHaveCount(0);
  await expect(page.getByLabel(/tone preset/i)).toHaveCount(0);
  await expect(page.getByRole("button", { name: /retry/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /playback/i })).toHaveCount(0);
  await expect(page.getByLabel(/mic/i)).toHaveCount(0);
});
```

**Use for Phase 2:** flip the textbox/tone/retry/playback expectations because those controls now belong on the studio root. Keep the no-mic assertion unless live conversation work lands in a later phase.

### `apps/web/tests/studio-generation.spec.ts` (test, request-response)

**Analog:** `apps/web/tests/studio-generation.spec.ts`

**Current request/result contract** (lines 3-23):
```ts
test("studio generation posts the bundled voice and renders the structured metadata card", async ({
  page,
}) => {
  await page.goto("/");
  const generationResponse = page.waitForResponse(
    (response) => response.url().endsWith("/generate") && response.status() === 200,
  );

  await page.getByRole("button", { name: "Generate stub reading" }).click();
  await generationResponse;

  const generationCard = page.getByRole("article", { name: "Generation result" });
  ...
});
```

**Use for Phase 2:** keep the same browser-to-API flow, but assert text entry, tone selection, queued/running/succeeded/failed job states, playback from a controlled URL, and retry after failure.

### `services/api/app/schemas/generation.py` (model, transform)

**Analog:** `services/api/app/schemas/generation.py`

**Strict model + validator pattern** (lines 13-101):
```py
class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    voice_id: str = Field(min_length=1)
    ...

class GenerationTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def _require_end_after_start(self) -> "GenerationTiming":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self
```

**Use for Phase 2:** extend this file with text, tone preset, job status, playback URL, and artifact metadata while keeping `extra="forbid"` and explicit validators.

### `services/api/app/routes/generate.py` (route, request-response)

**Analog:** `services/api/app/routes/generate.py`

**Current route shape** (lines 3-23):
```py
router = APIRouter(tags=["generation"])


@router.post("/generate", response_model=GenerationResult)
def generate(request: GenerationRequest) -> GenerationResult:
    profile = VOICE_REGISTRY.get(request.voice_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found.",
        )

    allowed_profile = ensure_voice_allowed(profile)
    return build_stub_generation_result(allowed_profile)
```

**Use for Phase 2:** keep `ensure_voice_allowed` ahead of any generation work, then create or fetch the job result instead of returning metadata-only output.

### `services/api/app/services/stub_generation.py` (service, request-response)

**Analog:** `services/api/app/services/stub_generation.py`

**Structured result assembly** (lines 17-57):
```py
def build_stub_generation_result(profile: VoiceProfile) -> GenerationResult:
    started_at = datetime.now(UTC)
    ended_at = started_at + timedelta(milliseconds=18)

    return GenerationResult(
        provider_type=STUB_PROVIDER_TYPE,
        voice_id=profile.id,
        rights_check=GenerationRightsCheck(
            status="approved",
            approved_for_generation=True,
            message="Rights gate approved the bundled voice profile.",
        ),
        result_metadata=GenerationResultMetadata(
            status="metadata-only",
            summary="Metadata-only stub generation completed without audio playback.",
            artifact_label="Structured studio result card",
            provider_note="Phase 1 keeps the stub provider inline in the API control plane.",
        ),
        provider_trace=[
            ...
        ],
        timing=GenerationTiming(...),
    )
```

**Use for Phase 2:** this is the assembly pattern to replace or wrap with the real job-based service. Keep the rights-check, trace, and timing fields, but make the result carry job state and playback metadata.

### `services/api/app/services/generation_jobs.py` (service, CRUD)

**Analog:** `services/api/app/services/stub_generation.py`

**Copy the same service boundary**:
```py
return GenerationResult(
    provider_type=STUB_PROVIDER_TYPE,
    voice_id=profile.id,
    rights_check=GenerationRightsCheck(...),
    result_metadata=GenerationResultMetadata(...),
    provider_trace=[...],
    timing=GenerationTiming(...),
)
```

**Use for Phase 2:** move from one-shot metadata assembly to persisted job rows, state transitions (`queued`, `running`, `succeeded`, `failed`), retry reuse of last inputs, and controlled playback URL attachment.

### `services/api/app/services/object_store.py` (store, file-I/O)

**Analog:** none in the current codebase.

**Use research pattern:** build a local filesystem-backed object-store abstraction that writes generated clips under a local storage directory and returns controlled playback URLs. Do not return inline bytes or base64. Follow `.planning/phases/02-consented-studio-generation/02-RESEARCH.md` lines 224-234 and 261-262.

### `services/api/tests/test_generate_stub.py` (test, request-response)

**Analog:** `services/api/tests/test_generate_stub.py`

**Current success and blocked-path assertions** (lines 15-91):
```py
def test_generate_stub_returns_structured_metadata_only() -> None:
    response = client.post("/generate", json={"voice_id": "vesper-glass"})
    ...
    assert payload["provider_type"] == "metadata-only-stub"
    assert "audio" not in payload
    assert "playback_url" not in payload
```

**Use for Phase 2:** if this file survives, rewrite it so it no longer expects the metadata-only stub contract. If the phase drops it, move the same coverage into `services/api/tests/test_generation_jobs.py`.

### `services/api/tests/test_generation_jobs.py` (test, request-response)

**Analog:** `services/api/tests/test_generate_stub.py`

**Copy the same TestClient pattern**:
```py
client = TestClient(app)

def test_generate_stub_returns_structured_metadata_only() -> None:
    response = client.post("/generate", json={"voice_id": "vesper-glass"})
    ...
```

**Use for Phase 2:** change the assertions to the job lifecycle contract, retry behavior, metadata persistence, and playback URL shape, while keeping the blocked-profile response exact.

### `services/api/tests/conftest.py` (utility, file-I/O)

**Analog:** `services/speech-worker/tests/conftest.py`

**Bootstrap pattern** (lines 1-10):
```py
ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)

if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)
```

**Use for Phase 2:** mirror the import bootstrap and add shared fixtures for temp storage, API clients, and any object-store or job-store overrides.

### `services/speech-worker/providers/cosyvoice_provider.py` (provider, request-response)

**Analog:** `services/speech-worker/providers/contracts.py`

**Provider contract** (lines 54-65):
```py
@runtime_checkable
class TTSProvider(Protocol):
    provider_name: str

    def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        """Synthesize spoken audio for the requested voice."""
```

**Secondary reference:** `services/speech-worker/tests/test_provider_contracts.py` lines 29-46 show a concrete `SpeechArtifact` return shape with `audio_bytes`, `sample_rate_hz`, `mime_type`, `provider_name`, and `duration_ms`.

**Use for Phase 2:** implement the real CosyVoice adapter behind the same contract, preserving tone steering and artifact shape.

### `services/speech-worker/audio/normalization.py` (utility, file-I/O)

**Analog:** none in the current codebase.

**Use research pattern:** implement FFmpeg-backed normalization in the worker path, keeping generated output in an accepted sample format before storage/playback. Follow `.planning/phases/02-consented-studio-generation/02-RESEARCH.md` lines 353, 385, and 418-419.

### `services/speech-worker/tests/test_cosyvoice_provider.py` (test, request-response)

**Analog:** `services/speech-worker/tests/test_provider_contracts.py`

**Swappable provider test pattern** (lines 29-46 and 69-88):
```py
class DummyTTS:
    provider_name = "dummy-tts"

    def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        payload = f"{voice_id}:{tone or 'neutral'}:{text}".encode("utf-8")
        return SpeechArtifact(
            audio_bytes=payload,
            sample_rate_hz=22_050,
            mime_type="audio/wav",
            provider_name=self.provider_name,
            duration_ms=25,
        )
```

**Use for Phase 2:** keep the provider-agnostic assertions, but swap in the real CosyVoice adapter and validate playable output plus duration/sample metadata.

### `services/speech-worker/tests/test_audio_normalization.py` (test, file-I/O)

**Analog:** `services/speech-worker/tests/test_provider_contracts.py` (partial)

**Audio-shape assertions to reuse** (lines 69-88):
```py
audio = AudioBuffer(pcm16=b"\x00\x01\x02\x03", sample_rate_hz=16_000)
...
assert audio.channels == 1
assert audio.mime_type == "audio/wav"
```

**Use for Phase 2:** extend this toward FFmpeg normalization checks and the accepted playback format, even though no direct normalization test exists yet in the codebase.

## Shared Patterns

### Rights Gate

**Source:** `services/api/app/services/rights_gate.py` (lines 53-60)
```py
def ensure_voice_allowed(profile: VoiceProfile) -> VoiceProfile:
    if not has_required_rights_metadata(profile):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=BLOCKED_RIGHTS_MESSAGE,
        )

    return profile
```

**Apply to:** `services/api/app/routes/generate.py`, any job creation path, and any retry flow. Do not bypass the server-owned approval check.

### Strict Schemas

**Source:** `services/api/app/schemas/voice_profile.py` (lines 10-64) and `services/api/app/schemas/generation.py` (lines 13-101)
```py
class VoiceRights(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

**Apply to:** generation request/job schemas, tone preset enums, and playback metadata. Keep `extra="forbid"` and explicit validators.

### Provider Boundary

**Source:** `services/speech-worker/providers/contracts.py` (lines 54-65)
```py
class TTSProvider(Protocol):
    provider_name: str

    def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        tone: str | None = None,
    ) -> SpeechArtifact:
        """Synthesize spoken audio for the requested voice."""
```

**Apply to:** any real TTS implementation, especially the CosyVoice adapter.

### Browser-to-API Bridge

**Source:** `apps/web/next.config.ts` (lines 3-17)
```ts
async rewrites() {
  return [
    {
      source: "/generate",
      destination: `${apiBaseUrl}/generate`,
    },
    {
      source: "/voices/:path*",
      destination: `${apiBaseUrl}/voices/:path*`,
    },
  ];
}
```

**Apply to:** any new status, retry, or playback endpoints that the browser needs to reach during local verification.

### Result Assembly

**Source:** `services/api/app/services/stub_generation.py` (lines 17-57)

**Apply to:** the Phase 2 job result service. Keep the compact trace/timing shape, but switch the payload from metadata-only output to job-backed playback metadata.

### In-Session UI State

**Source:** `apps/web/components/studio-shell.tsx` and `apps/web/tests/root-route.spec.ts`

**Apply to:** keep attempts in memory for the current browser session only. Do not add durable clip history or refresh restoration in Phase 2.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `services/api/app/services/object_store.py` | store | file-I/O | No existing storage helper or file-serving utility exists in the codebase. Follow the research decision for a local filesystem-backed object store and controlled playback URLs. |
| `services/speech-worker/audio/normalization.py` | utility | file-I/O | No existing FFmpeg/audio-normalization helper exists in the worker tree. Follow the research decision to normalize generated audio before storage/playback. |

## Metadata

**Analog search scope:** `apps/web/`, `services/api/`, `services/speech-worker/`, and the phase research docs
**Pattern extraction date:** 2026-07-01
