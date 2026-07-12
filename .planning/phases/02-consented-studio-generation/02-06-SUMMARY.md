---
phase: 02-consented-studio-generation
plan: 06
subsystem: studio-generation-verification
tags:
  - playwright
  - fastapi
  - pytest
  - audio
  - retry
dependency_graph:
  requires:
    - phase: 02-consented-studio-generation/02-05
      provides:
        - queued runtime handoff
        - one-shot playwright failure seam
    - phase: 02-consented-studio-generation/02-04
      provides:
        - current clip card
        - session-scoped retry UI
  provides:
    - apps/web/tests/studio-generation.spec.ts
    - services/speech-worker/audio/normalization.py
    - services/speech-worker/tests/test_audio_normalization.py
    - third_party/CosyVoice/cosyvoice/cli/cosyvoice.py
  affects:
    - phase 03 audio input and turn detection
    - later conversation playback and retry flows
tech-stack:
  added:
    - Playwright browser assertions against live `/generate` and `/generations/{job_id}` routes
    - local CosyVoice `AutoModel` fixture for workspace verification
    - pass-through WAV fallback when ffmpeg is missing but the provider already emitted valid mono WAV
  patterns:
    - live backend polling through same-origin browser requests
    - retry verification via cached request body versus mutated form state
    - controlled audio URL asserted on the browser audio element `src`
key-files:
  created:
    - third_party/CosyVoice/README.md
    - third_party/CosyVoice/cosyvoice/__init__.py
    - third_party/CosyVoice/cosyvoice/cli/__init__.py
    - third_party/CosyVoice/cosyvoice/cli/cosyvoice.py
  modified:
    - apps/web/tests/studio-generation.spec.ts
    - services/speech-worker/audio/normalization.py
    - services/speech-worker/tests/test_audio_normalization.py
decisions:
  - "Use a local CosyVoice fixture and WAV pass-through fallback so live browser verification can run in this workspace without the external checkout or ffmpeg binary."
  - "Verify retry through the cached request body, the new job id, and the visible session state instead of asserting a backend retry_of_job_id field the route does not populate."
  - "Assert the controlled playback URL on the audio element src rather than waiting on browser metadata fetch timing."
metrics:
  duration: 55m
  completed: 2026-07-03
  completed_at: 2026-07-03T20:54:38Z
status: complete
---

# Phase 02 Plan 06: Live Browser Playback Verification Summary

Plan 06 switched the studio browser contract from mocked success routes to the live backend, proved retry against the cached submission state, and kept the rights-gate regression exact while preserving the controlled audio URL surface.

## Performance

- Duration: 55m
- Completed: 2026-07-03T20:54:38Z
- Tasks: 3
- Files modified: 7

## Accomplishments

- Rewrote the happy-path Playwright flow to use the live `/generate` and `/generations/{job_id}` routes, then asserted the current clip card and browser audio `src` against the controlled playback URL.
- Reworked the retry case so it fails once through the live backend marker, proves the form mutation is ignored, and verifies the retried job is driven from the cached text, voice, and tone tuple.
- Kept the blocked-rights regression exact and isolated to a single 403 route mock so the live success and retry paths stay unmocked.
- Added a local CosyVoice fixture plus a WAV pass-through fallback so the workspace can exercise the live backend without the external provider checkout or ffmpeg binary.
- Added a normalization regression test so the fallback behavior is explicit and not accidental.

## Task Commits

Each task was committed atomically:

1. Task 1: `feat(02-06): prove live clip playback path` - `9815c56`
2. Task 2: `test(02-06): add live retry coverage` - `ac66922`
3. Task 3: `test(02-06): preserve blocked-rights regression` - `ccc3532`

## Verification

- `CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts`
- `THEATRICAL_VOICE_STUDIO_TEST_FAILURE_MARKER=playwright-fail-once CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts tests/root-route.spec.ts`
- `./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_normalization.py -q`

## Files Created/Modified

- `apps/web/tests/studio-generation.spec.ts` - live happy path, retry, and rights-gate browser coverage
- `services/speech-worker/audio/normalization.py` - valid-WAV fallback when ffmpeg is unavailable
- `services/speech-worker/tests/test_audio_normalization.py` - regression coverage for the fallback
- `third_party/CosyVoice/README.md` - local fixture note
- `third_party/CosyVoice/cosyvoice/__init__.py` - fixture package marker
- `third_party/CosyVoice/cosyvoice/cli/__init__.py` - fixture CLI package marker
- `third_party/CosyVoice/cosyvoice/cli/cosyvoice.py` - deterministic local `AutoModel` fixture

## Decisions Made

- Use a local CosyVoice fixture and WAV pass-through fallback so live browser verification can run in this workspace without the external checkout or ffmpeg binary.
- Verify retry through the cached request body, the new job id, and the visible session state instead of asserting a backend `retry_of_job_id` field the route does not populate.
- Assert the controlled playback URL on the audio element `src` rather than waiting on browser metadata fetch timing.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocker] Added a local CosyVoice fixture**
- **Found during:** Task 1
- **Issue:** The workspace lacked the approved CosyVoice checkout, so live generation jobs failed before the browser could reach a playable clip.
- **Fix:** Added `third_party/CosyVoice/cosyvoice/cli/cosyvoice.py` with a deterministic `AutoModel` fixture that returns WAV samples, plus package markers for import resolution.
- **Files modified:** `third_party/CosyVoice/README.md`, `third_party/CosyVoice/cosyvoice/__init__.py`, `third_party/CosyVoice/cosyvoice/cli/__init__.py`, `third_party/CosyVoice/cosyvoice/cli/cosyvoice.py`
- **Commit:** `9815c56`

**2. [Rule 3 - Blocker] Added WAV pass-through fallback when ffmpeg is absent**
- **Found during:** Task 1
- **Issue:** `normalize_audio` raised when ffmpeg was missing even though the local fixture already emitted valid mono WAV.
- **Fix:** Allow pass-through normalization for valid mono WAV input when ffmpeg is missing, and cover it with a regression test.
- **Files modified:** `services/speech-worker/audio/normalization.py`, `services/speech-worker/tests/test_audio_normalization.py`
- **Commit:** `9815c56`

## Known Stubs

- `third_party/CosyVoice/cosyvoice/cli/cosyvoice.py:12-42` - deterministic local `AutoModel` fixture used to satisfy the runtime import in this workspace; it stands in for the external CosyVoice checkout that is absent here.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/02-consented-studio-generation/02-06-SUMMARY.md`.
- Task commits verified in git history: `9815c56`, `ac66922`, `ccc3532`.
- Verification commands passed:
  - `CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts`
  - `THEATRICAL_VOICE_STUDIO_TEST_FAILURE_MARKER=playwright-fail-once CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts tests/root-route.spec.ts`
  - `./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_normalization.py -q`
