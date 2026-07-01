# Phase 2: Consented Studio Generation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-07-01
**Phase:** 2-Consented Studio Generation
**Areas discussed:** First Playable Voice Bar, Generation Job Shape, Tone Preset Set, Playback And Metadata Surface

---

## First Playable Voice Bar

### Provider completion bar

| Option | Description | Selected |
|--------|-------------|----------|
| Safe baseline | Use a real server-side TTS adapter that produces playable original/safe audio without requiring a cloned reference voice. | yes |
| Consent clone first | Do not count Phase 2 as done until a consented/licensed reference-driven voice can generate the first playable clip. | |
| Hybrid fallback | Support reference-driven generation when rights metadata is present, but fall back to a safe baseline provider for the first loop. | |

**User's choice:** Agent discretion.
**Notes:** Default locked as safe baseline because it validates the real playback loop without assuming a cloned consented reference is available.

### Vesper similarity bar

| Option | Description | Selected |
|--------|-------------|----------|
| Prototype audition | Playable and tone-steered, but may sound like an early baseline rather than final theatrical Vesper. | yes |
| Close character read | Strongly evoke Vesper's measured, icy, sarcastic delivery before the phase counts as complete. | |
| Quality gate only | Require clean playable audio, leaving voice character quality to benchmark work. | |

**User's choice:** Prototype audition.
**Notes:** Phase 2 should not overpromise final Vesper voice quality.

### Provider availability bar

| Option | Description | Selected |
|--------|-------------|----------|
| Real provider required for manual demo | Tests may use fixtures, but a configured real provider must produce playable audio locally or in intended runtime. | yes |
| Fixture acceptable for demo | Deterministic generated audio fixture can satisfy UI/playback while provider adapter is contract-tested. | |
| Provider optional behind flag | Ship both paths and silently fall back to fixture audio when the real provider fails. | |

**User's choice:** Real provider required for manual demo.
**Notes:** Fixtures are acceptable in tests, not as the completion proof.

### Provider preference

| Option | Description | Selected |
|--------|-------------|----------|
| Open-source/offline adapter | Prefer open-source or open-weight TTS behind the provider interface, even if setup is heavier. | yes |
| Cloud API adapter | Use a commercial TTS API if it gets the first playable loop working fastest. | |
| Dual-path spike | Plan both an open-source adapter and a cloud API fallback in Phase 2. | |

**User's choice:** Open-source/offline adapter.
**Notes:** Matches the project direction and avoids early dependency on a hosted voice API.

### Consent/reference intake

| Option | Description | Selected |
|--------|-------------|----------|
| Metadata only | Support consent/license notes in backend data/schema where needed, but no reference-audio intake UI. | yes |
| Minimal notes field | Add a simple internal consent/license notes field in the studio surface before generation. | |
| Reference upload/recording | Add upload/record reference-audio intake now so cloned generation can use it. | |

**User's choice:** Metadata only.
**Notes:** Reference-audio intake UI is deferred.

### Cloning-capable candidates

| Option | Description | Selected |
|--------|-------------|----------|
| Research candidates, implement one feasible baseline | Research license/runtime fit, then implement the safest feasible real provider behind TTS interface. | yes |
| Must implement cloning-capable provider | Phase 2 should specifically implement a cloning/style-transfer-capable provider. | |
| Defer cloning entirely | Use generic TTS in Phase 2 and leave cloning providers to Phase 5 benchmarking. | |

**User's choice:** Research candidates, implement one feasible baseline.
**Notes:** Research may select a cloning-capable provider, but final cloning quality is not required.

### Generic baseline labeling

| Option | Description | Selected |
|--------|-------------|----------|
| Allowed with clear labeling | Generic baseline audio is acceptable if labeled as prototype and not final Vesper quality. | yes |
| Not allowed | Any playable result shown as Vesper should sound meaningfully like the intended profile. | |
| Only in dev mode | Generic baseline audio may be used in tests/dev only. | |

**User's choice:** Allowed with clear labeling.
**Notes:** UI/metadata must avoid implying protected-character, performer, or final Vesper quality.

### Audio delivery mode

| Option | Description | Selected |
|--------|-------------|----------|
| Complete clips only | Return/store complete generated clips for playback; leave streaming to live conversation work. | yes |
| Streaming-capable now | Provider should support partial/streamed audio even if UI plays after completion. | |
| Provider-dependent | Accept either complete clips or streaming depending on selected provider. | |

**User's choice:** Complete clips only.
**Notes:** Streaming is deferred to live conversation.

---

## Generation Job Shape

### Lifecycle shape

| Option | Description | Selected |
|--------|-------------|----------|
| Job lifecycle | Create a generation job with status/progress/result metadata, even if local providers finish quickly. | yes |
| Synchronous response | Keep `POST /generate` returning the final audio result directly for Phase 2. | |
| Hybrid wrapper | Keep `POST /generate` for UI but internally create a job and return when complete. | |

**User's choice:** Job lifecycle.
**Notes:** Real TTS can be slow or cold-started.

### Progress detail

| Option | Description | Selected |
|--------|-------------|----------|
| Coarse states | `queued`, `running`, `succeeded`, `failed`, with user-friendly loading/error text. | yes |
| Stage trace | Include visible stages such as rights gate, provider call, normalization, storage, and URL creation. | |
| Percent progress | Show a numeric percentage/progress bar. | |

**User's choice:** Coarse states.
**Notes:** Keep visible state simple for the first real generation loop.

### Retry behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Retry same request | Reuse last text, voice, and tone to create a new job after failure while keeping failed metadata visible. | yes |
| Retry same job | Re-run provider under the same job ID and mutate its status. | |
| Clear and retry | Clear failed state and submit a new request with no visible failed history. | |

**User's choice:** Retry same request.
**Notes:** Failed attempts stay inspectable.

### Slow generation behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Keep waiting with status | Keep job visible as running and allow the user to wait or retry after failure. | yes |
| Client timeout marks failed | Browser marks job failed after a fixed timeout. | |
| Auto-retry once | Automatically retry a slow or failed provider call before showing error. | |

**User's choice:** Keep waiting with status.
**Notes:** Do not fail just because client-side waiting crossed an arbitrary threshold.

---

## Tone Preset Set

### Initial presets

| Option | Description | Selected |
|--------|-------------|----------|
| Three focused presets | `Measured`, `Cutting`, and `Grandiose`; small enough to validate audible differences. | yes |
| Four theatrical presets | `Measured`, `Honeyed`, `Icy`, and `Cynical`; more expressive but harder to distinguish. | |
| Neutral plus style presets | `Neutral`, `Vesper`, and `Sharper Vesper`; clearer baseline comparison but less polished. | |

**User's choice:** Three focused presets.
**Notes:** These names should appear in Phase 2 planning unless research uncovers a strong implementation conflict.

### Preset control scope

| Option | Description | Selected |
|--------|-------------|----------|
| Prompt/style metadata only | Presets map to text/style instructions; no numeric sliders in Phase 2. | yes |
| Provider parameters too | Presets may also adjust provider-specific speed, emotion, temperature, or reference options. | |
| UI labels only | Presets are stored in metadata but do not affect generation until provider support is proven. | |

**User's choice:** Prompt/style metadata only.
**Notes:** Keep provider-specific knobs hidden for now.

### Preset explanation

| Option | Description | Selected |
|--------|-------------|----------|
| Compact descriptions | Each preset gets a short one-line description near the selector, without exposing prompt internals. | yes |
| Detailed prompt preview | Show the style instructions sent to the provider. | |
| No descriptions | Only show preset names and let output make the difference. | |

**User's choice:** Compact descriptions.
**Notes:** Keep the studio product-like rather than a prompt editor.

### Preset safety boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Preset-safe by construction | Every preset includes original-voice boundary and prohibited-association guard. | yes |
| Global boundary only | Keep safety in the voice profile and rights gate, not duplicated in each preset. | |
| Warn but allow | Warn if protected associations appear, but still generate. | |

**User's choice:** Preset-safe by construction.
**Notes:** No preset may request a protected character or real performer.

---

## Playback And Metadata Surface

### Generated clip display

| Option | Description | Selected |
|--------|-------------|----------|
| Latest plus recent attempts | Show current playable clip prominently and keep recent in-session attempts with status/metadata. | yes |
| Latest only | Replace the result area with only the newest clip and its metadata. | |
| Full take list | Treat every generation as a take in a larger session list with comparison controls. | |

**User's choice:** Latest plus recent attempts.
**Notes:** Full comparison controls are out of scope.

### Visible metadata

| Option | Description | Selected |
|--------|-------------|----------|
| Operational essentials | Voice, tone, provider, status, duration/timing, and rights approval. | yes |
| Full provider trace | Include rights gate, provider call, normalization, storage, and result assembly details. | |
| Minimal product UI | Only show voice, tone, and audio duration; keep provider/timing hidden. | |

**User's choice:** Operational essentials.
**Notes:** Enough metadata for internal debugging without making the studio a debug log viewer.

### Audio storage and serving

| Option | Description | Selected |
|--------|-------------|----------|
| Local object-store abstraction | Store files under a local object-storage directory through an interface, returning controlled playback URLs. | yes |
| Inline audio payload | Return base64 or bytes directly in the job result. | |
| Cloud bucket now | Require S3-compatible storage in Phase 2. | |

**User's choice:** Local object-store abstraction.
**Notes:** Cloud bucket is deferred to deployment hardening.

### Refresh persistence

| Option | Description | Selected |
|--------|-------------|----------|
| In-session only | Attempts are visible during current browser session; no durable clip library. | yes |
| Persist latest job | Reloading can show the most recent generated clip/job metadata. | |
| Persistent local history | Keep a local no-login history of recent clips. | |

**User's choice:** In-session only.
**Notes:** Saved clip history remains out of v1 scope.

---

## the agent's Discretion

- The user answered "you decide" for the initial provider completion bar. The agent selected the safe-baseline path because it best fits the roadmap, rights constraints, and need to prove a real end-to-end loop.

## Deferred Ideas

- Reference-audio upload/recording and consent intake UI.
- Streaming/partial audio.
- Durable clip library and persisted history.
- Detailed tone sliders and provider-specific controls.
- Cloud object bucket requirement.
