---
phase: 02-consented-studio-generation
plan: 04
subsystem: ui
tags: [nextjs, react, playwright, css, audio, polling, retries]

# Dependency graph
requires:
  - phase: 02-consented-studio-generation/02-03
    provides: controlled generation job records plus `/generations/{job_id}` and `/generations/{job_id}/audio` routes
  - phase: 02-consented-studio-generation/02-02
    provides: normalized playable audio output behind the worker provider contract
provides:
  - browser playback card for the current controlled clip
  - session-scoped recent attempt list with retry reuse of cached inputs
  - Next.js rewrites for generation status and audio polling
affects:
  - phase 03 audio input and turn detection
  - later studio playback and conversation flows

# Tech tracking
tech-stack:
  added:
    - none
  patterns:
    - client-side polling of controlled generation status routes with in-memory session state
    - current playable clip separated from recent attempt history
    - retry resubmits cached submission inputs instead of reading the live form

key-files:
  created: []
  modified:
    - apps/web/components/studio-shell.tsx
    - apps/web/app/globals.css
    - apps/web/next.config.ts
    - apps/web/tests/studio-generation.spec.ts

key-decisions:
  - "Keep the current playable clip separate from recent session attempts so failures stay visible without hiding the last auditable success."
  - "Store retry inputs in component state and resubmit those cached values instead of whatever happens to be in the live form fields."
  - "Rewrite `/generations/:path*` through Next.js so the browser can poll status and load the controlled audio URL from the same origin."

patterns-established:
  - "Pattern 1: the session's latest successful record drives the playable clip card while the latest attempt drives the status badge."
  - "Pattern 2: retry is a resubmission of the cached voice/text/tone tuple, not a mutation of the existing failed job."
  - "Pattern 3: controlled playback always uses the relative `/generations/{job_id}/audio` URL and browser audio controls."

requirements-completed: [STUD-05, STUD-06, STUD-07]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "The current clip card renders the controlled audio URL through browser audio controls and shows the generated text plus operational metadata."
    requirement: STUD-06
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/studio-generation.spec.ts"
        status: pass
    human_judgment: false
  - id: D2
    description: "Recent attempts remain visible only in session state, and retry resubmits the cached last voice/text/tone inputs."
    requirement: STUD-07
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/studio-generation.spec.ts"
        status: pass
    human_judgment: false
  - id: D3
    description: "Queued, running, succeeded, and failed states are reflected in the browser while the exact blocked-rights message stays intact."
    requirement: STUD-05
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/studio-generation.spec.ts"
        status: pass
    human_judgment: false

# Metrics
duration: 32m
completed: 2026-07-02
status: complete
---

# Phase 2: Consented Studio Generation Summary

The studio now shows a current playable clip through a controlled audio URL, keeps recent generation attempts in session only, and lets the user retry a failed attempt without refreshing or restoring durable history.

## Performance

- **Duration:** 32m
- **Completed:** 2026-07-02T19:23:20Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Replaced the Phase 1 metadata-only browser contract with a playback-and-retry contract that proves the current clip, recent attempts, and blocked-rights behavior from the studio shell.
- Rebuilt `StudioShell` around a current playable clip card, a session-scoped recent attempts list, and polling against `/generations/{job_id}` until the latest attempt succeeds or fails.
- Kept retry local to the browser session by caching the last submitted voice, text, and tone preset in component state and resubmitting those exact values on demand.
- Added the `/generations/:path*` Next.js rewrite so browser polling and the controlled audio URL stay same-origin and do not expose raw storage paths.

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite the studio browser spec around playback, attempts, and retry** - `817bc06` (`test`)
2. **Task 2: Upgrade the studio shell for playback and session-scoped retries** - `e6d825f` (`feat`)

## Files Created/Modified

- `apps/web/components/studio-shell.tsx` - current clip card, recent attempts list, polling, and retry reuse flow
- `apps/web/app/globals.css` - theatrical playback surface, current clip, recent attempts, and retry button styling
- `apps/web/next.config.ts` - rewrites for `/generations/:path*` alongside the existing generation route
- `apps/web/tests/studio-generation.spec.ts` - browser contract for controlled playback, session-scoped attempts, retry, and exact rights gating

## Decisions Made

- Keep the current playable clip separate from recent session attempts so failures stay visible without hiding the last auditable success.
- Store retry inputs in component state and resubmit those cached values instead of whatever happens to be in the live form fields.
- Rewrite `/generations/:path*` through Next.js so the browser can poll status and load the controlled audio URL from the same origin.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The browser route announcer from Next.js shared the generic `alert` role during verification, so the retry test now targets the explicit alert paragraph instead of the route announcer.

## User Setup Required

None. The existing Playwright and web build setup was enough to verify the playback and retry loop.

## Next Phase Readiness

- Phase 2 now has the browser-side playback contract that Phase 3 can build on for microphone and audio input.
- Session-scoped retry behavior is in place without adding durable clip history or refresh restoration.
- The current clip now uses a controlled relative playback URL, so later phases can keep the same storage boundary.

## Known Stubs

None.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/02-consented-studio-generation/02-04-SUMMARY.md`.
- Task commits verified in git history: `817bc06` and `e6d825f`.
- Automated verification passed:
  - `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts`
  - `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts`
