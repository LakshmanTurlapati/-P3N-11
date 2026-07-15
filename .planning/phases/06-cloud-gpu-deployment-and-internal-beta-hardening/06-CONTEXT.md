# Phase 6: Cloud GPU Deployment and Internal Beta Hardening - Context

**Gathered:** 2026-07-15T03:31:08Z
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 6 turns the current no-login studio into an internal-beta deployment shape: web, API/control-plane, and speech-worker runtime can run as separate services; audio artifacts persist outside process memory/temp-only assumptions; services expose readiness checks; generation/conversation failures and latency are logged for debugging; and an internal user can follow a runbook from Mac development to a rented GPU host.

This phase clarifies deployment and hardening only. It should not add user accounts, saved clip libraries, public APIs, advanced studio controls, or new model/provider capabilities beyond the configurable worker/runtime boundaries needed to run the existing speech loop.

</domain>

<decisions>
## Implementation Decisions

### Service Orchestration
- **D-01:** Use Docker Compose as the first orchestration target. A single compose flow should make the web app, API/control-plane, and speech-worker runtime separately runnable for internal beta validation.
- **D-02:** Keep local development commands available, but treat Compose as the handoff contract for the rented GPU host. Planning should prefer reproducible env files, service names, mounted volumes, and documented commands over ad hoc shell setup.
- **D-03:** Do not target a cloud-provider-specific deployment in this phase. Provider-specific production infrastructure can come later after the internal beta service split is proven.

### Worker Boundary
- **D-04:** Add a configurable external worker boundary while preserving local fixture/in-process fallbacks for tests. The API should be able to point at a separately runnable worker/runtime service through env config, but existing deterministic local tests must not require GPU services.
- **D-05:** Do not hard-require external worker execution everywhere in this phase. The planner should separate deployable runtime configuration from test fixtures so CI/local validation remains stable.
- **D-06:** Speech-provider runtime configuration should stay behind existing provider interfaces and environment variables, not leak into the web UI.

### Audio Persistence
- **D-07:** Use a mounted filesystem volume as the internal-beta persistence target for reference audio, captured turns, generated clips, conversation input audio, conversation response audio, and SQLite/job records.
- **D-08:** Name and structure the storage abstraction/env vars so an S3-compatible object store can replace the mounted filesystem later without changing browser routes or provider contracts.
- **D-09:** Preserve the current controlled playback URLs (`/generations/{job_id}/audio`, `/conversation-turns/{turn_id}/audio`, and related same-origin routes). The browser should not receive raw storage paths or bucket paths.

### Health And Readiness
- **D-10:** Add dependency-aware readiness checks rather than basic liveness only. The API readiness check should verify writable storage, SQLite/job DB access, voice registry availability, and worker/runtime configuration.
- **D-11:** The speech-worker readiness check should verify storage access and required provider/runtime environment configuration without doing expensive model warmup by default.
- **D-12:** Avoid deep model warmup as a default readiness requirement. Heavy model load or GPU probes may be documented as an optional troubleshooting command, not a blocking startup path for every internal beta run.

### Observability
- **D-13:** Add structured JSON logs with request/job IDs for internal debugging. Logs should capture lifecycle events, status transitions, provider names, stage timings, errors, and safe storage references.
- **D-14:** Do not log raw audio bytes, generated audio payloads, reference audio contents, full transcript text, or full generation prompt text. Logging should support debugging while respecting voice/privacy boundaries.
- **D-15:** A metrics endpoint is optional future scope. Phase 6 should prioritize structured logs and readiness checks before adding a full metrics surface.

### Internal Beta Runbook
- **D-16:** Optimize setup documentation for Mac-to-GPU-host handoff: local prerequisites, Docker Compose commands, env vars, mounted storage volume setup, service health checks, log inspection, and troubleshooting.
- **D-17:** The runbook should explain both local fixture-mode validation and GPU-host runtime validation so an internal user knows what was actually tested in each mode.
- **D-18:** Include explicit setup notes for Python/CUDA/PyTorch/model-weight compatibility and license/runtime blockers carried forward from Phase 5. Do not imply that blocked model candidates are production-ready.

### the agent's Discretion
- **D-19:** Downstream agents may choose exact compose file names, service names, health endpoint paths, env var names, log field names, and storage helper boundaries as long as the decisions above are preserved.
- **D-20:** If a full external worker protocol is too large for one plan, planners may slice it as a deployable boundary plus fixture-compatible worker stub first, then harden provider runtime integration in a later Phase 6 plan.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning And Requirements
- `.planning/PROJECT.md` — Project constraints, current state, and phase-transition decisions.
- `.planning/REQUIREMENTS.md` — DEP-01 through DEP-05 deployment requirements and traceability.
- `.planning/ROADMAP.md` — Phase 6 goal, success criteria, and planned plan names.
- `.planning/STATE.md` — Current phase state, carried decisions, and blockers/concerns.

### Prior Phase Context
- `.planning/phases/05-model-benchmark-and-selection/05-CONTEXT.md` — Model/runtime evidence policy, blocked candidates, and conservative provider-selection decisions.
- `.planning/phases/05-model-benchmark-and-selection/05-VERIFICATION.md` — Verified benchmark outputs and Phase 5 requirement coverage.
- `.planning/phases/04-live-conversation-mode/04-CONTEXT.md` — Live conversation service behavior, interruption, latency, and provider-boundary decisions.
- `.planning/phases/03-audio-input-and-turn-detection/03-CONTEXT.md` — Spoken input, VAD/STT provider boundary, and session-scoped audio-turn decisions.

### Existing Code Surfaces
- `apps/web/next.config.ts` — Existing same-origin rewrites and `API_BASE_URL` integration point for separate web/API services.
- `services/api/app/main.py` — FastAPI app composition and likely home for health/readiness routes.
- `services/api/app/services/generation_jobs.py` — Current local object store, SQLite-backed generation jobs, and `THEATRICAL_VOICE_STUDIO_STORAGE_ROOT` pattern.
- `services/api/app/services/audio_turn_jobs.py` — Current audio-turn object store and storage-root pattern.
- `services/api/app/services/conversation_jobs.py` — Current conversation session/turn SQLite records and input/response audio object stores.
- `services/api/app/services/generation_runtime.py` — Existing worker-root env pattern and provider runtime boundary for generation.
- `services/api/app/services/audio_turn_runtime.py` — Existing worker-root env pattern and provider runtime boundary for audio turns.
- `services/api/app/services/conversation_runtime.py` — Existing turn-processing runtime and latency recording path.
- `apps/web/playwright.config.ts` — Existing two-process local verification pattern for Next.js plus Uvicorn.
- `pyproject.toml` — Python runtime and test dependencies.
- `apps/web/package.json` — Web runtime/build/test commands and package manager.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `apps/web/next.config.ts`: already routes browser calls through same-origin rewrites to `API_BASE_URL`; Phase 6 can keep web and API separate without changing browser fetch calls.
- `GenerationJobService`, `AudioTurnJobService`, `ConversationSessionService`, and `ConversationTurnService`: already use SQLite plus filesystem object stores and accept configurable storage roots.
- `THEATRICAL_VOICE_STUDIO_STORAGE_ROOT`: existing env var pattern for local artifact persistence; planning can either preserve it or formalize it into documented beta env.
- `THEATRICAL_VOICE_STUDIO_WORKER_ROOT`: existing env var pattern for provider runtime discovery; useful as the compatibility bridge while adding an external worker boundary.
- Existing Playwright config starts web and API as separate local processes, which can inform service readiness and smoke-test commands.

### Established Patterns
- Browser-facing audio routes stay controlled and same-origin; storage paths remain server-owned.
- Local tests use deterministic fixture/runtime fallbacks rather than real GPU dependencies.
- API services store job/session records in SQLite JSON rows colocated with object-store roots.
- Provider implementations are imported behind runtime/provider interfaces, not directly from the web UI.
- Phase 5 recommendations keep current defaults unless alternate candidates clear evidence, license, safety, and integration gates.

### Integration Points
- Add API health/readiness routes in `services/api/app/main.py` or a new router included from that app.
- Add worker readiness to the speech-worker/service boundary without forcing heavy model loading during normal tests.
- Add deployment configuration at repo root or a dedicated deployment directory, with env example files that wire web/API/worker/storage together.
- Update docs/runbook so internal users can run local fixture mode and rented GPU-host mode with clear differences.
- Extend logging around generation, audio-turn, and conversation runtimes rather than logging from UI components.

</code_context>

<specifics>
## Specific Ideas

- The internal beta should feel like a practical handoff: a developer on a Mac can validate locally, then copy the same env/compose mental model to a rented GPU host.
- Readiness should catch missing storage or worker config before a user discovers it through a failed generation.
- Mounted volume persistence is enough for this MVP, but the naming should keep object storage migration open.
- Structured logs should make failed generation and live conversation turns diagnosable by job ID or turn ID without exposing sensitive audio or prompt content.

</specifics>

<deferred>
## Deferred Ideas

- Cloud-provider-specific deployment guide — defer until the rented GPU provider is chosen.
- S3/MinIO production object storage — keep the interface path open, but defer full object-store implementation unless planning finds it cheap enough for this phase.
- Metrics endpoint and dashboards — useful after structured logs and readiness are in place.
- Deep model warmup readiness — keep as optional troubleshooting or later hardening, not default readiness.

</deferred>

---

*Phase: 6-Cloud GPU Deployment and Internal Beta Hardening*
*Context gathered: 2026-07-15T03:31:08Z*
