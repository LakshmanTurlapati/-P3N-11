# Phase 1: No-Login Vertical Skeleton - Research

**Researched:** 2026-06-30
**Domain:** Greenfield web studio shell + typed API control plane for consent-gated voice generation
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The first screen should be a focused studio surface, not a landing page, cinematic splash page, or developer harness.
- **D-02:** The root route `/` should open the studio directly for the no-login MVP. Do not add a marketing/landing detour.
- **D-03:** Phase 1 UI should expose a voice-first control set: voice selector, voice profile card, rights/approval status, and a single stub generation action.
- **D-04:** Do not show Phase 2 controls yet. Text input, tone presets, real generation states, retry UX, and playback belong to later phases unless required only as internal scaffolding.
- **D-05:** Visual tone should be restrained theatrical: clean studio UI with subtle stage-like cues in copy, typography, and contrast. Avoid fan-page styling, protected-character references, and heavy cinematic presentation.
- **D-06:** The bundled original voice display name is **Vesper Glass**.
- **D-07:** Describe Vesper Glass through archetype-safe traits: measured theatrical delivery, cool charm, philosophical cynicism, and honey-edged sarcasm.
- **D-08:** The UI should include a concise visible boundary: Vesper Glass is an original voice profile, not a clone of any actor or protected character.
- **D-09:** The voice profile schema should include rights plus style fields: rights status, approval flag, source/consent notes, style traits, prohibited associations, and intended use.
- **D-10:** Do not frame Vesper Glass as Marvel Loki, Tom Hiddleston, or any other unlicensed identity in code, UI copy, prompts, fixtures, tests, or sample data.
- **D-11:** Show an inline approval badge near the voice selector plus a profile-card detail row for rights status/source notes.
- **D-12:** Unapproved voices may remain selectable for internal testing, but generation must be disabled with a clear reason.
- **D-13:** The backend must enforce the same safety gate. It must reject every generation request where `approvedForGeneration` is false or required rights metadata is incomplete, even if the UI already disabled the action.
- **D-14:** Blocked-generation error wording should be operational and specific, for example: `Generation blocked: this voice profile is missing approved rights metadata.`
- **D-15:** Approved stub generation should show a structured generation result, not just a toast.
- **D-16:** The structured result should include provider type, voice id, rights check result, placeholder result metadata, and a compact provider trace.
- **D-17:** Record basic request timing for the stub path: start time, end time, and duration.
- **D-18:** Do not add an audio playback surface in Phase 1. Stub generation returns metadata only; real generated audio playback belongs to Phase 2.
- **D-19:** Provider-interface details should be compact and secondary. Show enough to confirm the stub provider and contract stages are wired, but do not turn the studio into a debug log viewer.

### the agent's Discretion
- **D-20:** The user delegated the entry-route decision. The chosen default is that `/` opens the studio directly because it best matches a no-login internal MVP.

### Deferred Ideas (OUT OF SCOPE)
None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GOV-01 | User can only generate with a voice profile that has explicit rights metadata. | Backend-enforced voice schema and request validation; UI must not be the source of truth. |
| GOV-02 | System blocks generation requests for voice profiles that are not approved for generation. | Server-side approval gate and negative-path tests on the generation endpoint. |
| GOV-03 | First bundled voice profile is described as an original theatrical trickster voice, not as Marvel Loki, Tom Hiddleston, or any other unlicensed identity. | Voice profile fixture/data shape, copy rules, and test fixtures must preserve the persona boundary. |
| STUD-01 | User can open a no-login web studio. | Next.js App Router root route and root layout pattern for `/`. |
| STUD-02 | User can select the bundled original theatrical voice profile. | Studio shell state, voice selector, and server-provided bundled voice record. |
| PIPE-01 | System exposes provider interfaces for VAD, STT, TTS, and speech-to-speech candidates. | Python `Protocol` / `abc.ABC` boundaries plus typed request/result schemas. |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Use a GSD workflow command before any file-changing work; do not make direct repo edits outside a GSD workflow unless explicitly asked.
- Use `apply_patch` for manual file edits; do not create or edit repo files with heredocs or `cat`.
- Prefer `rg` / `rg --files` for search and file discovery.
- Do not use destructive git commands such as `git reset --hard` or `git checkout --` unless explicitly requested.
- Do not amend commits unless explicitly requested.
- Preserve existing user changes and do not revert unrelated work.
- Keep frontend work intentional and non-generic; avoid boilerplate layouts when the repo is asking for a product surface.

## Summary

Phase 1 should be planned as a thin vertical skeleton: `/` opens directly into a no-login studio, the bundled voice profile is `Vesper Glass`, and the only generation action is a rights-gated stub path that proves UI -> API -> provider-contract plumbing without real speech synthesis, audio playback, tone presets, mic capture, or live conversation. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/ROADMAP.md]

The best fit is Next.js App Router for the studio shell, FastAPI for the rights-gating control plane, and Python `Protocol` / `abc.ABC` provider contracts for the speech boundary. Next.js App Router docs center root layouts, nested routing, and server/client components; FastAPI docs center typed request validation and dependency injection; Python's typing and ABC docs give a stable interface boundary for future VAD/STT/TTS/S2S swaps. [CITED: https://nextjs.org/docs/app/getting-started/layouts-and-pages; https://nextjs.org/docs/app/glossary; https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/; https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html]

Current registry pins were checked on 2026-06-30: `next` 16.2.9, `react` 19.2.7, `react-dom` 19.2.7, `typescript` 6.0.3, `fastapi` 0.138.2, `pydantic` 2.13.4, and `uvicorn` 0.49.0. The package-legitimacy gate returned `OK` only for `typescript`; the others were flagged `SUS` because they are very recent releases, so exact patch pins should stay behind human-verify checkpoints rather than being treated as locked install decisions. [VERIFIED: local command]

**Primary recommendation:** Build the root route as a server-rendered App Router studio shell with a client-only voice selector and approval badge, enforce rights on the API boundary with a typed voice-profile schema, and keep all speech backends behind `Protocol`-based provider adapters so Phase 2 can swap real providers without changing the UI contract. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://nextjs.org/docs/app; https://fastapi.tiangolo.com/tutorial/body/; https://docs.python.org/3/library/typing.html]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Web studio shell | Browser / Client | Frontend Server | The studio is an interactive surface, but App Router root rendering can still deliver the first paint from the server. [CITED: https://nextjs.org/docs/app/getting-started/layouts-and-pages] |
| No-login routing | Frontend Server | Browser / Client | The root route `/` should open the studio directly, and App Router is the layer that owns that route shape. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://nextjs.org/docs/app/api-reference/file-conventions/layout] |
| Voice profile schema and approval badge | API / Backend | Browser / Client | Rights state must come from the server-controlled registry; the browser only renders it. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/research/ARCHITECTURE.md] |
| Rights-gated generation block | API / Backend | Database / Storage | The backend has to reject unapproved or incomplete profiles even when the UI already disables generation. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/body/] |
| Provider interface + stub generation path | API / Backend | Speech Worker | Provider contracts belong behind a backend boundary so the first stub can later be replaced with real VAD/STT/TTS/S2S providers. [CITED: .planning/research/ARCHITECTURE.md; https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html] |

## Standard Stack

Version snapshot on 2026-06-30: `next` 16.2.9, `react` 19.2.7, `react-dom` 19.2.7, `typescript` 6.0.3, `fastapi` 0.138.2, `pydantic` 2.13.4, and `uvicorn` 0.49.0. Exact patch pins were observed from registry commands; only `typescript` passed the legitimacy gate, so the rest remain checkpointed installation decisions. [VERIFIED: local command]

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | `16.2.x` [CITED: .planning/research/STACK.md; https://nextjs.org/docs/app] | Web studio UI and root routing | App Router is the current official routing model and supports layouts, nested routing, loading states, and server/client component boundaries. [CITED: https://nextjs.org/docs/app; https://nextjs.org/docs/app/glossary; https://nextjs.org/docs/app/getting-started/layouts-and-pages] |
| React | `19.2.x` [CITED: https://react.dev/versions] | UI components | The React docs at `react.dev` currently target React 19.2. [CITED: https://react.dev/versions] |
| TypeScript | `6.0.3` [VERIFIED: local command] | UI and API type safety | Current registry release is clean in the legitimacy audit and is the right baseline for typed shared contracts. [VERIFIED: local command] |
| FastAPI | `0.138.x` [CITED: .planning/research/STACK.md; https://fastapi.tiangolo.com/; https://fastapi.tiangolo.com/release-notes/] | API control plane and request validation | FastAPI is built around standard Python type hints and typed request bodies, which is exactly what the rights gate needs. [CITED: https://fastapi.tiangolo.com/; https://fastapi.tiangolo.com/tutorial/body/] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | `v2` [CITED: https://docs.pydantic.dev/2.3/blog/pydantic-v2-final/] | Runtime schema validation | Use for voice-profile, generation-request, and stub-result models. [CITED: https://docs.pydantic.dev/2.3/blog/pydantic-v2-final/] |
| Python `typing.Protocol` / `abc.ABC` | stdlib [CITED: https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html] | Provider interfaces | Use for swappable VAD, STT, TTS, and speech-to-speech provider contracts. [CITED: https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html] |
| Browser `getUserMedia` / `MediaRecorder` | browser-native [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia; https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder] | Future mic capture and playback | Do not surface this in Phase 1; it becomes relevant when Phase 3 adds audio input. [CITED: .planning/ROADMAP.md; https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia; https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Next.js App Router | Pages Router | Pages Router is still valid, but it is the wrong default for a root-layout-first studio shell. [CITED: https://nextjs.org/docs/app/glossary; https://nextjs.org/docs/pages/building-your-application/routing/pages-and-layouts] |
| FastAPI | Bare Starlette or Flask | You lose the typed body validation and dependency-injection ergonomics that the rights gate needs. [CITED: https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/] |
| `Protocol` / `ABC` provider contracts | Hard-coded model imports | Hard-coded imports would lock the app to one model stack and make Phase 2 provider swaps painful. [CITED: .planning/research/PITFALLS.md; https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html] |

**Installation:**
```bash
pnpm add next react react-dom typescript
pip install fastapi pydantic uvicorn
```

If the phase owner wants the exact patch pins from the registry snapshot, keep them behind human-verify checkpoints because the current `next` / `react` / `fastapi` / `pydantic` / `uvicorn` releases were flagged `SUS` by the legitimacy gate. [VERIFIED: local command]

## Package Legitimacy Audit

> Required because this phase will install external packages for the web and API skeleton.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| next | npm | 21 days [VERIFIED: local command] | 39,590,260/wk [VERIFIED: local command] | git+https://github.com/vercel/next.js.git [VERIFIED: local command] | SUS [VERIFIED: local command] | Flagged - planner must add `checkpoint:human-verify` before install |
| react | npm | 29 days [VERIFIED: local command] | 146,247,311/wk [VERIFIED: local command] | git+https://github.com/facebook/react.git [VERIFIED: local command] | SUS [VERIFIED: local command] | Flagged - planner must add `checkpoint:human-verify` before install |
| react-dom | npm | 29 days [VERIFIED: local command] | 137,950,070/wk [VERIFIED: local command] | git+https://github.com/facebook/react.git [VERIFIED: local command] | SUS [VERIFIED: local command] | Flagged - planner must add `checkpoint:human-verify` before install |
| typescript | npm | 75 days [VERIFIED: local command] | 217,486,890/wk [VERIFIED: local command] | git+https://github.com/microsoft/TypeScript.git [VERIFIED: local command] | OK [VERIFIED: local command] | Approved |
| fastapi | PyPI | 1 day [VERIFIED: local command] | unknown [VERIFIED: local command] | https://github.com/fastapi/fastapi [VERIFIED: local command] | SUS [VERIFIED: local command] | Flagged - planner must add `checkpoint:human-verify` before install |
| pydantic | PyPI | 55 days [VERIFIED: local command] | unknown [VERIFIED: local command] | https://github.com/pydantic/pydantic [VERIFIED: local command] | SUS [VERIFIED: local command] | Flagged - planner must add `checkpoint:human-verify` before install |
| uvicorn | PyPI | 27 days [VERIFIED: local command] | unknown [VERIFIED: local command] | https://github.com/Kludex/uvicorn [VERIFIED: local command] | SUS [VERIFIED: local command] | Flagged - planner must add `checkpoint:human-verify` before install |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** next, react, react-dom, fastapi, pydantic, uvicorn

## Architecture Patterns

### System Architecture Diagram

```text
User / Browser
    -> Next.js App Router root route (/)
    -> Studio shell UI
       -> voice selector
       -> rights/approval badge
       -> stub generation action
    -> POST /generate
    -> FastAPI control plane
       -> load bundled voice profile
       -> validate rights metadata + approval flag
       -> if blocked: return operational error
       -> if approved: call provider contract
    -> stub provider / provider adapter boundary
    -> structured stub generation result
    -> render status card back in the studio
```

The phase does not need audio playback, live conversation, or mic capture in the diagram because those are explicitly deferred. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/ROADMAP.md]

### Recommended Project Structure

```text
apps/
  web/
    app/
      page.tsx
      layout.tsx
    components/
    lib/
services/
  api/
    app/
      routes/
      schemas/
      voice_registry/
  speech-worker/
    providers/
      stt/
      vad/
      tts/
      s2s/
packages/
  shared/
    schemas/
    persona/
infra/
  deploy/
```

This split keeps the studio UI, control plane, shared schema boundary, and speech worker boundary separate from the first phase. [CITED: .planning/research/ARCHITECTURE.md]

### Pattern 1: Root Studio Route
**What:** Make `app/page.tsx` render the studio directly at `/`, with `app/layout.tsx` providing the root document wrapper. [CITED: https://nextjs.org/docs/app/getting-started/layouts-and-pages; https://nextjs.org/docs/app/api-reference/file-conventions/layout]  
**When to use:** Always for this phase, because the product is no-login and studio-first. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md]  
**Example:**
```tsx
// Source: https://nextjs.org/docs/app/getting-started/layouts-and-pages
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

// app/page.tsx
export default function Page() {
  return <StudioShell />;
}
```

### Pattern 2: Server-Enforced Rights Gate
**What:** The backend reads voice rights metadata from the registry, rejects missing or unapproved profiles, and never trusts the client payload as the source of truth. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/]  
**When to use:** Every generation request. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md]  
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/body/
from fastapi import Body, Depends, FastAPI, HTTPException
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    voice_id: str
    approved_for_generation: bool
    rights_notes: str | None = None


def enforce_rights(req: GenerateRequest = Body(...)) -> GenerateRequest:
    if not req.approved_for_generation:
        raise HTTPException(
            status_code=403,
            detail="Generation blocked: this voice profile is missing approved rights metadata.",
        )
    return req


app = FastAPI()


@app.post("/generate")
def generate(req: GenerateRequest = Depends(enforce_rights)):
    return {"status": "stubbed", "voice_id": req.voice_id}
```

### Pattern 3: Provider Contract Boundary
**What:** Define each speech backend behind a `Protocol` or ABC so the app can swap VAD, STT, TTS, and speech-to-speech candidates without changing the studio surface. [CITED: https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html]  
**When to use:** Every provider-facing module in the worker boundary. [CITED: .planning/research/ARCHITECTURE.md]  
**Example:**
```python
# Source: https://docs.python.org/3/library/typing.html
from typing import Protocol


class TTSProvider(Protocol):
    def synthesize(self, text: str, voice_id: str) -> bytes: ...
```

### Anti-Patterns to Avoid
- **UI-only consent gating:** the disable state is easy to bypass if the backend trusts it. [CITED: .planning/research/PITFALLS.md; .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md]
- **Hard-coded model imports:** bind the product to one speech repo and Phase 2 becomes a rewrite. [CITED: .planning/research/PITFALLS.md]
- **Phase creep into tone presets, text input, or playback:** those controls belong to later phases and will muddy the Phase 1 signal. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/ROADMAP.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Root routing and studio entry | Landing page or auth detour | Next.js App Router root `/` | The product is no-login and should open directly into the studio. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://nextjs.org/docs/app] |
| Rights enforcement | Client-only disable logic | FastAPI validation / dependency gate | The backend must reject invalid or unapproved profiles even when the UI is bypassed. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/] |
| Provider dispatch | One-off model imports | `Protocol` / `ABC` provider interfaces | The phase must keep VAD, STT, TTS, and S2S swappable. [CITED: .planning/research/ARCHITECTURE.md; https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html] |
| Voice data shape | Free-form dicts or ad hoc JSON blobs | Typed voice-profile schema | Rights status, approval, notes, and prohibited associations need stable fields. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/body/] |

**Key insight:** a stub generation path is enough for Phase 1, but the interface boundaries and rights checks must already look like the real system so Phase 2 can swap in a genuine provider without changing the product contract. [CITED: .planning/ROADMAP.md; .planning/research/PITFALLS.md]

## Common Pitfalls

### Pitfall 1: UI Only Looks Safe
**What goes wrong:** The voice card shows an approval badge, but direct API calls can still generate with blocked or incomplete rights metadata.  
**Why it happens:** The client owns the disable state and the server trusts the client payload.  
**How to avoid:** Put the gate in the FastAPI handler or dependency chain and test the reject path.  
**Warning signs:** `approvedForGeneration=false` still returns a generation result, or blocked requests succeed through the API. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/]

### Pitfall 2: Phase Creep From Later Studio Controls
**What goes wrong:** Text input, tone presets, retry UX, or playback appear in Phase 1 and blur the MVP signal.  
**Why it happens:** It is tempting to make the surface feel complete too early.  
**How to avoid:** Keep the UI to voice selector, profile card, approval status, and one stub generation action.  
**Warning signs:** The first page starts looking like Phase 2 instead of a thin skeleton. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/ROADMAP.md]

### Pitfall 3: Model Lock-In Before a Real Provider Exists
**What goes wrong:** The first stub path bakes in a single model repo or one-off response shape.  
**Why it happens:** It is faster to hard-code one adapter than to define a clean contract.  
**How to avoid:** Keep provider requests/responses typed and behind `Protocol` / `ABC` boundaries.  
**Warning signs:** UI code imports a specific model package or provider-specific JSON fields. [CITED: .planning/research/PITFALLS.md; https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html]

### Pitfall 4: Persona Drift Into a Protected Identity
**What goes wrong:** Sample text or fixtures start saying Loki or Tom Hiddleston instead of an original voice profile.  
**Why it happens:** The persona is easy to describe by reference rather than by its own constraints.  
**How to avoid:** Keep Vesper Glass described through its own archetype-safe traits and ban the protected-name references in code and fixtures.  
**Warning signs:** Any UI copy, prompt, or test says "exactly like" a protected character or actor. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/PROJECT.md]

## Code Examples

Verified patterns from official sources:

### App Router root surface
```tsx
// Source: https://nextjs.org/docs/app/getting-started/layouts-and-pages
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### Rights-gated FastAPI request
```python
# Source: https://fastapi.tiangolo.com/tutorial/body/
from fastapi import Body, Depends, FastAPI, HTTPException
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    voice_id: str
    approved_for_generation: bool


def enforce_rights(req: GenerateRequest = Body(...)) -> GenerateRequest:
    if not req.approved_for_generation:
        raise HTTPException(403, "Generation blocked: this voice profile is missing approved rights metadata.")
    return req
```

### Provider adapter boundary
```python
# Source: https://docs.python.org/3/library/typing.html
from typing import Protocol


class VADProvider(Protocol):
    def detect_turns(self, audio: bytes) -> list[tuple[float, float]]: ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pages Router root redirects | App Router root layout + page | Next.js App Router docs | The studio can own `/` directly without a separate routing detour. [CITED: https://nextjs.org/docs/app/glossary; https://nextjs.org/docs/pages/building-your-application/routing/pages-and-layouts] |
| Ad hoc dict parsing | FastAPI typed bodies and dependencies | FastAPI current docs | Request validation and rights checks become explicit instead of implicit. [CITED: https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/] |
| Model-specific imports | Provider contracts with adapters | Python typing / ABC docs | Future provider swaps stay isolated from the UI contract. [CITED: https://docs.python.org/3/library/typing.html; https://docs.python.org/3/library/abc.html] |

**Deprecated/outdated:**
- Browser-only speech synthesis: not enough for custom voice cloning or a rights-gated provider boundary. [CITED: .planning/research/STACK.md]
- Exact Marvel Loki / Tom Hiddleston cloning: explicitly out of scope for rights, safety, and product ownership reasons. [CITED: .planning/PROJECT.md]

## Assumptions Log

> None. All planning-critical claims were cited from project docs, official docs, or verified local commands; suspicious registry observations are tracked in the package audit rather than treated as assumptions.

## Open Questions

1. **Should the phase use `uv` now or stay on `pip` + `venv` for the Python skeleton?**
   - What we know: `uv` is missing in the current environment, while `python3` and `pip3` are present. [VERIFIED: local command]
   - What's unclear: whether the phase owner wants to install `uv` immediately or use the available fallback for Phase 1.
   - Recommendation: plan a small environment-decision task before Wave 0 so the backend scaffold uses one toolchain consistently.

2. **Should the first stub generation path live inline in the API control plane or in a separate `services/speech-worker` stub service?**
   - What we know: the architecture guidance prefers a separate worker boundary, but Phase 1 only needs a stub result. [CITED: .planning/research/ARCHITECTURE.md]
   - What's unclear: whether the initial stub should be an in-process adapter or a separate internal service.
   - Recommendation: keep the contract in `services/speech-worker` even if the first stub implementation is thin or inline.

3. **Should exact patch pins for the SUS packages be locked before planning starts, or after a checkpointed human review?**
   - What we know: the current releases for `next`, `react`, `react-dom`, `fastapi`, `pydantic`, and `uvicorn` were flagged `SUS` by the legitimacy gate. [VERIFIED: local command]
   - What's unclear: whether the team wants to accept those exact patches now or adjust the install set after review.
   - Recommendation: keep them behind `checkpoint:human-verify` tasks and let the planner lock them only after review.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Node.js | Next.js app scaffold and route shell | ✓ | `v24.2.0` [VERIFIED: local command] | — |
| npm | JavaScript package installation | ✓ | `11.3.0` [VERIFIED: local command] | — |
| pnpm | Preferred frontend package manager | ✓ | `10.30.3` [VERIFIED: local command] | `npm` |
| Python 3 | FastAPI control plane scaffold | ✓ | `3.13.5` [VERIFIED: local command] | — |
| pip | Python package installation | ✓ | `25.1.1` [VERIFIED: local command] | — |
| uv | Recommended Python environment manager | ✗ | — [VERIFIED: local command] | Use `python -m venv` + `pip`, or install `uv` in Wave 0 |
| pytest | Backend/API test runner | ✗ | — [VERIFIED: local command] | Install `pytest` in Wave 0 |
| Playwright | Browser smoke tests for the studio shell | ✗ | — [VERIFIED: local command] | Install `@playwright/test` in Wave 0 or defer browser smoke until installed |

**Missing dependencies with no fallback:**
- None.

**Missing dependencies with fallback:**
- `uv`
- `pytest`
- Playwright

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` for API/provider tests; Playwright for web smoke tests once installed |
| Config file | none yet - the phase must create `pytest.ini` or `pyproject.toml` test config and `playwright.config.ts` |
| Quick run command | `pytest -q` and `pnpm playwright test --grep studio` |
| Full suite command | `pytest` and `pnpm playwright test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|-----------|-----------|-------------------|-------------|
| GOV-01 | Generation is blocked unless the voice profile has explicit rights metadata | unit/integration | `pytest tests/api/test_rights_gate.py -q` | ❌ Wave 0 |
| GOV-02 | Unapproved profiles cannot generate | unit/integration | `pytest tests/api/test_rights_gate.py -q` | ❌ Wave 0 |
| GOV-03 | Bundled voice data never frames Vesper Glass as Loki or Tom Hiddleston | fixture/snapshot | `pytest tests/fixtures/test_voice_profile.py -q` | ❌ Wave 0 |
| STUD-01 | Root route opens the studio directly | browser smoke | `pnpm playwright test tests/web/studio.spec.ts --grep root-route` | ❌ Wave 0 |
| STUD-02 | Bundled Vesper Glass voice is selectable and shows approval status | browser smoke | `pnpm playwright test tests/web/studio.spec.ts --grep voice-selector` | ❌ Wave 0 |
| PIPE-01 | Provider interfaces exist for VAD, STT, TTS, and speech-to-speech candidates | unit | `pytest tests/providers/test_contracts.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest -q` once the first backend tests exist, plus the smallest relevant Playwright grep for studio smoke once the browser scaffold exists.
- **Per wave merge:** `pytest` and `pnpm playwright test`.
- **Phase gate:** Full suite green before `$gsd-verify-work`.

### Wave 0 Gaps
- `pytest.ini` or `pyproject.toml` test config - missing and must be created.
- `playwright.config.ts` - missing and must be created if browser smoke is part of the first wave.
- `tests/` directories and initial fixtures for API, provider contracts, and studio smoke tests - missing.
- Tool installation for `pytest` and `@playwright/test` - missing from the current environment.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 1 is no-login; do not introduce auth or sessions yet. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md] |
| V3 Session Management | no | No authenticated user sessions exist in this MVP slice. [CITED: .planning/REQUIREMENTS.md; .planning/ROADMAP.md] |
| V4 Access Control | yes | Backend rights gate on `approvedForGeneration` and complete rights metadata. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/dependencies/] |
| V5 Input Validation | yes | FastAPI request models + Pydantic validation. [CITED: https://fastapi.tiangolo.com/tutorial/body/; https://docs.pydantic.dev/2.3/blog/pydantic-v2-final/] |
| V6 Cryptography | no | No custom crypto or secret-handling logic belongs in Phase 1. [CITED: .planning/research/PITFALLS.md] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Direct API call bypasses disabled UI | Elevation of privilege / Tampering | Enforce the rights gate in the API handler or dependency chain, not only in the client. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; https://fastapi.tiangolo.com/tutorial/body/; https://fastapi.tiangolo.com/tutorial/dependencies/] |
| Tampered voice-profile payload | Tampering | Load the voice record by ID from the server registry and ignore client-supplied approval state. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/research/ARCHITECTURE.md] |
| Persona drift into protected identity wording | Repudiation / Information disclosure | Keep Vesper Glass fixtures and copy on the original archetype-safe description only; ban protected-name references in code and tests. [CITED: .planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md; .planning/PROJECT.md] |
| Shared schema drift between UI and API | Tampering | Use typed request/result models and keep the voice-profile contract shared across layers. [CITED: .planning/research/ARCHITECTURE.md; https://fastapi.tiangolo.com/tutorial/body/] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md` - locked Phase 1 decisions, Vesper Glass, rights gate, and explicit out-of-scope items.
- `.planning/ROADMAP.md` - Phase 1 goal, slices, and success criteria.
- `.planning/REQUIREMENTS.md` - GOV-01, GOV-02, GOV-03, STUD-01, STUD-02, PIPE-01 traceability.
- `https://nextjs.org/docs/app/getting-started/layouts-and-pages` - root layout / page conventions.
- `https://nextjs.org/docs/app/api-reference/file-conventions/layout` - root layout behavior.
- `https://nextjs.org/docs/app/getting-started/project-structure` - App Router folder conventions.
- `https://fastapi.tiangolo.com/tutorial/body/` - request body validation.
- `https://fastapi.tiangolo.com/tutorial/dependencies/` - dependency injection / backend gates.
- `https://docs.python.org/3/library/typing.html` - `Protocol` and structural subtyping.
- `https://docs.python.org/3/library/abc.html` - abstract base classes.

### Secondary (MEDIUM confidence)
- `https://react.dev/versions` - React 19.2 docs line.
- `https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia` - browser mic permission flow.
- `https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder` - browser media recording API.
- `https://fastapi.tiangolo.com/release-notes/` - FastAPI current 0.x release line.
- `https://docs.pydantic.dev/2.3/blog/pydantic-v2-final/` - Pydantic V2 official release and usage framing.

### Tertiary (LOW confidence)
- `npm view` / `pip index versions` / package-legitimacy-check outputs on 2026-06-30 - current registry observations and legitimacy verdicts for install candidates.
- Local availability checks for `node`, `npm`, `pnpm`, `python3`, `pip3`, `uv`, `pytest`, and Playwright.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - the architecture and docs are stable, but several current package pins are still flagged SUS and must stay behind human-verify checkpoints.
- Architecture: HIGH - the phase boundary and route shape are locked in CONTEXT and line up with official framework docs.
- Pitfalls: HIGH - the main failure modes are directly supported by the project pitfalls doc and the official framework guidance.

**Research date:** 2026-06-30
**Valid until:** 2026-07-07 for exact package pins; 2026-07-30 for the architecture guidance
