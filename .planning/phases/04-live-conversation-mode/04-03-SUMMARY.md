---
phase: 04-live-conversation-mode
plan: 03
subsystem: ui
tags: [conversation, interrupt, latency, playwright, fastapi, nextjs]
requires:
  - phase: 04-02
    provides: audio capture/session plumbing, same-origin rewrites, and turn record persistence
provides:
  - explicit interrupt control with cooperative cancel semantics for live conversation turns
  - backend turn metadata for cancel state and stage timings
  - compact seconds-based latency chips on each live turn card
affects:
  - phase 05
  - phase 06
tech-stack:
  added: []
  patterns:
    - cooperative cancel state machine with persisted cancel metadata
    - compact latency chip formatting on live turn cards
    - best-effort playback pause followed by server-side interrupt confirmation
key-files:
  created:
    - .planning/phases/04-live-conversation-mode/04-03-SUMMARY.md
  modified:
    - services/api/app/schemas/conversation.py
    - services/api/app/services/conversation_runtime.py
    - services/api/app/services/conversation_jobs.py
    - services/api/app/routes/conversation.py
    - apps/web/components/conversation-panel.tsx
    - apps/web/components/studio-shell.tsx
    - apps/web/app/globals.css
    - services/api/tests/test_conversation_jobs.py
    - apps/web/tests/conversation-mode.spec.ts
key-decisions:
  - "Keep interrupt cooperative: the browser pauses playback immediately, then POSTs the active turn to the server so late completions cannot resurrect canceled work."
  - "Show the live-turn latency as a compact seconds chip instead of a timing table; detailed stage timings remain server-side."
  - "Render Interrupt as a first-class live-panel control and let the handler bootstrap a session on demand so the control is reachable even before the first turn is active."
patterns-established:
  - "Pattern 1: turn-service helpers now own cancel-state persistence and ignore late success/failure writes after interruption."
  - "Pattern 2: live conversation cards render only a compact latency chip while detailed stage timings stay in backend records and tests."
  - "Pattern 3: browser interrupt interactions use same-origin fetch plus immediate HTMLMediaElement.pause() for best-effort playback stop."
requirements-completed: [CONV-04, CONV-05]
coverage:
  - id: D1
    description: "Explicit Interrupt control that pauses playback immediately and persists cooperative cancel state on the active conversation turn."
    requirement: CONV-04
    verification:
      - kind: unit
        ref: "services/api/tests/test_conversation_jobs.py#test_conversation_turn_interrupt_route_records_cancel_state_and_stage_timings"
        status: pass
      - kind: automated_ui
        ref: "apps/web/tests/conversation-mode.spec.ts#interrupt control pauses playback and returns the panel to listening"
        status: pass
    human_judgment: false
  - id: D2
    description: "Conversation turns persist speech-end-to-transcript, response-text, TTS-complete, playback-start, and total latency metadata while the UI renders a compact seconds-based latency chip."
    requirement: CONV-05
    verification:
      - kind: unit
        ref: "services/api/tests/test_conversation_jobs.py#test_synthesize_conversation_turn_persists_stage_timing_metadata"
        status: pass
      - kind: automated_ui
        ref: "apps/web/tests/conversation-mode.spec.ts#response playback shows up in the live conversation turn card"
        status: pass
    human_judgment: false
  - id: D3
    description: "Regression coverage for the complete live conversation loop, including start, interrupt, playback, and turn list updates."
    verification:
      - kind: automated_ui
        ref: "pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts"
        status: pass
      - kind: unit
        ref: "./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k \"cancel or latency\" -q"
        status: pass
    human_judgment: false
duration: 63min
completed: 2026-07-13
status: complete
---

# Phase 04 Plan 03: Live Conversation Mode Summary

**Cooperative interrupt handling with persisted turn timings and a compact live latency chip**

## Performance

- **Duration:** 1h 3m
- **Started:** 2026-07-13T19:09:30Z
- **Completed:** 2026-07-13T20:12:27Z
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments

- Added a cooperative cancel path for live conversation turns, including `POST /conversation-turns/{turn_id}/interrupt`, cancel-state persistence, and late-completion guards.
- Added detailed turn timing metadata on the backend while keeping the browser surface to a compact seconds-based latency chip.
- Wired the studio shell to pause playback immediately, interrupt the active turn, and keep the inline live conversation workflow on `/`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the failing interrupt and latency contracts** - `131fd83` (test)
2. **Task 2: Implement cooperative cancel and timing persistence** - `1069380` (feat)
3. **Task 3: Wire the Interrupt button and compact latency chip** - `adeb0a3` (feat)

**Plan metadata:** this SUMMARY and phase tracking close-out are committed separately.

## Files Created/Modified

- `.planning/phases/04-live-conversation-mode/04-03-SUMMARY.md` - Phase completion record and traceability matrix
- `services/api/app/schemas/conversation.py` - Conversation turn cancel-state and timing schema fields
- `services/api/app/services/conversation_runtime.py` - Cooperative interrupt helper and turn timing propagation
- `services/api/app/services/conversation_jobs.py` - Cancel-state persistence and late-write guards
- `services/api/app/routes/conversation.py` - `POST /conversation-turns/{turn_id}/interrupt`
- `apps/web/components/conversation-panel.tsx` - Live turn latency chip and interrupt control
- `apps/web/components/studio-shell.tsx` - Playback pause plus interrupt request flow
- `apps/web/app/globals.css` - Latency chip and interrupt button styling
- `services/api/tests/test_conversation_jobs.py` - API regression coverage for cancel and timing metadata
- `apps/web/tests/conversation-mode.spec.ts` - Browser regression coverage for interrupt and compact latency

## Decisions Made

- Keep interrupt cooperative: the browser pauses playback immediately, then POSTs the active turn to the server so late completions cannot resurrect canceled work.
- Show the live-turn latency as a compact seconds chip instead of a timing table; detailed stage timings remain server-side.
- Render Interrupt as a first-class live-panel control and let the handler bootstrap a session on demand so the control is reachable even before the first turn is active.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The `04-03` executor stopped returning completion signals after Task 2. Spot checks later found Task 3 commit `adeb0a3` and this summary on disk, so the orchestrator completed the metadata close-out without re-dispatching duplicate work.
- The browser interrupt path needed a short animation-frame delay after session bootstrap so the rendered audio element existed before the pause call; that was handled inside the interrupt click flow.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Live conversation now has explicit interruption, server-owned cancel state, and stable timing metadata for benchmark comparisons.
- Phase 05 can measure provider quality and latency against a turn loop that already exposes the interrupt semantics required for real conversation tests.

## Self-Check: PASSED

- Summary file found on disk at `.planning/phases/04-live-conversation-mode/04-03-SUMMARY.md`.
- Task commits found: `131fd83`, `1069380`, and `adeb0a3`.
- Verification passed: `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "cancel or latency" -q` and `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts`.

---
*Phase: 04-live-conversation-mode*
*Completed: 2026-07-13*
