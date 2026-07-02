# Phase 2: Consented Studio Generation - Research

**Researched:** 2026-07-01
**Domain:** consented studio generation, real TTS provider integration, and browser audio playback
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Phase 2 should prioritize a safe real-audio baseline provider first. The exact provider is left to research/planning, but it must produce real playable audio through the server-side provider interface.
- **D-02:** The first generated audio is a prototype audition: it should be playable and tone-steered, but it may sound like an early baseline rather than the final theatrical Vesper Glass voice.
- **D-03:** Tests may use fixtures, but the phase only counts as complete when a configured real provider produces playable audio locally or in the intended runtime.
- **D-04:** Prefer an open-source, offline, or open-weight TTS adapter behind the provider interface, even if setup is heavier than a commercial API.
- **D-05:** Do not add reference-audio upload, recording, or consent intake UI in Phase 2. Support consent/license notes in backend data/schema where needed, but keep the first generation loop text-to-speech focused.
- **D-06:** Research cloning-capable candidates such as OpenVoice, F5-TTS, and CosyVoice for license/runtime fit, then implement the safest feasible real baseline provider. Phase 2 does not require final cloning quality.
- **D-07:** A generic or non-final Vesper voice is allowed if the UI and metadata clearly label it as a prototype baseline and never claim protected-character, performer, or final Vesper quality.
- **D-08:** Phase 2 should return/store complete generated clips for playback. Streaming and partial audio belong to the later live conversation work.

### Generation Job Shape
- **D-09:** Introduce a generation job lifecycle instead of keeping `/generate` as a direct synchronous final-result response.
- **D-10:** The first lifecycle should expose coarse states: `queued`, `running`, `succeeded`, and `failed`, with user-friendly loading and error text.
- **D-11:** Retry should reuse the last text, voice, and tone to create a new job after a failure. Keep the failed job metadata visible instead of mutating it away.
- **D-12:** If generation takes longer than expected, keep the job visible as running. Do not mark it failed only because the browser waited a fixed time; show status and allow retry after failure.

### Tone Preset Set
- **D-13:** Ship three focused presets: `Measured`, `Cutting`, and `Grandiose`.
- **D-14:** Tone presets map to prompt/style metadata passed to the provider or future persona layer. Do not add numeric sliders or provider-specific controls in Phase 2.
- **D-15:** Show compact one-line descriptions for presets near the selector without exposing prompt internals.
- **D-16:** Presets must be safe by construction: each preset carries the original-voice boundary and prohibited-association guard, and no preset may request a protected character or real performer.

### Playback And Metadata Surface
- **D-17:** Show the current playable clip prominently and keep recent in-session attempts with status and metadata.
- **D-18:** Normal UI should show operational essentials: voice, tone, provider, status, audio duration/timing, and rights approval.
- **D-19:** Store generated audio through a local object-store abstraction that writes files under a local storage directory and returns controlled playback URLs. Do not return inline audio bytes/base64, and do not require an S3-compatible bucket in Phase 2.
- **D-20:** Generated attempts are in-session only across the browser session. Do not add a durable clip library, persistent local history, or page-refresh restoration in Phase 2.

### the agent's Discretion
- **D-21:** The user delegated the initial provider-bar choice. The chosen default is a safe real-audio baseline first, because it validates the end-to-end generation and playback loop without pretending that a consented cloned reference voice already exists.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GOV-04 | User can attach or record consent/license notes for a voice reference before that voice is used for cloning. | Keep rights/consent data in backend schemas only; Phase 2 should not add reference intake UI. Existing `VoiceRights` already carries `source_notes`, `consent_notes`, and `intended_use`. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| STUD-03 | User can enter text to synthesize into speech. | The current studio shell is already the right extension point; Phase 2 should add a text input there and keep the root-route handoff intact. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/01-no-login-vertical-skeleton/01-03-SUMMARY.md] |
| STUD-04 | User can choose a tone preset for generation. | Use the three locked presets from CONTEXT.md and map them to provider/style metadata only; no sliders or provider knobs. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/FEATURES.md] |
| STUD-05 | User can submit a generation request and see loading, success, and error states. | Preserve the existing client loading/error state path in `StudioShell`, but change the request to job creation and status polling/result rendering. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| STUD-06 | User can play the generated audio in the browser. | Phase 2 must add a real playable clip and browser audio controls; generated clips should come back through controlled URLs, not inline audio bytes. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] |
| STUD-07 | User can retry a failed generation without refreshing the app. | Retry must reuse the last text, voice, and tone and keep the failed attempt visible in-session. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| PIPE-02 | System can synthesize speech through at least one real TTS or voice-cloning provider adapter. | Research and implement one real provider behind `TTSProvider`; the best current candidate is a CosyVoice repo checkout, with F5-TTS and OpenVoice as alternatives. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: https://github.com/SWivid/F5-TTS] [CITED: https://github.com/myshell-ai/OpenVoice] |
| PIPE-03 | System stores generated audio with metadata that includes provider, voice profile, tone preset, and generation timing. | Extend the existing generation schema so the job result carries the metadata surface the roadmap expects. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| PIPE-04 | System can normalize uploaded, recorded, or generated audio into formats accepted by the selected providers. | Use FFmpeg-backed normalization in the worker path; Phase 2 only needs generated audio, but the worker should normalize the output format now. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/STACK.md] [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Keep the product centered on consented or licensed voice use only. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]
- Preserve the persona boundary: the first voice may evoke a theatrical trickster archetype, but it must not claim to be or exactly sound like Marvel's Loki, Tom Hiddleston, or another protected/unlicensed identity. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]
- Treat v1 as a cloud web app on rented GPU infrastructure; do not plan around local-only assumptions. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]
- Keep v1 no-login and keep the studio controls minimal. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]
- Keep speech components behind provider interfaces so future model swaps do not require product rewrites. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]
- Respect the latency/quality balance and keep rights/consent metadata attached to voice profiles before generation. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]
- Use the GSD workflow before direct repo edits; do not bypass `/gsd-quick`, `/gsd-debug`, or `/gsd-execute-phase` unless the user explicitly asks to bypass the workflow. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md]

## Summary

Phase 2 should be planned as a real job-based generation loop that extends the Phase 1 rights gate and provider contracts into playable audio, not as another synchronous metadata stub. The code already has the important handoff points: server-owned rights metadata, strict generation/voice schemas, the backend `/generate` route, Next.js rewrites that send browser traffic to FastAPI, and a client shell that already owns loading/error state. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx]

The best current baseline provider to plan around is the official CosyVoice repo checkout, starting from the 0.5B/3.0 line, because the repo explicitly documents zero-shot multilingual synthesis, zero-shot voice cloning, and bi-streaming while carrying an Apache-2.0 license. F5-TTS is technically viable, but its official repo says the pretrained models are CC-BY-NC, and the package-legitimacy gate flags the obvious PyPI names for CosyVoice, F5-TTS, torch, and torchaudio as suspicious enough to require human checkpoints before any install. That makes a repo checkout path with explicit verification a better planning target than a blind package install. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: https://github.com/SWivid/F5-TTS] [CITED: gsd package-legitimacy check]

The README is stale relative to the planning artifacts: it still describes Clerk, Drizzle, pgvector, Trigger.dev, Upstash Redis, and Azure/Cartesia, while the current planning docs and codebase are already aligned around a no-login studio, a backend rights gate, provider interfaces, and a job-based generation path. Treat the README drift as a docs follow-up, not as a Phase 2 design input. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/README.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/PROJECT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/ROADMAP.md]

**Primary recommendation:** implement Phase 2 around the official CosyVoice repo checkout behind the existing `TTSProvider` contract, with a job record plus worker/background-task seam, filesystem-backed object storage, and browser playback from controlled URLs. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] [CITED: https://fastapi.tiangolo.com/advanced/custom-response/]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Text input and tone preset selection | Browser / Client | API / Backend | The browser owns the form, but the backend owns the actual generation request and preset mapping. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx] |
| Rights gate and job lifecycle | API / Backend | Database / Storage | Rights approval stays server-side and the job states must survive long enough for retry and playback metadata. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] |
| Speech synthesis and normalization | GPU Worker | API / Backend | Model code belongs behind the provider boundary so the API stays model-agnostic. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] |
| Audio artifact persistence and playback URL creation | Database / Storage | API / Backend | Generated audio should be stored outside the request process and exposed through controlled URLs. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 16.2.9 | Studio UI and browser-to-API rewrites | Already pinned in the repo and already used for the Phase 1 browser-to-API bridge. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] |
| React | 19.2.7 | UI components | Already pinned in the repo and aligned with the current Next.js app router surface. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] |
| TypeScript | 6.0.3 | UI and API type safety | Already pinned in the repo; keeps the studio request/response shapes explicit. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] |
| FastAPI | 0.138.2 | API/control plane and job endpoints | Already pinned in the repo; official docs support `BackgroundTasks`, `FileResponse`, and `StreamingResponse` for the job-based pattern. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/] [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] |
| Python | 3.11.12 | Speech worker runtime | The workspace already has a 3.11 venv, which is the safer worker target than the global 3.13 interpreter for speech-model repos. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.venv/bin/python] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] |
| Pydantic | 2.13.4 | Strict request/response validation | Already pinned in the repo; the current schemas use `extra="forbid"` and explicit validators. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] |
| CosyVoice | Fun-CosyVoice3-0.5B-2512 / CosyVoice 3.0 repo checkout | First real TTS baseline | Official repo documentation says zero-shot multilingual speech synthesis, zero-shot voice cloning, bi-streaming, and Apache-2.0; use the repo checkout path rather than a PyPI package name. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: https://arxiv.org/abs/2407.05407] [CITED: https://arxiv.org/abs/2412.10117] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @playwright/test | 1.61.1 | Browser verification | Already pinned in the repo for the studio smoke tests. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] |
| pytest | 9.1.1 | API/worker tests | Already pinned in the repo for backend regression coverage. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] |
| uvicorn | 0.49.0 | Local API server | Already pinned in the repo and used by the Playwright web server setup. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts] |
| `torch` | 2.12.1 `[WARNING: flagged as suspicious - verify before using.]` | Speech-model runtime | Required by the chosen TTS runtime path; the package gate flagged this install target as SUS, so add a human checkpoint before install. [CITED: gsd package-legitimacy check] |
| `torchaudio` | 2.11.0 `[WARNING: flagged as suspicious - verify before using.]` | Audio IO and waveform handling | Required by the worker runtime path; human-verify before install. [CITED: gsd package-legitimacy check] |
| FFmpeg | system binary | Audio normalization and format conversion | Missing locally; install it in the worker image or via the OS package manager. [CITED: command -v ffmpeg] |
| SQLite 3 | system database | Local metadata/job store | Matches the project's SQLite-first internal MVP direction. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/PROJECT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/STACK.md] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CosyVoice repo checkout | F5-TTS repo or pip package | F5-TTS has the simplest pip-based startup path and a strong zero-shot story, but the official repo says the pretrained models are CC-BY-NC, and the package gate flags the PyPI name as suspicious, so it is a weaker Phase 2 baseline. [CITED: https://github.com/SWivid/F5-TTS] [CITED: gsd package-legitimacy check] |
| CosyVoice repo checkout | OpenVoice repo | OpenVoice has MIT code and strong tone/color cloning and style-control language, but it is more reference-clip oriented and the `openvoice` PyPI install target does not exist, so it does not match the text-only Phase 2 shape as cleanly. [CITED: https://github.com/myshell-ai/OpenVoice] [CITED: gsd package-legitimacy check] |
| Job lifecycle + controlled URLs | Synchronous `/generate` with inline bytes | Simpler code today, but it recreates the exact latency and storage problems Phase 2 is supposed to fix. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] |

**Installation:**
```bash
# Keep the existing repo-pinned web stack for Phase 2.
pnpm install

# Use the project venv or python3.11 for the worker runtime.
./.venv/bin/python -m pip install -e '.[dev]'

# Install the selected provider from its official repo checkout, not a blind registry name.
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `openvoice` | PyPI | none | none | none | SLOP | REMOVED |
| `f5-tts` | PyPI | 2026-04-20 | unknown | https://github.com/SWivid/F5-TTS | SUS | Flagged - planner must add checkpoint |
| `cosyvoice` | PyPI | 2024-11-17 | unknown | https://github.com/lucasjinreal/CosyVoice | SUS | Flagged - planner must add checkpoint |
| `torch` | PyPI | 2026-06-17 | unknown | https://pytorch.org | SUS | Flagged - planner must add checkpoint |
| `torchaudio` | PyPI | 2026-03-23 | unknown | https://github.com/pytorch/audio | SUS | Flagged - planner must add checkpoint |

**Packages removed due to [SLOP] verdict:** `openvoice`
**Packages flagged as suspicious [SUS]:** `f5-tts`, `cosyvoice`, `torch`, `torchaudio`

## Architecture Patterns

### System Architecture Diagram

```text
User browser
  -> Next.js studio UI
  -> API generation request
  -> backend rights gate and job creation
  -> job store / metadata store
  -> worker/provider adapter
  -> audio normalization
  -> filesystem-backed object store
  -> controlled playback URL
  -> browser audio element
```

### Recommended Project Structure

```text
apps/
  web/
    app/
    components/
    lib/
services/
  api/
    app/
      routes/
      schemas/
      services/
  speech-worker/
    providers/
    audio/
    benchmarks/
packages/
  shared/
infra/
  docker/
  deploy/
```

### Pattern 1: Provider Adapter Boundary
**What:** Keep each TTS or voice-cloning implementation behind the `TTSProvider` contract. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py]
**When to use:** Always for Phase 2, because provider choice is still unsettled and the phase needs to preserve future swapability. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md]
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
class TTSProvider(Protocol):
    provider_name: str

    def synthesize(self, text: str, voice_id: str, *, tone: str | None = None) -> SpeechArtifact:
        raise NotImplementedError
```

### Pattern 2: Job Lifecycle Before Completion
**What:** Create a job row first, then move it through `queued`, `running`, `succeeded`, and `failed` instead of returning a final audio blob in the request handler. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md]
**When to use:** Always in Phase 2, because the UX must show loading, success, error, and retry states. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md]
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import BackgroundTasks

@app.post("/generations/{job_id}")
async def start_generation(job_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_generation, job_id)
    return {"job_id": job_id, "status": "queued"}
```

### Pattern 3: Controlled File Responses
**What:** Return playback through controlled file responses or controlled URLs, not inline audio bytes. [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md]
**When to use:** Always for playable clips in Phase 2.
**Example:**
```python
# Source: https://fastapi.tiangolo.com/advanced/custom-response/
from fastapi.responses import FileResponse

return FileResponse(path=artifact_path, media_type="audio/wav", filename="output.wav")
```

### Anti-Patterns to Avoid
- **Synchronous generation in the route handler:** it hides latency and removes the retry/status UX that Phase 2 explicitly needs. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md]
- **Inline audio bytes/base64:** it bloats the response and bypasses the local object-store abstraction. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md]
- **Freeform tone controls:** they create prompt drift and make the audible differences harder to validate. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/PITFALLS.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TTS provider integration | One-off model script inside the route | Official repo checkout behind `TTSProvider` | Keeps model swaps, licensing, and audio shaping isolated. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: https://github.com/SWivid/F5-TTS] |
| Job orchestration | Synchronous `/generate` or in-memory-only status | Job record plus worker/background-task seam | Gives Phase 2 the loading, failure, and retry states it requires. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| Audio serving | Inline base64 or raw filesystem paths | Filesystem-backed object store with controlled URL or `FileResponse` | Prevents payload bloat and path leakage. [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] |
| Tone control | Dozens of sliders or ad-hoc prompt concatenation | Three fixed presets with explicit metadata mapping | Fits the locked phase scope and keeps the UI auditable. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |

**Key insight:** the hard part in Phase 2 is not audio synthesis alone; it is keeping provider, storage, and job state separable while still returning something playable fast. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/PITFALLS.md]

## Common Pitfalls

### Pitfall 1: Package-name drift
**What goes wrong:** the plan drifts into `pip install openvoice`, or upgrades to `f5-tts`/`cosyvoice` PyPI names without checking legitimacy first. `openvoice` is not a real PyPI install target here, and the other two names are flagged SUS by the package gate. [CITED: gsd package-legitimacy check]
**Why it happens:** repo names and package names are easy to conflate, especially when the official repo docs are the real source of truth. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: https://github.com/SWivid/F5-TTS] [CITED: https://github.com/myshell-ai/OpenVoice]
**How to avoid:** use official repo checkout paths and add a human checkpoint before any registry install.
**Warning signs:** a plan step says `pip install openvoice` or uses an unreviewed package name as the baseline provider.

### Pitfall 2: Generation stays synchronous
**What goes wrong:** the UI spinner hangs and retry logic becomes impossible to preserve.
**Why it happens:** the route tries to do synthesis, normalization, and storage before returning.
**How to avoid:** create a job first, keep the state visible, and let the worker/backend update the result later.
**Warning signs:** no `queued` or `running` state and no persisted job id.

### Pitfall 3: Tone presets do not audibly differ
**What goes wrong:** `Measured`, `Cutting`, and `Grandiose` look good on paper but sound the same.
**Why it happens:** the preset mapping is too weak or the prompt/style metadata is not constrained.
**How to avoid:** keep the preset mapping explicit and compare a fixed test sentence through each preset.
**Warning signs:** reviewers cannot hear a stable difference between the three outputs.

### Pitfall 4: Raw file serving leaks implementation details
**What goes wrong:** the API leaks local file paths or giant inline audio payloads.
**Why it happens:** the app shortcuts artifact handling instead of using the object-store abstraction.
**How to avoid:** store artifacts behind a local filesystem-backed object store and serve playback through controlled URLs or `FileResponse`.
**Warning signs:** response payloads contain base64 blobs or OS file paths.

## Code Examples

Verified patterns from official sources:

### Background Job Kickoff
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def run_generation(job_id: str) -> None:
    ...

@app.post("/generations/{job_id}")
async def start_generation(job_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_generation, job_id)
    return {"job_id": job_id, "status": "queued"}
```

### Controlled Audio Response
```python
# Source: https://fastapi.tiangolo.com/advanced/custom-response/
from fastapi.responses import FileResponse

@app.get("/generations/{job_id}/audio")
async def read_audio(job_id: str):
    return FileResponse(
        path=f"/var/lib/theatrical-voice-studio/{job_id}.wav",
        media_type="audio/wav",
        filename=f"{job_id}.wav",
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Direct `/generate` returns a final metadata stub | Phase 2 should create a queued/running/succeeded/failed job and then return a playable clip | 2026-07-01 phase decision | Enables loading, success, error, and retry states. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| Inline bytes/base64 audio | Filesystem-backed object store plus controlled playback URLs | 2026-07-01 phase decision | Keeps the API payload small and avoids storage leakage. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| Clone-first provider bar | Safe baseline provider first | 2026-07-01 phase decision | Validates the loop without assuming a reference voice already exists. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |

**Deprecated/outdated:**
- The README stack (`Clerk`, `Drizzle`, `pgvector`, `Trigger.dev`, `Upstash Redis`, `Azure Personal Voice`, `Cartesia`) is stale for this phase and should not steer the Phase 2 plan. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/README.md]
- `openvoice` is not a valid PyPI install target in this environment; the package-legitimacy gate marked it `SLOP`, so remove that install path entirely. [CITED: gsd package-legitimacy check]
- `f5-tts` and `cosyvoice` PyPI names exist but are suspicious enough to require human verification before any install. [CITED: gsd package-legitimacy check]

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| None | None - all phase-specific claims in this research were verified or cited. | N/A | N/A |

**If this table is empty:** All claims in this research were verified or cited - no user confirmation needed.

## Open Questions

1. **Which CosyVoice checkpoint should Phase 2 default to?**
   - What we know: the repo recommends `Fun-CosyVoice3-0.5B-2512` for better performance, and the current repo docs also show 300M and 0.5B-era model paths. [CITED: https://github.com/FunAudioLLM/CosyVoice]
   - What's unclear: whether the smaller 300M path is enough for the first playable loop or whether the 0.5B path is worth the extra setup.
   - Recommendation: start planning around the 0.5B line and keep 300M as a fallback baseline.

2. **Does the chosen model artifact carry the same license terms as the repo?**
   - What we know: the official CosyVoice repo is Apache-2.0, and the repo/issue trail says the code and models are intended to be Apache-2.0. [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: https://github.com/FunAudioLLM/CosyVoice/issues/853]
   - What's unclear: the exact download artifact terms for the specific checkpoint that Phase 2 will use.
   - Recommendation: human-verify the checkpoint before install or cloud deployment.

3. **Should generation run through a lightweight background-task seam or a durable queue in Phase 2?**
   - What we know: FastAPI supports background tasks after a response, while the architecture docs warn that long jobs are safer behind a queue. [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md]
   - What's unclear: whether the first provider run will be fast enough to stay inside a lightweight seam.
   - Recommendation: keep the job API and worker seam separate; choose the smallest execution mechanism that still preserves job ids, status transitions, and retry.

4. **Should the README be updated in this phase or deferred to a docs-only follow-up?**
   - What we know: the README still describes a different stack than the planning artifacts and current code. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/README.md]
   - What's unclear: whether the team wants the docs cleanup bundled with Phase 2 planning or kept separate.
   - Recommendation: treat it as a documentation follow-up, not a scope blocker.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Node.js | Next.js web app and Playwright | ✓ | 24.2.0 | - |
| npm | package management | ✓ | 11.3.0 | - |
| pnpm | repo web app scripts | ✓ | 10.30.3 | npm if needed |
| Python 3.11 | worker runtime and `.venv` | ✓ | 3.11.12 | `python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'` |
| Python 3.13 | global interpreter | ✓ | 3.13.5 | do not use for the speech worker until model compatibility is validated |
| FFmpeg | audio normalization | ✗ | - | install in the worker image or via the OS package manager |
| uv | Python env workflow | ✗ | - | use the existing `python3.11` + venv + pip path |
| git | repository operations | ✓ | 2.50.1 | - |

**Missing dependencies with no fallback:**
- None.

**Missing dependencies with fallback:**
- `ffmpeg` - install it in the worker image or via the OS package manager before normalization tests.
- `uv` - use the existing Python 3.11 virtualenv and pip workflow instead.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 9.1.1` for Python + `@playwright/test 1.61.1` for browser flows [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] |
| Config file | `pyproject.toml` and `apps/web/playwright.config.ts` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts] |
| Quick run command | `./.venv/bin/python -m pytest services/api/tests/test_rights_gate.py services/api/tests/test_voice_profile.py services/api/tests/test_generate_stub.py services/speech-worker/tests/test_provider_contracts.py -q && pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` |
| Full suite command | `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests -q && pnpm --dir apps/web exec playwright test` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GOV-04 | Consent/license notes remain backend-owned and gate generation eligibility | unit/integration | `./.venv/bin/python -m pytest services/api/tests/test_voice_profile.py services/api/tests/test_rights_gate.py -q` | ✅ |
| STUD-03 | Text field sends generation text to the backend | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | ✅ |
| STUD-04 | Tone presets render and map to generation metadata | e2e + unit | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | ✅ |
| STUD-05 | Loading, success, and error states render correctly | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | ✅ |
| STUD-06 | Generated audio is playable in the browser | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | ✅ |
| STUD-07 | Retry reuses the last text/voice/tone after a failure | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | ✅ |
| PIPE-02 | Real provider adapter synthesizes playable audio | integration/manual smoke | `./.venv/bin/python -m pytest services/speech-worker/tests/test_cosyvoice_provider.py -q` | ❌ Wave 0 |
| PIPE-03 | Metadata includes provider, voice, tone, and timing | integration/API | `./.venv/bin/python -m pytest services/api/tests/test_generation_jobs.py -q` | ❌ Wave 0 |
| PIPE-04 | Audio is normalized into accepted formats | integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_normalization.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `./.venv/bin/python -m pytest services/api/tests/test_rights_gate.py services/api/tests/test_voice_profile.py services/api/tests/test_generate_stub.py services/speech-worker/tests/test_provider_contracts.py -q`
- **Per wave merge:** `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests -q && pnpm --dir apps/web exec playwright test`
- **Phase gate:** full suite green before `$gsd-verify-work`

### Wave 0 Gaps
- `services/api/tests/test_generation_jobs.py` - covers queued/running/succeeded/failed, retry, and metadata persistence.
- `services/speech-worker/tests/test_cosyvoice_provider.py` - covers the real provider adapter and playable-audio contract.
- `services/speech-worker/tests/test_audio_normalization.py` - covers FFmpeg output shape and accepted sample format.
- `apps/web/tests/studio-generation.spec.ts` - extend the existing spec for actual text input, tone selection, playback, and retry assertions.
- `services/api/tests/conftest.py` - add shared fixtures if the job store and object-store abstraction need them.
- Framework install: none - the existing pytest and Playwright infrastructure is already present.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | v1 is no-login; do not add auth flows in Phase 2. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/PROJECT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/REQUIREMENTS.md] |
| V3 Session Management | no | Keep Phase 2 in-session only; do not add persisted account sessions or saved libraries. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |
| V4 Access Control | yes | Server-side rights gate with `ensure_voice_allowed` and approved voice-profile metadata. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py] |
| V5 Input Validation | yes | Pydantic strict models, `extra="forbid"`, fixed tone presets, and explicit validators. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py] |
| V6 Cryptography | no | No custom crypto in Phase 2; keep storage and transport on platform defaults. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] |

### Known Threat Patterns for Python/Next.js voice studio

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Rights bypass through direct API calls | Elevation of Privilege / Tampering | Enforce `ensure_voice_allowed` on the server before any generation work starts. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py] |
| Malformed text or tone input | Tampering / DoS | Use strict schema validation, enum-backed tone presets, and `extra="forbid"`. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] |
| Raw audio path exposure | Information Disclosure | Serve clips through controlled URLs or `FileResponse`, not raw filesystem paths or base64 blobs. [CITED: https://fastapi.tiangolo.com/advanced/custom-response/] |
| Long-running inference blocking the request path | Denial of Service | Keep a job lifecycle and a worker seam so the request can return quickly with status. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] |

## Sources

### Primary (HIGH confidence)
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md` - Phase 2 locked decisions and out-of-scope boundaries.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/ROADMAP.md` - phase goal, dependencies, and success criteria.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/REQUIREMENTS.md` - GOV-04, STUD-03..PIPE-04 traceability.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/STATE.md` - current project state and Phase 1 handoff.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md` - provider adapter boundary, object storage role, and worker split.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/STACK.md` - stack directions and candidate provider families.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/PITFALLS.md` - lock-in, latency, and storage risks.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json` - current web stack pins.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml` - current Python stack pins.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts` - API rewrite bridge.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py` - current rights-gated generation route.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py` - current generation schema.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py` - current metadata-only stub behavior.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py` - current consent/right metadata shape.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py` - current server-side approval gate.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py` - provider adapter boundary.
- `/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx` - current studio shell and state handling.
- `gsd package-legitimacy check` - package legitimacy results for CosyVoice/F5-TTS/OpenVoice/Torch/Torchaudio install targets.
- `https://github.com/FunAudioLLM/CosyVoice` - official CosyVoice repo.
- `https://github.com/SWivid/F5-TTS` - official F5-TTS repo.
- `https://github.com/myshell-ai/OpenVoice` - official OpenVoice repo.
- `https://fastapi.tiangolo.com/tutorial/background-tasks/` - FastAPI background tasks.
- `https://fastapi.tiangolo.com/advanced/custom-response/` - FileResponse / StreamingResponse patterns.

### Secondary (MEDIUM confidence)
- `https://arxiv.org/abs/2407.05407` - CosyVoice paper.
- `https://arxiv.org/abs/2412.10117` - CosyVoice 2 streaming paper.
- `https://arxiv.org/abs/2410.06885` - F5-TTS paper.
- `https://arxiv.org/abs/2312.01479` - OpenVoice paper.
- `https://www.npmjs.com/package/next` - registry version confirmation.
- `https://www.npmjs.com/package/react` - registry version confirmation.
- `https://www.npmjs.com/package/@playwright/test` - registry version confirmation.
- `https://www.npmjs.com/package/typescript` - registry version confirmation.
- `https://pypi.org/project/fastapi/` - registry version confirmation.
- `https://pypi.org/project/pydantic/` - registry version confirmation.
- `https://pypi.org/project/uvicorn/` - registry version confirmation.
- `https://pypi.org/project/torch/` - registry version confirmation.
- `https://pypi.org/project/torchaudio/` - registry version confirmation.

### Tertiary (LOW confidence)
- None - no tertiary sources were needed after the official-doc and registry pass.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - repo pins are current, but the provider choice and install path still need human checkpoints because the package gate flagged the model-runtime installs as suspicious. [CITED: gsd package-legitimacy check]
- Architecture: HIGH - the phase context, roadmap, and current code all point at the same browser -> API -> worker -> storage flow. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/research/ARCHITECTURE.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py]
- Pitfalls: HIGH - the main failure modes are directly supported by official FastAPI docs, official provider repos, and the phase decision log. [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/] [CITED: https://github.com/FunAudioLLM/CosyVoice] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/02-consented-studio-generation/02-CONTEXT.md]

**Research date:** 2026-07-01
**Valid until:** 2026-07-31
