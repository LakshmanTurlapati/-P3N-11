---
phase: 01
slug: no-login-vertical-skeleton
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-30
---

# Phase 01 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` for API/provider tests via `uv run` when available; Playwright for web studio smoke tests |
| **Config file** | `pyproject.toml` for Python test config and `apps/web/playwright.config.ts` for browser smoke tests |
| **Quick run command** | `uv run pytest -q` plus targeted `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts` after web smoke tests exist |
| **Full suite command** | `uv run pytest` and `pnpm --dir apps/web exec playwright test` |
| **Estimated runtime** | unknown until Wave 0 installs dependencies |

---

## Sampling Rate

- **After every task commit:** Run the smallest relevant automated command for the files changed.
- **After every plan wave:** Run `uv run pytest` and `pnpm --dir apps/web exec playwright test` once both harnesses exist.
- **Before `$gsd-verify-work`:** Full pytest and Playwright suites must be green.
- **Max feedback latency:** Establish during Wave 0; target under 60 seconds for quick checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01-01 | 0 | STUD-01 | - | No-login root route opens studio directly | browser smoke | `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts` | no - Wave 0 | pending |
| 01-01-02 | 01-01 | 0 | STUD-02 | - | Bundled Vesper Glass voice is selectable and visible | browser smoke | `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts` | no - Wave 0 | pending |
| 01-02-01 | 01-02 | 0 | GOV-01 | T-01 | Generation requires explicit rights metadata | unit/integration | `uv run pytest services/api/tests/test_rights_gate.py -q` | no - Wave 0 | pending |
| 01-02-02 | 01-02 | 0 | GOV-02 | T-01 | Unapproved profiles cannot generate | unit/integration | `uv run pytest services/api/tests/test_rights_gate.py -q` | no - Wave 0 | pending |
| 01-02-03 | 01-02 | 0 | GOV-03 | T-03 | Bundled profile avoids protected character or actor identity claims | fixture/snapshot | `uv run pytest services/api/tests/test_voice_profile.py -q` | no - Wave 0 | pending |
| 01-03-01 | 01-03 | 0 | PIPE-01 | T-04 | Provider interfaces exist for VAD, STT, TTS, and speech-to-speech candidates | unit | `uv run pytest services/speech-worker/tests/test_provider_contracts.py -q` | no - Wave 0 | pending |
| 01-03-02 | 01-03 | 0 | PIPE-01 | T-04 | Rights-gated stub generation returns structured metadata only | unit/integration | `uv run pytest services/api/tests/test_generate_stub.py -q` | no - Wave 0 | pending |

---

## Wave 0 Requirements

- [ ] `pyproject.toml` test config and `apps/web/playwright.config.ts` for web smoke tests.
- [ ] `apps/web/tests/root-route.spec.ts` covering the root studio route and bundled voice selector.
- [ ] `services/api/tests/test_rights_gate.py`, `services/api/tests/test_voice_profile.py`, `services/api/tests/test_generate_stub.py`, and `services/speech-worker/tests/test_provider_contracts.py` covering the Phase 1 backend and provider checks.
- [ ] `uv` is the selected Phase 1 Python toolchain; use `python -m venv` + `pip` only if `uv` cannot be installed or run in Wave 0.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Package version legitimacy and Python toolchain checkpoint | STUD-01, PIPE-01 | Research flagged fresh `next`, `react`, `react-dom`, `fastapi`, `pydantic`, and `uvicorn` releases as suspicious due to recency, and the phase still needs one Python install path | Before pinning exact patches, review source repo, registry metadata, and release notes; confirm `uv` as the Phase 1 Python toolchain or approve `python -m venv` + `pip` only if `uv` cannot be installed. |

---

## Threat References

| Ref | Threat | Expected Mitigation |
|-----|--------|---------------------|
| T-01 | Direct API call bypasses disabled UI | Backend rights gate rejects unapproved or incomplete profiles. |
| T-03 | Persona drift into protected identity wording | Fixtures, UI copy, and tests use original Vesper Glass language only. |
| T-04 | Shared schema/provider drift between UI and API | Typed request/result models and explicit provider contracts define boundaries. |

---

## Validation Sign-Off

- [ ] All tasks have automated verification or explicit Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive implementation tasks without automated verification.
- [ ] Wave 0 covers all missing test-file references.
- [ ] No watch-mode flags in verification commands.
- [ ] Feedback latency target is measured after tooling is installed.
- [ ] `nyquist_compliant: true` is set only after Wave 0 validation infrastructure exists.

**Approval:** pending
