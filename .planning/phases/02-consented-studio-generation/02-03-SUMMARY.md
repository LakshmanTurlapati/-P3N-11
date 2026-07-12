---
phase: 02-consented-studio-generation
plan: 03
subsystem: api
tags: [fastapi, pydantic, sqlite, file-response, jobs, audio]

# Dependency graph
requires:
  - phase: 01-no-login-vertical-skeleton
    provides: server-owned rights gate, bundled voice registry, and generation route seam
  - phase: 02-consented-studio-generation/02-02
    provides: real provider adapter and normalized audio clips for the job-backed playback path
provides:
  - queued, running, succeeded, and failed generation job records
  - local filesystem object store-backed controlled playback URLs
  - retry lineage that preserves failed job metadata
affects:
  - 02-04 browser playback and retry
  - later studio job polling flows

# Tech tracking
tech-stack:
  added: [none]
  patterns:
    - sqlite-backed generation job repository with JSON-serialized job records
    - local filesystem object store for audio artifacts
    - controlled FileResponse audio serving from `/generations/{job_id}/audio`

key-files:
  created:
    - services/api/app/services/generation_jobs.py
    - services/api/tests/conftest.py
    - services/api/tests/test_generation_jobs.py
  modified:
    - services/api/app/schemas/generation.py
    - services/api/app/routes/generate.py
    - services/api/tests/test_generate_stub.py

key-decisions:
  - "Persist each generation as one job row with a single current attempt and create a new row for every retry."
  - "Keep playback constrained to the relative `/generations/{job_id}/audio` route and back it with a local filesystem object store."
  - "Preserve `GenerationResult` as a compatibility subclass while introducing `GenerationJobRecord` and `GenerationAttempt`."
  - "Update the legacy stub regression test because the required verify set still includes it after the route change."

patterns-established:
  - "Pattern 1: job state transitions are explicit (`queued`, `running`, `succeeded`, `failed`) and are persisted through sqlite."
  - "Pattern 2: successful playback is controlled by a relative audio URL, not raw filesystem paths."
  - "Pattern 3: retry preserves the failed job row and creates a brand new queued job from cached inputs."

requirements-completed: [GOV-04, STUD-05, PIPE-03]

coverage:
  - id: D1
    description: "Generation jobs persist queued/running/succeeded/failed state and preserve retry lineage."
    requirement: STUD-05
    verification:
      - kind: unit
        ref: "services/api/tests/test_generation_jobs.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Succeeded jobs expose a controlled playback URL and audio route backed by the local object store."
    requirement: PIPE-03
    verification:
      - kind: unit
        ref: "services/api/tests/test_generation_jobs.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Unapproved voices are still blocked before generation work begins."
    requirement: GOV-04
    verification:
      - kind: unit
        ref: "services/api/tests/test_generate_stub.py"
        status: pass
      - kind: unit
        ref: "services/api/tests/test_rights_gate.py"
        status: pass
    human_judgment: false

# Metrics
duration: 23min
completed: 2026-07-02
status: complete
---

# Phase 02: Consented Studio Generation Summary

Job-backed generation now persists queued, running, succeeded, and failed records, stores controlled audio under a local object store, and serves playback through status and audio routes with retry lineage intact.

## Performance
- **Duration:** 23 min
- **Started:** 2026-07-02T18:24:11Z
- **Completed:** 2026-07-02T18:47:13Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Added a job-oriented generation schema and sqlite-backed `GenerationJobService` that persist queued, running, succeeded, and failed states.
- Exposed `GET /generations/{job_id}` and `GET /generations/{job_id}/audio` so the API returns controlled playback URLs instead of raw audio paths or inline bytes.
- Preserved failed-job visibility and retry lineage by creating a brand new queued job from the cached request inputs.
- Rewrote the legacy stub regression test to the new queued-job contract while keeping the rights gate assertion intact.

## Task Commits
Each task was committed atomically:

1. **Task 1: Add failing API tests for job lifecycle, retry, and controlled playback** - `666f2bd` (`test`)
2. **Task 2: Implement the job schema, storage helper, and generation routes** - `62d70ff` (`feat`)

## Files Created/Modified
- `services/api/app/schemas/generation.py` - job record, attempt, playback URL, and compatibility model updates
- `services/api/app/services/generation_jobs.py` - sqlite-backed job service and local filesystem object store
- `services/api/app/routes/generate.py` - job creation, status, and controlled audio routes
- `services/api/tests/conftest.py` - shared API fixtures and service patching for the job tests
- `services/api/tests/test_generation_jobs.py` - job lifecycle, retry, and playback contract coverage
- `services/api/tests/test_generate_stub.py` - legacy stub test rewritten for the job-backed queued response

## Decisions Made
- Persist each generation as one job row with a single current attempt and create a new row for every retry.
- Keep playback constrained to the relative `/generations/{job_id}/audio` route and back it with a local filesystem object store.
- Preserve `GenerationResult` as a compatibility subclass while introducing `GenerationJobRecord` and `GenerationAttempt`.
- Update the legacy stub regression test because the required verify set still includes it after the route change.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Rewrote the legacy stub regression test to the queued-job contract**
- **Found during:** Task 2 (implementation)
- **Issue:** `services/api/tests/test_generate_stub.py` still asserted the Phase 1 metadata-only payload, which would fail the task 2 verification set once `/generate` became job-backed.
- **Fix:** Updated the test to assert the queued job record, retry lineage fields, and controlled playback metadata.
- **Files modified:** `services/api/tests/test_generate_stub.py`
- **Verification:** `./.venv/bin/python -m pytest services/api/tests/test_generation_jobs.py services/api/tests/test_generate_stub.py services/api/tests/test_rights_gate.py services/api/tests/test_voice_profile.py -q`
- **Committed in:** `62d70ff`

**Total deviations:** 1 auto-fixed (Rule 3)
**Impact on plan:** Necessary to keep the required verification suite aligned with the new API contract. No scope creep beyond the job-backed generation slice.

## Issues Encountered
- The legacy `test_generate_stub.py` contract still targeted the Phase 1 metadata-only response and had to be rewritten to the queued-job shape as part of the implementation task.
- The new storage helper uses a local sqlite database and filesystem object store under a configurable storage root, which is intentional for this phase and keeps the API path-safe.

## User Setup Required
None. The existing Python 3.11 virtualenv and pytest environment were sufficient.

## Next Phase Readiness
- The API can create queued jobs, progress them through running and succeeded or failed states, and serve controlled audio through a dedicated route.
- Retry lineage is preserved without mutating failed jobs, so Phase 02-04 can wire browser playback and session-scoped retry UI onto these endpoints.

## Self-Check: PASSED
- Summary file exists at `.planning/phases/02-consented-studio-generation/02-03-SUMMARY.md`.
- Task commits verified in git history: `666f2bd` and `62d70ff`.
- Automated verification passed:
  - `./.venv/bin/python -m pytest services/api/tests/test_generation_jobs.py services/api/tests/test_generate_stub.py services/api/tests/test_rights_gate.py services/api/tests/test_voice_profile.py -q`

---
*Phase: 02-consented-studio-generation*
*Completed: 2026-07-02*
