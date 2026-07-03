---
phase: 02-consented-studio-generation
plan: 05
subsystem: api
tags:
  - fastapi
  - background-tasks
  - cosyvoice
  - pytest
dependency_graph:
  requires:
    - phase: 02-consented-studio-generation/02-03
      provides:
        - queued job schema
        - local object-store playback URLs
    - phase: 02-consented-studio-generation/02-04
      provides:
        - browser session contract for queued generation and retry
  provides:
    - services/api/app/services/generation_runtime.py
    - queued-first POST /generate handoff
    - one-shot playwright-fail-once failure seam
  affects:
    - phase 02-06 live backend generation browser tests
    - future worker hardening and retries
tech-stack:
  added:
    - FastAPI BackgroundTasks
    - lazy CosyVoice runtime loading from services/speech-worker
    - test-only one-shot failure marker seam
  patterns:
    - queued-first generation route
    - runtime-managed job state transitions
    - provider-agnostic synthesis wrapper
key-files:
  created:
    - services/api/app/services/generation_runtime.py
    - services/api/tests/test_generation_runtime.py
  modified:
    - services/api/app/routes/generate.py
    - services/api/tests/conftest.py
decisions:
  - "Queue generation first, then hand off to BackgroundTasks after the rights gate."
  - "Load CosyVoice lazily from the approved worker root only when the default provider is needed."
  - "Use a one-shot playwright-fail-once seam gated by CI/Playwright env for live retry coverage."
metrics:
  duration: 30m
  completed: 2026-07-03
  completed_at: 2026-07-03T19:55:29Z
status: complete
---

# Phase 02 Plan 05: Queued Runtime Handoff Summary

POST /generate now returns a queued job immediately after the rights gate and schedules a lazy-loaded CosyVoice runtime in the background. The runtime advances jobs through running, succeeded, and failed states, stores normalized audio for controlled playback, and includes a one-shot playwright-fail-once seam so live retry tests can fail once and recover.

## Performance

- **Duration:** 30m
- **Completed:** 2026-07-03T19:55:29Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added a RED contract for `process_generation_job` that exercises queued -> running -> succeeded, provider failure -> failed, and the one-shot marker seam.
- Patched the API test harness so legacy queued-job tests keep background dispatch deterministic by stubbing the route-level task callable.
- Implemented a lazy CosyVoice runtime wrapper that loads the worker package only when the default provider is needed, then marks jobs running, synthesizes audio, stores the clip, and marks success or failure.
- Updated `POST /generate` to create the queued job after `ensure_voice_allowed(...)` and schedule background processing instead of blocking the request.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add failing runtime contract and no-op route dispatch patch** - `3b0b58d` (`test`)
2. **Task 2: Wire queued jobs to the real generation runtime** - `66f5e0b` (`feat`)

## Files Created/Modified

- `services/api/app/services/generation_runtime.py` - lazy provider loader, background runtime, one-shot failure seam
- `services/api/app/routes/generate.py` - queued-first `/generate` background-task handoff
- `services/api/tests/conftest.py` - autouse no-op patch for the route-level background callable
- `services/api/tests/test_generation_runtime.py` - runtime contract for success, failure, and seam recovery

## Decisions Made

- Queue generation first, then hand off to `BackgroundTasks` after the rights gate.
- Load CosyVoice lazily from the approved worker root only when the default provider is needed.
- Use a one-shot `playwright-fail-once` seam gated by CI/Playwright env for live retry coverage.

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

- Phase 02-06 can now switch the browser spec to the live backend path and prove the playable clip against the real controlled audio URL.
- The runtime seam gives the live retry test a deterministic first failure without adding a second queueing layer.
- Background generation is still isolated behind the provider boundary, so later model swaps stay localized.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/02-consented-studio-generation/02-05-SUMMARY.md`.
- Task commits verified in git history: `3b0b58d` and `66f5e0b`.
- Automated verification passed:
  - `./.venv/bin/python -m pytest services/api/tests/test_generation_runtime.py services/api/tests/test_generation_jobs.py services/api/tests/test_generate_stub.py services/api/tests/test_rights_gate.py -q`
