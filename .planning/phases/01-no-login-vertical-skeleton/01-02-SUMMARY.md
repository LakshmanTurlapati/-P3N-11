---
phase: 01-no-login-vertical-skeleton
plan: 01-02
subsystem: api/voice-rights
tags: [fastapi, pydantic, rights-gate, voice-registry, pytest]

# Dependency graph
requires:
  - 01-01
provides:
  - Server-owned Vesper Glass voice profile
  - Strict voice profile schema with rights and style metadata
  - Rights gate for approved generation paths
  - Voice registry routes mounted in the FastAPI app
affects:
  - 01-03 rights-gated stub generation
  - Future voice profile registry and generation provider adapters

# Tech tracking
tech-stack:
  added:
    - fastapi==0.138.2
    - pydantic==2.13.4
    - pytest==9.1.1
  patterns:
    - Pydantic v2 models with `extra="forbid"` for rights metadata
    - Server-owned bundled voice registry record
    - Backend rights gate raises one exact blocked-path message
    - FastAPI routers mounted from `services/api/app/main.py`

key-files:
  created:
    - conftest.py
    - services/__init__.py
    - services/api/__init__.py
    - services/api/app/__init__.py
    - services/api/app/schemas/__init__.py
    - services/api/app/schemas/voice_profile.py
    - services/api/app/voice_registry/__init__.py
    - services/api/app/voice_registry/bundled_voice.py
    - services/api/app/main.py
    - services/api/app/routes/__init__.py
    - services/api/app/routes/voices.py
    - services/api/app/services/__init__.py
    - services/api/app/services/rights_gate.py
    - services/api/tests/test_voice_profile.py
    - services/api/tests/test_rights_gate.py
  modified:
    - pyproject.toml
    - .gitignore

key-decisions:
  - "Keep Vesper Glass server-owned in the backend registry while the browser seed remains render-only."
  - "Require rights status, approval state, source notes, consent notes, intended use, boundary note, style summary, traits, and prohibited associations before generation is allowed."
  - "Use one exact blocked-path message for missing or unapproved rights metadata: `Generation blocked: this voice profile is missing approved rights metadata.`"
  - "Declare FastAPI, Pydantic, and pytest in `pyproject.toml` so backend verification is reproducible under the approved Python 3.11 fallback."

patterns-established:
  - "Voice profile schemas live under `services/api/app/schemas/`."
  - "Bundled voice data lives under `services/api/app/voice_registry/` and satisfies the same Pydantic contract exposed by routes."
  - "Server-side authorization for generation starts with `ensure_voice_allowed`, not client UI state."

requirements-completed: [GOV-01, GOV-02, GOV-03]

coverage:
  - id: D3
    description: "Bundled Vesper Glass profile includes rights and style metadata and remains inside the original theatrical boundary."
    requirement: GOV-01
    verification:
      - kind: automated
        ref: "services/api/tests/test_voice_profile.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Backend rights gate blocks missing or unapproved metadata with the exact Phase 1 safety message."
    requirement: GOV-02
    verification:
      - kind: automated
        ref: "services/api/tests/test_rights_gate.py"
        status: pass
    human_judgment: false
  - id: D5
    description: "Server-owned voice registry route exposes the bundled Vesper Glass profile."
    requirement: GOV-03
    verification:
      - kind: automated
        ref: "services/api/tests/test_rights_gate.py"
        status: pass
    human_judgment: false

metrics:
  duration: 21min
  completed: 2026-07-01
  status: complete
---

# Phase 1: No-Login Vertical Skeleton - 01-02 Summary

Server-owned Vesper Glass voice profile, strict rights/style schema, voice registry route, and backend rights gate are implemented for the consent-safe generation boundary.

## Performance

- **Duration:** 21 min
- **Completed:** 2026-07-01
- **Tasks:** 2
- **Files modified:** 17

## Accomplishments

- Added a strict Pydantic voice profile contract with required rights metadata and original theatrical style fields.
- Added the bundled Vesper Glass server registry record with explicit non-impersonation boundaries and prohibited associations.
- Added a FastAPI voice registry route for listing and fetching bundled voices.
- Added the backend rights gate that blocks incomplete or unapproved profiles with the exact Phase 1 safety message.
- Declared backend dependencies and package discovery so tests run from the approved Python 3.11 venv fallback.

## Task Commits

1. **Task 1: Define the Vesper Glass voice profile contract** - `3b45de9` (`feat`)
2. **Task 2: Add the server rights gate and voice registry route** - `4bfbf09` (`feat`)
3. **Post-task fix: Declare backend test dependencies** - `4cea135` (`fix`)

## Files Created/Modified

- `conftest.py` - root path setup for service tests
- `services/api/app/schemas/voice_profile.py` - `VoiceProfile`, `VoiceRights`, and `VoiceStyle`
- `services/api/app/voice_registry/bundled_voice.py` - bundled `VESPER_GLASS_PROFILE`
- `services/api/app/services/rights_gate.py` - `ensure_voice_allowed`, metadata check, and blocked-path message
- `services/api/app/routes/voices.py` - voice registry list/get route handlers
- `services/api/app/main.py` - FastAPI app mounting the voice registry router
- `services/api/tests/test_voice_profile.py` - schema and persona-boundary tests
- `services/api/tests/test_rights_gate.py` - route and rights-gate tests
- `pyproject.toml` - backend dependency declarations and service package discovery
- `.gitignore` - generated Python package metadata ignore

## Decisions Made

- The server registry is authoritative for rights metadata; the UI seed remains display-only.
- Vesper Glass uses original theatrical language and forbids protected character voices or unlicensed performer likenesses.
- Missing metadata and unapproved profiles use the same blocked-path message to avoid leaking policy internals.
- The Python fallback environment is reproducible through `python3.11 -m venv .venv` and `pip install -e '.[dev]'`.

## Deviations from Plan

### Manual Closeout Recovery

- **Found during:** Executor closeout
- **Issue:** The executor committed implementation tasks but stalled before writing `01-02-SUMMARY.md`.
- **Fix:** Orchestrator inspected the committed changes, verified tests, wrote this summary, and committed summary/tracking manually rather than redispatching duplicate implementation work.
- **Impact:** No implementation scope change.

### Dependency Declaration Fix

- **Found during:** Verification
- **Issue:** `pytest`, FastAPI, and Pydantic were not declared or installed in the project environment, so the raw test command was not reproducible.
- **Fix:** Added FastAPI `0.138.2`, Pydantic `2.13.4`, pytest `9.1.1`, and `services*` package discovery to `pyproject.toml`; ignored generated `*.egg-info/`.
- **Verification:** `.venv/bin/python -m pytest services/api/tests/test_voice_profile.py -q`; `.venv/bin/python -m pytest services/api/tests/test_rights_gate.py -q`
- **Committed in:** `4cea135`

## Issues Encountered

- Raw `pytest` was not available on PATH. The approved Python 3.11 fallback venv was created and used for verification.
- Editable install initially failed because setuptools discovered both `apps` and `services` as top-level packages. Package discovery is now constrained to `services*`.

## User Setup Required

- For backend tests in this workspace, use:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## Next Phase Readiness

- Plan `01-03` can reuse `VoiceProfile`, `VESPER_GLASS_PROFILE`, and `ensure_voice_allowed` to protect the stub generation route.
- Backend tests now have declared dependencies for the generation schema and route work.

## Self-Check: PASSED

- `01-02-SUMMARY.md` exists.
- Implementation commits are present: `3b45de9`, `4bfbf09`, `4cea135`.
- `.venv/bin/python -m pytest services/api/tests/test_voice_profile.py -q` passed.
- `.venv/bin/python -m pytest services/api/tests/test_rights_gate.py -q` passed.

---
*Phase: 01-no-login-vertical-skeleton*
*Completed: 2026-07-01*
