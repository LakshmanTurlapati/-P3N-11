# Phase 2: Consented Studio Generation - Context

**Gathered:** 2026-07-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 turns the Phase 1 metadata-only studio skeleton into the first playable text-to-speech loop. It adds text input, tone presets, a real server-side TTS provider adapter, generation jobs, audio normalization/storage, browser playback, retry behavior, and generated-audio metadata while preserving the Phase 1 backend rights gate and original-voice boundary.

This phase does not add microphone input, upload-based audio input, VAD, STT, live conversation, streaming playback, benchmark dashboards, cloud deployment hardening, user accounts, durable clip libraries, batch generation, or detailed tone sliders.

</domain>

<decisions>
## Implementation Decisions

### First Playable Voice Bar
- **D-01:** Phase 2 should prioritize a safe real-audio baseline provider first. The exact provider is left to research/planning, but it must produce real playable audio through the server-side provider interface.
- **D-02:** The first generated audio is a prototype audition: it should be playable and tone-steered, but it may sound like an early baseline rather than the final theatrical Vesper Glass voice.
- **D-03:** Tests may use fixtures, but the phase only counts as complete when a configured real provider produces playable audio locally or in the intended runtime.
- **D-04:** Prefer an open-source, offline, or open-weight TTS adapter behind the provider interface, even if setup is heavier than a commercial API.
- **D-05:** Do not add reference-audio upload, recording, or consent intake UI in Phase 2. Support consent/license notes in backend data/schema where needed, but keep the first generation loop text-to-speech focused.
- **D-06:** Research cloning-capable candidates such as OpenVoice, F5-TTS, and CosyVoice for license/runtime fit, then implement the safest feasible real baseline provider. Phase 2 does not require final cloning quality.
- **D-07:** A generic or non-final Vesper voice is allowed if the UI and metadata clearly label it as a prototype baseline and never claim protected-character, performer, or final Vesper quality.
- **D-08:** Phase 2 should return/store complete generated clips for playback. Streaming and partial audio belong to the later live conversation work.

### Generation Job Shape
- **D-09:** Introduce a generation job lifecycle instead of keeping `/generate` as a direct synchronous final-result response.
- **D-10:** The first lifecycle should expose coarse states: `queued`, `running`, `succeeded`, and `failed`, with user-friendly loading and error text.
- **D-11:** Retry should reuse the last text, voice, and tone to create a new job after a failure. Keep the failed job metadata visible instead of mutating it away.
- **D-12:** If generation takes longer than expected, keep the job visible as running. Do not mark it failed only because the browser waited a fixed time; show status and allow retry after failure.

### Tone Preset Set
- **D-13:** Ship three focused presets: `Measured`, `Cutting`, and `Grandiose`.
- **D-14:** Tone presets map to prompt/style metadata passed to the provider or future persona layer. Do not add numeric sliders or provider-specific controls in Phase 2.
- **D-15:** Show compact one-line descriptions for presets near the selector without exposing prompt internals.
- **D-16:** Presets must be safe by construction: each preset carries the original-voice boundary and prohibited-association guard, and no preset may request a protected character or real performer.

### Playback And Metadata Surface
- **D-17:** Show the current playable clip prominently and keep recent in-session attempts with status and metadata.
- **D-18:** Normal UI should show operational essentials: voice, tone, provider, status, audio duration/timing, and rights approval.
- **D-19:** Store generated audio through a local object-store abstraction that writes files under a local storage directory and returns controlled playback URLs. Do not return inline audio bytes/base64, and do not require an S3-compatible bucket in Phase 2.
- **D-20:** Generated attempts are in-session only across the browser session. Do not add a durable clip library, persistent local history, or page-refresh restoration in Phase 2.

### the agent's Discretion
- **D-21:** The user delegated the initial provider-bar choice. The chosen default is a safe real-audio baseline first, because it validates the end-to-end generation and playback loop without pretending that a consented cloned reference voice already exists.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` - Defines the current product direction, Phase 2 starting point, safety constraints, Vesper Glass boundary, and no-login studio-first shape.
- `.planning/REQUIREMENTS.md` - Maps Phase 2 to GOV-04, STUD-03 through STUD-07, and PIPE-02 through PIPE-04.
- `.planning/ROADMAP.md` - Defines the Phase 2 goal, success criteria, and planned work slices.
- `.planning/STATE.md` - Current project position, Phase 1 completion state, accumulated decisions, and blockers.

### Prior Phase Handoff
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md` - Locks Phase 1 decisions about the direct studio route, Vesper Glass identity, rights gate UX, metadata-only stub boundary, and provider-interface posture.
- `.planning/phases/01-no-login-vertical-skeleton/01-03-SUMMARY.md` - Summarizes the generation contract, provider protocols, FastAPI route, Next.js rewrites, and UI result-card handoff that Phase 2 extends.

### Research and Architecture
- `.planning/research/ARCHITECTURE.md` - Defines the web/API/worker/storage split, job flow, object storage role, and provider adapter boundary.
- `.planning/research/STACK.md` - Defines the recommended Next.js/FastAPI/Python stack, TTS candidates, object storage direction, and the warning against long synchronous generation requests.
- `.planning/research/PITFALLS.md` - Defines the key Phase 2 risks: unauthorized voice use, model lock-in, dependency conflicts, synchronous generation hangs, unsafe storage paths, and weak generation feedback.
- `.planning/research/FEATURES.md` - Defines text-to-speech studio generation, tone presets, generated playback, consent metadata, and provider abstraction as expected v1 capabilities.

No separate Phase 2 SPEC.md exists as of this discussion.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `apps/web/components/studio-shell.tsx` - Current client component owns voice selection, generation loading/error state, `POST /generate`, and the structured metadata result card. Phase 2 should extend this into text input, tone preset selection, job status, playback, and recent in-session attempts.
- `apps/web/lib/voice-registry.ts` - Browser display seed for Vesper Glass remains render-only. Do not treat it as canonical generation rights data.
- `services/api/app/routes/generate.py` - Current FastAPI route looks up the server voice profile, enforces the rights gate, and returns a metadata-only result. Phase 2 should evolve this into job creation/result behavior without bypassing `ensure_voice_allowed`.
- `services/api/app/schemas/generation.py` - Current strict Pydantic schemas cover request, rights check, provider trace, timing, and metadata. Phase 2 should extend these toward text, tone, job status, audio artifact metadata, and playback URL shape.
- `services/api/app/services/stub_generation.py` - Current inline metadata stub is the piece to replace with a real provider-backed generation service.
- `services/speech-worker/providers/contracts.py` - Existing `TTSProvider.synthesize(text, voice_id, tone=None)` contract already matches Phase 2 needs and should stay provider-agnostic.

### Established Patterns
- Server-owned voice registry and `rights_gate.ensure_voice_allowed` are authoritative for generation approval.
- Pydantic models use strict `extra="forbid"` validation and explicit validators.
- The browser uses Next.js rewrites for `/generate` and `/voices` so local browser tests exercise the FastAPI control plane.
- Phase 1 intentionally kept audio playback out. Phase 2 is responsible for adding it now, not earlier phases.

### Integration Points
- Web: extend the root studio surface at `/` rather than adding a landing page or separate app route.
- API: replace or wrap the metadata-only `/generate` behavior with generation job creation/status/result endpoints.
- Worker/provider: implement one real TTS provider behind the existing provider interface; isolate model-specific details from UI/API schemas.
- Storage: add a local object-store abstraction for generated clips and return controlled playback URLs to the browser.
- Tests: extend API tests around rights gating, job status, provider result metadata, and playback URL shape; extend Playwright tests around text input, tone preset, loading/error/retry states, and audio player rendering.

</code_context>

<specifics>
## Specific Ideas

- Initial tone preset names: `Measured`, `Cutting`, and `Grandiose`.
- The UI should label first-provider output as a prototype baseline when it does not yet represent final Vesper Glass quality.
- Visible metadata should stay product-useful rather than becoming a full debug log: voice, tone, provider, status, timing/duration, and rights approval.

</specifics>

<deferred>
## Deferred Ideas

- Reference-audio upload/recording and consent intake UI - belongs after the first text-to-speech loop or in a dedicated voice-onboarding phase.
- Streaming/partial audio - belongs to live conversation mode.
- Durable clip library, persisted history, and page-refresh restoration - belongs to a later studio/library phase.
- Detailed tone sliders and provider-specific parameters - deferred beyond the minimal v1 preset surface.
- Cloud bucket requirement - deferred to cloud GPU deployment and beta hardening.

</deferred>

---

*Phase: 2-Consented Studio Generation*
*Context gathered: 2026-07-01*
