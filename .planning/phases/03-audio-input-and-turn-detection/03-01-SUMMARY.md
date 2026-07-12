---
phase: 03-audio-input-and-turn-detection
plan: 01
subsystem: ui
tags: [nextjs, fastapi, playwright, mediarecorder, accessibility, sqlite]

# Dependency graph
requires:
  - phase: 02-consented-studio-generation
    provides: generation job shell, same-origin rewrite pattern, session-scoped playback, retry state
provides:
  - Browser mic and upload controls beside the composer
  - Session-scoped audio-turn job service and control-plane routes
  - Accessible spoken-turn list separate from generation attempts
affects: [phase 04 live conversation mode, future VAD/STT turn detection, same-origin control-plane routing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Same-origin POST/GET rewrites for browser audio capture"
    - "Session-scoped spoken-turn history kept separate from generation attempts"
    - "Accessible recording status and timer feedback in the studio shell"

key-files:
  created:
    - services/api/app/routes/audio_turns.py
    - services/api/app/schemas/audio_turn.py
    - services/api/app/services/audio_turn_jobs.py
    - .planning/phases/03-audio-input-and-turn-detection/03-01-SUMMARY.md
  modified:
    - apps/web/components/studio-shell.tsx
    - apps/web/next.config.ts
    - apps/web/tests/audio-input.spec.ts
    - apps/web/tests/root-route.spec.ts
    - services/api/app/main.py
    - services/api/tests/test_audio_turn_jobs.py
    - .planning/STATE.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Kept spoken capture on the same studio surface instead of introducing a separate audio page or mode switcher."
  - "Sent capture and upload as raw audio blobs to same-origin /audio-turns routes so the browser can hand off directly to the control plane."
  - "Modeled spoken-turn history separately from generation attempts so the session can inspect audio capture without mixing the two workflows."

patterns-established:
  - "Separate generation and spoken capture lists with shared attempt-card styling but distinct data sources."
  - "Accessible live recording status text plus a timer indicator for audio capture."
  - "Relative playback URLs served through same-origin rewrites."

requirements-completed: [AUD-01]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: Browser mic and upload controls render beside the composer with visible labels, keyboard focus, and assistive-tech-readable recording status.
    requirement: AUD-01
    verification:
      - kind: automated_ui
        ref: "pnpm --dir apps/web exec playwright test tests/root-route.spec.ts tests/audio-input.spec.ts"
        status: pass
    human_judgment: false
  - id: D2
    description: Audio-turn job records can be created and retrieved through the control-plane service and route layer.
    requirement: AUD-01
    verification:
      - kind: unit
        ref: "./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -q"
        status: pass
    human_judgment: false
  - id: D3
    description: Spoken-turn history stays separate from generation attempts and auto-appends recording or upload jobs through the same-origin rewrite path.
    requirement: AUD-01
    verification:
      - kind: automated_ui
        ref: "pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts"
        status: pass
    human_judgment: false

# Metrics
duration: 19m
completed: 2026-07-07
status: complete
---

# Phase 03: Audio Input and Turn Detection Summary

**Browser mic/upload controls now queue session-scoped spoken-turn jobs beside the studio composer, with accessible recording feedback and separate turn history.**

## Performance

- **Duration:** 19 min
- **Started:** 2026-07-07T17:26:39Z
- **Completed:** 2026-07-07T17:45:44Z
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments
- Added a dedicated audio-turn control-plane seam with `POST /audio-turns`, `GET /audio-turns/{job_id}`, and controlled audio serving from the same origin.
- Wired the studio shell to record, stop, and upload spoken input beside the composer with visible labels, focus styling, status text, and a live timer.
- Kept spoken turns in their own session list, separate from generation attempts, and verified the flow with Playwright plus API unit coverage.

## Task Commits

Each task was committed atomically:

1. **Task 1: Red-line the audio-input capture, accessibility, and queue contract** - `e6ef8d2` (test)
2. **Task 2: Add the audio-turn job service and control-plane routes** - `54aacf6` (feat)
3. **Task 3: Wire the studio capture controls and spoken-turn list** - `1509dad` (feat)

**Plan metadata:** pending final docs commit

## Files Created/Modified
- `services/api/app/schemas/audio_turn.py` - Audio-turn schema and record types.
- `services/api/app/services/audio_turn_jobs.py` - Object store plus SQLite-backed audio-turn job service.
- `services/api/app/routes/audio_turns.py` - Control-plane routes for creating, reading, and serving spoken turns.
- `apps/web/components/studio-shell.tsx` - Record/stop/upload capture UI, spoken-turn list, and polling state.
- `apps/web/next.config.ts` - Same-origin rewrites for the audio-turn routes.
- `apps/web/tests/audio-input.spec.ts` - Playwright coverage for capture, accessibility, and session separation.
- `apps/web/tests/root-route.spec.ts` - Root-route smoke coverage for the new controls.
- `services/api/app/main.py` - Mounted the audio-turn router.
- `services/api/tests/test_audio_turn_jobs.py` - API contract coverage for queued audio-turn jobs.
- `.planning/STATE.md` - Updated execution state and plan progress.
- `.planning/ROADMAP.md` - Updated phase progress.
- `.planning/REQUIREMENTS.md` - Marked AUD-01 complete.
- `.planning/phases/03-audio-input-and-turn-detection/03-01-SUMMARY.md` - Plan summary artifact.

## Decisions Made
- Kept spoken capture on the same studio surface instead of introducing a separate audio page or mode switcher.
- Sent capture and upload as raw audio blobs to same-origin `/audio-turns` routes so the browser can hand off directly to the control plane.
- Modeled spoken-turn history separately from generation attempts so the session can inspect audio capture without mixing the two workflows.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed `studio-shell.tsx` typecheck failures in the new audio-turn flow**
- **Found during:** Task 3 (Wire the studio capture controls and spoken-turn list)
- **Issue:** The new generic record helper left `getPlaybackState` calling a removed helper name, which blocked the Next.js typecheck.
- **Fix:** Repointed playback state lookup to the generic helper and kept the generation and spoken-turn lists using the shared upsert utility.
- **Files modified:** `apps/web/components/studio-shell.tsx`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts tests/audio-input.spec.ts`
- **Committed in:** `1509dad` (Task 3 commit)

**2. [Rule 3 - Blocking] Narrowed the audio-turn error payload to satisfy TypeScript**
- **Found during:** Task 3 (Wire the studio capture controls and spoken-turn list)
- **Issue:** `submitAudioTurn` tried to read `payload.detail` from a union type without narrowing, which stopped the build.
- **Fix:** Introduced a typed `responseError` alias before reading the optional error message.
- **Files modified:** `apps/web/components/studio-shell.tsx`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts tests/audio-input.spec.ts`
- **Committed in:** `1509dad` (Task 3 commit)

**3. [Rule 1 - Bug] Separated the hidden file input label from the visible Upload button**
- **Found during:** Task 3 (Wire the studio capture controls and spoken-turn list)
- **Issue:** The hidden file input and visible upload button shared the same accessible name, which made the Playwright role query ambiguous.
- **Fix:** Renamed the hidden input label so the visible upload button is uniquely addressable while file uploads still work.
- **Files modified:** `apps/web/components/studio-shell.tsx`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts tests/audio-input.spec.ts`
- **Committed in:** `1509dad` (Task 3 commit)

**Total deviations:** 3 auto-fixed (2x Rule 3, 1x Rule 1)
**Impact on plan:** No scope creep. The fixes were required to make the shipped browser contract compile and stay accessible.

## Issues Encountered
- Next.js typechecking caught the audio-turn response narrowing issue during the browser verification pass.
- The hidden file input needed a distinct accessible name so the visible upload button could be queried unambiguously in Playwright.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Phase 03 plan 1 is complete and the browser/audio-turn seam is in place. Phase 03 plan 2 can build on the new session-scoped audio-turn job path for VAD-based segmentation without changing the studio surface.

---
*Phase: 03-audio-input-and-turn-detection*
*Completed: 2026-07-07*

## Self-Check: PASSED

- Summary file exists at `.planning/phases/03-audio-input-and-turn-detection/03-01-SUMMARY.md`.
- Task commit hashes are present in git history: `e6ef8d2`, `54aacf6`, `1509dad`.
