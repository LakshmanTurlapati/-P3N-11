---
phase: 02-consented-studio-generation
plan: 01
subsystem: ui/api/contracts
tags: [nextjs, playwright, fastapi, pydantic, typescript, css, jobs, enums]

# Dependency graph
requires:
  - phase: 01-no-login-vertical-skeleton
    provides: phase-1 rights-gated studio shell, metadata-only generation seam, and browser rewrite plumbing
provides:
  - queued prototype generation contract with fixed tone presets
  - text-entry studio surface with accessible job and rights status badges
  - browser regression coverage for text, tone, and blocked-rights behavior
affects:
  - 02-02 real provider integration
  - 02-03 job persistence and controlled playback
  - 02-04 browser playback and retry

# Tech tracking
tech-stack:
  added:
    - none
  patterns:
    - strict Pydantic request/result models with fixed enums and `extra="forbid"`
    - form-driven studio shell with tone chips and job-state badges
    - queued prototype baseline labeling for pre-final voice output

key-files:
  created: []
  modified:
    - apps/web/components/studio-shell.tsx
    - apps/web/app/globals.css
    - apps/web/tests/studio-generation.spec.ts
    - apps/web/tests/root-route.spec.ts
    - services/api/app/schemas/generation.py
    - services/api/app/routes/generate.py
    - services/api/app/services/stub_generation.py
    - services/api/tests/test_generate_stub.py

key-decisions:
  - "Use lowercase machine values for the three tone presets and render capitalized labels in the browser."
  - "Return a queued prototype baseline job from the Phase 1 stub instead of the old metadata-only card."
  - "Update the stale root-route smoke test so the repo matches the new Phase 2 studio surface."

patterns-established:
  - "Pattern 1: Fixed tone chips map cleanly to a strict request enum and no sliders are exposed."
  - "Pattern 2: The browser contract treats the generation response as a queued job with accessible status badges."
  - "Pattern 3: The backend keeps the exact rights gate ahead of any generation work."

requirements-completed: [GOV-04, STUD-03, STUD-04, STUD-05]

coverage:
  - id: D1
    description: "Browser contract accepts text and fixed tone presets, then surfaces queued-job and blocked-rights behavior."
    requirement: STUD-05
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/studio-generation.spec.ts"
        status: pass
    human_judgment: false
  - id: D2
    description: "API contract accepts text plus a fixed tone preset and returns a queued prototype job while preserving the exact rights gate."
    requirement: GOV-04
    verification:
      - kind: unit
        ref: "services/api/tests/test_generate_stub.py"
        status: pass
      - kind: unit
        ref: "services/api/tests/test_rights_gate.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Root studio renders text input, tone presets, and the queued-job surface without playback, mic, upload, or live-conversation controls."
    requirement: STUD-03
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/root-route.spec.ts"
        status: pass
      - kind: automated_ui
        ref: "apps/web/tests/studio-generation.spec.ts"
        status: pass
    human_judgment: false

# Metrics
duration: 1h 20m
completed: 2026-07-02
status: complete
---

# Phase 2: Consented Studio Generation Summary

Text-and-tone studio generation now posts queued prototype jobs with fixed Measured/Cutting/Grandiose presets, and the root studio shows an accessible queued-job surface without adding playback or live conversation controls.

## Performance

- **Duration:** 1h 20m
- **Started:** 2026-07-02T15:06:56Z
- **Completed:** 2026-07-02
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Replaced the Phase 1 metadata-only browser contract with a text-and-tone generation flow that asserts queued-job state and the exact blocked-rights message.
- Extended the generation schema and stub response to accept `text` plus a fixed tone preset and return a queued prototype baseline job with timing, trace, and rights metadata.
- Rebuilt the studio shell around a textarea, three fixed tone chips, a generation-status badge, and a job card that stays playback-free.
- Updated the root-route smoke test so it matches the new Phase 2 controls instead of the old no-text metadata-only shell.

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite the studio browser spec around text, preset, and queued-job state** - `b406fea` (`test`)
2. **Task 2: Extend the generation contract and stub response to carry job metadata** - `3c5b60b` (`feat`)
3. **Task 3: Rebuild the studio shell for text entry and tone presets** - `e3c7f47` (`feat`)

## Files Created/Modified

- `apps/web/components/studio-shell.tsx` - Phase 2 studio form, tone chips, status badge, and queued-job card
- `apps/web/app/globals.css` - textarea, tone-chip, generation-status, and responsive form/card styling
- `apps/web/tests/studio-generation.spec.ts` - browser contract for text, tone, queued jobs, and blocked-rights handling
- `apps/web/tests/root-route.spec.ts` - updated smoke test for the new studio controls
- `services/api/app/schemas/generation.py` - fixed tone and job-status enums plus job-shaped generation result schema
- `services/api/app/routes/generate.py` - passes the text/tone request into the stub builder
- `services/api/app/services/stub_generation.py` - queued prototype baseline stub response builder
- `services/api/tests/test_generate_stub.py` - API regression coverage for the queued prototype job and exact rights gate

## Decisions Made

- Use lowercase tone preset values on the wire and capitalize them only in the browser.
- Keep the first Phase 2 response as a queued prototype baseline job rather than pretending the final voice is ready.
- Update the root-route smoke test now so the repo does not carry a guaranteed stale failure after the UI rewrite.
- Keep the blocked-rights browser assertion by stubbing the 403 response in the Playwright test while the API test continues to verify the real rights gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Routed the new request fields through `/generate`**
- **Found during:** Task 2 (backend contract)
- **Issue:** The existing route still called the stub with only `voice_id`, which would have discarded the new text/tone request shape.
- **Fix:** Updated `services/api/app/routes/generate.py` to pass the full request into the queued prototype stub builder.
- **Files modified:** `services/api/app/routes/generate.py`, `services/api/app/schemas/generation.py`, `services/api/app/services/stub_generation.py`, `services/api/tests/test_generate_stub.py`
- **Verification:** `./.venv/bin/python -m pytest services/api/tests/test_generate_stub.py services/api/tests/test_rights_gate.py -q`
- **Committed in:** `3c5b60b`

**2. [Rule 1 - Bug] Updated the stale root-route smoke test to the Phase 2 studio surface**
- **Found during:** Task 3 (UI rewrite)
- **Issue:** The existing smoke test still asserted the old metadata-only shell and the `Generate stub reading` button.
- **Fix:** Rewrote `apps/web/tests/root-route.spec.ts` to assert the textarea, tone preset group, generation button, and the continued absence of playback/live-conversation controls.
- **Files modified:** `apps/web/tests/root-route.spec.ts`
- **Verification:** `CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts tests/root-route.spec.ts`
- **Committed in:** `e3c7f47`

**Total deviations:** 2 auto-fixed (Rule 1)
**Impact on plan:** Both changes were necessary to keep the new studio contract coherent end-to-end. No scope creep beyond the text-and-tone slice.

## Issues Encountered

- Playwright initially reused a stale Next.js/FastAPI pair from an earlier run. Restarting those processes and rerunning with `CI=1` forced the browser suite to exercise the updated code.

## User Setup Required

None. The existing local Python venv and web dependencies were sufficient for the verification commands in this plan.

## Next Phase Readiness

- The root studio now accepts text and one of the three fixed tone presets.
- The backend returns a queued prototype job with the exact rights gate intact.
- Phase 02-02 can replace the stub provider without changing the studio shape or request contract.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/02-consented-studio-generation/02-01-SUMMARY.md`.
- Task commits verified in git history: `b406fea`, `3c5b60b`, and `e3c7f47`.
- Automated verification passed:
  - `./.venv/bin/python -m pytest services/api/tests/test_generate_stub.py services/api/tests/test_rights_gate.py -q`
  - `CI=1 pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts tests/root-route.spec.ts`
