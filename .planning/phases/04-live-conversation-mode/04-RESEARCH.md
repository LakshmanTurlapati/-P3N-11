<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Keep live conversation as an inline panel on the root studio route `/`, near the existing spoken-input and generation controls. Do not add a separate route for Phase 4.
- **D-02:** Starting conversation should arm the mic and use VAD-driven automatic end-of-turn detection. The user should not need to click Stop for every live turn.
- **D-03:** The live panel should show compact recent turn cards with the user transcript, generated response text, status, playback, and a readable per-turn latency chip.
- **D-04:** Start conversation creates a session-scoped conversation record for the current browser session. Stop ends listening/playback and keeps recent turns visible until refresh.
- **D-05:** Optimize Phase 4 for a turn-based live loop with complete response clips: VAD/STT user turn, persona response text, TTS output, then controlled playback.
- **D-06:** Add a first-class conversation-turn record that links input audio/STT, persona response text, output audio, status, and latency. The implementation may reuse existing audio-turn and generation services internally, but the UI should not have to stitch unrelated records together.
- **D-07:** Add a persona/LLM response provider interface with a deterministic Vesper-safe local responder as the default. A real LLM can be swapped in later behind the same contract.
- **D-08:** Failures should be scoped to the individual conversation turn. Mark the failed stage, show concise error text, keep the session recoverable, and allow the next user turn to continue.
- **D-09:** Live responses should be stylized but concise: measured, theatrical, cool, and dryly witty without long monologues.
- **D-10:** The existing `measured`, `cutting`, and `grandiose` tone presets should steer both the response text and the TTS tone, so live mode matches the existing studio controls.
- **D-11:** The response provider input/schema must include the original-voice boundary, prohibited associations, and tone/persona instructions. Tests must assert generated responses do not claim to be protected characters, real performers, Marvel Loki, Tom Hiddleston, or other unlicensed identities.
- **D-12:** Response generation should include short session memory from recent conversation turns for coherence. Do not persist memory after refresh.
- **D-13:** Interrupt should stop current playback immediately, cancel pending response work where possible, mark the turn interrupted or canceled, and return live mode to listening.
- **D-14:** Phase 4 should include both an explicit Interrupt button and best-effort VAD barge-in when reliable enough. The button is a fallback, not a replacement for VAD.
- **D-15:** Record structured stage timings per conversation turn: user speech end to transcript, response text, TTS complete, playback start, and total turn duration.
- **D-16:** Show only a compact total-latency chip on each live turn card. Keep detailed stage timings in backend metadata, API responses, and tests rather than rendering a debug timeline in the normal UI.

### the agent's Discretion
- **D-17:** Downstream agents may choose exact endpoint names, schema names, state-machine enum names, fixture text, and implementation boundaries as long as the decisions above are preserved.
- **D-18:** If reliable VAD barge-in is too risky in the first implementation slice, planners should still include the explicit Interrupt button and represent VAD barge-in as best-effort capability with clear tests for the implemented behavior.

### Deferred Ideas (OUT OF SCOPE)
- Streaming-first response audio and deep WebRTC/LiveKit transport selection - defer until the turn-based loop, interruption semantics, and latency records are proven.
- Persistent conversation logs, saved memory, accounts, and libraries - deferred beyond the no-login v1 scope.
- Real LLM provider as the required default - defer until the provider contract and deterministic local responder are in place.
- Detailed live-mode debug timeline in the UI - keep stage timings in metadata/API/tests unless a later diagnostics phase needs a richer surface.
- Multi-provider VAD/TTS/end-to-end speech comparison - belongs to Phase 5 benchmark work.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONV-01 | User can start a live conversation mode from the web app. | Keep the surface inline on `/`, preserve the client-component shell, and add same-origin conversation routes behind rewrites. |
| CONV-02 | User can speak a turn and receive a spoken response using the selected voice and tone. | Reuse the current session-scoped turn/job patterns, browser capture/playback controls, and the provider boundary for response text + TTS. |
| CONV-03 | System response text follows the original theatrical persona boundary without claiming to be a protected character or real person. | Enforce the boundary in the response-provider schema and tests, using the existing rights-gate vocabulary. |
| CONV-04 | User can interrupt or cancel a spoken response and continue the conversation. | Use browser playback stop/cancel primitives plus a cooperative turn state machine; do not assume background tasks can be hard-killed. |
| CONV-05 | System records basic end-to-end conversation latency for each turn. | Extend the current timing metadata pattern and keep detailed stage timings server-side with only a compact chip in the UI. |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Only consented or licensed reference voices may be cloned.
- The first voice must remain an original theatrical trickster voice and must not be framed as Marvel Loki, Tom Hiddleston, or another protected or unlicensed identity.
- Phase 1 targets a cloud web app using rented GPU infrastructure, so local-only assumptions should not leak into the plan.
- Phase 1 is no-login; prioritize the core speech and generation loop over accounts.
- Studio controls are intentionally minimal; voice, input, tone preset, generate, and live conversation controls are enough for v1.
- Speech components must stay behind provider interfaces so future voice or model swaps do not require rewriting the product.
- The product must balance conversational latency, voice quality, and future scale rather than optimizing only one dimension.
- Voice profiles should carry rights and consent metadata before generation.
- Use the GSD workflow for file-changing work instead of direct edits outside a GSD command.
</user_constraints>

## Summary

Phase 4 should be planned as a turn-state and cancellation problem first, and a UI expansion second. The current codebase already has the right substrate: a client-owned studio shell on `/`, same-origin rewrites to a FastAPI control plane, SQLite-backed session-scoped job records, strict Pydantic schemas, provider interfaces, and deterministic fixtures for the existing speech pipeline [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py].

The main architectural decision is to add a first-class conversation-turn record and cooperative cancel path, not to create a separate live page. The docs and current code both point to a client component boundary for interactive audio controls, same-origin rewrites for API calls, and controlled file serving for audio artifacts, while the browser APIs needed for interruption are `MediaRecorder`, `AbortController`, and `HTMLMediaElement.pause()` [CITED: https://nextjs.org/docs/app/api-reference/directives/use-client] [CITED: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/start] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/AbortController] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause] [CITED: https://fastapi.tiangolo.com/advanced/custom-response/].

**Primary recommendation:** Plan Phase 4 as an inline root-route conversation panel that writes and polls a dedicated conversation-turn record, keeps interruption cooperative, and uses a deterministic local responder behind a provider interface until a real LLM is chosen.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Start/stop live conversation and capture mic input | Browser / Client | API / Backend | The client owns permissions, state, and browser APIs; the API only owns the turn record and server-side validation [CITED: https://nextjs.org/docs/app/api-reference/directives/use-client]. |
| VAD end-of-turn detection and turn segmentation | API / Backend | Speech Worker | The current turn-analysis path already normalizes audio and runs VAD/STT behind provider boundaries; Phase 4 should preserve that split [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/silero_vad_provider.py]. |
| Persona-safe response text generation | API / Backend | Speech Worker | The response provider must enforce the original-voice boundary and short-memory context server-side; the browser should never generate persona text [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py]. |
| TTS synthesis and audio artifact storage | Speech Worker | API / Backend | Existing generation already keeps synthesis behind a worker-root provider and stores controlled audio through the job service; Phase 4 should reuse that pattern [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py]. |
| Playback interruption and cancel UX | Browser / Client | API / Backend | The browser can stop audio immediately, abort polling/fetch, and reflect interrupted state while the backend cooperatively marks the turn canceled [CITED: https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/AbortController]. |
| Conversation latency recording | API / Backend | Browser / Client | Turn timing should live in the server record with only a compact total-latency chip in the UI, matching the existing job timing model [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/audio_turn.py]. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 16.2.9 in repo; 16.2.10 latest registry on 2026-07-01 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites] | Web studio UI and rewrites | The live panel stays inline on `/` and needs the App Router client boundary plus same-origin rewrites already in use. |
| React | 19.2.7 in repo; 19.2.7 latest registry on 2026-06-01 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: https://nextjs.org/docs/app/api-reference/directives/use-client] | Interactive UI | Client components are required for state, effects, and browser APIs in the live panel. |
| TypeScript | 6.0.3 in repo; 7.0.2 latest registry on 2026-07-08 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Web and schema typing | Current code already uses typed job records and explicit state objects; Phase 4 should keep that discipline. |
| FastAPI | 0.138.2 in repo; 0.139.0 latest registry on 2026-07-01 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/] | API control plane | The existing route/service pattern is already FastAPI-native and same-origin compatible. |
| Python | 3.11.12 in the project venv; project range 3.10-3.12 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.venv/bin/python] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | Backend and worker runtime | The speech-worker and API code already run in a Python 3.11 environment. |
| Pydantic | 2.13.4 in repo; 2.13.4 latest registry on 2026-05-06 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] [CITED: https://docs.pydantic.dev/latest/concepts/validators/] [CITED: https://docs.pydantic.dev/latest/concepts/config/] | Strict nested validation | Current schemas use `ConfigDict`, `field_validator`, and `model_validator` for immutable job-state rules. |
| @playwright/test | 1.61.1 in repo; 1.61.1 latest registry on 2026-06-23 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts] | Browser verification | The existing root and audio-input regression tests already prove the studio shell pattern. |
| pytest | 9.1.1 in repo; 9.1.1 latest registry on 2026-06-19 [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | API and worker tests | The API and worker suites already use pytest with strict fixtures and deterministic fallbacks. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| MediaRecorder / Web Audio API | Browser-native | Mic capture and chunked audio delivery | Use for the live mic surface if the first slice stays on same-origin browser capture. |
| AbortController | Browser-native | Abort fetch/polling and other async work | Use for interrupt and teardown flows in the browser, and for canceling in-flight requests [CITED: https://developer.mozilla.org/en-US/docs/Web/API/AbortController]. |
| HTMLMediaElement | Browser-native | Playback stop/pause/reset | Use to stop generated speech immediately on interrupt [CITED: https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause]. |
| FileResponse | FastAPI response helper | Controlled audio serving | Use for same-origin audio artifacts instead of raw filesystem paths [CITED: https://fastapi.tiangolo.com/advanced/custom-response/]. |
| BackgroundTasks | FastAPI helper | Simple follow-up work | Acceptable for non-interruptible follow-up jobs, but not a hard-cancel boundary [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/]. |
| SQLite | Built-in | Session-scoped turn/job records | Matches the current job-service pattern and keeps Phase 4 lightweight. |
| FFmpeg | Current stable; missing locally | Audio normalization | Required if response audio needs normalization; the current workspace does not have it, so the plan needs a fixture or install fallback [VERIFIED: local command]. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Inline client panel on `/` | Separate `/conversation` route | Cleaner in isolation, but it breaks the established studio surface and the locked Phase 4 decision. |
| MediaRecorder chunking | Web Audio `AudioWorklet` frame capture | Lower-level timing, but higher implementation cost and not necessary for the first proof if barge-in remains best-effort. |
| FastAPI `BackgroundTasks` | Durable queue / worker cancellation API | Stronger cancellation semantics, but more infrastructure than the first slice needs. |
| Session-local turn memory | Durable conversation memory | Easier to recover, but it violates the no-login v1 scope. |

**Installation:**
```bash
# No new packages are required for Phase 4; reuse the existing Next.js/FastAPI/Playwright stack.
```

**Version verification:** Current registry checks showed `next` 16.2.10 (2026-07-01), `react` 19.2.7 (2026-06-01), `react-dom` 19.2.7 (2026-06-01), `@playwright/test` 1.61.1 (2026-06-23), `fastapi` 0.139.0 (2026-07-01), `pydantic` 2.13.4 (2026-05-06), and `pytest` 9.1.1 (2026-06-19) [CITED: npm view / pip index version checks in this session].

## Architecture Patterns

### System Architecture Diagram

```text
User speaks or clicks Start on `/`
    -> `StudioShell` client component owns session-local live state
    -> Browser capture uses MediaRecorder / Web Audio
    -> VAD detects end-of-turn or barge-in
        -> if interrupted: stop playback immediately, mark current turn canceled, return to listening
        -> else: submit turn audio + session state to same-origin conversation route
    -> API creates a first-class conversation-turn record
    -> Response provider generates persona-safe text with short session memory
    -> TTS provider synthesizes response audio
    -> Worker/API stores controlled audio artifact + timing metadata
    -> Browser polls turn status and plays controlled audio URL
    -> UI renders compact turn card and total-latency chip
```

The diagram deliberately keeps transport abstract. The locked scope proves the turn-based loop, interruption semantics, and latency recording before any WebRTC/LiveKit decision is made [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].

### Recommended Project Structure
```text
apps/
  web/
    app/
    components/
    tests/
services/
  api/
    app/
      routes/
      schemas/
      services/
      voice_registry/
  speech-worker/
    providers/
    audio/
```

Likely Phase 4 additions should stay inside the existing folders rather than creating a new app shell:

```text
apps/web/components/
  studio-shell.tsx
  conversation-panel.tsx  # optional subcomponent, if the root shell grows too large
services/api/app/
  routes/conversation*.py
  schemas/conversation*.py
  services/conversation*.py
apps/web/tests/
  conversation-mode.spec.ts  # or an extension of audio-input.spec.ts if the same file remains readable
```

### Pattern 1: Inline client shell with session-local state
**What:** Keep the live conversation UI in the root studio shell and manage live turn state in client state plus polling.
**When to use:** Always for the first slice, because the live mode must remain on `/` and the browser owns mic permission and playback control.
**Example:**
```tsx
// Source: [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx]
"use client";

const [activeJobId, setActiveJobId] = useState<string | null>(null);
const [spokenTurns, setSpokenTurns] = useState<AudioTurnJobRecord[]>([]);
```

### Pattern 2: First-class turn record with nested status/timing metadata
**What:** Model the conversation turn as the authoritative record and keep status, attempt data, and timing nested together.
**When to use:** For every conversation turn, including interrupted and failed turns.
**Example:**
```py
# Source: [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py]
class GenerationJobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    timing: GenerationTiming
    attempt: GenerationAttempt
```

### Pattern 3: Same-origin rewrite bridge for browser/API separation
**What:** Keep the browser on the root origin and rewrite API paths to the FastAPI control plane.
**When to use:** For all conversation/session/status/audio routes in Phase 4.
**Example:**
```ts
// Source: [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts]
async rewrites() {
  return [
    { source: "/audio-turns/:path*", destination: `${apiBaseUrl}/audio-turns/:path*` },
  ];
}
```

### Pattern 4: Cooperative interruption instead of hard preemption
**What:** Stop browser playback immediately, abort pending fetch/poll work, and mark the turn interrupted or canceled in the record.
**When to use:** For the explicit Interrupt button and any best-effort VAD barge-in path.
**Example:**
```ts
// Source: [CITED: https://developer.mozilla.org/en-US/docs/Web/API/AbortController]
const controller = new AbortController();
await fetch("/conversation-turns", { signal: controller.signal });
audio.pause();
controller.abort();
```

### Anti-Patterns to Avoid
- **Separate conversation route:** It drifts away from the locked inline-studio decision and adds a second product surface [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].
- **UI-only conversation state:** The browser should reflect server-owned turn records, not become the source of truth.
- **Hard-cancel assumptions about background work:** FastAPI `BackgroundTasks` are for after-response follow-up, so conversation cancel needs a cooperative design [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/].
- **Debug-timeline overload in the UI:** Keep detailed stage timings in metadata and tests; render only a compact total-latency chip [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Conversation session lifecycle | Ad hoc browser flags or merged generation history | First-class conversation session + turn records | The session record needs status, timing, and recovery semantics [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md]. |
| Interrupt / cancel behavior | One-off pause buttons with no server state | Cooperative cancel flag + immediate playback stop | Playback should stop instantly, but the backend still needs a consistent turn state [CITED: https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/AbortController]. |
| Persona safety | Free-form prompt text from the browser | Response-provider schema + backend tests | The original-voice boundary must be enforced server-side, not just in the UI [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py]. |
| Audio artifact serving | Raw filesystem paths or base64 blobs | FastAPI `FileResponse` on same-origin routes | Controlled serving keeps artifacts auditable and avoids path leakage [CITED: https://fastapi.tiangolo.com/advanced/custom-response/]. |
| Audio capture timing | Assume `MediaRecorder` timeslices are exact | Record relative timings separately from blob arrival | The browser API explicitly says `timeslice` is not exact [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/start]. |

**Key insight:** If a turn cannot be canceled, reconciled, and measured, it is not yet a live conversation system; it is just a sequence of clips.

## Common Pitfalls

### Pitfall 1: Treating `MediaRecorder` as exact realtime streaming
**What goes wrong:** Turn timing looks better on paper than it is in the browser, and barge-in feels delayed or inconsistent.
**Why it happens:** `MediaRecorder.start(timeslice)` produces blobs on a schedule, but MDN explicitly notes that the intervals are not exact [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/start].
**How to avoid:** Treat `MediaRecorder` as a capture transport, not a clock; store turn timing separately in the API record.
**Warning signs:** The UI depends on blob arrival time to infer end-of-turn or latency.

### Pitfall 2: Assuming background tasks can be hard-canceled
**What goes wrong:** The interrupt button stops playback, but the server continues work and later overwrites the turn state.
**Why it happens:** FastAPI frames `BackgroundTasks` as after-response follow-up work, not a cancelable job system [CITED: https://fastapi.tiangolo.com/tutorial/background-tasks/].
**How to avoid:** Model cancellation as a cooperative state transition, and have the runtime check cancel state between stages.
**Warning signs:** Late completions resurrect interrupted turns.

### Pitfall 3: Letting the browser become the source of truth
**What goes wrong:** Refreshes, retries, or race conditions corrupt turn history.
**Why it happens:** Session-local React state is easy to mutate, but the live system needs auditable turn records.
**How to avoid:** Poll or fetch the authoritative conversation-turn record and derive the UI from it.
**Warning signs:** A page refresh loses the only copy of the turn's state.

### Pitfall 4: Persona leakage or protected-character drift
**What goes wrong:** The live responder starts sounding like a protected character or performer.
**Why it happens:** Prompt text alone is too weak if the schema and tests do not enforce the original-voice boundary.
**How to avoid:** Put the boundary in the response-provider input/schema and regression-test for prohibited names and associations.
**Warning signs:** Any response claims to be Loki, Tom Hiddleston, or another unlicensed identity.

### Pitfall 5: Overloading the normal UI with diagnostics
**What goes wrong:** The live panel becomes a debug console.
**Why it happens:** Detailed stage timings are tempting to render because they are available.
**How to avoid:** Keep only one compact latency chip on the turn card and move the rest to metadata/tests.
**Warning signs:** The main conversation cards become hard to scan.

## Code Examples

Verified patterns from official sources and the current codebase:

### Same-Origin Rewrite Bridge
```ts
// Source: [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts] [CITED: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites]
async rewrites() {
  return [
    { source: "/generate", destination: `${apiBaseUrl}/generate` },
    { source: "/audio-turns/:path*", destination: `${apiBaseUrl}/audio-turns/:path*` },
  ];
}
```

### Client-Side Interrupt Controls
```ts
// Source: [CITED: https://nextjs.org/docs/app/api-reference/directives/use-client] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/AbortController]
"use client";

const controller = new AbortController();
audio.pause();
audio.currentTime = 0;
controller.abort();
```

### Strict Nested Schema Validation
```py
# Source: [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [CITED: https://docs.pydantic.dev/latest/concepts/validators/] [CITED: https://docs.pydantic.dev/latest/concepts/config/]
class ConversationTurn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_status(self) -> "ConversationTurn":
        ...
        return self
```

### Controlled Audio Serving
```py
# Source: [CITED: https://fastapi.tiangolo.com/advanced/custom-response/]
return FileResponse(
    path=audio_path,
    media_type="audio/wav",
    filename=f"{turn_id}.wav",
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate live conversation route | Inline live panel on `/` | Phase 4 context, 2026-07-12 | Keeps the studio single-surface and avoids adding a second product entry point [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md]. |
| Manual stop for every turn | VAD-driven end-of-turn with an explicit interrupt fallback | Phase 4 context, 2026-07-12 | Makes the interaction feel conversational while preserving a dependable cancel button. |
| UI debug timeline | Compact latency chip plus backend stage metadata | Phase 4 context, 2026-07-12 | Keeps the normal UI readable and shifts diagnostic detail to the backend/tests. |
| Browser-only speech logic | Server-owned provider boundary and deterministic local responder | Phase 4 context, 2026-07-12 | Preserves auditability and keeps model swaps isolated behind a contract. |

**Deprecated/outdated:**
- Persistent conversation history in v1: deferred by the phase context and the no-login product scope [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].
- Final WebRTC/LiveKit transport selection: deferred until the turn-based loop and interruption semantics are proven [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].
- Real LLM default: deferred until the provider contract exists and the deterministic local responder is in place [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].

## Assumptions Log

All claims in this research were verified from the current codebase, official docs, registry checks, or explicit phase/context decisions. No additional user confirmation is needed for the planning baseline.

## Open Questions

1. **What is the minimal live transport for Phase 4?**
   - What we know: The phase is explicitly turn-based and defers final WebRTC/LiveKit selection [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/phases/04-live-conversation-mode/04-CONTEXT.md].
   - What's unclear: Whether the first slice should rely on chunked HTTP posts, polling, or a WebSocket bridge for live turn exchange.
   - Recommendation: Keep the API contract transport-agnostic and choose the simplest mechanism that satisfies interruption and latency measurement.

2. **How much cancellation must be hard versus cooperative?**
   - What we know: The browser can stop playback immediately, and the backend can mark a turn canceled or interrupted.
   - What's unclear: Whether the first slice needs a runtime that can truly abort synthesis mid-call.
   - Recommendation: Require cooperative cancellation in the turn state machine and treat provider abort as best-effort.

3. **How much short-term memory should the default responder keep?**
   - What we know: The phase allows short session memory but forbids persistent memory after refresh.
   - What's unclear: Exact window size and schema for recent-turn context.
   - Recommendation: Keep it small and explicit so the response provider remains deterministic and testable.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Next.js build/start and Playwright tooling | ✓ | v24.2.0 | Use the installed Node runtime |
| pnpm | Web dependency management and scripts | ✓ | 10.30.3 | Use `npm` only if absolutely necessary |
| Python venv | API and worker tests/runtime | ✓ | 3.11.12 | Use `./.venv/bin/python`, not the global 3.13.5 |
| FastAPI | API runtime | ✓ | 0.138.2 | None |
| Pydantic | Schema/runtime validation | ✓ | 2.13.4 | None |
| pytest | API and worker tests | ✓ | 9.1.1 | None |
| Playwright | Browser verification | ✓ | 1.61.1 | Use the existing Playwright config |
| ffmpeg | Audio normalization | ✗ | — | Use fixture WAV output or install ffmpeg in the worker image before real normalization |

**Missing dependencies with no fallback:**
- None for Phase 4 planning.

**Missing dependencies with fallback:**
- `ffmpeg` - fallback exists for fixture/WAV-based tests, but a real synthesis path should install it in the worker/runtime image.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 9.1.1` for API/worker tests and `@playwright/test 1.61.1` for browser verification |
| Config file | `pyproject.toml`, `apps/web/playwright.config.ts` |
| Quick run command | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -x` |
| Full suite command | `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && pnpm --dir apps/web exec playwright test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|-----------|-----------|-------------------|-------------|
| CONV-01 | User can start live conversation mode from the web app and see the inline panel on `/`. | browser/e2e | `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "start conversation"` | ❌ Wave 0 |
| CONV-02 | User speech produces a spoken response using the selected voice and tone. | integration + browser/e2e | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "response or tone" -x && pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "response"` | ❌ Wave 0 |
| CONV-03 | Response text stays inside the original theatrical boundary. | unit | `./.venv/bin/python -m pytest services/api/tests/test_conversation_provider.py -k "persona" -x` | ❌ Wave 0 |
| CONV-04 | User can interrupt or cancel a spoken response and continue. | browser/e2e + unit | `pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "interrupt" && ./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "cancel" -x` | ❌ Wave 0 |
| CONV-05 | System records end-to-end conversation latency for each turn. | unit + browser/e2e | `./.venv/bin/python -m pytest services/api/tests/test_conversation_jobs.py -k "latency" -x && pnpm --dir apps/web exec playwright test tests/conversation-mode.spec.ts -g "latency"` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** run the smallest relevant conversation test slice first.
- **Per wave merge:** run the full pytest + Playwright suites once the conversation tests exist.
- **Phase gate:** full suite green before `$gsd-verify-work`.

### Wave 0 Gaps
- [ ] `services/api/tests/test_conversation_jobs.py` - session/turn state transitions, cancel state, and latency metadata.
- [ ] `services/api/tests/test_conversation_provider.py` - persona-boundary assertions and short-memory behavior.
- [ ] `services/speech-worker/tests/test_conversation_provider.py` - deterministic local responder and tone steering.
- [ ] `apps/web/tests/conversation-mode.spec.ts` - root-panel start, response playback, interrupt control, and latency chip.
- [ ] `services/api/tests/conftest.py` or a sibling fixture module - conversation session fixtures and deterministic provider stubs.
- [ ] `services/api/app/routes/conversation*.py`, `services/api/app/schemas/conversation*.py`, `services/api/app/services/conversation*.py` - the implementation seams these tests will drive.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | v1 is no-login; avoid adding auth complexity into the Phase 4 slice. |
| V3 Session Management | yes | Use an ephemeral conversation-session id or equivalent server-owned session record; keep browser-visible state scoped to that session. |
| V4 Access Control | yes | Only the current session should be able to read or cancel its own conversation-turn records and controlled audio URLs. |
| V5 Input Validation | yes | Keep strict Pydantic schemas, MIME/size checks, and provider-bound response validation. |
| V6 Cryptography | no | No new cryptography work is needed; do not hand-roll any. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Transcript or response text injection into the UI | Tampering / XSS | Render text as text only, never as HTML, and keep the transcript handoff explicit. |
| Oversized or malformed audio payloads | DoS | Validate content type and size before queueing or processing. |
| Interrupt race conditions | Tampering / DoS | Use a cooperative cancel flag plus immediate playback stop, and ignore late completions. |
| Raw audio path disclosure | Information disclosure | Serve audio only through controlled same-origin routes and `FileResponse`. |
| Persona drift into protected identity claims | Repudiation / policy bypass | Enforce the original-voice boundary in the provider schema and regression tests. |

## Sources

### Primary (HIGH confidence)
- [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx) - current client shell, session-local state, polling, mic/upload capture, playback, and separate spoken/generation lists.
- [apps/web/next.config.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts) - same-origin rewrite bridge for browser/API separation.
- [apps/web/tests/audio-input.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/audio-input.spec.ts) - existing mic/upload, transcript, and accessibility browser coverage.
- [apps/web/tests/studio-generation.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/studio-generation.spec.ts) - generation/retry/playback browser coverage and same-origin audio URL assertions.
- [apps/web/tests/root-route.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/root-route.spec.ts) - root-route smoke contract.
- [services/api/app/main.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py) - router mounting.
- [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py) - generation route shape and controlled audio serving.
- [services/api/app/routes/audio_turns.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/audio_turns.py) - audio-turn route shape and controlled artifact serving.
- [services/api/app/services/generation_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py) - SQLite/object-store job service and retry lineage.
- [services/api/app/services/audio_turn_jobs.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py) - session-scoped spoken-turn job service.
- [services/api/app/services/generation_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py) - provider loading, fixture failure seam, and synthesis pipeline.
- [services/api/app/services/audio_turn_runtime.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_runtime.py) - VAD/STT runtime and normalization bridge.
- [services/api/app/schemas/generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py) - strict job/timing schema pattern.
- [services/api/app/schemas/audio_turn.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/audio_turn.py) - strict turn/timing schema pattern.
- [services/api/app/schemas/voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py) - rights and boundary schema.
- [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py) - backend rights enforcement.
- [services/api/app/voice_registry/bundled_voice.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py) - bundled original voice profile.
- [services/speech-worker/providers/contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py) - provider boundary.
- [services/speech-worker/providers/cosyvoice_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/cosyvoice_provider.py) - current TTS adapter.
- [services/speech-worker/providers/faster_whisper_stt_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/faster_whisper_stt_provider.py) - current STT adapter.
- [services/speech-worker/providers/silero_vad_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/silero_vad_provider.py) - current VAD adapter.
- [services/speech-worker/tests/test_provider_contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/tests/test_provider_contracts.py) - provider-swappability regression.
- [services/speech-worker/tests/test_audio_turn_providers.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/tests/test_audio_turn_providers.py) - deterministic VAD/STT fixture coverage.

### Secondary (MEDIUM confidence)
- [Next.js rewrites docs](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites)
- [Next.js use client docs](https://nextjs.org/docs/app/api-reference/directives/use-client)
- [MDN MediaRecorder.start](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/start)
- [MDN AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [MDN HTMLMediaElement.pause](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause)
- [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [FastAPI FileResponse](https://fastapi.tiangolo.com/advanced/custom-response/)
- [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic config](https://docs.pydantic.dev/latest/concepts/config/)
- `npm view` and `pip index versions` checks in this session for `next`, `react`, `react-dom`, `@playwright/test`, `fastapi`, `pydantic`, `pytest`, and `typescript`.

### Tertiary (LOW confidence)
- None. No low-confidence external claims are needed for this phase plan.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - the codebase and registry checks confirm the current pinned stack, but the exact live transport and cancellation implementation remain intentionally open.
- Architecture: HIGH - the current code, phase context, and official docs align on inline client UI, same-origin rewrites, controlled audio serving, and session-scoped records.
- Pitfalls: MEDIUM - several pitfalls are directly documented in the codebase and docs, while the cancellation implications are partly inferred from the browser and FastAPI behavior.

**Research date:** 2026-07-12
**Valid until:** 2026-08-11, or sooner if the stack version, browser API behavior, or conversation transport decision changes.
