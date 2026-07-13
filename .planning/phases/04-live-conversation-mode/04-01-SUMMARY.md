---
phase: 04-live-conversation-mode
plan: 01
subsystem: web-api
tags:
  - conversation
  - fastapi
  - nextjs
  - playwright
dependency_graph:
  requires:
    - Phase 3 audio input and turn detection
    - Existing studio shell and same-origin rewrite patterns
  provides:
    - Inline live conversation controls on the root studio route
    - Server-owned conversation session records
    - Same-origin start/stop rewrites for conversation session requests
  affects:
    - apps/web/components/studio-shell.tsx
    - apps/web/components/conversation-panel.tsx
    - apps/web/app/globals.css
    - apps/web/next.config.ts
    - apps/web/tests/conversation-mode.spec.ts
    - apps/web/tests/root-route.spec.ts
    - services/api/app/main.py
    - services/api/app/routes/conversation.py
    - services/api/app/schemas/conversation.py
    - services/api/app/services/conversation_jobs.py
    - services/api/tests/test_conversation_jobs.py
tech_stack:
  added:
    - FastAPI conversation session router
    - SQLite-backed conversation session service
    - Next.js same-origin rewrites for conversation routes
    - Client-side live conversation panel component
  patterns:
    - Session-scoped record stored server-side
    - Inline live panel beside the existing composer
    - Playwright route stubs for the same-origin browser contract
key_files:
  created:
    - apps/web/components/conversation-panel.tsx
    - apps/web/tests/conversation-mode.spec.ts
    - services/api/app/routes/conversation.py
    - services/api/app/schemas/conversation.py
    - services/api/app/services/conversation_jobs.py
    - services/api/tests/test_conversation_jobs.py
  modified:
    - apps/web/components/studio-shell.tsx
    - apps/web/app/globals.css
    - apps/web/next.config.ts
    - apps/web/tests/root-route.spec.ts
    - services/api/app/main.py
decisions:
  - Keep live conversation inline on `/` instead of adding a separate route.
  - Use a server-owned SQLite session record as the authoritative browser-session conversation state.
  - Keep start/stop requests same-origin through Next.js rewrites.
  - Extract the conversation panel into a sibling client component to keep `studio-shell.tsx` maintainable.
metrics:
  duration: "~1h 10m"
  completed: "2026-07-12"
status: complete
---

# Phase 04 Plan 01: Live Conversation Mode Summary

Inline live conversation now lives on the root studio route with server-owned session records, same-origin session rewrites, and a browser-visible start/stop panel, without introducing a separate conversation page or durable history.

## Outcome

- Added the failing API and Playwright contracts first so the session lifecycle and inline `/` surface were pinned before implementation.
- Implemented strict conversation session and turn models, a SQLite-backed `ConversationSessionService`, and `POST /conversation-sessions`, `GET /conversation-sessions/{session_id}`, and `POST /conversation-sessions/{session_id}/stop`.
- Wired the live conversation panel into the existing studio shell and routed conversation requests through Next.js rewrites on the same origin.
- Kept the panel visually aligned with the rest of the theatrical studio through the existing card and control language.

## Verification

- Red phase: `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -x` failed on the missing session route before the backend slice landed.
- Red phase: `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "start conversation"` failed on the missing live conversation panel before the UI slice landed.
- Green phase: `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -x` passed after the backend session router landed.
- Green phase: `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts tests/root-route.spec.ts` passed after the inline panel and rewrites landed.

## Commit Log

- `8ba1909` - `test(04-01): add failing conversation session and live panel contracts`
- `5fb9fc6` - `feat(04-01): add conversation session service and router`
- `c994193` - `feat(04-01): add inline live conversation shell and rewrites`

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- Found `.planning/phases/04-live-conversation-mode/04-01-SUMMARY.md`.
- Found `apps/web/components/conversation-panel.tsx`.
- Found `services/api/app/routes/conversation.py`.
- Found `services/api/tests/test_conversation_jobs.py`.
- Found commits `8ba1909`, `5fb9fc6`, and `c994193` in `git log --oneline --all`.
