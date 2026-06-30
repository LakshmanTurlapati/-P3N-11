# Phase 1: No-Login Vertical Skeleton - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-30
**Phase:** 1-No-Login Vertical Skeleton
**Areas discussed:** First Studio Surface, Bundled Voice Identity, Rights Gate UX, Stub Generation Feedback

---

## First Studio Surface

### First screen feel

| Option | Description | Selected |
|--------|-------------|----------|
| Focused studio | A single work surface with voice selection, approval status, and a generation test action; polished enough to feel real without building phase 2 controls early. | yes |
| Lean harness | A sparse developer-style page optimized for proving API and provider wiring, with minimal visual polish. | |
| Cinematic studio | A more theatrical interface that establishes the voice mood strongly, at the cost of spending more phase 1 effort on presentation. | |

**User's choice:** Focused studio.

### Entry route

| Option | Description | Selected |
|--------|-------------|----------|
| Root opens studio | `/` shows the studio directly. Best fit for a no-login internal MVP with no landing-page detour. | yes |
| Dedicated `/studio` route | `/studio` holds the app, while `/` can redirect or show a minimal project entry. | |
| Split routes | `/studio` for generation testing and `/conversation` reserved early for the later live mode shell. | |

**User's choice:** User said "you decide." Agent selected root `/` opening the studio directly.

### Visible controls

| Option | Description | Selected |
|--------|-------------|----------|
| Voice-first control set | Voice selector, voice profile card, approval/rights status, and a single stub generation action. Keeps phase 1 aligned to its actual scope. | yes |
| Early studio placeholders | Also show disabled text input and tone preset controls to preview Phase 2. Helps communicate direction, but risks building UI before behavior exists. | |
| System wiring panel | Show voice selection plus provider-interface/status details for VAD, STT, TTS, and S2S. Useful for internal debugging, less product-like. | |

**User's choice:** Voice-first control set.

### Visual tone

| Option | Description | Selected |
|--------|-------------|----------|
| Restrained theatrical | Clean studio UI with subtle stage-like cues in copy, typography, and contrast; avoids looking like a fan/character page. | yes |
| Plain operational | Quiet dashboard/tool styling with minimal persona atmosphere; safest and fastest. | |
| Highly atmospheric | Strong theatrical lighting, dramatic visuals, and mood-heavy presentation; memorable but more expensive and easier to overdo. | |

**User's choice:** Restrained theatrical.

**Notes:** User chose to move to the next area after these decisions.

---

## Bundled Voice Identity

### Voice name

| Option | Description | Selected |
|--------|-------------|----------|
| The Aureate Stranger | Theatrical, charming, and slightly cold; suggests honeyed speech without referencing a protected character. | |
| Vesper Glass | Icy, polished, and philosophical; more abstract and less obviously trickster. | yes |
| Silvertongue | Directly communicates persuasive theatrical wit, but it is more archetypal and less distinctive. | |

**User's choice:** User clarified that the previous naming question should use Vesper Glass.

### Persona framing

| Option | Description | Selected |
|--------|-------------|----------|
| Archetype-safe traits | Measured theatrical delivery, cool charm, philosophical cynicism, and honey-edged sarcasm. Clear vibe without protected-character language. | yes |
| Minimal label | Original theatrical voice profile. Safest and shortest, but less useful for internal testing. | |
| Verbose profile note | A longer paragraph describing motivations, temperament, and performance notes. More expressive, but likely too much for Phase 1 UI. | |

**User's choice:** Archetype-safe traits.

### Boundary language

| Option | Description | Selected |
|--------|-------------|----------|
| Visible concise boundary | Show a short note like "Original voice profile. Not a clone of any actor or protected character." Strong enough for safety without dominating the UI. | yes |
| Metadata-only boundary | Store the boundary in the voice profile and tests, but keep it out of the main UI unless blocked. | |
| Prominent safety banner | Make the non-impersonation boundary highly visible on the page. Very clear, but heavier than the studio workflow needs. | |

**User's choice:** Visible concise boundary.

### Profile metadata

| Option | Description | Selected |
|--------|-------------|----------|
| Rights plus style fields | Include rights status, approval flag, source/consent notes, style traits, prohibited associations, and intended use. Gives planners enough structure for safety and future generation. | yes |
| Rights-only minimum | Include only rights status, approval flag, and notes. Simpler, but persona/style safety may live in scattered UI copy. | |
| Full audit record now | Include detailed provenance, reviewer, approval date, expiration, and usage scope. Stronger governance, but may overbuild Phase 1. | |

**User's choice:** Rights plus style fields.

**Notes:** User chose to move to the next area after these decisions.

---

## Rights Gate UX

### Approval status

| Option | Description | Selected |
|--------|-------------|----------|
| Inline status badge and detail row | Show "Approved for generation" near the voice selector and include rights status/source notes in the profile card. Visible, compact, and testable. | yes |
| Profile card only | Keep approval and rights details inside the voice profile card. Cleaner, but less immediate. | |
| Pre-generation confirmation | Require the user to acknowledge rights status before triggering generation. Stronger, but too much friction for a no-login internal MVP. | |

**User's choice:** Inline status badge and detail row.

### Blocked state

| Option | Description | Selected |
|--------|-------------|----------|
| Disable action with clear reason | Keep the voice selectable, disable the generation action, and show why: missing approval/rights metadata. Best for internal debugging and safety. | yes |
| Hide unapproved voices | Only approved profiles appear. Simpler UI, but less useful for testing enforcement. | |
| Allow click then block with error | Let the user submit and show an API rejection. Useful to prove backend enforcement, but worse UX if it is the only signal. | |

**User's choice:** Disable action with clear reason.

### Backend enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Server blocks every request | UI disables unsafe actions, and the API still rejects any generation request where `approvedForGeneration` is false or rights metadata is incomplete. | yes |
| API blocks only approval flag | Backend checks `approvedForGeneration`, while metadata completeness is mostly UI/schema validation. | |
| UI-only for now | The front end prevents blocked requests, but the backend path stays permissive until real generation. Fastest, but violates the core safety constraint. | |

**User's choice:** Server blocks every request.

### Error wording

| Option | Description | Selected |
|--------|-------------|----------|
| Operational and specific | "Generation blocked: this voice profile is missing approved rights metadata." Clear for internal users and tests. | yes |
| Safety-first plain language | "This voice cannot be used until consent or license approval is recorded." More human, less schema-specific. | |
| Minimal technical | "Voice profile is not approved for generation." Short, but may not explain what to fix. | |

**User's choice:** Operational and specific.

**Notes:** User chose to move to the next area after these decisions.

---

## Stub Generation Feedback

### Approved path result

| Option | Description | Selected |
|--------|-------------|----------|
| Structured stub result | Show a completed "generation request" panel with provider type, voice id, rights check result, and placeholder audio/result metadata. Best for proving the vertical path. | yes |
| Simple success toast | Show "Generation path verified." Fast and minimal, but less useful for downstream provider work. | |
| Mock audio playback | Return a bundled placeholder clip so the UI can exercise playback early. More realistic, but may blur Phase 1 and Phase 2 scope. | |

**User's choice:** Structured stub result.

### Provider visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Compact provider trace | Show the chosen stub provider and contract stages checked, but keep technical details secondary. Good internal signal without turning the UI into logs. | yes |
| No provider details | Only show success/failure and voice metadata. Cleaner, but hides whether provider contracts are wired. | |
| Detailed debug trace | Show every interface stage and request/response payload shape. Useful for developers, too noisy for the focused studio. | |

**User's choice:** Compact provider trace.

### Timing and latency

| Option | Description | Selected |
|--------|-------------|----------|
| Record basic timing now | Include request start/end/duration in the result metadata. Helps establish latency observability before real providers. | yes |
| Skip timing until real providers | Avoid fake or uninteresting numbers in phase 1. | |
| Record full telemetry now | Capture structured events for every stage. Useful, but probably overbuilt before real generation. | |

**User's choice:** Record basic timing now.

### Placeholder audio

| Option | Description | Selected |
|--------|-------------|----------|
| No playback yet | Stub returns metadata only; real audio player arrives in Phase 2 where `STUD-06` belongs. | yes |
| Disabled playback placeholder | Show a disabled player area labeled as awaiting real provider output. Communicates direction, but adds nonfunctional UI. | |
| Bundled silent/test clip | Exercise browser audio playback in Phase 1. Useful technically, but crosses into Phase 2 playback scope. | |

**User's choice:** No playback yet.

---

## Agent Discretion

- User said "you decide" for the entry route. Agent selected root `/` as the studio route.

## Deferred Ideas

None.
