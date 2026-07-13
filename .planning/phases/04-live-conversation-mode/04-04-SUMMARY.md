---
phase: 04-live-conversation-mode
plan: 04
subsystem: ui
tags: [react, playwright, vad, conversation, interruption]

# Dependency graph
requires:
  - phase: 03-audio-input-and-turn-detection
    provides: spoken-input capture, VAD/STT baseline, transcript inspection, and same-origin audio turn plumbing
provides:
  - best-effort browser mic-energy barge-in that reuses the existing interrupt route
  - regression coverage for barge-in without clicking Interrupt
  - regression coverage for failed-turn recovery within the same conversation session
affects: [phase 05, conversation reliability, live session playback]

# Tech tracking
tech-stack:
  added: []
  patterns: [session-scoped mic-energy monitor, pause-then-interrupt barge-in flow, forced-failure recovery regression]

key-files:
  created:
    - .planning/phases/04-live-conversation-mode/04-04-SUMMARY.md
  modified:
    - apps/web/components/studio-shell.tsx
    - apps/web/tests/conversation-mode.spec.ts
    - services/api/tests/test_conversation_jobs.py
    - .planning/STATE.md
    - .planning/ROADMAP.md

key-decisions:
  - "Keep barge-in best-effort on the browser side and reuse the existing interrupt route instead of introducing a new cancellation path."
  - "Leave the backend turn-scoping logic unchanged because the forced failure regression showed the existing session recovery path already works."

patterns-established:
  - "Pattern 1: start and stop a session-scoped mic-energy loop from a React effect that follows conversation listening state."
  - "Pattern 2: model active playback in Playwright by overriding a specific audio element's play/pause behavior, then assert the existing interrupt route fires."
  - "Pattern 3: force a first-turn provider failure and prove a second turn still succeeds in the same session."

requirements-completed: [CONV-02, CONV-03, CONV-04]

coverage:
  - id: D1
    description: "Best-effort browser mic-energy barge-in pauses live playback and calls the existing interrupt route without clicking the Interrupt button."
    requirement: "CONV-04"
    verification:
      - kind: automated_ui
        ref: "pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g \"barge-in|interrupt\""
        status: pass
    human_judgment: false
  - id: D2
    description: "A forced first-turn conversation failure stays scoped to that turn while the next turn in the same session still completes."
    requirement: "CONV-02"
    verification:
      - kind: unit
        ref: "./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k \"test_conversation_turn_failure_stays_scoped_to_the_turn_and_next_turn_completes\" -x"
        status: pass
    human_judgment: false

# Metrics
duration: 16m
completed: 2026-07-13
status: complete
---

# Phase 04: Live Conversation Mode Summary

Best-effort browser mic barge-in now pauses live playback and reuses the existing interrupt flow, while forced first-turn failures stay isolated to the turn and do not poison the next conversation turn.

## Performance

- **Duration:** 16m
- **Started:** 2026-07-13T21:24:12Z
- **Completed:** 2026-07-13T21:40:31Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added a browser mic-energy barge-in fallback inside `StudioShell` that pauses playback and calls the existing interrupt route.
- Added Playwright coverage proving barge-in works without clicking the explicit Interrupt button.
- Added backend regression coverage proving a forced failed first turn stays scoped to that turn and the next turn in the same session still completes.

## Task Commits

- `49544af` - `test(04-04): add live barge-in and recovery regressions`
  - Added the Playwright barge-in regression.
  - Added the backend same-session failure-recovery regression.
- `e07cadc` - `feat(04-04): add speech-triggered barge-in monitor`
  - Added the best-effort browser mic-energy monitor.
  - Reused the existing pause-then-interrupt flow for barge-in.

## Deviations from Plan

None. The backend regression passed without requiring a server-side code change, so the plan closed with the minimal UI-only implementation.


## Self-Check: PASSED

- Summary file exists on disk.
- Task commit `49544af` exists in git history.
- Task commit `e07cadc` exists in git history.
