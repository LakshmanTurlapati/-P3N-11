---
phase: 04
slug: live-conversation-mode
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-12
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest 9.1.1` for API/worker tests and `@playwright/test 1.61.1` for browser verification |
| **Config file** | `pyproject.toml`, `apps/web/playwright.config.ts` |
| **Quick run command** | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -x` |
| **Full suite command** | `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && pnpm --dir apps/web exec playwright test` |
| **Estimated runtime** | ~120 seconds after conversation tests exist |

---

## Sampling Rate

- **After every task commit:** Run the smallest relevant conversation test slice for the changed layer.
- **After every plan wave:** Run `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && pnpm --dir apps/web exec playwright test`.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 120 seconds for focused checks, accepting longer full-suite runtime at wave boundaries.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-W0 | 01 | 1 | CONV-01 | T-04-SESSION | Session records are scoped to the current browser session | API/browser | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "session" -x && pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "start conversation"` | missing W0 | pending |
| 04-02-W0 | 02 | 2 | CONV-02 | T-04-AUDIO | Spoken turns produce controlled same-origin response audio | API/browser | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "response or tone" -x && pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "response"` | missing W0 | pending |
| 04-03-W0 | 02 | 2 | CONV-03 | T-04-PERSONA | Response provider rejects protected identity claims and real-performer framing | unit | `./.venv/bin/python -m pytest services/api/tests/test_conversation_provider.py -k "persona" -x` | missing W0 | pending |
| 04-04-W0 | 03 | 3 | CONV-04 | T-04-CANCEL | Interrupted turns cannot resurrect late completions and live mode returns to listening | unit/browser | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "cancel" -x && pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "interrupt"` | missing W0 | pending |
| 04-05-W0 | 03 | 3 | CONV-05 | T-04-TIMING | Server records stage timing metadata while UI shows only compact total latency | unit/browser | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "latency" -x && pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "latency"` | missing W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `services/api/tests/test_conversation_jobs.py` - session and turn state transitions, cancel state, and latency metadata.
- [ ] `services/api/tests/test_conversation_provider.py` - persona-boundary assertions and short-memory behavior.
- [ ] `services/speech-worker/tests/test_conversation_provider.py` - deterministic local responder and tone steering.
- [ ] `apps/web/tests/conversation-mode.spec.ts` - root-panel start, response playback, interrupt control, and latency chip.
- [ ] `services/api/tests/conftest.py` or a sibling fixture module - conversation session fixtures and deterministic provider stubs.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Best-effort VAD barge-in feel | CONV-04 | Automated tests can prove explicit interrupt and state recovery, but real barge-in timing depends on microphone and playback conditions | Start live mode, trigger playback, speak over the response, confirm either VAD barge-in interrupts reliably or the explicit Interrupt button remains the dependable fallback |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all missing requirement references.
- [ ] No watch-mode flags in verification commands.
- [ ] Feedback latency remains bounded by focused test slices.
- [ ] Set `nyquist_compliant: true` only after Wave 0 tests exist and pass.

**Approval:** pending
