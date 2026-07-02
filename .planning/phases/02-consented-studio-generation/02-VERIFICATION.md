---
phase: 02-consented-studio-generation
verified: 2026-07-02T19:43:04Z
status: gaps_found
score: 7/9 must-haves verified
behavior_unverified: 1
overrides_applied: 0
gaps:
  - truth: "User can generate speech through at least one real TTS or voice-cloning provider and play the resulting audio in the browser."
    status: failed
    reason: "The codebase has the provider adapter, job schema, and playback surface, but `POST /generate` only creates a queued job record. No production code path invokes `CosyVoiceTTSProvider.synthesize(...)` or advances a job to succeeded, so real audio is only reachable through tests and mocked browser routes."
    artifacts:
      - path: "services/api/app/routes/generate.py"
        issue: "POST /generate returns `GenerationJobService.create_job(...)` only; it never hands the request to a real provider or worker."
      - path: "services/api/app/services/generation_jobs.py"
        issue: "Contains `mark_succeeded(...)` and `get_generation_audio(...)`, but nothing in production calls those methods."
      - path: "services/speech-worker/providers/cosyvoice_provider.py"
        issue: "The real CosyVoice adapter exists, but it is not consumed by any runtime generation path."
    missing:
      - "A runtime worker or background task that consumes queued jobs and calls `CosyVoiceTTSProvider.synthesize(...)`."
      - "A production handoff that stores normalized audio and marks the job succeeded or failed."
      - "An end-to-end success path that yields a playable `/generations/{job_id}/audio` response without Playwright route mocks."
behavior_unverified_items:
  - truth: "The browser can play a real generated clip from the controlled audio URL, not just a mocked success response."
    test: "Run the studio flow against a live backend job that completes with real provider output."
    expected: "The current clip audio element loads the controlled `/generations/{job_id}/audio` response and plays successfully."
    why_human: "The Playwright spec intercepts `/generate` and `/generations/**`, so it proves the UI and session wiring but not a live synthesized clip."
---

# Phase 2: Consented Studio Generation Verification Report

**Phase Goal:** User can enter text, choose a tone preset, generate speech through a real provider, and play the resulting audio.

**Verified:** 2026-07-02T19:43:04Z

**Status:** gaps_found

**Re-verification:** No

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User can enter text and choose one of the fixed tone presets. | VERIFIED | `apps/web/components/studio-shell.tsx:316-410` renders the textarea and three fixed tone chips; `apps/web/tests/studio-generation.spec.ts:254-259` drives them. |
| 2 | User sees loading, success, error, and retry states in the studio surface. | VERIFIED | `apps/web/components/studio-shell.tsx:339-417` and `apps/web/tests/studio-generation.spec.ts:261-420` exercise queued, running, failed, succeeded, and retry states. |
| 3 | User can play generated audio in the browser. | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `apps/web/components/studio-shell.tsx:148-214` renders the controlled audio element, but the Playwright spec mocks the audio route instead of proving a live synthesized clip. |
| 4 | The backend stores generated audio with provider, voice, tone, and timing metadata. | VERIFIED | `services/api/app/schemas/generation.py:152-208`, `services/api/app/services/generation_jobs.py:226-263`, and `services/api/tests/test_generation_jobs.py:54-82` cover the stored metadata and controlled playback URL. |
| 5 | The system can synthesize speech through a real provider from the app path. | FAILED | `services/api/app/routes/generate.py:21-31` only queues a job; no production caller invokes `CosyVoiceTTSProvider` or advances queued jobs into a playable clip. |
| 6 | Consent and rights metadata remain enforced before generation. | VERIFIED | `services/api/app/services/rights_gate.py:22-60` and `services/api/app/voice_registry/bundled_voice.py:5-46` preserve the approved rights metadata and blocked message. |

**Score:** 7/9 truths verified (1 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `services/api/app/schemas/generation.py` | Tone enum, job status enum, job record, attempt, and playback fields | VERIFIED | Strict Pydantic schema with queued/running/succeeded/failed states and controlled playback metadata. |
| `services/api/app/services/generation_jobs.py` | Job store and local object store | VERIFIED | Persists job rows, retry lineage, and controlled audio files under a local storage root. |
| `services/api/app/routes/generate.py` | Generate/status/audio endpoints | VERIFIED | Routes exist and enforce rights before creating a job, but the route still stops at job creation. |
| `services/speech-worker/providers/cosyvoice_provider.py` | Real TTS provider adapter | VERIFIED | Real CosyVoice adapter exists and threads tone into synthesis before normalization. |
| `services/speech-worker/audio/normalization.py` | FFmpeg normalization helper | VERIFIED | Normalizes speech artifacts to playable mono WAV output. |
| `apps/web/components/studio-shell.tsx` | Studio UI for text, tone, playback, and retry | VERIFIED | Renders the expected controls and session-scoped playback surface. |
| `apps/web/next.config.ts` | Same-origin rewrites for generation and playback routes | VERIFIED | Rewrites `/generate` and `/generations/:path*` to the API. |
| `apps/web/tests/studio-generation.spec.ts` | Browser contract for text, tone, playback, and retry | VERIFIED | Covers the UI surface, but uses route mocks for `/generate` and `/generations/**`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `StudioShell` submit action | `POST /generate` | `fetch("/generate")` | WIRED | The browser posts text, voice, and tone to the generation route. |
| `POST /generate` | `GenerationJobService.create_job` | route handler call | WIRED | Rights are checked first, then a queued job record is created. |
| `GenerationJobService.create_job` | `CosyVoiceTTSProvider.synthesize` | runtime worker handoff | NOT_WIRED | No production worker or background task consumes the queued job. |
| `CosyVoiceTTSProvider.synthesize` | `normalize_audio` | direct function call | WIRED | The worker adapter normalizes the clip before returning it. |
| `CurrentClipCard` | browser audio controls | `playback_url` on `<audio>` | WIRED | The UI renders a controlled audio element when a succeeded job exists. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| GOV-04 | 02-01, 02-03 | Consent and rights metadata are preserved and enforced before generation. | SATISFIED | `services/api/app/services/rights_gate.py:22-60`, `services/api/app/voice_registry/bundled_voice.py:5-46` |
| STUD-03 | 02-01 | User can enter text to synthesize into speech. | SATISFIED | `apps/web/components/studio-shell.tsx:396-409` |
| STUD-04 | 02-01 | User can choose a tone preset for generation. | SATISFIED | `apps/web/components/studio-shell.tsx:321-409` |
| STUD-05 | 02-01, 02-04 | User can submit generation and see loading, success, error, and retry states. | SATISFIED | `apps/web/components/studio-shell.tsx:339-417`, `apps/web/tests/studio-generation.spec.ts:261-420` |
| STUD-06 | 02-04 | User can play the generated audio in the browser. | NEEDS HUMAN | `apps/web/components/studio-shell.tsx:148-214` and `apps/web/tests/studio-generation.spec.ts:212-296` prove the UI shape, but not a real synthesized clip. |
| STUD-07 | 02-04 | User can retry a failed generation without refreshing the app. | SATISFIED | `apps/web/components/studio-shell.tsx:412-417`, `apps/web/tests/studio-generation.spec.ts:298-420` |
| PIPE-02 | 02-02 | System can synthesize speech through at least one real provider adapter. | BLOCKED | `services/speech-worker/providers/cosyvoice_provider.py:92-161` exists, but nothing in `services/api/app/**` calls it. |
| PIPE-03 | 02-03 | System stores generated audio with provider, voice, tone, and timing metadata. | SATISFIED | `services/api/app/schemas/generation.py:152-208`, `services/api/app/services/generation_jobs.py:226-263` |
| PIPE-04 | 02-02 | System can normalize uploaded, recorded, or generated audio into accepted formats. | SATISFIED | `services/speech-worker/audio/normalization.py:20-74`, `services/speech-worker/tests/test_audio_normalization.py:21-54` |

### Anti-Patterns Found

None. The modified files do not contain unresolved `TODO`, `FIXME`, `XXX`, placeholder, or empty-implementation markers.

### Behavior Unverified

The browser playback surface is present, but a real synthesized clip was not exercised in this workspace because the browser spec mocks both the generation and audio routes. The provider adapter also lacks a production caller, so the live playback flow remains unproven end to end.

### Gaps Summary

The phase built the studio controls, rights gate, job schema, storage helper, worker adapter, and controlled playback surface, but it stopped short of the one thing that makes the feature real: a runtime handoff from `/generate` into the CosyVoice provider and back into a succeeded job with audio. Until that wiring exists, the browser can only prove the UI contract with mocked responses.

---

_Verified: 2026-07-02T19:43:04Z_
_Verifier: the agent (gsd-verifier)_
