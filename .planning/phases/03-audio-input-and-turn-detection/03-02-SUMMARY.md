---
phase: 03-audio-input-and-turn-detection
plan: 02
subsystem: api
tags: [vad, torchaudio, fastapi, playwright, nextjs, wav]

# Dependency graph
requires:
  - phase: 02-consented-studio-generation
    provides: queued generation job model, same-origin audio routes, session-scoped object storage, and browser capture patterns
provides:
  - Silero-compatible VAD provider behind `VADProvider`
  - Audio-turn runtime that normalizes captured audio and persists compact turn-boundary metadata
  - Spoken-turn cards that show provider, speech range, speech duration, confidence, and weak-turn warnings
affects: [03-03 STT/transcript inspection, 04 live conversation mode, 05 benchmark and selection]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BackgroundTasks-backed audio-turn processing with queued job polling"
    - "Silero-compatible provider with deterministic fixture fallback for WAV-only tests"
    - "Compact VAD metadata surfaced inline on spoken-turn cards"

key-files:
  created:
    - services/api/app/services/audio_turn_runtime.py
    - services/speech-worker/providers/silero_vad_provider.py
    - services/speech-worker/tests/test_audio_turn_providers.py
  modified:
    - services/api/app/routes/audio_turns.py
    - services/api/app/schemas/audio_turn.py
    - services/api/app/services/audio_turn_jobs.py
    - services/api/tests/test_audio_turn_jobs.py
    - apps/web/components/studio-shell.tsx
    - apps/web/playwright.config.ts
    - apps/web/tests/audio-input.spec.ts
    - services/speech-worker/providers/__init__.py

key-decisions:
  - "Kept the approved Silero path behind `VADProvider`, with a deterministic fixture fallback so local tests do not depend on torch or torchaudio being installed."
  - "Queued audio-turn jobs in the API and polled the session-scoped record in the browser, instead of adding a separate transcript or debug surface."
  - "Rendered compact turn-boundary metadata inline on spoken-turn cards and kept the capture list separate from generation attempts."

patterns-established:
  - "Audio capture stays on the studio surface, but processing happens in the backend runtime through the worker/provider boundary."
  - "The UI uses WAV-only fixtures for deterministic capture tests and renders only compact VAD metadata instead of a debug dashboard."
  - "Weak turns remain visible in-session with a warning, rather than mutating a prior job into a retry."

requirements-completed: [AUD-02]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: Audio-turn jobs are processed through a Silero-compatible VAD provider and persist compact boundary metadata.
    requirement: AUD-02
    verification:
      - kind: unit
        ref: "./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_turn_providers.py services/api/tests/test_audio_turn_jobs.py -q"
        status: pass
    human_judgment: false
  - id: D2
    description: Spoken-turn cards surface the VAD provider, speech range, speech duration, and confidence inline.
    requirement: AUD-02
    verification:
      - kind: e2e
        ref: "pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts -g \"vad|weak\""
        status: pass
    human_judgment: false
  - id: D3
    description: Thin turns stay reviewable and separate from generation attempts, with a warning instead of retry mutation.
    requirement: AUD-02
    verification:
      - kind: e2e
        ref: "pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts"
        status: pass
    human_judgment: false

# Metrics
duration: 13m 11s
completed: 2026-07-12
status: complete
---

# Phase 03: Audio Input and Turn Detection Summary

**Silero-compatible VAD processing with compact turn-boundary metadata and WAV-only browser fixtures in the studio.**

## Performance

- **Duration:** 13m 11s
- **Started:** 2026-07-12T16:39:42Z
- **Completed:** 2026-07-12T16:52:53Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments
- Added a Silero-compatible VAD provider on the approved torch/torchaudio path, with a deterministic fixture fallback for local and browser tests.
- Introduced an audio-turn runtime that normalizes captured audio, marks the job running, and persists compact VAD metadata plus weak-turn warnings.
- Updated the studio shell so spoken turns poll to completion and show provider, range, duration, and confidence inline while staying separate from generation attempts.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add failing tests for Silero VAD runtime** - `f6014d9` (test)
2. **Task 2: Implement Silero VAD provider and turn runtime** - `8231e71` (feat)
3. **Task 3: Surface compact VAD metadata in spoken-turn cards** - `92a27f2` (feat)

## Files Created/Modified
- `services/api/app/services/audio_turn_runtime.py` - Normalizes captured audio, runs VAD, and persists compact metadata.
- `services/speech-worker/providers/silero_vad_provider.py` - Silero-compatible provider with deterministic fixture fallback.
- `services/speech-worker/tests/test_audio_turn_providers.py` - Provider contract and fallback coverage.
- `services/api/app/routes/audio_turns.py` - Queues background VAD processing for audio-turn jobs.
- `services/api/app/schemas/audio_turn.py` - Added VAD segment and metadata models to audio-turn records.
- `services/api/app/services/audio_turn_jobs.py` - Persists VAD metadata and weak-turn annotations.
- `services/api/tests/test_audio_turn_jobs.py` - API contract coverage for queued-to-processed audio turns and weak-turn warnings.
- `apps/web/components/studio-shell.tsx` - Spoken-turn polling and compact metadata rendering.
- `apps/web/playwright.config.ts` - Forced the browser test API server onto the fixture VAD path.
- `apps/web/tests/audio-input.spec.ts` - WAV-only browser fixtures and VAD metadata regression coverage.
- `services/speech-worker/providers/__init__.py` - Exported the Silero VAD provider.

## Decisions Made
- Kept the approved Silero path behind `VADProvider`, with a deterministic fixture fallback so local tests do not depend on torch or torchaudio being installed.
- Queued audio-turn jobs in the API and polled the session-scoped record in the browser, instead of adding a separate transcript or debug surface.
- Rendered compact turn-boundary metadata inline on spoken-turn cards and kept the capture list separate from generation attempts.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Forced the browser test harness onto the fixture VAD path**
- **Found during:** Task 3 (Surface compact VAD metadata in the spoken-turn cards)
- **Issue:** The browser regression needed WAV-only deterministic fixtures, but the API server could otherwise select a real Silero backend if torch ever appears in the venv.
- **Fix:** Prefixed the Playwright API server command with `THEATRICAL_VOICE_STUDIO_VAD_FIXTURE=1` so the local browser run always exercises the deterministic fallback path.
- **Files modified:** `apps/web/playwright.config.ts`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts -g "vad|weak"` and `pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts`
- **Committed in:** `92a27f2` (Task 3 commit)

**Total deviations:** 1 auto-fixed (Rule 3)
**Impact on plan:** No scope creep. The harness adjustment keeps the approved deterministic WAV-only test path stable.

## Issues Encountered
- The spoken-turn provider label initially rendered as `Silero Vad`; the browser regression exposed the acronym casing mismatch, so the formatter now preserves `VAD`.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Phase 3 plan 3 can build STT/transcript inspection on top of the now-queued, VAD-processed spoken-turn path without changing the studio capture surface.

---
*Phase: 03-audio-input-and-turn-detection*
*Completed: 2026-07-12*

## Self-Check: PASSED

- Summary file exists at `.planning/phases/03-audio-input-and-turn-detection/03-02-SUMMARY.md`.
- Task commit hashes are present in git history: `f6014d9`, `8231e71`, `92a27f2`.
