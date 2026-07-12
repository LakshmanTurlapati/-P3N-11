# Phase 4: Live Conversation Mode - Context

**Gathered:** 2026-07-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 adds live conversation mode to the existing no-login studio at `/`. It builds on Phase 3 spoken input, VAD, STT, transcript metadata, and Phase 2 queued generation/playback to let a user start a session, speak a VAD-detected turn, receive a persona-safe spoken response in the selected Vesper Glass voice and tone, interrupt or cancel the response, and inspect compact per-turn latency.

This phase does not add persistent conversation history, user accounts, saved clip libraries, detailed debug dashboards, multi-provider benchmarking, final WebRTC/LiveKit transport selection, or a production real-LLM requirement. It should prove the conversation loop through provider interfaces and session-scoped records first.

</domain>

<decisions>
## Implementation Decisions

### Live Session Shape
- **D-01:** Keep live conversation as an inline panel on the root studio route `/`, near the existing spoken-input and generation controls. Do not add a separate route for Phase 4.
- **D-02:** Starting conversation should arm the mic and use VAD-driven automatic end-of-turn detection. The user should not need to click Stop for every live turn.
- **D-03:** The live panel should show compact recent turn cards with the user transcript, generated response text, status, playback, and a readable per-turn latency chip.
- **D-04:** Start conversation creates a session-scoped conversation record for the current browser session. Stop ends listening/playback and keeps recent turns visible until refresh.

### Conversation Response Loop
- **D-05:** Optimize Phase 4 for a turn-based live loop with complete response clips: VAD/STT user turn, persona response text, TTS output, then controlled playback.
- **D-06:** Add a first-class conversation-turn record that links input audio/STT, persona response text, output audio, status, and latency. The implementation may reuse existing audio-turn and generation services internally, but the UI should not have to stitch unrelated records together.
- **D-07:** Add a persona/LLM response provider interface with a deterministic Vesper-safe local responder as the default. A real LLM can be swapped in later behind the same contract.
- **D-08:** Failures should be scoped to the individual conversation turn. Mark the failed stage, show concise error text, keep the session recoverable, and allow the next user turn to continue.

### Persona Response Behavior
- **D-09:** Live responses should be stylized but concise: measured, theatrical, cool, and dryly witty without long monologues.
- **D-10:** The existing `measured`, `cutting`, and `grandiose` tone presets should steer both the response text and the TTS tone, so live mode matches the existing studio controls.
- **D-11:** The response provider input/schema must include the original-voice boundary, prohibited associations, and tone/persona instructions. Tests must assert generated responses do not claim to be protected characters, real performers, Marvel Loki, Tom Hiddleston, or other unlicensed identities.
- **D-12:** Response generation should include short session memory from recent conversation turns for coherence. Do not persist memory after refresh.

### Interruption And Latency Feedback
- **D-13:** Interrupt should stop current playback immediately, cancel pending response work where possible, mark the turn interrupted or canceled, and return live mode to listening.
- **D-14:** Phase 4 should include both an explicit Interrupt button and best-effort VAD barge-in when reliable enough. The button is a fallback, not a replacement for VAD.
- **D-15:** Record structured stage timings per conversation turn: user speech end to transcript, response text, TTS complete, playback start, and total turn duration.
- **D-16:** Show only a compact total-latency chip on each live turn card. Keep detailed stage timings in backend metadata, API responses, and tests rather than rendering a debug timeline in the normal UI.

### the agent's Discretion
- **D-17:** Downstream agents may choose exact endpoint names, schema names, state-machine enum names, fixture text, and implementation boundaries as long as the decisions above are preserved.
- **D-18:** If reliable VAD barge-in is too risky in the first implementation slice, planners should still include the explicit Interrupt button and represent VAD barge-in as best-effort capability with clear tests for the implemented behavior.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` - Defines the current product direction, Vesper Glass persona boundary, no-login studio-first shape, and Phase 4 starting point after Phase 3.
- `.planning/REQUIREMENTS.md` - Maps Phase 4 to CONV-01 through CONV-05: live mode start, spoken response, persona boundary, interruption/cancel, and latency recording.
- `.planning/ROADMAP.md` - Defines the Phase 4 goal, success criteria, and planned slices: session state/UI controls, persona-safe response and speech loop, interruption and latency metrics.
- `.planning/STATE.md` - Captures current phase position and accumulated Phase 1-3 decisions affecting live conversation.

### Prior Phase Handoff
- `.planning/phases/03-audio-input-and-turn-detection/03-CONTEXT.md` - Locks spoken-input session scope, VAD/STT provider baseline, transcript inspection, and deferred live-conversation behaviors.
- `.planning/phases/03-audio-input-and-turn-detection/03-03-SUMMARY.md` - Summarizes the completed faster-whisper-compatible STT provider, transcript metadata persistence, editable transcript review, and Phase 4 readiness.
- `.planning/phases/03-audio-input-and-turn-detection/03-UI-SPEC.md` - Defines the existing studio surface, spoken input layout, session-scoped turn visibility, and accessibility/copy conventions that Phase 4 should extend.
- `.planning/phases/03-audio-input-and-turn-detection/03-VERIFICATION.md` - Verifies Phase 3 audio-input, VAD, STT, transcript review, and same-origin route behavior that Phase 4 builds on.
- `.planning/phases/02-consented-studio-generation/02-CONTEXT.md` - Locks queued generation jobs, controlled playback URLs, session-scoped attempts, tone presets, and the local object-store pattern.
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md` - Locks the direct root studio route, Vesper Glass identity boundary, backend rights gate, and provider-interface posture.

### Research and Architecture
- `.planning/research/ARCHITECTURE.md` - Defines the live conversation flow, provider boundary, web/API/worker split, session API role, and transport considerations.
- `.planning/research/FEATURES.md` - Defines live conversation with interruption as a v1 differentiator and notes that conversation requires mic capture, VAD, STT, LLM/persona response, and TTS.
- `.planning/research/PITFALLS.md` - Calls out realtime latency, interruption overlap, VAD false starts, and stage timing as core risks for Phases 3 and 4.
- `.planning/research/STACK.md` - Recommends Next.js/FastAPI/provider interfaces, MediaRecorder/Web Audio, VAD/STT/TTS baselines, and notes WebRTC/LiveKit as later transport options when interruption and streaming demand it.

No separate Phase 4 SPEC.md exists as of this discussion.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `apps/web/components/studio-shell.tsx` - Current client component owns root studio state, voice/tone selection, generation jobs, spoken-turn jobs, MediaRecorder capture, polling, transcript review, and controlled playback. Phase 4 should extend this surface with an inline live conversation panel rather than adding a separate route.
- `apps/web/app/globals.css` - Existing custom studio styles cover cards, form groups, status chips, metadata layouts, attempt lists, and responsive behavior. Live turn cards should reuse these patterns and avoid a debug-console look.
- `apps/web/next.config.ts` - Existing same-origin rewrites cover `/generate`, `/generations/:path*`, `/audio-turns`, and `/audio-turns/:path*`. Add conversation routes through the same rewrite pattern.
- `services/api/app/routes/audio_turns.py` - Existing audio-turn route accepts captured audio, validates it, queues background processing, exposes status, and serves controlled input audio artifacts.
- `services/api/app/routes/generate.py` - Existing generation route enforces the backend rights gate, creates queued jobs, exposes status, and serves controlled output audio artifacts.
- `services/api/app/services/audio_turn_jobs.py` and `services/api/app/services/generation_jobs.py` - Existing SQLite-backed job services and object stores provide the persistence and state-transition style for conversation sessions and turns.
- `services/api/app/services/audio_turn_runtime.py` - Existing runtime normalizes captured audio, runs VAD/STT providers, crops to the speech window, and persists transcript/VAD metadata.
- `services/api/app/services/generation_runtime.py` - Existing runtime loads the TTS provider from the approved worker root and stores synthesized audio for playback.
- `services/api/app/schemas/audio_turn.py` and `services/api/app/schemas/generation.py` - Existing Pydantic schemas use strict `extra="forbid"` validation, explicit job status enums, timing fields, provider metadata, and state validation.
- `services/speech-worker/providers/contracts.py` - Existing `VADProvider`, `STTProvider`, `TTSProvider`, and `SpeechToSpeechProvider` contracts are the provider boundary Phase 4 should preserve and extend with a persona/response provider contract.
- `apps/web/tests/audio-input.spec.ts` and `apps/web/tests/studio-generation.spec.ts` - Existing Playwright coverage verifies MediaRecorder mocking, audio-turn polling, transcript handoff, live backend generation, retry, and controlled audio URLs. Phase 4 browser tests should mirror these patterns.

### Established Patterns
- The root route `/` remains the direct no-login studio; avoid landing pages, separate live-mode routes, or saved-history assumptions in Phase 4.
- Browser-visible state is session-scoped. Refresh clearing conversation state is acceptable for v1.
- Backend/provider boundaries are authoritative. Browser code should not generate persona responses, run model-specific STT/VAD/TTS logic, or bypass the rights gate.
- Jobs use `queued`, `running`, `succeeded`, and `failed` states with strict Pydantic records and explicit timing metadata.
- Controlled audio playback uses same-origin API URLs, not raw filesystem paths or inline base64 audio.
- Deterministic fixtures are acceptable for local and browser tests, but provider interfaces should still make the real runtime boundary clear.

### Integration Points
- Web: add an inline live conversation panel near the current spoken input and generation controls, with Start/Stop, listening/thinking/speaking/interrupted states, Interrupt button, compact turn cards, playback, and total-latency chips.
- API: add conversation session and conversation turn routes that create session-scoped records, accept/associate captured user audio, orchestrate STT, persona response, TTS, interruption/cancel, and expose turn status.
- Worker/provider: add a persona response provider contract and deterministic Vesper-safe responder; reuse VAD/STT/TTS providers behind existing contracts.
- Storage: reuse controlled local object-store patterns for input and response audio artifacts; do not add durable saved conversation history.
- Tests: add API tests for session/turn state transitions, persona-boundary assertions, interruption/cancel state, and stage timing; add Playwright tests for live panel start, VAD-driven turn submission or mocked equivalent, response playback, interrupt control, and latency chip.

</code_context>

<specifics>
## Specific Ideas

- The live mode should feel like a conversation panel inside the studio, not a separate product surface.
- VAD remains central: it detects end-of-user-turn after Start conversation and should support best-effort barge-in while the bot is speaking when reliable enough.
- The Interrupt button exists because users need a dependable control even if VAD barge-in is not perfect.
- Keep normal UI latency readable: one total value per turn card; detailed stage timings belong in metadata and tests.
- The deterministic local responder should produce concise, original Vesper Glass style and never mention protected characters or real actors.

</specifics>

<deferred>
## Deferred Ideas

- Streaming-first response audio and deep WebRTC/LiveKit transport selection - defer until the turn-based loop, interruption semantics, and latency records are proven.
- Persistent conversation logs, saved memory, accounts, and libraries - deferred beyond the no-login v1 scope.
- Real LLM provider as the required default - defer until the provider contract and deterministic local responder are in place.
- Detailed live-mode debug timeline in the UI - keep stage timings in metadata/API/tests unless a later diagnostics phase needs a richer surface.
- Multi-provider VAD/TTS/end-to-end speech comparison - belongs to Phase 5 benchmark work.

</deferred>

---

*Phase: 4-Live Conversation Mode*
*Context gathered: 2026-07-12*
