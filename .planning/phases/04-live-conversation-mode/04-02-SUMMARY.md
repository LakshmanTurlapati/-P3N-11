---
phase: 04-live-conversation-mode
plan: 02
subsystem: web-api-speech-worker
tags:
  - conversation
  - persona-boundary
  - tts
  - fastapi
  - nextjs
dependency_graph:
  requires:
    - Phase 3 audio input and turn detection
    - 04-01 inline conversation session controls
  provides:
    - Persona-safe conversation response provider contract
    - Deterministic Vesper Glass conversation responder
    - Turn-backed response text and controlled playback URLs
    - Live conversation response cards on the root studio surface
  affects:
    - services/speech-worker/providers/conversation_provider.py
    - services/api/app/services/conversation_runtime.py
    - services/api/app/services/conversation_jobs.py
    - services/api/app/routes/conversation.py
    - apps/web/components/conversation-panel.tsx
    - apps/web/components/studio-shell.tsx
tech_stack:
  added:
    - Conversation response provider protocol
    - Deterministic local responder fixture
    - Conversation turn object store and SQLite records
  patterns:
    - Server-side prompt boundary carries prohibited associations before response generation
    - Conversation turns persist response text, providers, tone, latency, and playback metadata together
    - Same-origin conversation turn routes hide raw storage paths from the browser
key_files:
  created:
    - services/speech-worker/providers/conversation_provider.py
  modified:
    - apps/web/components/conversation-panel.tsx
    - apps/web/components/studio-shell.tsx
    - apps/web/next.config.ts
    - services/api/app/routes/conversation.py
    - services/api/app/schemas/conversation.py
    - services/api/app/services/conversation_jobs.py
    - services/api/app/services/conversation_runtime.py
    - services/api/tests/test_conversation_provider.py
    - services/speech-worker/providers/__init__.py
    - services/speech-worker/tests/test_conversation_provider.py
    - apps/web/tests/conversation-mode.spec.ts
    - pyproject.toml
key_decisions:
  - Keep the conversation responder deterministic for v1 local validation instead of adding a real LLM dependency.
  - Keep response prompt construction server-side so original-voice boundary and prohibited associations are enforced before response text exists.
  - Store conversation turn input and response audio behind controlled same-origin routes instead of exposing object store paths.
requirements-completed:
  - CONV-02
  - CONV-03
coverage:
  - id: D1
    description: Persona-safe responder emits concise tone-steered text without protected identity claims.
    requirement: CONV-03
    verification:
      - kind: unit
        ref: services/speech-worker/tests/test_conversation_provider.py#test_vesper_conversation_responder_stays_inside_the_original_voice_boundary
        status: pass
      - kind: unit
        ref: services/speech-worker/tests/test_conversation_provider.py#test_vesper_conversation_responder_steers_tone_without_changing_the_boundary
        status: pass
    human_judgment: false
  - id: D2
    description: Runtime prompt includes the original voice boundary, prohibited associations, selected tone, and short session memory.
    requirement: CONV-03
    verification:
      - kind: unit
        ref: services/api/tests/test_conversation_provider.py#test_build_conversation_response_prompt_keeps_the_original_voice_boundary_and_memory
        status: pass
    human_judgment: false
  - id: D3
    description: Spoken conversation turns persist response text, tone, provider names, playback URL, and response audio bytes.
    requirement: CONV-02
    verification:
      - kind: integration
        ref: services/api/tests/test_conversation_provider.py#test_synthesize_conversation_turn_persists_response_and_playback_metadata
        status: pass
    human_judgment: false
  - id: D4
    description: Root studio live panel shows response text and controlled audio playback for a conversation turn.
    requirement: CONV-02
    verification:
      - kind: automated_ui
        ref: apps/web/tests/conversation-mode.spec.ts#response playback shows up in the live conversation turn card
        status: pass
    human_judgment: false
metrics:
  duration: "~1h 45m"
  completed: "2026-07-13"
status: complete
---

# Phase 04 Plan 02: Persona-Safe Conversation Response Loop Summary

Persona-safe live conversation turns now run through a deterministic responder, persist response and playback metadata server-side, and render response text plus controlled audio in the inline studio panel.

## Performance

- **Duration:** ~1h 45m
- **Started:** 2026-07-13T17:20:00Z
- **Completed:** 2026-07-13T19:07:27Z
- **Tasks:** 3
- **Files modified:** 12

## Accomplishments

- Added failing API, worker-provider, and browser contracts for tone-steered persona-safe response playback.
- Added `ConversationResponseProvider` and `VesperConversationResponder` behind the speech-worker provider boundary.
- Added runtime prompt construction with boundary notes, prohibited associations, tone preset, and recent-turn memory.
- Added turn persistence for input audio, response text, response providers, TTS provider, tone, latency, playback URL, and controlled response audio.
- Wired `/conversation-turns` routes and Next.js rewrites so the browser can submit a live turn and poll the authoritative session record.
- Updated the inline live panel to show response text, tone, latency, and a same-origin audio player for conversation turns.

## Task Commits

1. **Task 1: Write the failing persona-safe response contracts** - `e0c0189` (`test(04-02)`)
2. **Task 2: Implement the deterministic response provider and runtime prompt** - `016b452` (`feat(04-02)`)
3. **Task 3: Wire the turn response, playback, and live card UI** - `ef0156d` (`feat(04-02)`)

## Files Created/Modified

- `services/speech-worker/providers/conversation_provider.py` - Conversation response protocol and deterministic Vesper responder.
- `services/speech-worker/providers/__init__.py` - Lazy exports for the conversation provider.
- `services/api/app/schemas/conversation.py` - Response prompt/result schemas and response-aware turn metadata.
- `services/api/app/services/conversation_runtime.py` - Prompt building, response generation, and turn synthesis pipeline.
- `services/api/app/services/conversation_jobs.py` - Conversation turn object store, SQLite records, state transitions, and playback paths.
- `services/api/app/routes/conversation.py` - Turn creation, detail, input audio, and response audio routes.
- `apps/web/components/conversation-panel.tsx` - Response-aware live turn cards.
- `apps/web/components/studio-shell.tsx` - Live conversation turn submission, session polling, and turn state updates.
- `apps/web/next.config.ts` - Same-origin conversation turn rewrites.
- `services/api/tests/test_conversation_provider.py` - Prompt and turn-synthesis persistence coverage.
- `services/speech-worker/tests/test_conversation_provider.py` - Responder boundary and tone coverage.
- `apps/web/tests/conversation-mode.spec.ts` - Browser response playback coverage.

## Decisions Made

- Kept v1 response generation deterministic and local so the provider contract, prompt boundary, and playback loop can be tested without a real LLM dependency.
- Kept short session memory in authoritative server turn records and did not persist refresh memory.
- Used controlled same-origin `/conversation-turns/{turn_id}/audio` playback instead of exposing raw storage paths.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Recovered partial executor state after stalled subagent**
- **Found during:** Task 3 close-out
- **Issue:** The executor produced two `04-02` commits and left Task 3 files modified without `04-02-SUMMARY.md`.
- **Fix:** Closed the stalled agent, inspected the partial diff, completed Task 3 inline, and committed the remaining response-playback slice.
- **Files modified:** `apps/web/components/studio-shell.tsx`, `services/api/tests/test_conversation_provider.py`, `services/speech-worker/tests/test_conversation_provider.py`, plus the Task 3 implementation files.
- **Verification:** `./.venv/bin/python -m pytest services/api/tests/test_conversation_provider.py services/speech-worker/tests/test_conversation_provider.py -q` and `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts` passed.
- **Committed in:** `ef0156d`

**2. [Rule 2 - Missing Critical] Added full turn-attempt fixture metadata and runtime persistence coverage**
- **Found during:** Task 3 verification
- **Issue:** The response-turn schema required succeeded turns to include attempt metadata, but the persona prompt tests still built historical succeeded turns without attempts.
- **Fix:** Updated fixtures to include full attempt metadata and added an integration test proving synthesis persists response text, provider names, tone, playback URL, and response audio bytes.
- **Files modified:** `services/api/tests/test_conversation_provider.py`, `services/speech-worker/tests/test_conversation_provider.py`
- **Verification:** Provider/runtime tests passed.
- **Committed in:** `ef0156d`

**Total deviations:** 2 auto-fixed (1 blocking recovery, 1 missing critical coverage fix).
**Impact on plan:** The fixes completed the intended plan surface without adding a new transport, LLM dependency, or persistent conversation history.

## Issues Encountered

- The `04-02` executor stalled after two commits and left uncommitted Task 3 files. The plan was recovered inline and closed with a committed summary.
- The focused browser test initially failed type checking because conversation turns use `turn_id` while the existing UI helper only upserted `job_id` records. A conversation-turn-specific upsert helper resolved the mismatch.

## Verification

- `./.venv/bin/python -m pytest services/api/tests/test_conversation_provider.py services/speech-worker/tests/test_conversation_provider.py -q` - passed, 4 tests.
- `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "response"` - passed, 1 test.
- `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts` - passed, 2 tests.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The live conversation loop now has session state, response text, controlled turn audio, and browser playback. Plan 04-03 can build interruption and latency controls on top of the persisted turn timing and status fields.

## Self-Check: PASSED

- Found `.planning/phases/04-live-conversation-mode/04-02-SUMMARY.md`.
- Found `services/speech-worker/providers/conversation_provider.py`.
- Found `services/api/app/services/conversation_runtime.py`.
- Found `services/api/app/routes/conversation.py`.
- Found `apps/web/components/conversation-panel.tsx`.
- Found commits `e0c0189`, `016b452`, and `ef0156d` in `git log --oneline --all`.
- Re-ran the plan verification commands successfully.
