---
phase: 02-consented-studio-generation
verified: 2026-07-03T21:09:14Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 7/9
  gaps_closed:
    - "POST /generate now hands queued jobs to the background runtime, which loads the provider and persists succeeded audio."
    - "The Playwright studio-generation spec now drives the live success and retry flow without mocking the success/audio path."
  gaps_remaining: []
  regressions: []
---

# Phase 2: Consented Studio Generation Verification Report

**Phase Goal:** User can enter text, choose a tone preset, generate speech through a real provider, and play the resulting audio.

**Verified:** 2026-07-03T21:09:14Z
**Status:** passed
**Re-verification:** Yes - after gap closure plans 02-05 and 02-06

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User can enter text and choose one of the fixed tone presets. | VERIFIED | `apps/web/components/studio-shell.tsx:316-409` renders the textarea and Measured/Cutting/Grandiose chips; `apps/web/tests/studio-generation.spec.ts:172-180` and `:199-247` drive the live form inputs. |
| 2 | User sees loading, success, error, and retry states in the studio surface. | VERIFIED | `apps/web/components/studio-shell.tsx:339-487` derives queued/running/succeeded/failed copy and retry behavior; `apps/web/tests/studio-generation.spec.ts:175-274` covers success, failure, retry, and alert states. |
| 3 | User can play generated audio in the browser. | VERIFIED | `apps/web/components/studio-shell.tsx:148-214` renders a controlled `<audio>` element with browser controls, and `apps/web/tests/studio-generation.spec.ts:136-155` / `:258-272` verify the live clip resolves to `/generations/{job_id}/audio`. |
| 4 | The backend stores generated audio with provider, voice, tone, and timing metadata. | VERIFIED | `services/api/app/schemas/generation.py:152-208` defines the job record, and `services/api/app/services/generation_jobs.py:226-324` persists succeeded audio plus provider/timing data and controlled playback URLs. |
| 5 | The system can synthesize speech through a real provider from the app path. | VERIFIED | `services/api/app/services/generation_runtime.py:69-156` loads `CosyVoiceTTSProvider` lazily, calls `synthesize(...)` with the tone preset, and writes the resulting artifact through `GenerationJobService.mark_succeeded(...)`; `services/speech-worker/providers/cosyvoice_provider.py:92-161` is the provider adapter. |
| 6 | Consent and rights metadata remain enforced before generation. | VERIFIED | `services/api/app/services/rights_gate.py:22-60` still blocks unapproved voices, and `services/api/app/routes/generate.py:22-39` calls `ensure_voice_allowed(...)` before queuing work. |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `apps/web/components/studio-shell.tsx` | Text entry, tone presets, current clip, retry, and status UI | VERIFIED | Renders the Phase 2 studio shell, live polling, current clip card, and session-scoped retry. |
| `apps/web/tests/studio-generation.spec.ts` | Live browser contract for success, retry, and blocked rights | VERIFIED | Drives the live backend path, asserts the controlled audio URL, and keeps the exact 403 rights regression. |
| `apps/web/next.config.ts` | Same-origin rewrites for generation and playback routes | VERIFIED | Rewrites `/generate`, `/generations/:path*`, and `/voices/:path*` to the API. |
| `services/api/app/routes/generate.py` | Rights-gated queued generation route | VERIFIED | Queues the job, then schedules `process_generation_job(...)` through `BackgroundTasks`. |
| `services/api/app/services/generation_runtime.py` | Lazy provider handoff and live job runner | VERIFIED | Loads CosyVoice from the worker root, handles the one-shot failure seam, and advances jobs to succeeded or failed. |
| `services/api/app/services/generation_jobs.py` | Job store and controlled audio persistence | VERIFIED | Stores queued/running/succeeded/failed records and writes the playable audio file for `/generations/{job_id}/audio`. |
| `services/api/app/services/rights_gate.py` | Backend-owned consent/rights gate | VERIFIED | Preserves the exact blocked message and rejects unapproved profiles before synthesis. |
| `services/api/app/schemas/generation.py` | Tone enum, job status, and job-shaped result schema | VERIFIED | Defines `GenerationTonePreset`, `GenerationJobStatus`, and the job/result record fields used throughout the phase. |
| `services/speech-worker/providers/cosyvoice_provider.py` | Provider adapter behind the shared TTS contract | VERIFIED | Accepts text/voice/tone, synthesizes through the CosyVoice backend, and normalizes the resulting artifact. |
| `services/speech-worker/audio/normalization.py` | Audio normalization helper | VERIFIED | Normalizes generated audio to playable mono WAV and preserves metadata. |
| `services/speech-worker/tests/test_cosyvoice_provider.py` | Provider contract regression | VERIFIED | Verifies tone steering, provider wiring, and normalized playable output. |
| `services/speech-worker/tests/test_audio_normalization.py` | Normalization regression | VERIFIED | Verifies ffmpeg-backed normalization and the WAV fallback path. |
| `services/api/tests/conftest.py` | Deterministic route-test harness | VERIFIED | Autouse fixture keeps the legacy queued-job API tests from dispatching background work. |
| `services/api/tests/test_generation_runtime.py` | Runtime handoff regression | VERIFIED | Verifies queued -> running -> succeeded, provider failure, and the one-shot marker seam. |
| `services/api/tests/test_generate_stub.py` | Generation route contract regression | VERIFIED | Verifies the queued job response and the exact blocked-rights 403 message. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `StudioShell` submit action | `POST /generate` | `fetch("/generate")` with Next.js rewrite | WIRED | The browser posts text, voice, and tone to the generation route. |
| `POST /generate` | `process_generation_job(...)` | `BackgroundTasks.add_task(...)` | WIRED | Rights are checked first, then the queued job is handed to the live runtime. |
| `process_generation_job(...)` | `CosyVoiceTTSProvider.synthesize(...)` | lazy provider loader | WIRED | The runtime loads the provider from the worker root and passes the tone preset through. |
| `CosyVoiceTTSProvider.synthesize(...)` | `normalize_audio(...)` | direct function call | WIRED | Provider output is normalized before it becomes the persisted playable clip. |
| `GenerationJobService.mark_succeeded(...)` | `/generations/{job_id}/audio` | controlled FileResponse route | WIRED | Successful jobs store audio bytes and expose only the relative playback URL. |
| `CurrentClipCard` | browser audio controls | `playback_url` on `<audio>` | WIRED | The UI renders a controlled audio element when a succeeded job exists. |
| `Retry current generation` | cached submission state | `lastSubmission` replay | WIRED | Retry resubmits the cached `voice_id`/`text`/`tone_preset` tuple instead of the live form. |

### Data-Flow Trace

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `apps/web/components/studio-shell.tsx` | `attempts`, `currentClip`, `latestAttempt` | Live `POST /generate` plus polling of `/generations/{job_id}` through Next.js rewrites | Yes, backed by sqlite job state and filesystem audio storage | FLOWING |
| `services/api/app/services/generation_jobs.py` | `playback_url`, `audio_duration_ms`, `provider_name`, `timing` | `mark_succeeded(...)` after provider synthesis | Yes, writes audio bytes and metadata to the local object store and sqlite record | FLOWING |
| `services/api/app/services/generation_runtime.py` | `artifact` from provider synthesis | `CosyVoiceTTSProvider.synthesize(...)` or an injected provider in tests | Yes, the live Playwright spec reaches the real runtime path and then the job/audio routes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| API runtime handoff, queued job contract, and rights gate | `./.venv/bin/python -m pytest services/api/tests/test_generation_runtime.py services/api/tests/test_generate_stub.py services/api/tests/test_rights_gate.py -q` | `11 passed in 0.03s` | PASS |
| Live browser generation, retry, and blocked-rights regression | `THEATRICAL_VOICE_STUDIO_TEST_FAILURE_MARKER=playwright-fail-once CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts tests/root-route.spec.ts` | `4 passed (10.1s)` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| GOV-04 | 02-01, 02-03, 02-05 | Consent/license metadata is enforced before generation. | SATISFIED | `services/api/app/services/rights_gate.py:22-60`, `services/api/app/routes/generate.py:22-39` |
| STUD-03 | 02-01, 02-04 | User can enter text to synthesize into speech. | SATISFIED | `apps/web/components/studio-shell.tsx:396-409` |
| STUD-04 | 02-01 | User can choose a tone preset for generation. | SATISFIED | `apps/web/components/studio-shell.tsx:321-409` |
| STUD-05 | 02-01, 02-04, 02-05, 02-06 | User can submit generation and see loading, success, error, and retry states. | SATISFIED | `apps/web/components/studio-shell.tsx:339-487`, `apps/web/tests/studio-generation.spec.ts:175-274` |
| STUD-06 | 02-04, 02-06 | User can play the generated audio in the browser. | SATISFIED | `apps/web/components/studio-shell.tsx:148-214`, `apps/web/tests/studio-generation.spec.ts:136-155` |
| STUD-07 | 02-04, 02-06 | User can retry a failed generation without refreshing the app. | SATISFIED | `apps/web/components/studio-shell.tsx:412-417`, `apps/web/tests/studio-generation.spec.ts:192-274` |
| PIPE-02 | 02-02, 02-05 | System can synthesize speech through at least one real TTS or voice-cloning provider adapter. | SATISFIED | `services/api/app/services/generation_runtime.py:69-156`, `services/speech-worker/providers/cosyvoice_provider.py:92-161` |
| PIPE-03 | 02-03 | System stores generated audio with provider, voice profile, tone preset, and generation timing. | SATISFIED | `services/api/app/schemas/generation.py:152-208`, `services/api/app/services/generation_jobs.py:226-324` |
| PIPE-04 | 02-02, 02-06 | System can normalize uploaded, recorded, or generated audio into accepted formats. | SATISFIED | `services/speech-worker/audio/normalization.py:32-96`, `services/speech-worker/tests/test_audio_normalization.py:21-78` |

### Anti-Patterns Found

None. The phase artifacts do not contain unresolved `TODO`, `FIXME`, `XXX`, placeholder, or empty-implementation markers that would block completion.

### Gaps Summary

None. The prior gaps were closed by the queued runtime handoff and the live browser spec that exercises the success and retry path against the real `/generate` and `/generations/{job_id}` routes.

---

_Verified: 2026-07-03T21:09:14Z_
_Verifier: the agent (gsd-verifier)_
