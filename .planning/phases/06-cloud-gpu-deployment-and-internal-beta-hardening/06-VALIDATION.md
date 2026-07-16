---
phase: 06
slug: cloud-gpu-deployment-and-internal-beta-hardening
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-15
---

# Phase 06 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest 9.1.1` for API/worker tests; `Playwright 1.61.1` for browser smoke tests |
| **Config file** | `pyproject.toml`; `apps/web/playwright.config.ts` |
| **Quick run command** | `pytest services/api/tests/test_generation_jobs.py services/api/tests/test_audio_turn_jobs.py services/api/tests/test_conversation_jobs.py services/api/tests/test_generation_runtime.py -x` |
| **Full suite command** | `pytest services/api/tests -x && pytest services/speech-worker/tests -x && pnpm --dir apps/web test` |
| **Estimated runtime** | ~120 seconds without Compose; Compose smoke depends on host Docker/GPU availability |

---

## Sampling Rate

- **After every task commit:** Run `pytest services/api/tests/test_generation_jobs.py services/api/tests/test_audio_turn_jobs.py services/api/tests/test_conversation_jobs.py services/api/tests/test_generation_runtime.py -x`
- **After every plan wave:** Run `pytest services/api/tests -x && pytest services/speech-worker/tests -x && pnpm --dir apps/web test`
- **Before `$gsd-verify-work`:** Full suite plus available Compose config checks must be green
- **Max feedback latency:** 180 seconds for non-Compose automated checks

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-W0 | 01 | 1 | DEP-01 | T-06-01 / T-06-04 | Compose keeps browser same-origin and separates web, API, and worker services | config / smoke | `docker compose config` | missing W0 | pending |
| 06-02-W0 | 02 | 1 | DEP-02 | T-06-02 | API and worker share mounted storage without exposing raw file paths to the browser | unit / integration | `pytest services/api/tests/test_generation_jobs.py services/api/tests/test_audio_turn_jobs.py services/api/tests/test_conversation_jobs.py -x` | partial | pending |
| 06-03-W0 | 02 | 1 | DEP-03 | T-06-03 | Readiness verifies storage, DB, voice registry, and worker config without model warmup | integration | `pytest services/api/tests/test_health.py services/speech-worker/tests/test_health.py -x` | missing W0 | pending |
| 06-04-W0 | 03 | 3 | DEP-04 | T-06-05 | Logs include correlation IDs and safe stage metadata, not raw audio, prompt, or transcript payloads | unit | `pytest services/api/tests/test_logging.py -x` | missing W0 | pending |
| 06-05-W0 | 03 | 2 | DEP-05 | T-06-06 | Runbook distinguishes fixture validation from GPU-host validation and preserves rights/persona boundaries | docs / manual | `rg -n "fixture|GPU|Docker Compose|health|logs|rights|persona" docs .env.example compose.yaml` | missing W0 | pending |

---

## Wave 0 Requirements

- [ ] `compose.yaml` or an equivalent Compose entrypoint defines separate `web`, `api`, and `speech-worker` services.
- [ ] `.env.example` documents the service URLs, storage root, worker URL/runtime mode, and fixture/GPU mode knobs used by Compose and local commands.
- [ ] `services/api/tests/test_health.py` covers dependency-aware API readiness.
- [ ] `services/speech-worker/tests/test_health.py` covers worker readiness without GPU/model warmup.
- [ ] `services/api/tests/test_logging.py` covers log correlation IDs, stage timing fields, and payload redaction.
- [ ] `docs/deployment/internal-beta.md` or an equivalent runbook covers Mac-to-GPU-host setup and verification.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GPU-host Compose startup | DEP-01, DEP-05 | This workstation does not currently provide Docker/Compose/GPU runtime for a real host smoke test | On the rented GPU host, install Docker/Compose, copy the repo/env file, run `docker compose config`, run `docker compose up -d`, and verify each documented health URL |
| Model/runtime compatibility | DEP-05 | Phase 5 identified model/runtime license and package constraints that may vary by selected GPU image | Follow the runbook's Python/CUDA/PyTorch/model-weight checklist and record any provider-specific blocker before beta use |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or explicit Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification.
- [ ] Wave 0 covers all missing health, logging, Compose, and docs references.
- [ ] No watch-mode flags are used in verification commands.
- [ ] Non-Compose feedback latency is under 180 seconds.
- [ ] `nyquist_compliant: true` is set in frontmatter after Wave 0 artifacts exist and pass.

**Approval:** pending
