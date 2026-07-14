---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 05
current_phase_name: model-benchmark-and-selection
status: executing
stopped_at: Completed 05-02-PLAN.md
last_updated: "2026-07-14T16:30:03.869Z"
last_activity: 2026-07-14
last_activity_desc: Phase 05 execution started
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 19
  completed_plans: 18
  percent: 67
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-30)

**Core value:** Users can speak or write an input and receive a high-quality spoken response in a controllable, consented character voice with low enough latency to feel conversational.
**Current focus:** Phase 05 — model-benchmark-and-selection

## Current Position

Phase: 05 (model-benchmark-and-selection) — EXECUTING
Plan: 3 of 3
Status: Ready to execute
Last activity: 2026-07-14 — Phase 05 execution started

Progress: [███████░░░] 67%

## Performance Metrics

**Velocity:**

- Total plans completed: 20
- Average duration: 29 min
- Total execution time: 3.4 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. No-Login Vertical Skeleton | 3 | 3 | 15 min |
| 2. Consented Studio Generation | 6 | 6 | 40 min |
| 3. Audio Input and Turn Detection | 3 | 3 | 20 min |
| 4. Live Conversation Mode | 4 | 4 | ~1h 04m |
| 5. Model Benchmark and Selection | 0 | 3 | - |
| 6. Cloud GPU Deployment and Internal Beta Hardening | 0 | 3 | - |
| 04 | 4 | - | - |

**Recent Trend:**

- Last 5 plans: Phase 02 P02, Phase 02 P03, Phase 02 P04, Phase 02 P05, Phase 02 P06
- Trend: phase 2 completed

*Updated after each plan completion*
| Phase 01 P01 | 19min | 3 tasks | 15 files |
| Phase 01 P02 | 21min | 2 tasks | 17 files |
| Phase 01 P03 | 6min | 3 tasks | 13 files |
| Phase 02 P01 | 1h 20m | 3 tasks | 8 files |
| Phase 02 P02 | 20min | 3 tasks | 5 files |
| Phase 02 P03 | 23min | 2 tasks | 6 files |
| Phase 02 P04 | 32m | 2 tasks | 4 files |
| Phase 02 P05 | 30m | 2 tasks | 4 files |
| Phase 02 P06 | 55m | 3 tasks | 7 files |
| Phase 03 P01 | 19m | 3 tasks | 13 files |
| Phase 03 P02 | 13m 11s | 3 tasks | 11 files |
| Phase 03-audio-input-and-turn-detection P03 | 29 min | 3 tasks | 11 files |
| Phase 04 P01 | ~1h 10m | 3 tasks | 11 files |
| Phase 04 P02 | ~1h 45m | 3 tasks | 12 files |
| Phase 04 P03 | 1h 3m | 3 tasks | 13 files |
| Phase 04 P04 | 16m | 2 tasks | 5 files |
| Phase 05 P01 | 25m | 3 tasks | 11 files |
| Phase 05 P02 | 13m | 4 tasks | 13 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Initialization: Build an original theatrical trickster voice, not an exact Loki/Tom Hiddleston clone.
- Initialization: Web app first, no-login v1, studio-first with live conversation included.
- Initialization: Cloud GPU target with modular open-source model benchmarks.
- Initialization: Use Vertical MVP roadmap structure.
- [Phase 01]: Keep / as the direct studio entry point with no landing or login detour.
- [Phase 01]: Render Vesper Glass as an original theatrical voice with concise non-impersonation boundary copy.
- [Phase 01]: Use a render-only browser seed for Vesper Glass now and leave canonical rights ownership for the backend slice.
- [Phase 01]: Use a Playwright root-route smoke test as the regression guard for the first studio surface.
- [Phase 01]: Use python3.11 -m venv + pip as the approved Python fallback because uv is unavailable in this environment.
- [Phase 01]: Model Vesper Glass as nested rights and style records so the server can enforce consent metadata directly.
- [Phase 01]: Keep the blocked-generation message exact on the API gate and verify the mounted route through the FastAPI app.
- [Phase 01]: Add a root pytest conftest to keep greenfield backend imports stable.
- [Phase 01]: Server-owned voice registry metadata is authoritative for generation rights; browser voice data remains render-only. — Prevents direct API calls from bypassing consent and approval metadata, and keeps future generation routes behind the backend rights gate.
- [Phase 01]: Keep Phase 1 generation metadata-only with no audio payload or playback surface.
- [Phase 01]: Route generation through the server-owned rights gate before assembling the stub result.
- [Phase 01]: Mock the `/generate` browser contract in Playwright so the studio can prove the web-to-API shape without a live speech backend.
- [Phase 01]: Add `httpx2` to the dev extras so `fastapi.testclient` can run under the approved Python venv.
- [Phase 02]: Use lowercase machine values for the three tone presets and render capitalized labels in the browser.
- [Phase 02]: Return a queued prototype baseline job from the Phase 1 stub instead of the old metadata-only card.
- [Phase 02]: Update the stale root-route smoke test so the repo matches the new Phase 2 studio surface.
- [Phase 02]: Keep the blocked-rights browser assertion by stubbing the 403 response in the Playwright test while the API test continues to verify the real rights gate.
- [Phase 02]: Use the official FunAudioLLM/CosyVoice repo checkout with the Fun-CosyVoice3-0.5B-2512 baseline.
- [Phase 02]: Keep tone steering in prompt text instead of adding provider-specific knobs.
- [Phase 02]: Normalize generated audio to mono WAV via FFmpeg before playback or storage.
- [Phase 02]: Persist each generation as one job row with a single current attempt and create a new row for every retry.
- [Phase 02]: Keep playback constrained to the relative /generations/{job_id}/audio route and back it with a local filesystem object store.
- [Phase 02]: Preserve GenerationResult as a compatibility subclass while introducing GenerationJobRecord and GenerationAttempt.
- [Phase 02]: Update the legacy stub regression test because the required verify set still includes it after the route change.
- [Phase 02]: Keep the current playable clip separate from recent session attempts so failures stay visible without hiding the last auditable success.
- [Phase 02]: Store retry inputs in component state and resubmit those cached values instead of whatever happens to be in the live form fields.
- [Phase 02]: Rewrite /generations/:path* through Next.js so the browser can poll status and load the controlled audio URL from the same origin.
- [Phase 02]: Queue generation first, then hand off to BackgroundTasks after the rights gate.
- [Phase 02]: Load CosyVoice lazily from the approved worker root only when the default provider is needed.
- [Phase 02]: Use a one-shot playwright-fail-once seam gated by CI/Playwright env for live retry coverage.
- [Phase 02]: Use a local CosyVoice fixture and WAV pass-through fallback so live browser verification can run in this workspace without the external checkout or ffmpeg binary.
- [Phase 02]: Verify retry through the cached request body, the new job id, and the visible session state instead of asserting a backend retry_of_job_id field the route does not populate.
- [Phase 02]: Assert the controlled playback URL on the audio element src rather than waiting on browser metadata fetch timing.
- [Phase 03]: Kept spoken capture on the same studio surface instead of introducing a separate audio page or mode switcher. — Keeps the capture flow beside the composer and avoids a separate navigation mode.
- [Phase 03]: Sent capture and upload as raw audio blobs to same-origin /audio-turns routes so the browser can hand off directly to the control plane. — Lets the browser hand captured audio straight to the control plane while keeping the API boundary same-origin.
- [Phase 03]: Modeled spoken-turn history separately from generation attempts so the session can inspect audio capture without mixing the two workflows. — Prevents spoken input history from being mixed into generation retry state or current clip playback.
- [Phase 03]: Kept the approved Silero path behind VADProvider, with a deterministic fixture fallback so local tests do not depend on torch or torchaudio being installed.
- [Phase 03]: Queued audio-turn jobs in the API and polled the session-scoped record in the browser, instead of adding a separate transcript or debug surface.
- [Phase 03]: Rendered compact turn-boundary metadata inline on spoken-turn cards and kept the capture list separate from generation attempts.
- [Phase 03]: Use a faster-whisper-compatible STT provider behind STTProvider with deterministic fixture fallback so the worker/runtime boundary stays intact. — Keeps the worker boundary intact and makes local validation deterministic.
- [Phase 03]: Persist transcript language and confidence on the same session-scoped audio-turn record that stores VAD metadata. — Keeps VAD and transcript review on the same auditable record.
- [Phase 03]: Keep transcript review separate from the generation composer and require an explicit Use as generation text action to copy the transcript. — Prevents silent overwrites of the generation draft and matches the plan's no-overwrite handoff.
- [Phase 4]: Keep live conversation inline on / instead of adding a separate route; use a server-owned SQLite session record as the authoritative conversation state and keep start/stop requests same-origin through Next.js rewrites. — This preserves the studio-first workflow and keeps the live panel maintainable as a sibling client component.
- [Phase 04]: Keep v1 response generation deterministic and local so the provider contract, prompt boundary, and playback loop can be tested without a real LLM dependency. — This preserves the provider interface and avoids introducing a production LLM dependency before the benchmark phase.
- [Phase 04]: Keep response prompt construction server-side so original-voice boundary and prohibited associations are enforced before response text exists. — The browser should receive only final response text and controlled playback metadata, not own persona boundary construction.
- [Phase 04]: Use controlled same-origin /conversation-turns/{turn_id}/audio playback instead of exposing raw storage paths. — This matches existing generation playback boundaries and keeps audio storage replaceable behind API routes.
- [Phase 04]: Keep interrupt cooperative: the browser pauses playback immediately, then POSTs the active turn to the server so late completions cannot resurrect canceled work. — This gives the user immediate recovery while preserving server-owned cancel state for auditability and late-write guards.
- [Phase 04]: Show live-turn latency as a compact seconds chip instead of a timing table. — The studio surface should stay readable while detailed stage timings remain available in backend records and tests.
- [Phase 04]: Render Interrupt as a first-class live-panel control and keep barge-in as best-effort fallback behavior. — Explicit user control must work even when VAD-based barge-in is unreliable.
- [Phase 04]: Keep barge-in best-effort on the browser side and reuse the existing interrupt route. — Adds speech-triggered interruption without a new cancellation path.
- [Phase 04]: Leave the backend turn-scoping logic unchanged because the forced failure regression showed the existing session recovery path already works. — Confirms the session boundary was already correct and only needed regression coverage.
- [Phase 05]: Use a small fixed corpus with three tone-preserving text prompts and three audio paths worth of consent-safe rows backed by two tiny WAV fixtures.
- [Phase 05]: Keep fixture paths resolved and containment-checked under services/speech-worker/benchmarks/corpus/fixtures.
- [Phase 05]: Emit benchmark results as JSON, CSV, and escaped Markdown so later adapters can compare reruns without a dashboard.
- [Phase 05-02]: Use Silero VAD as the runnable baseline and keep FireRedVAD blocked in the local workspace until package legitimacy and GPU runtime validation are proven.
- [Phase 05-02]: Treat the approved Qwen3-TTS source checkout and weights as the alternate TTS candidate, but keep it blocked from local runtime execution until GPU-worker evidence is captured.
- [Phase 05-02]: Keep benchmark execution fixture-only with fake backends and select recommendations only from runnable baselines.

### Pending Todos

None yet.

### Blockers/Concerns

- Need a consented/licensed reference voice or original synthetic seed before real cloning work.
- Need implementation-time model compatibility checks for Python, CUDA, PyTorch, and model weight licenses.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accounts | User accounts and saved clip library | Deferred to v2 | Initialization |
| Studio | Detailed tone sliders and batch generation | Deferred to v2 | Initialization |
| Platform | Public API and team approvals | Deferred to v2 | Initialization |

## Session Continuity

Last session: 2026-07-14T16:30:03.864Z
Stopped at: Completed 05-02-PLAN.md
Resume file: None
