# Phase 6: Cloud GPU Deployment and Internal Beta Hardening - Research

**Researched:** 2026-07-14
**Domain:** Cloud GPU deployment, service orchestration, persistence, readiness, and observability for the Theatrical Voice Studio internal beta
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Use Docker Compose as the first orchestration target. A single compose flow should make the web app, API/control-plane, and speech-worker runtime separately runnable for internal beta validation.
- D-02: Keep local development commands available, but treat Compose as the handoff contract for the rented GPU host. Planning should prefer reproducible env files, service names, mounted volumes, and documented commands over ad hoc shell setup.
- D-03: Do not target a cloud-provider-specific deployment in this phase. Provider-specific production infrastructure can come later after the internal beta service split is proven.

### Worker Boundary
- D-04: Add a configurable external worker boundary while preserving local fixture/in-process fallbacks for tests. The API should be able to point at a separately runnable worker/runtime service through env config, but existing deterministic local tests must not require GPU services.
- D-05: Do not hard-require external worker execution everywhere in this phase. The planner should separate deployable runtime configuration from test fixtures so CI/local validation remains stable.
- D-06: Speech-provider runtime configuration should stay behind existing provider interfaces and environment variables, not leak into the web UI.

### Audio Persistence
- D-07: Use a mounted filesystem volume as the internal-beta persistence target for reference audio, captured turns, generated clips, conversation input audio, conversation response audio, and SQLite/job records.
- D-08: Name and structure the storage abstraction/env vars so an S3-compatible object store can replace the mounted filesystem later without changing browser routes or provider contracts.
- D-09: Preserve the current controlled playback URLs (`/generations/{job_id}/audio`, `/conversation-turns/{turn_id}/audio`, and related same-origin routes). The browser should not receive raw storage paths or bucket paths.

### Health And Readiness
- D-10: Add dependency-aware readiness checks rather than basic liveness only. The API readiness check should verify writable storage, SQLite/job DB access, voice registry availability, and worker/runtime configuration.
- D-11: The speech-worker readiness check should verify storage access and required provider/runtime environment configuration without doing expensive model warmup by default.
- D-12: Avoid deep model warmup as a default readiness requirement. Heavy model load or GPU probes may be documented as an optional troubleshooting command, not a blocking startup path for every internal beta run.

### Observability
- D-13: Add structured JSON logs with request/job IDs for internal debugging. Logs should capture lifecycle events, status transitions, provider names, stage timings, errors, and safe storage references.
- D-14: Do not log raw audio bytes, generated audio payloads, reference audio contents, full transcript text, or full generation prompt text. Logging should support debugging while respecting voice/privacy boundaries.
- D-15: A metrics endpoint is optional future scope. Phase 6 should prioritize structured logs and readiness checks before adding a full metrics surface.

### Internal Beta Runbook
- D-16: Optimize setup documentation for Mac-to-GPU-host handoff: local prerequisites, Docker Compose commands, env vars, mounted storage volume setup, service health checks, log inspection, and troubleshooting.
- D-17: The runbook should explain both local fixture-mode validation and GPU-host runtime validation so an internal user knows what was actually tested in each mode.
- D-18: Include explicit setup notes for Python/CUDA/PyTorch/model-weight compatibility and license/runtime blockers carried forward from Phase 5. Do not imply that blocked model candidates are production-ready.

### the agent's Discretion
- D-19: Downstream agents may choose exact compose file names, service names, health endpoint paths, env var names, log field names, and storage helper boundaries as long as the decisions above are preserved.
- D-20: If a full external worker protocol is too large for one plan, planners may slice it as a deployable boundary plus fixture-compatible worker stub first, then harden provider runtime integration in a later Phase 6 plan.

### Deferred Ideas (OUT OF SCOPE)
- Cloud-provider-specific deployment guide — defer until the rented GPU provider is chosen.
- S3/MinIO production object storage — keep the interface path open, but defer full object-store implementation unless planning finds it cheap enough for this phase.
- Metrics endpoint and dashboards — useful after structured logs and readiness are in place.
- Deep model warmup readiness — keep as optional troubleshooting or later hardening, not default readiness.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEP-01 | System can run as separate web, API/control-plane, and speech-worker services. | Architectural Responsibility Map, Standard Stack, Service Separation and Docker Compose Notes |
| DEP-02 | System can persist reference audio and generated clips outside the application process. | Current Codebase Findings, Persistence and Storage Notes, Common Pitfalls |
| DEP-03 | System exposes health checks for API and speech-worker readiness. | Readiness and Health Check Notes, Validation Architecture, Common Pitfalls |
| DEP-04 | System logs generation errors and latency in a way that supports internal debugging. | Observability and Correlation ID Notes, Code Examples, Security Domain |
| DEP-05 | Internal user can follow setup documentation to run or deploy the v1 web app on a rented GPU environment. | Internal Beta Runbook Notes, Environment Availability, Validation Architecture |
</phase_requirements>

## Summary

Phase 6 is packaging and hardening work, not a new speech-capability phase. The repository already has the important seams the phase needs: Next.js rewrites keep browser calls same-origin, FastAPI owns the control plane, and generation/audio-turn/conversation services already persist records plus audio through storage-root abstractions. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py]

The main planning risk is scope creep into a new provider protocol, a cloud-provider-specific deployment, or heavier readiness semantics than the phase requires. The best plan shape is a single Docker Compose handoff with three services, one shared mounted storage root, dependency-aware readiness checks, and structured JSON logs with request/job IDs. The current workstation lacks Docker, Docker Compose, and ffmpeg, so the runbook must spell out the host prerequisites instead of assuming them. [VERIFIED: local shell `docker --version`, `docker compose version`, `ffmpeg -version`] [CITED: https://docs.docker.com/reference/compose-file/services/] [CITED: https://docs.docker.com/reference/compose-file/volumes/] [CITED: https://docs.python.org/3/howto/logging-cookbook.html]

**Primary recommendation:** keep the existing provider/import seams, add Compose and health/logging scaffolding around them, and write a Mac-to-GPU-host runbook that clearly separates local fixture validation from rented-host validation. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Browser fetch proxying and same-origin route masking | Frontend Server (SSR) | Browser / Client | `apps/web/next.config.ts` already rewrites browser routes to `API_BASE_URL`, so the browser should stay ignorant of the backend host. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] |
| Job creation, rights gate, readiness, and controlled playback URLs | API / Backend | Frontend Server (SSR) | The FastAPI routes and job services own the control plane and should continue to own status, storage, and readiness semantics. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py] |
| Provider execution and speech normalization | API / Backend | Database / Storage | The worker boundary is backend-only and already isolated behind provider protocols plus worker-root imports. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py] |
| Audio artifacts and job/session records | Database / Storage | API / Backend | The job services already persist JSON records and audio files under storage-root abstractions. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py] |
| Structured logging and correlation IDs | API / Backend | Browser / Client | Logging belongs in the backend services; the browser should not be asked to assemble operational traces. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] [CITED: https://docs.python.org/3/library/contextvars.html] |

## Current Codebase Findings

- `apps/web/next.config.ts` already proxies `/generate`, `/generations/:path*`, `/conversation-sessions`, `/conversation-turns`, `/voices`, and `/audio-turns` through `API_BASE_URL`, so the browser can remain same-origin while the API runs separately. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts]
- `services/api/app/main.py` currently only includes the functional routers; there is no readiness or health router yet. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py]
- `GenerationJobService`, `AudioTurnJobService`, `ConversationSessionService`, and `ConversationTurnService` already persist JSON rows in SQLite and store audio artifacts under path-checked filesystem roots with controlled playback URLs. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py]
- The runtime modules already use `THEATRICAL_VOICE_STUDIO_WORKER_ROOT` to import provider classes from the checked-out `services/speech-worker` tree and fall back to fixture/in-process behavior when the worker checkout is not available. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_runtime.py]
- `services/speech-worker/` is currently a provider library and benchmark package, not a deployable server application. I found no standalone ASGI or CLI worker entrypoint in the tree. [VERIFIED: local file scan]
- `apps/web/playwright.config.ts` already starts the API and Next.js as separate local processes, which is a good model for Phase 6 smoke validation. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts]

## Recommended Plan Shape

1. Use one Compose stack with three named services: `web`, `api`, and `speech-worker`. The stack should be the handoff contract for the internal beta, not a provider-specific deployment. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: https://docs.docker.com/reference/compose-file/services/]
2. Keep the first cut of the worker boundary import-based rather than introducing a new HTTP speech RPC protocol. That is an inference from the current runtime seam and the explicit allowance to slice a deployable boundary plus fixture-compatible stub first. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
3. Mount a shared filesystem root into API and worker containers, then keep all artifact paths and SQLite job records under that root. This preserves the current playback URLs and keeps a later S3-compatible swap possible. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py]
4. Add cheap readiness endpoints and structured logging before adding any broader metrics surface. The phase should make misconfiguration obvious without forcing heavy model warmup. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: https://fastapi.tiangolo.com/advanced/events/]
5. Write the internal beta runbook in a Mac-to-GPU-host shape: local fixture mode first, then Compose on the rented GPU host, then operational checks and troubleshooting. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]

## Standard Stack

### Core

| Library / Tool | Version / Target | Purpose | Why Standard |
|----------------|------------------|---------|--------------|
| Next.js | `16.2.9` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Web studio UI and same-origin rewrites | The browser already depends on Next.js for its UI shell and API proxy seam. |
| React | `19.2.7` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | UI rendering | Current repo pin matches the app shell. |
| react-dom | `19.2.7` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Browser render runtime | Required by the Next.js app runtime. |
| TypeScript | `6.0.3` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Type safety for browser and API contracts | The repo already uses TypeScript for the web surface and client-side contract shapes. |
| FastAPI | `0.138.2` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | API/control-plane | The API routes and job services already use it. |
| Pydantic | `2.13.4` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | Runtime validation | Job, turn, and voice schemas already depend on it. |
| Uvicorn | `0.49.0` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | ASGI runtime | Keeps the API container command explicit. |
| pytest | `9.1.1` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | API/worker tests | Existing test infrastructure already uses it. |
| Playwright | `1.61.1` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Browser smoke tests | Existing local validation already uses it. |

### Supporting

| Tool / Dependency | Purpose | When to Use |
|------------------|---------|-------------|
| Docker Compose | Multi-service deployment contract | Use for the internal beta handoff and service dependency wiring. [CITED: https://docs.docker.com/reference/compose-file/services/] [CITED: https://docs.docker.com/reference/compose-file/volumes/] |
| FFmpeg | Audio normalization and WAV coercion | Keep it in the worker image or host; the current workspace does not have it. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/audio/normalization.py] |
| Python stdlib `logging` + `contextvars` | Structured JSON logs and correlation IDs | Use this instead of adding a logging dependency. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] [CITED: https://docs.python.org/3/library/logging.config.html] [CITED: https://docs.python.org/3/library/contextvars.html] |

**Installation:** no new external packages are required for Phase 6. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml]

## Service Separation and Docker Compose Notes

- Use Compose service names that make the split obvious: `web`, `api`, and `speech-worker`. Avoid a single omnibus container that hides boundaries or makes health checks ambiguous. [CITED: https://docs.docker.com/reference/compose-file/services/]
- Keep the browser pointing at the Next.js service and let `API_BASE_URL` remain a server-side bridge to the API host. The current rewrite seam already supports this pattern. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts]
- Give the API its own container command and healthcheck. It owns rights gating, job lifecycle, storage-root wiring, and readiness checks. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py]
- Give the speech-worker container its own runtime command or bootstrap script, even if the first cut still uses the checked-out provider code through the current worker-root seam. That keeps the boundary explicit without inventing a network protocol too early. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_runtime.py]
- Use Compose `depends_on` and healthchecks for startup ordering, but do not turn readiness into a model-warmup gate. [CITED: https://docs.docker.com/reference/compose-file/services/] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]

## Persistence and Storage Notes

- Use one mounted filesystem root for the beta, then keep the current storage subpaths under it for generation clips, audio-turn uploads, conversation input audio, conversation response audio, and SQLite records. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- The current services already enforce path safety with `Path(...).name` checks and `resolve().is_relative_to(...)` checks; the plan should preserve those helpers rather than replacing them with ad hoc path joins. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py]
- Keep the browser-facing URLs controlled and same-origin. The browser should continue to load audio through `/generations/{job_id}/audio`, `/audio-turns/{job_id}/audio`, `/conversation-turns/{turn_id}/audio`, and `/conversation-turns/{turn_id}/input.wav`. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py]
- Structure the storage env var names so a later object-store swap can happen behind the same storage abstraction. The current `THEATRICAL_VOICE_STUDIO_STORAGE_ROOT` and storage-root classes are the right seam to formalize. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py]
- Do not let storage paths leak to the browser. The API should keep returning playback URLs, not filesystem paths or bucket paths. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py]

## Readiness and Health Check Notes

- API readiness should verify four things: writable storage, SQLite/job DB access, voice registry availability, and worker/runtime configuration. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- Worker readiness should verify storage access plus required environment configuration, but it should not load or warm the speech models by default. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- Add a cheap liveness route only if it helps operator debugging; the phase requirement is readiness, not a richer monitoring surface. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- Prefer startup-time checks and explicit troubleshooting commands over readiness probes that load GPU models. FastAPI startup/lifespan hooks are the correct place for expensive initialization if any is needed. [CITED: https://fastapi.tiangolo.com/advanced/events/]
- The current codebase has no dedicated health/readiness router yet, so the plan needs to add one rather than extend an existing endpoint. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py] [VERIFIED: local file scan]

## Observability and Correlation ID Notes

- Use the Python logging stack, not ad hoc `print()` statements, and emit JSON logs to stdout so Compose and host log collection can ingest them consistently. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] [CITED: https://docs.python.org/3/library/logging.config.html]
- Carry correlation state with `contextvars` or `LoggerAdapter` so request IDs and job/turn IDs can be attached to logs without threading them through every call manually. [CITED: https://docs.python.org/3/library/contextvars.html] [CITED: https://docs.python.org/3/howto/logging-cookbook.html]
- Log lifecycle events that help internal debugging: queued, running, succeeded, failed, retry, interrupted, readiness failure, provider name, stage timings, and sanitized storage references. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- Do not log raw audio bytes, audio payloads, transcript text, prompt text, or other voice content. Keep debugging useful without crossing the phase boundary. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: https://docs.python.org/3/howto/logging-cookbook.html]
- The useful correlation keys are `request_id`, `job_id`, and `turn_id`; session IDs can be added when they help conversation debugging, but keep the schema compact. [CITED: https://docs.python.org/3/library/contextvars.html]

## Internal Beta Runbook Notes

- The runbook should be written for a Mac-to-GPU-host handoff. Local fixture validation on a Mac is still valuable, but it should be clearly labeled as fixture-mode validation, not as a real GPU runtime proof. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- Local validation already has a pattern: Playwright starts the API and Next.js separately, and the API tests use fixture env vars such as `THEATRICAL_VOICE_STUDIO_VAD_FIXTURE` and `THEATRICAL_VOICE_STUDIO_STT_FIXTURE`. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generation_runtime.py]
- The GPU-host path should document: install Docker/Compose, mount the shared storage volume, set `API_BASE_URL`, set the worker-root and provider env vars, start Compose, verify readiness, and inspect JSON logs. [CITED: https://docs.docker.com/reference/compose-file/services/] [CITED: https://docs.docker.com/reference/compose-file/volumes/]
- The runbook should explicitly call out the Phase 5 blockers that remain blocked on real GPU-host evidence: FireRedVAD package legitimacy/runtime validation, Qwen3-TTS GPU-host evidence, and end-to-end S2S candidates such as Moshi, MiniCPM-o 4.5, FlashLabs Chroma, and Qwen3-Omni. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/05-model-benchmark-and-selection/05-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md]
- The current `README.md` is still a planning-stage project overview, not an internal beta operator runbook, so Phase 6 needs a new deployment doc or a clearly repurposed docs page. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/README.md]

## Safety/Audit Notes

- Keep the rights gate authoritative. Generation remains blocked unless the voice profile has approved rights metadata, and that logic must stay on the backend. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py]
- Preserve the original theatrical voice boundary. The first voice stays an original persona and must not drift into a protected Loki/Tom Hiddleston clone. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py]
- Preserve controlled same-origin playback URLs and avoid exposing raw storage paths to the browser. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py]
- Treat readiness and logging as operational controls, not as a place to broaden scope into accounts, public APIs, or advanced controls. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]
- The safe logging boundary is backend IDs, durations, provider names, and sanitized error summaries only. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 9.1.1` for API/worker tests; `Playwright 1.61.1` for browser smoke tests [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] |
| Config file | `pyproject.toml`; `apps/web/playwright.config.ts` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts] |
| Quick run command | `pytest services/api/tests/test_generation_jobs.py services/api/tests/test_audio_turn_jobs.py services/api/tests/test_conversation_jobs.py services/api/tests/test_generation_runtime.py -x` |
| Full suite command | `pytest services/api/tests -x && pytest services/speech-worker/tests -x && pnpm --dir apps/web test` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DEP-01 | Separate web, API/control-plane, and speech-worker services | integration / smoke | `docker compose config && docker compose up -d` once the compose files exist | ❌ Wave 0 |
| DEP-02 | Persist audio and jobs outside the application process | unit / integration | `pytest services/api/tests/test_generation_jobs.py services/api/tests/test_audio_turn_jobs.py services/api/tests/test_conversation_jobs.py -x` | ✅ |
| DEP-03 | API and worker readiness health checks | integration | `pytest services/api/tests/test_health.py services/speech-worker/tests/test_health.py -x` | ❌ Wave 0 |
| DEP-04 | Generation errors and latency are logged for internal debugging | unit | `pytest services/api/tests/test_logging.py -x` | ❌ Wave 0 |
| DEP-05 | Internal beta runbook covers rented GPU deployment | manual / docs | `docker compose config && runbook checklist` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest services/api/tests/test_generation_jobs.py services/api/tests/test_audio_turn_jobs.py services/api/tests/test_conversation_jobs.py services/api/tests/test_generation_runtime.py -x`
- **Per wave merge:** `pytest services/api/tests -x && pytest services/speech-worker/tests -x && pnpm --dir apps/web test`
- **Phase gate:** full suite green before verification sign-off.

### Wave 0 Gaps

- `compose.yaml` and/or `compose.override.yaml` do not exist yet. [VERIFIED: local file scan]
- `services/api/app/routes/health.py` or an equivalent readiness router does not exist yet. [VERIFIED: local file scan]
- `services/speech-worker/app.py` or an equivalent worker entrypoint does not exist yet. [VERIFIED: local file scan]
- Dedicated health and logging test files are missing. [VERIFIED: local file scan]
- Dedicated deployment/runbook docs for the internal beta are missing. [VERIFIED: local file scan]

## Planner Inputs: likely files to modify/create and risks

| File / Area | Likely Change | Risk |
|-------------|---------------|------|
| `compose.yaml` | Define `web`, `api`, and `speech-worker` services plus a shared volume and health dependencies. | Getting the service boundary wrong could hide a single-process deployment behind Compose. |
| `.env.example` | Add the host/volume/runtime vars needed for local fixture mode and GPU-host mode. | Env sprawl can drift if the same names are not used across docs and services. |
| `services/api/app/main.py` or `services/api/app/routes/health.py` | Add readiness/liveness routes and include them in the FastAPI app. | A health endpoint that warms models would violate the phase constraint. |
| `services/api/app/services/generation_runtime.py` | Preserve the worker-root seam while making runtime config observable. | Turning the boundary into a hard network dependency too early would make local tests brittle. |
| `services/api/app/services/audio_turn_runtime.py` | Keep fixture fallbacks and surface worker config checks. | Overfitting readiness to GPU runtime would block local validation. |
| `services/api/app/services/conversation_runtime.py` | Keep conversation synthesis behind the provider seam and log the right IDs. | Logging transcript or prompt content would violate the safety boundary. |
| `services/speech-worker/app.py` or `services/speech-worker/health.py` | Add a worker entrypoint or readiness surface. | A missing entrypoint would leave the worker service non-operational in Compose. |
| `services/api/tests/test_health.py` | Add API readiness coverage. | Without this, the plan can add routes without proving dependency-aware checks. |
| `services/speech-worker/tests/test_health.py` | Add worker readiness coverage. | Without this, the worker may look runnable while missing storage/env wiring. |
| `services/api/tests/test_logging.py` | Add log schema and correlation-ID coverage. | Log regressions are easy to miss without a dedicated test. |
| `docs/deployment/internal-beta.md` or similar | Write the Mac-to-GPU-host runbook. | If this stays in memory or chat, the handoff will not be reproducible. |

## Sources

### Primary (HIGH confidence)
- Official Next.js rewrites docs - same-origin proxy behavior for separate web/API deployment. [CITED: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites]
- Official Docker Compose services docs - service definitions, healthchecks, and dependency ordering. [CITED: https://docs.docker.com/reference/compose-file/services/]
- Official Docker Compose volumes docs - persisted data volumes. [CITED: https://docs.docker.com/reference/compose-file/volumes/]
- Official FastAPI background tasks docs - post-response work for job queues. [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/]
- Official FastAPI lifespan/events docs - startup/shutdown hooks for expensive initialization. [CITED: https://fastapi.tiangolo.com/advanced/events/]
- Official Python logging cookbook - dictConfig, LoggerAdapter, contextvars, and structured logging patterns. [CITED: https://docs.python.org/3/howto/logging-cookbook.html]
- Official Python logging.config docs - configuration-driven logging. [CITED: https://docs.python.org/3/library/logging.config.html]
- Official Python contextvars docs - request/job-scoped context propagation. [CITED: https://docs.python.org/3/library/contextvars.html]
- Local code: current rewrite seam, storage-root services, runtime worker boundary, and route structure. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/audio/normalization.py]

### Secondary (MEDIUM confidence)
- Local package manifests and pins for the current web and API stack. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml]

## Common Pitfalls

### Pitfall 1: Treating readiness as model warmup
**What goes wrong:** startup hangs or fails on GPU-heavy load before the service can be considered ready.  
**Why it happens:** health checks are doing work that belongs in container startup or operator troubleshooting.  
**How to avoid:** verify storage, DB, env, and provider wiring only; keep heavy model load optional.  
**Warning signs:** probes take several seconds or readiness failures disappear when the model is already warm. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: https://fastapi.tiangolo.com/advanced/events/]

### Pitfall 2: Mounting audio storage in only one container
**What goes wrong:** the API can read the record but the worker cannot see the file, or playback 404s after container restart.  
**Why it happens:** the current code expects a shared storage root, but Compose can easily drift into per-container temp directories.  
**How to avoid:** mount the same root into API and worker and keep `THEATRICAL_VOICE_STUDIO_STORAGE_ROOT` consistent.  
**Warning signs:** success records exist but playback URLs return 404. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py]

### Pitfall 3: Logging transcript or audio payloads
**What goes wrong:** sensitive content leaks into log streams or support exports.  
**Why it happens:** debugging starts with dumping request bodies, transcript text, or raw audio metadata.  
**How to avoid:** log IDs, stages, durations, provider names, and sanitized error summaries only.  
**Warning signs:** logs contain transcript text, prompt text, or raw audio payloads. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md]

### Pitfall 4: Breaking the same-origin browser contract
**What goes wrong:** the browser needs a backend hostname, CORS rules proliferate, and local/prod parity gets worse.  
**Why it happens:** code starts calling the API host directly instead of going through the Next.js rewrite seam.  
**How to avoid:** keep `API_BASE_URL` server-side and preserve the existing rewrite bridge for browser fetches.  
**Warning signs:** browser code references `127.0.0.1:8000` or another backend host directly. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts]

## Code Examples

Verified patterns from official sources and the current repo:

### Same-Origin Rewrite Bridge
```ts
// Source: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts
const apiBaseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

async rewrites() {
  return [
    { source: "/generate", destination: `${apiBaseUrl}/generate` },
    { source: "/conversation-turns/:path*", destination: `${apiBaseUrl}/conversation-turns/:path*` },
  ];
}
```

### FastAPI Queue Boundary
```py
# Source: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py
@router.post("/generate", response_model=GenerationJobRecord)
def generate(request: GenerationRequest, background_tasks: BackgroundTasks) -> GenerationJobRecord:
    queued_job = job_service.create_job(request, profile)
    background_tasks.add_task(process_generation_job, queued_job.job_id, job_service=job_service)
    return queued_job
```

### Context-Local Structured Logging
```py
# Source: https://docs.python.org/3/howto/logging-cookbook.html
from contextvars import ContextVar
import logging
import logging.config

request_id = ContextVar("request_id", default="-")
job_id = ContextVar("job_id", default="-")
logging.config.dictConfig({...})
logger = logging.getLogger("theatrical_voice_studio")
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Audio persistence path management | Ad hoc path joins in routes | Current storage-root object-store abstractions | They already enforce path safety and controlled playback URLs. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] |
| Readiness warmup | GPU model loading in probes | Cheap dependency-aware readiness checks | Warmup belongs in optional troubleshooting or startup hooks, not readiness. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] |
| Logging schema | `print()` statements or payload dumps | `logging.config.dictConfig` + `contextvars` | This gives correlation IDs without exposing voice content. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] |
| Browser host wiring | Direct API host calls from the client | Next.js rewrites with `API_BASE_URL` | Keeps same-origin browser behavior and deploy-time flexibility. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] |

**Key insight:** Phase 6 should package and observe the current speech stack, not redesign it. The code already separates rights gating, same-origin routes, storage, and provider contracts; the planning risk is scope creep into accounts, new model selection, or cloud-provider-specific deployment. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 6 stays no-login; do not add auth-only controls into this phase. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md] |
| V3 Session Management | no | Conversation sessions are application records, not auth sessions; keep them as backend state. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/conversation.py] |
| V4 Access Control | yes | Rights gate and approved voice registry remain the control point for generation. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py] |
| V5 Input Validation | yes | Validate job IDs, voice IDs, tone presets, capture sources, MIME types, and storage paths. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/conversation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/audio_turn.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/conversation.py] |
| V6 Cryptography | no | No phase work depends on custom cryptography; use platform-managed secrets and storage later if needed. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/PROJECT.md] |

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal / arbitrary file read-write | Tampering / Information Disclosure | Keep `Path(...).name` checks, `resolve().is_relative_to(...)` checks, and controlled `FileResponse` routes. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py] |
| Sensitive transcript / prompt leakage in logs | Information Disclosure | Use structured logs with IDs and stage names only; exclude payload content. [CITED: https://docs.python.org/3/howto/logging-cookbook.html] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] |
| Unauthorized voice generation | Spoofing / Elevation of Privilege | Keep the rights gate and approved voice registry authoritative. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py] |
| Origin confusion / direct backend access from the browser | Spoofing / Information Disclosure | Preserve Next.js rewrites and keep `API_BASE_URL` server-side. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] [CITED: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites] |
| Resource exhaustion from startup warmups | Denial of Service | Keep readiness cheap and move expensive loading out of probes. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/06-cloud-gpu-deployment-and-internal-beta-hardening/06-CONTEXT.md] [CITED: https://fastapi.tiangolo.com/advanced/events/] |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Node.js | Web build/test tooling | ✓ | `v24.2.0` [VERIFIED: local shell `node --version`] | — |
| npm | Registry/version verification | ✓ | `11.3.0` [VERIFIED: local shell `npm --version`] | — |
| pnpm | Web package manager | ✓ | `10.30.3` [VERIFIED: local shell `pnpm --version`] | — |
| Python | API/worker test tooling | ✓ | `3.13.5` [VERIFIED: local shell `python3 --version`] | Use a worker-image Python 3.12.x when model deps require it. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/AGENTS.md] |
| Docker | Compose-based deployment validation | ✗ | — | Install Docker Desktop/Engine on the development machine, or validate the Compose stack directly on the rented GPU host. [VERIFIED: local shell `docker --version`] |
| Docker Compose | Compose-based deployment validation | ✗ | — | Same as Docker; Compose is the phase's handoff contract, so it must exist on the host where the beta is validated. [VERIFIED: local shell `docker compose version`] |
| FFmpeg | Worker-side audio normalization | ✗ | — | Install ffmpeg in the worker image or host; fixture-mode tests can still cover non-GPU logic. [VERIFIED: local shell `ffmpeg -version`; CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/audio/normalization.py] |

**Missing dependencies with no fallback:**
- None for planning. Docker/Compose and FFmpeg are missing on this workstation, but the phase can still be planned and the runbook can instruct installation or GPU-host validation. [VERIFIED: local shell commands above]

**Missing dependencies with fallback:**
- Docker / Docker Compose: install locally or run the Compose handoff directly on the GPU host. [VERIFIED: local shell commands above]
- FFmpeg: install in the worker image or host; the worker code already documents the requirement when it cannot normalize audio. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/audio/normalization.py]

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

**If this table is empty:** All claims in this research were verified or cited - no user confirmation needed.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - repo pins, local file scan, and official docs are enough for planning, but the phase does not require a registry-driven dependency change. [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: https://docs.docker.com/reference/compose-file/services/]
- Architecture: HIGH - the code already shows the deployment seams, and the Compose/logging/readiness primitives are documented by the official sources. [CITED: code and docs above]
- Pitfalls: MEDIUM - the warnings are grounded in current code plus docs, but some failure modes will only be proven once the Compose stack exists. [CITED: code and docs above]

**Research date:** 2026-07-14
**Valid until:** 2026-08-13
