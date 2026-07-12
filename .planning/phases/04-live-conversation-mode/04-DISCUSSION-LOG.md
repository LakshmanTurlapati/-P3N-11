# Phase 4: Live Conversation Mode - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-07-12
**Phase:** 4-Live Conversation Mode
**Areas discussed:** Live Session Shape, Conversation Response Loop, Persona Response Behavior, Interruption And Latency Feedback

---

## Live Session Shape

### Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Inline panel beside current controls | Add a dedicated conversation panel on `/` near spoken input/generation, reusing the existing no-login studio surface and session-scoped patterns. | yes |
| Separate route | Add a `/conversation` page for a cleaner live-mode workspace, but this breaks from the established root-studio pattern. | |
| Replace spoken input section while active | Keep the page compact by swapping the Phase 3 spoken-input controls into live-mode controls when conversation starts. | |
| Other | Freeform preference. | |

**User's choice:** Inline panel beside current controls.
**Notes:** Live conversation should stay in the existing studio instead of becoming a separate page.

### Turn Capture

| Option | Description | Selected |
|--------|-------------|----------|
| VAD-driven live turns | Start conversation arms the mic, detects end-of-turn automatically, then submits the spoken turn without a Stop click. | yes |
| Manual per-turn recording | User clicks Record/Stop for each turn, reusing the Phase 3 capture pattern with less new behavior. | |
| Hybrid | Start conversation arms the mic, but the user can also force-send or stop a turn manually when VAD feels uncertain. | |
| Other | Freeform preference. | |

**User's choice:** VAD-driven live turns.
**Notes:** Phase 4 should feel meaningfully live and should not require Stop for every turn.

### Turn History

| Option | Description | Selected |
|--------|-------------|----------|
| Compact transcript + response cards | Show recent user transcript, generated response text, status, playback, and latency per turn. | yes |
| Minimal current-turn only | Show listening/thinking/speaking state and the latest response, keeping history out of the MVP. | |
| Detailed timeline | Show audio-turn job, VAD metadata, LLM text, TTS job, provider trace, and playback for every turn. | |
| Other | Freeform preference. | |

**User's choice:** Compact transcript + response cards.
**Notes:** Enough for internal evaluation without turning the studio into a debug console.

### Session Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Session-scoped start/stop | Start creates a browser-session conversation record; Stop ends listening/playback and keeps recent turns visible until refresh. | yes |
| Ephemeral toggle only | Start/Stop only changes UI listening state; each turn is independent with no conversation session record. | |
| Persistent conversation log | Start creates a durable conversation record that survives refresh. | |
| Other | Freeform preference. | |

**User's choice:** Session-scoped start/stop.
**Notes:** Conversation state should remain no-login and session-scoped.

---

## Conversation Response Loop

### Primary Loop Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Turn-based live loop with full response clips | After VAD ends the user turn, run STT -> persona text -> TTS as a conversation turn job, then play the complete spoken response. | yes |
| Streaming-first response | Start sending/playing response audio as it is produced, requiring deeper transport and cancellation plumbing immediately. | |
| Text response first, audio second | Show the persona reply text quickly, then attach spoken playback when TTS finishes. | |
| Other | Freeform preference. | |

**User's choice:** Turn-based live loop with full response clips.
**Notes:** Reuse the current job and playback patterns before solving full streaming.

### Record Shape

| Option | Description | Selected |
|--------|-------------|----------|
| First-class conversation-turn record | Create a session turn that links input audio/STT, response text, output generation/audio, status, and latency. | yes |
| Reuse separate records only | Keep audio-turn and generation job records separate and let the browser correlate them in state. | |
| Conversation session record only | Store a session and list lightweight turn IDs, but leave most metadata in existing jobs. | |
| Other | Freeform preference. | |

**User's choice:** First-class conversation-turn record.
**Notes:** Existing services may be reused internally, but the UI should have one coherent turn record.

### Response Provider

| Option | Description | Selected |
|--------|-------------|----------|
| Provider interface with deterministic local default | Add an LLM/persona response provider contract and deterministic Vesper-safe local responder first. | yes |
| Real LLM immediately | Wire a configured LLM provider now, with tests mocking it. | |
| Static canned replies | Use a fixed response for all turns to prove audio plumbing only. | |
| Other | Freeform preference. | |

**User's choice:** Provider interface with deterministic local default.
**Notes:** A real LLM should be swappable later without destabilizing tests or requiring secrets now.

### Failure Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Per-turn failure with recoverable session | Mark the turn failed at the failed stage, show concise error text, keep the session active, and let the next user turn continue. | yes |
| Stop the whole conversation | Any stage failure stops live mode until restart. | |
| Fallback text-only response | If TTS fails, show response text and keep listening. | |
| Other | Freeform preference. | |

**User's choice:** Per-turn failure with recoverable session.
**Notes:** Failed STT/response/TTS stages should not kill the session.

---

## Persona Response Behavior

### Persona Strength

| Option | Description | Selected |
|--------|-------------|----------|
| Stylized but concise | Replies sound measured, theatrical, cool, and dryly witty while remaining useful. | yes |
| Highly theatrical | Lean into elaborate, dramatic, philosophical responses even if answers get longer. | |
| Mostly practical | Keep responses short and helpful with only light stylistic flavor. | |
| Other | Freeform preference. | |

**User's choice:** Stylized but concise.
**Notes:** Avoid long monologues in live mode.

### Tone Presets

| Option | Description | Selected |
|--------|-------------|----------|
| Same presets steer both text and voice | `Measured`, `Cutting`, and `Grandiose` affect response wording and TTS tone together. | yes |
| Tone affects voice only | Keep response text stable and apply tone only to the spoken generation provider. | |
| Separate conversation tone | Add a live-mode-specific tone choice. | |
| Other | Freeform preference. | |

**User's choice:** Same presets steer both text and voice.
**Notes:** Live mode should reuse the current minimal studio controls.

### Persona Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Prompt/schema guard plus test assertions | Provider input includes prohibited associations and tests assert protected-character/real-performer claims do not appear. | yes |
| Prompt-only | Put the safety boundary in the response prompt and rely on model behavior. | |
| Post-generation blocker | Generate freely, then reject responses that mention prohibited associations. | |
| Other | Freeform preference. | |

**User's choice:** Prompt/schema guard plus test assertions.
**Notes:** Safety boundary should be enforceable and regression-tested.

### Session Memory

| Option | Description | Selected |
|--------|-------------|----------|
| Short session memory | Include recent conversation turns in response-provider context, without persistence after refresh. | yes |
| No memory | Each turn stands alone. | |
| Persistent memory | Remember across refresh/sessions. | |
| Other | Freeform preference. | |

**User's choice:** Short session memory.
**Notes:** Coherence matters inside one live session; persistence conflicts with no-login v1.

---

## Interruption And Latency Feedback

### Interrupt Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Stop playback and cancel pending response work where possible | Immediately stop current audio, mark the turn interrupted/canceled, and return to listening. | yes |
| Stop playback only | Pause/stop browser audio but leave backend work untouched. | |
| Disable interrupt until streaming exists | Provide Stop conversation only. | |
| Other | Freeform preference. | |

**User's choice:** Stop playback and cancel pending response work where possible.
**Notes:** Interrupt needs to change user experience and turn state, not only pause the element.

### Barge-In

| Option | Description | Selected |
|--------|-------------|----------|
| Button-first with visible interrupt control | VAD handles user turn endings, but interruption is explicit with an Interrupt button during bot speech. | |
| Auto-barge-in | VAD listens during bot playback and interrupts when it detects the user speaking over the bot. | |
| Both | Keep the button and add best-effort VAD barge-in if feasible. | yes |
| Other | Freeform preference. | |

**User's choice:** Both.
**Notes:** The user asked whether a button means VAD is not being used. Clarification captured: VAD still handles end-of-turn and should support best-effort barge-in when reliable enough; the button is the fallback.

### Timing Fields

| Option | Description | Selected |
|--------|-------------|----------|
| Stage + end-to-end timing | Record user speech end -> transcript, response text, TTS complete, playback start, and total turn duration. | yes |
| End-to-end only | Record one total latency number per turn. | |
| Visible UI timing only | Show rough elapsed time in the UI without structured backend fields. | |
| Other | Freeform preference. | |

**User's choice:** Stage + end-to-end timing.
**Notes:** Structured timing will support Phase 4 debugging and Phase 5 benchmark work.

### UI Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Compact per-turn latency chip | Show one readable total latency value on each turn card; keep stage timings in metadata/API/tests. | yes |
| Detailed stage timings in UI | Show STT, response, TTS, playback-start, and total timings on every turn card. | |
| No visible timing | Record latency only in backend metadata. | |
| Other | Freeform preference. | |

**User's choice:** Compact per-turn latency chip.
**Notes:** Normal UI should stay product-focused rather than diagnostic-heavy.

## the agent's Discretion

- Exact endpoint names, schema names, enum names, fixture response copy, and component boundaries can be chosen by downstream agents.
- Best-effort VAD barge-in may be implemented to the level that can be reliably verified in Phase 4, but the explicit Interrupt control should still exist.

## Deferred Ideas

- Streaming-first response audio and full WebRTC/LiveKit transport selection.
- Persistent conversation logs, saved memory, accounts, and libraries.
- Real LLM as a required default provider.
- Detailed live-mode debug timeline in the UI.
- Multi-provider conversation benchmarking.
