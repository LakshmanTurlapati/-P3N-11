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
| **Framework** | pytest for API/provider tests; Playwright for web studio smoke tests |
| **Config file** | none yet - Wave 0 must create Python test config and `playwright.config.ts` |
| **Quick run command** | `pytest -q` plus targeted `pnpm playwright test --grep studio` after web smoke tests exist |
| **Full suite command** | `pytest` and `pnpm playwright test` |
| **Estimated runtime** | unknown until Wave 0 installs dependencies |

---

## Sampling Rate

- **After every task commit:** Run the smallest relevant automated command for the files changed.
- **After every plan wave:** Run `pytest` and `pnpm playwright test` once both harnesses exist.
- **Before `$gsd-verify-work`:** Full pytest and Playwright suites must be green.
- **Max feedback latency:** Establish during Wave 0; target under 60 seconds for quick checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01-01 | 0 | STUD-01 | - | No-login root route opens studio directly | browser smoke | `pnpm playwright test tests/web/studio.spec.ts --grep root-route` | no - Wave 0 | pending |
| 01-01-02 | 01-01 | 0 | STUD-02 | - | Bundled Vesper Glass voice is selectable and visible | browser smoke | `pnpm playwright test tests/web/studio.spec.ts --grep voice-selector` | no - Wave 0 | pending |
| 01-02-01 | 01-02 | 0 | GOV-01 | T-01 | Generation requires explicit rights metadata | unit/integration | `pytest tests/api/test_rights_gate.py -q` | no - Wave 0 | pending |
| 01-02-02 | 01-02 | 0 | GOV-02 | T-01 | Unapproved profiles cannot generate | unit/integration | `pytest tests/api/test_rights_gate.py -q` | no - Wave 0 | pending |
| 01-02-03 | 01-02 | 0 | GOV-03 | T-03 | Bundled profile avoids protected character or actor identity claims | fixture/snapshot | `pytest tests/fixtures/test_voice_profile.py -q` | no - Wave 0 | pending |
| 01-03-01 | 01-03 | 0 | PIPE-01 | T-04 | Provider interfaces exist for VAD, STT, TTS, and speech-to-speech candidates | unit | `pytest tests/providers/test_contracts.py -q` | no - Wave 0 | pending |

---

## Wave 0 Requirements

- [ ] Python test configuration, either `pytest.ini` or `pyproject.toml`.
- [ ] `tests/api/test_rights_gate.py` with blocked and approved stub-generation cases.
- [ ] `tests/fixtures/test_voice_profile.py` covering Vesper Glass rights metadata and persona boundary copy.
- [ ] `tests/providers/test_contracts.py` covering VAD, STT, TTS, and speech-to-speech provider interfaces.
- [ ] `playwright.config.ts` for web smoke tests.
- [ ] `tests/web/studio.spec.ts` covering the root studio route and bundled voice selector.
- [ ] Dependency installation path for `pytest` and `@playwright/test`; research noted both are missing locally.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Package version legitimacy checkpoints | STUD-01, PIPE-01 | Research flagged fresh `next`, `react`, `react-dom`, `fastapi`, `pydantic`, and `uvicorn` releases as suspicious due to recency | Before pinning exact patches, review source repo, registry metadata, and release notes; approve or choose older stable patches. |

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
