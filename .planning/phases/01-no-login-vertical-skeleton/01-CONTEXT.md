# Phase 1: No-Login Vertical Skeleton - Context

**Gathered:** 2026-06-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the first no-login vertical skeleton: a focused web studio at `/`, a bundled original voice profile named Vesper Glass, rights-gated generation enforcement, and provider contracts/stub generation plumbing for VAD, STT, TTS, and speech-to-speech candidates. It proves the web/API/provider path and consent-safe voice registry without adding real text-to-speech generation, tone presets, microphone input, audio playback, conversation mode, benchmarking, accounts, or cloud deployment hardening.

</domain>

<decisions>
## Implementation Decisions

### First Studio Surface
- **D-01:** The first screen should be a focused studio surface, not a landing page, cinematic splash page, or developer harness.
- **D-02:** The root route `/` should open the studio directly for the no-login MVP. Do not add a marketing/landing detour.
- **D-03:** Phase 1 UI should expose a voice-first control set: voice selector, voice profile card, rights/approval status, and a single stub generation action.
- **D-04:** Do not show Phase 2 controls yet. Text input, tone presets, real generation states, retry UX, and playback belong to later phases unless required only as internal scaffolding.
- **D-05:** Visual tone should be restrained theatrical: clean studio UI with subtle stage-like cues in copy, typography, and contrast. Avoid fan-page styling, protected-character references, and heavy cinematic presentation.

### Bundled Voice Identity
- **D-06:** The bundled original voice display name is **Vesper Glass**.
- **D-07:** Describe Vesper Glass through archetype-safe traits: measured theatrical delivery, cool charm, philosophical cynicism, and honey-edged sarcasm.
- **D-08:** The UI should include a concise visible boundary: Vesper Glass is an original voice profile, not a clone of any actor or protected character.
- **D-09:** The voice profile schema should include rights plus style fields: rights status, approval flag, source/consent notes, style traits, prohibited associations, and intended use.
- **D-10:** Do not frame Vesper Glass as Marvel Loki, Tom Hiddleston, or any other unlicensed identity in code, UI copy, prompts, fixtures, tests, or sample data.

### Rights Gate UX
- **D-11:** Show an inline approval badge near the voice selector plus a profile-card detail row for rights status/source notes.
- **D-12:** Unapproved voices may remain selectable for internal testing, but generation must be disabled with a clear reason.
- **D-13:** The backend must enforce the same safety gate. It must reject every generation request where `approvedForGeneration` is false or required rights metadata is incomplete, even if the UI already disabled the action.
- **D-14:** Blocked-generation error wording should be operational and specific, for example: `Generation blocked: this voice profile is missing approved rights metadata.`

### Stub Generation Feedback
- **D-15:** Approved stub generation should show a structured generation result, not just a toast.
- **D-16:** The structured result should include provider type, voice id, rights check result, placeholder result metadata, and a compact provider trace.
- **D-17:** Record basic request timing for the stub path: start time, end time, and duration.
- **D-18:** Do not add an audio playback surface in Phase 1. Stub generation returns metadata only; real generated audio playback belongs to Phase 2.
- **D-19:** Provider-interface details should be compact and secondary. Show enough to confirm the stub provider and contract stages are wired, but do not turn the studio into a debug log viewer.

### Agent Discretion
- **D-20:** The user delegated the entry-route decision. The chosen default is that `/` opens the studio directly because it best matches a no-login internal MVP.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` - Defines the product direction, core value, constraints, first voice boundary, and key project decisions.
- `.planning/REQUIREMENTS.md` - Maps Phase 1 to GOV-01, GOV-02, GOV-03, STUD-01, STUD-02, and PIPE-01.
- `.planning/ROADMAP.md` - Defines Phase 1 goal, success criteria, and the three planned work slices.
- `.planning/STATE.md` - Current project position and accumulated context.

### Architecture and Stack Research
- `.planning/research/ARCHITECTURE.md` - Recommended greenfield structure, provider adapter boundary, rights-gated voice profiles, and thin vertical skeleton pattern.
- `.planning/research/STACK.md` - Recommended Next.js/FastAPI/Python/provider stack, development tools, and explicit "what not to use" guidance.
- `.planning/research/PITFALLS.md` - Critical pitfalls for unauthorized voice impersonation, model lock-in, realtime latency, and phase-specific prevention.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No application source exists yet. The repository currently contains planning artifacts only, so Phase 1 should scaffold the initial app/API/provider structure.

### Established Patterns
- Planning research recommends a greenfield split of `apps/web`, `services/api`, `services/speech-worker`, `packages/shared`, and `infra`.
- Provider adapters are a core architecture pattern. Do not bind UI or API schemas to a single model repository.
- Rights-gated voice profiles are required before generation. Consent/rights metadata must be enforceable data, not only UI prose.
- A thin vertical skeleton is the correct Phase 1 shape: UI -> API/control plane -> provider contract -> stub generation metadata.

### Integration Points
- Web studio: root route `/`, voice selector, profile card, approval status, and stub generation action.
- API/control plane: voice registry lookup, rights metadata validation, generation request endpoint, blocked-generation error response.
- Shared schema boundary: voice profile, rights metadata, provider contract request/result, stub generation result, and timing metadata.
- Speech provider boundary: VAD, STT, TTS, and speech-to-speech interfaces can start as contracts/stubs in Phase 1.

</code_context>

<specifics>
## Specific Ideas

- Bundled voice name: Vesper Glass.
- Voice traits: measured theatrical delivery, cool charm, philosophical cynicism, honey-edged sarcasm.
- Non-impersonation note: original voice profile, not a clone of any actor or protected character.
- Blocked generation wording should be operational and specific.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 1-No-Login Vertical Skeleton*
*Context gathered: 2026-06-30*
