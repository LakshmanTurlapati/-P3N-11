---
phase: 01-no-login-vertical-skeleton
plan: 01-01
subsystem: ui/testing
tags: [nextjs, playwright, typescript, pnpm, css]

# Dependency graph
requires: []
provides:
  - Direct-root no-login studio shell at `/`
  - Vesper Glass render-only voice seed with approval badge and boundary copy
  - Playwright root-route smoke harness
affects:
  - 01-02 voice profile schema and consent enforcement
  - 01-03 provider contracts and stub generation
  - Phase 2 studio generation

# Tech tracking
tech-stack:
  added:
    - next@16.2.9
    - react@19.2.7
    - react-dom@19.2.7
    - typescript@6.0.3
    - @playwright/test@1.61.1
    - pnpm@10.30.3
    - python3.11 -m venv + pip fallback for the Phase 1 Python scaffold
  patterns:
    - Next.js App Router root page renders the studio directly at `/`
    - Single-source voice registry seed for the bundled Vesper Glass display copy
    - Theatrical but restrained CSS token set with stage-like gradients and contrast
    - Playwright webServer bootstrap for browser smoke verification

key-files:
  created:
    - .gitignore
    - pyproject.toml
    - apps/web/package.json
    - apps/web/pnpm-lock.yaml
    - apps/web/tsconfig.json
    - apps/web/next-env.d.ts
    - apps/web/app/layout.tsx
    - apps/web/app/page.tsx
    - apps/web/app/globals.css
    - apps/web/lib/voice-registry.ts
    - apps/web/components/studio-shell.tsx
    - apps/web/playwright.config.ts
    - apps/web/tests/root-route.spec.ts
  modified:
    - .planning/STATE.md
    - .planning/config.json

key-decisions:
  - "Keep `/` as the direct studio entry point with no landing or login detour."
  - "Render Vesper Glass as an original theatrical voice with concise non-impersonation boundary copy."
  - "Use a render-only browser seed for Vesper Glass now and leave canonical rights ownership for the backend slice."
  - "Use a Playwright root-route smoke test as the regression guard for the first studio surface."
  - "Use `python3.11 -m venv` + `pip` as the approved Python fallback because `uv` is unavailable in this environment."

patterns-established:
  - "Root route owns the studio: `app/page.tsx` renders `StudioShell` directly."
  - "Voice identity lives in one render-only registry object to keep UI copy and safety boundary aligned."
  - "The UX surface stays minimal: selector, approval badge, profile card, and stub action."
  - "Browser verification runs headlessly against the Next dev server via Playwright."

requirements-completed: [GOV-03, STUD-01, STUD-02]

coverage:
  - id: D1
    description: "Direct-root studio shell at `/` with Vesper Glass, approval badge, and profile card visible on first paint."
    requirement: STUD-01
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/root-route.spec.ts#root route opens the studio directly"
        status: pass
      - kind: other
        ref: "pnpm --dir apps/web build"
        status: pass
    human_judgment: false
  - id: D2
    description: "Browser smoke harness that blocks regressions back to a landing detour or Phase 2 controls."
    verification:
      - kind: automated_ui
        ref: "apps/web/tests/root-route.spec.ts#root route opens the studio directly"
        status: pass
    human_judgment: false

metrics:
  duration: 19min
  completed: 2026-07-01
  status: complete
---

# Phase 1: No-Login Vertical Skeleton - 01-01 Summary

Direct-root studio shell with Vesper Glass and a Playwright smoke harness, keeping Phase 1 on the no-login surface and out of the later generation controls.

## Performance

- **Duration:** 19 min
- **Started:** 2026-07-01T00:24:21.510Z
- **Completed:** 2026-07-01T00:43:09Z
- **Tasks:** 3
- **Files modified:** 15

## Accomplishments
- Built the direct `/` studio surface in Next.js App Router and kept the page focused on Vesper Glass, the approval badge, and the voice profile card.
- Added a render-only Vesper Glass registry seed with original-voice boundary copy and restrained theatrical styling.
- Added a Playwright root-route smoke harness and verified it passes after fixing the web-server bootstrap and an ambiguous selector.

## Task Commits

Each task was committed atomically:

1. **Task 1: Approve the dependency version lines and Phase 1 Python toolchain before scaffold install** - user checkpoint approved, no commit
2. **Task 2: Scaffold the direct-root studio shell** - `b1d014a` (`feat`)
3. **Task 3: Add the browser smoke test harness** - `79b2a39` (`test`)
4. **Post-wave gate fix: Stabilize production smoke server** - `e6dc8c1` (`fix`)

**Plan metadata:** `3413782` (`docs`)

## Files Created/Modified
- `.gitignore` - repo hygiene for Node, Python, and Playwright artifacts
- `pyproject.toml` - pytest scaffold for later Python validation
- `apps/web/package.json` - Next.js app manifest and scripts
- `apps/web/pnpm-lock.yaml` - pinned web dependency resolution
- `apps/web/tsconfig.json` - TypeScript config aligned to Next.js
- `apps/web/next-env.d.ts` - Next-generated type import alignment
- `apps/web/app/layout.tsx` - root HTML wrapper and metadata
- `apps/web/app/page.tsx` - direct-root route that renders the studio
- `apps/web/app/globals.css` - theatrical studio styling and layout tokens
- `apps/web/lib/voice-registry.ts` - Vesper Glass render-only seed and boundary copy
- `apps/web/components/studio-shell.tsx` - voice-first studio shell
- `apps/web/playwright.config.ts` - browser smoke config and Next web server bootstrap
- `apps/web/tests/root-route.spec.ts` - root-route regression test
- `.planning/STATE.md` - execution state advanced by the phase
- `.planning/config.json` - orchestrator auto-chain update preserved

## Decisions Made
- Kept `/` as the studio entry point to match the no-login product shape.
- Chose Vesper Glass as an original theatrical profile with explicit non-impersonation language.
- Used a render-only voice seed on the browser surface so backend rights ownership can land in the next plan.
- Verified the first surface with Playwright instead of relying on manual inspection.
- Used `python3.11 -m venv` + `pip` as the approved fallback because `uv` is unavailable here.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed the Playwright web-server bootstrap command**
- **Found during:** Task 3 (Add the browser smoke test harness)
- **Issue:** `pnpm dev -- --hostname 127.0.0.1 --port 3000` was parsed as an invalid project directory, so Playwright could not start the app.
- **Fix:** Changed `apps/web/playwright.config.ts` to use `pnpm exec next dev --hostname 127.0.0.1 --port 3000`.
- **Files modified:** `apps/web/playwright.config.ts`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts`
- **Committed in:** `79b2a39` (Task 3 commit)

**2. [Rule 1 - Bug] Tightened the root-route smoke assertion to avoid strict-mode ambiguity**
- **Found during:** Task 3 (Add the browser smoke test harness)
- **Issue:** `getByText("Vesper Glass")` matched three elements and failed Playwright strict mode.
- **Fix:** Switched the assertion to `getByRole("heading", { name: "Vesper Glass" })`.
- **Files modified:** `apps/web/tests/root-route.spec.ts`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts`
- **Committed in:** `79b2a39` (Task 3 commit)

**Total deviations:** 2 auto-fixed (1 Rule 1, 1 Rule 3)
**Impact on plan:** No scope creep. Both fixes were necessary to get the planned browser smoke test to pass.

**3. [Post-wave gate] Stabilized the Playwright server mode**
- **Found during:** Wave 0 post-wave verification
- **Issue:** `next dev` rewrote `apps/web/next-env.d.ts` to a development route-types path, while `next build` rewrote it back to the production route-types path, leaving the tree dirty after verification.
- **Fix:** Changed the Playwright web server to run `next build` followed by `next start` so smoke tests verify the production build and keep `next-env.d.ts` stable.
- **Files modified:** `apps/web/playwright.config.ts`, `apps/web/next-env.d.ts`
- **Verification:** `pnpm --dir apps/web build`; `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts`
- **Committed in:** `e6dc8c1` (post-wave fix commit)

## Issues Encountered
- Playwright Chromium was not installed on the machine at first. I installed it with `pnpm --dir apps/web exec playwright install chromium` before rerunning the smoke test.
- Next.js updated `apps/web/next-env.d.ts` during the verified build to point at `.next/dev/types/routes.d.ts`; I kept that generated alignment in the Task 3 commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 1 now has a direct-root studio shell, a visible Vesper Glass profile, and a browser smoke harness that guards the entry route.
- Phase 1 plan 01-02 can build on the direct-root UI without revisiting routing or the initial browser scaffold.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/01-no-login-vertical-skeleton/01-01-SUMMARY.md`.
- Task commits verified in git history: `b1d014a` and `79b2a39`.
- Smoke test passed: `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts`.

---
*Phase: 01-no-login-vertical-skeleton*
*Completed: 2026-07-01*
