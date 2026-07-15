# Phase 6: Cloud GPU Deployment and Internal Beta Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-15T03:31:08Z
**Phase:** 6-cloud-gpu-deployment-and-internal-beta-hardening
**Areas discussed:** Gray area selection, Service orchestration, Worker boundary, Audio persistence, Health and readiness, Observability, Setup documentation

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| All core areas | Cover service boundaries, storage, health/observability, and setup docs in sequence. | ✓ |
| Service split | Focus first on how web, API, and speech-worker should run separately. | |
| Storage health | Focus first on durable audio persistence, readiness checks, and logging. | |

**User's choice:** 1 — All core areas.
**Notes:** The user chose to cover the full Phase 6 deployment/hardening decision set.

---

## Service Orchestration

| Option | Description | Selected |
|--------|-------------|----------|
| Docker Compose first | One command starts web, API, and speech-worker-like runtime with shared env/storage; best fit for rented GPU handoff docs. | ✓ |
| Separate local commands | Document `pnpm dev`, `uvicorn`, and worker setup separately; lighter but easier to drift. | |
| Cloud deployment files first | Prioritize production host config over local orchestration; useful if the target GPU platform is already known. | |

**User's choice:** 1 — Docker Compose first.
**Notes:** Compose should be the internal beta handoff contract, while local commands remain available.

---

## Worker Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Configurable external worker boundary | Add compose/services/env/docs so the worker is a separately runnable service, while preserving local fixture/in-process fallbacks for tests. | ✓ |
| Hard worker separation now | API must never run speech work in-process; higher fidelity but more disruptive. | |
| Documented separation only | Keep code mostly as-is and document how services would split later; lower risk but weaker proof. | |

**User's choice:** 1 — Configurable external worker boundary.
**Notes:** The user wants a real separation path without destabilizing local deterministic tests.

---

## Audio Persistence

| Option | Description | Selected |
|--------|-------------|----------|
| Filesystem volume now, S3-compatible interface next | Use mounted storage in Compose for the internal beta, design the abstraction/env names so S3-compatible storage can replace it later. | ✓ |
| S3-compatible storage now | Add MinIO/S3-style config immediately; stronger cloud parity but more setup surface. | |
| SQLite/filesystem only | Keep the existing local object-store shape and just make paths configurable; simplest but less cloud-ready. | |

**User's choice:** 1 — Filesystem volume now, S3-compatible interface next.
**Notes:** The first beta should use mounted persistence while keeping object storage migration open.

---

## Health And Readiness

| Option | Description | Selected |
|--------|-------------|----------|
| Dependency-aware readiness | API checks writable storage, SQLite/job DB access, voice registry, and worker runtime config; worker checks provider/runtime env and storage access. | ✓ |
| Basic liveness only | `/healthz` returns OK for each process; fastest but weak for deployment confidence. | |
| Deep model warmup | Readiness loads or warms speech models; strong signal but expensive and risky for startup. | |

**User's choice:** 1 — Dependency-aware readiness.
**Notes:** Readiness should catch deployment misconfiguration without making heavy model warmup mandatory.

---

## Observability

| Option | Description | Selected |
|--------|-------------|----------|
| Structured JSON logs plus request/job IDs | Log lifecycle events, failures, provider names, stage timings, and storage paths safely without audio/text payloads. | ✓ |
| Human-readable console logs | Simpler logs for local debugging, less useful for deployed aggregation. | |
| Metrics endpoint too | Add counters/timers in addition to logs; useful but more scope. | |

**User's choice:** 1 — Structured JSON logs plus request/job IDs.
**Notes:** Logs should support internal debugging without exposing audio, transcript, or prompt payloads.

---

## Setup Documentation

| Option | Description | Selected |
|--------|-------------|----------|
| Mac-to-GPU-host handoff | Local dev commands plus Docker Compose GPU-host steps, env vars, storage volume setup, health checks, and troubleshooting. | ✓ |
| Cloud-provider-specific guide | Target one provider in detail; more actionable if the host is already known. | |
| Minimal README appendix | Just enough commands to run services; faster but weaker for beta handoff. | |

**User's choice:** 1 — Mac-to-GPU-host handoff.
**Notes:** The runbook should distinguish local fixture validation from GPU-host runtime validation.

---

## Final Confirmation

| Option | Description | Selected |
|--------|-------------|----------|
| Write context now | Create and commit the Phase 6 context artifacts. | ✓ |
| More questions | Continue discussing Phase 6 details. | |
| Revise decisions | Change one of the locked decisions. | |

**User's choice:** 1 — Write context now.
**Notes:** The user approved writing `06-CONTEXT.md` and this discussion log.

---

## the agent's Discretion

- Downstream agents may choose exact compose file names, service names, env var names, health endpoint paths, log field names, and storage helper boundaries.
- Planners may slice worker separation as a deployable boundary plus fixture-compatible worker stub before hardening real GPU-provider execution.

## Deferred Ideas

- Cloud-provider-specific deployment guide.
- S3/MinIO production object storage implementation.
- Metrics endpoint and dashboards.
- Deep model warmup as a blocking readiness check.
