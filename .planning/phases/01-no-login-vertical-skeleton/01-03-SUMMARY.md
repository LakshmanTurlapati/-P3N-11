---
phase: 01-no-login-vertical-skeleton
plan: 01-03
subsystem: api/web/contracts
tags: [fastapi, pydantic, playwright, typescript, python, protocols]
requires:
  - 01-02
provides:
  - Generation request, result, timing, and provider-trace models
  - Swappable VAD, STT, TTS, and speech-to-speech provider protocols
  - Rights-gated metadata-only stub generation route and service
  - StudioShell generation trigger and structured metadata result card
affects:
  - 02-01 studio text input and tone preset UX
  - 02-02 real TTS provider adapter work
  - 02-03 playback, retry, and audio storage behavior
tech-stack:
  added:
    - httpx2==2.5.0
    - uvicorn==0.49.0
    - FastAPI TestClient support for API regression tests
    - Next.js API rewrites via `API_BASE_URL`
  patterns:
    - Pydantic v2 strict models with `extra="forbid"` for generation contracts
    - Python `Protocol` provider boundary for VAD, STT, TTS, and speech-to-speech adapters
    - Metadata-only stub responses with compact trace and timing fields
    - Playwright starts both FastAPI and Next.js so the studio-to-API browser contract uses the real metadata stub
key-files:
  created:
    - services/api/app/schemas/generation.py
    - services/api/app/routes/generate.py
    - services/api/app/services/stub_generation.py
    - services/api/tests/test_generate_stub.py
    - services/speech-worker/providers/__init__.py
    - services/speech-worker/providers/contracts.py
    - services/speech-worker/tests/conftest.py
    - services/speech-worker/tests/test_provider_contracts.py
    - apps/web/next.config.ts
    - apps/web/tests/studio-generation.spec.ts
  modified:
    - services/api/app/main.py
    - pyproject.toml
    - apps/web/components/studio-shell.tsx
    - apps/web/app/globals.css
    - apps/web/playwright.config.ts
decisions:
  - "Keep Phase 1 generation metadata-only with no audio payload or playback surface."
  - "Route generation through the server-owned rights gate before assembling the stub result."
  - "Route `/generate` and `/voices` from Next.js to the FastAPI control plane through `API_BASE_URL` so local browser usage exercises the real metadata stub."
  - "Add `httpx2` and `uvicorn` to the dev extras so API regression tests and local Playwright web servers run under the approved Python venv."
metrics:
  duration: 6min
  completed: 2026-07-01
  status: complete
status: complete
---

# Phase 01 Plan 01-03: Metadata-Only Generation Contract Summary

Metadata-only stub generation is now wired end to end: the API owns the rights-gated route and structured response model, the speech-worker boundary has swappable provider protocols, and the studio button renders a result card instead of audio playback.

## Performance

- **Duration:** 6 min
- **Started:** 2026-07-01T01:28:33Z
- **Completed:** 2026-07-01T01:34:27Z
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments

- Added strict generation contracts for request, rights-check, metadata, provider trace, and timing data.
- Defined provider protocols for VAD, STT, TTS, and speech-to-speech so later model swaps stay behind a narrow boundary.
- Implemented a metadata-only stub generation service and FastAPI route that enforce the server rights gate before assembling the response.
- Added a Next.js rewrite for `/generate` and `/voices` so the browser can reach the FastAPI control plane locally.
- Wired StudioShell to POST the selected Vesper Glass voice id to `/generate` and render the structured metadata result card.
- Kept the Phase 1 surface free of audio playback, mic input, tone presets, retry controls, and live conversation UI.
- Preserved the root-route smoke test while adding the new studio-generation browser regression.

## Task Commits

Each task was committed atomically, with TDD red/green commits for Task 3:

1. **Task 1: Define generation contracts and provider interfaces** - `e6d1613` (`feat`)
2. **Task 2: Add rights-gated metadata-only stub generation route** - `1ac1586` (`feat`)
3. **Task 3 RED: Add failing test for studio generation result card** - `85fdd9a` (`test`)
4. **Task 3 GREEN: Wire StudioShell to generation route and render result card** - `9769e8b` (`feat`)

## Files Created/Modified

- `services/api/app/schemas/generation.py` - strict generation request/result/timing models
- `services/api/app/routes/generate.py` - rights-gated metadata-only generation endpoint
- `services/api/app/services/stub_generation.py` - metadata-only stub result builder
- `services/api/app/main.py` - FastAPI app mounting for the generation route
- `services/api/tests/test_generate_stub.py` - approved and blocked API regression coverage
- `services/speech-worker/providers/contracts.py` - provider protocols and audio-shape dataclasses
- `services/speech-worker/providers/__init__.py` - provider export surface
- `services/speech-worker/tests/conftest.py` - import bootstrap for the hyphenated worker path
- `services/speech-worker/tests/test_provider_contracts.py` - provider contract shape coverage
- `apps/web/next.config.ts` - API rewrite bridge to the FastAPI control plane
- `apps/web/components/studio-shell.tsx` - generation trigger, loading state, result card
- `apps/web/app/globals.css` - result-card and state styling
- `apps/web/playwright.config.ts` - starts FastAPI and Next.js for browser verification
- `apps/web/tests/studio-generation.spec.ts` - browser regression for the real API-backed generation contract
- `pyproject.toml` - added `httpx2` and `uvicorn` dev dependencies

## Decisions Made

- Keep Phase 1 generation metadata-only, with no audio payload or playback surface.
- Keep rights enforcement on the server before any stub result is assembled.
- Keep the studio browser test contract explicit by letting Playwright start the API and web servers, then asserting the result-card content through the real `/generate` path.
- Add `httpx2` and `uvicorn` to the dev extras so the API regression tests and local API server remain runnable in the approved Python venv.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added `httpx2` so FastAPI TestClient could run**
- **Found during:** Task 2 verification
- **Issue:** `fastapi.testclient` required `httpx2`, so API test collection failed before the route assertions ran.
- **Fix:** Added `httpx2==2.5.0` to `pyproject.toml` and reinstalled the editable environment with `pip install -e '.[dev]'`.
- **Files modified:** `pyproject.toml`
- **Commit:** `1ac1586`

**2. [Rule 3 - Blocking] Added a local API rewrite and API web server for the browser test**
- **Found during:** Final local run verification
- **Issue:** `StudioShell` posted to `/generate`, but the Next.js app did not proxy that route to the FastAPI control plane outside the mocked browser test.
- **Fix:** Added `apps/web/next.config.ts` with `/generate` and `/voices` rewrites through `API_BASE_URL`, added `uvicorn==0.49.0`, and changed Playwright to start both FastAPI and Next.js.
- **Files modified:** `apps/web/next.config.ts`, `apps/web/playwright.config.ts`, `apps/web/tests/studio-generation.spec.ts`, `pyproject.toml`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts`

**2. [Rule 1 - Bug] Tightened generation timing validation**
- **Found during:** Task 2 wiring
- **Issue:** The generation timing model needed a direct `ended_at >= started_at` check to keep the result schema honest.
- **Fix:** Replaced the fragile validator shape with a direct model-level check on the timing model.
- **Files modified:** `services/api/app/schemas/generation.py`
- **Commit:** `1ac1586`

## Issues Encountered

- Running browser tests sequentially avoids competing Next.js production builds. The Playwright config now starts FastAPI and Next.js for each browser contract test.

## User Setup Required

None. The existing `.venv` plus the added `httpx2` and `uvicorn` dev dependencies are enough to run the verification commands used in this plan.

## Next Phase Readiness

- The API now exposes a structured, metadata-only generation result that Phase 2 can replace with a real provider.
- The studio shell has the trigger/result-card pattern that Phase 2 can extend with text input and playback once the real audio path lands.
- The speech-worker boundary is now explicitly typed, so later provider swaps can stay isolated from the UI contract.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/01-no-login-vertical-skeleton/01-03-SUMMARY.md`.
- Task commits verified in git history: `e6d1613`, `1ac1586`, `85fdd9a`, and `9769e8b`.
- Automated verification passed:
  - `.venv/bin/python -m pytest services/speech-worker/tests/test_provider_contracts.py -q`
  - `.venv/bin/python -m pytest services/api/tests/test_generate_stub.py -q`
  - `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts`
  - `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts`
