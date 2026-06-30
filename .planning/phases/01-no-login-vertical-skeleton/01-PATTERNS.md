# Phase 1: No-Login Vertical Skeleton - Pattern Map

**Mapped:** 2026-06-30
**Files analyzed:** 19
**Analogs found:** 0 / 19

> No application source exists in this repository yet. The mappings below are a greenfield ownership map inferred from phase decisions and architecture research, not copies of existing implementation code.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `apps/web/app/layout.tsx` | route | request-response | none (planning-only repo) | none |
| `apps/web/app/page.tsx` | route | request-response | none (planning-only repo) | none |
| `apps/web/components/studio-shell.tsx` | component | event-driven | none (planning-only repo) | none |
| `apps/web/tests/root-route.spec.ts` | test | request-response | none (planning-only repo) | none |
| `packages/shared/persona/vesper-glass.ts` | model | transform | none (planning-only repo) | none |
| `packages/shared/schemas/voice-profile.ts` | model | transform | none (planning-only repo) | none |
| `packages/shared/schemas/generation.ts` | model | transform | none (planning-only repo) | none |
| `services/api/app/main.py` | config | request-response | none (planning-only repo) | none |
| `services/api/app/routes/voices.py` | route | request-response | none (planning-only repo) | none |
| `services/api/app/routes/generate.py` | route | request-response | none (planning-only repo) | none |
| `services/api/app/schemas/voice_profile.py` | model | transform | none (planning-only repo) | none |
| `services/api/app/schemas/generation.py` | model | transform | none (planning-only repo) | none |
| `services/api/app/voice_registry/bundled_voice.py` | model | transform | none (planning-only repo) | none |
| `services/api/app/services/rights_gate.py` | service | request-response | none (planning-only repo) | none |
| `services/api/app/services/stub_generation.py` | service | request-response | none (planning-only repo) | none |
| `services/api/tests/test_generate_rights_gate.py` | test | request-response | none (planning-only repo) | none |
| `services/speech-worker/providers/contracts.py` | provider | request-response | none (planning-only repo) | none |
| `services/speech-worker/tests/test_provider_contracts.py` | test | request-response | none (planning-only repo) | none |

## Pattern Assignments

### Web studio shell

**Files:** `apps/web/app/layout.tsx`, `apps/web/app/page.tsx`, `apps/web/components/studio-shell.tsx`, `apps/web/tests/root-route.spec.ts`

**Analog:** none. The repo contains planning docs only.

**Greenfield ownership:** `apps/web`

**Design anchors:**
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md:16-21`
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md:30-41`
- `.planning/phases/01-no-login-vertical-skeleton/01-RESEARCH.md:63-69`
- `.planning/research/ARCHITECTURE.md:191-209`

**Copy this pattern:**
- `app/layout.tsx` owns the root HTML shell.
- `app/page.tsx` renders the studio directly at `/`.
- `StudioShell` stays client-side and only exposes Phase 1 controls: voice selector, approval badge, profile card, stub generation action, and the structured result card.
- The Playwright/root test should assert that `/` is studio-first and does not surface Phase 2 controls.

**Reference pattern from research:**
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

export default function Page() {
  return <StudioShell />;
}
```

### Voice registry and rights gate

**Files:** `packages/shared/persona/vesper-glass.ts`, `packages/shared/schemas/voice-profile.ts`, `services/api/app/schemas/voice_profile.py`, `services/api/app/voice_registry/bundled_voice.py`, `services/api/app/routes/voices.py`, `services/api/app/services/rights_gate.py`, `services/api/tests/test_generate_rights_gate.py`

**Analog:** none. The repo contains planning docs only.

**Greenfield ownership:** `packages/shared` for canonical persona/data contracts; `services/api` for registry lookup and enforcement; `services/api/tests` for the blocked-path check.

**Design anchors:**
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md:24-34`
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md:79-82`
- `.planning/phases/01-no-login-vertical-skeleton/01-RESEARCH.md:43-48`
- `.planning/research/ARCHITECTURE.md:115-128`
- `.planning/research/ARCHITECTURE.md:211-242`

**Copy this pattern:**
- `vesper-glass.ts` holds the bundled original persona and its safe boundary notes.
- `voice-profile.ts` mirrors the rights fields across TS and Python schemas.
- `bundled_voice.py` is the server-owned canonical record for Vesper Glass.
- `rights_gate.py` rejects any missing or unapproved voice profile before generation.
- The API test must assert the exact blocked message: `Generation blocked: this voice profile is missing approved rights metadata.`

**Reference pattern from research:**
```typescript
type VoiceProfile = {
  id: string;
  displayName: string;
  rightsStatus: "original" | "licensed" | "consented";
  approvedForGeneration: boolean;
};
```

### Stub generation and provider contracts

**Files:** `services/api/app/main.py`, `services/api/app/routes/generate.py`, `services/api/app/schemas/generation.py`, `services/api/app/services/stub_generation.py`, `services/speech-worker/providers/contracts.py`, `services/speech-worker/tests/test_provider_contracts.py`

**Analog:** none. The repo contains planning docs only.

**Greenfield ownership:** `services/api` owns request validation and stub result assembly; `services/speech-worker` owns provider interface definitions and the future adapter boundary.

**Design anchors:**
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md:37-41`
- `.planning/phases/01-no-login-vertical-skeleton/01-RESEARCH.md:63-69`
- `.planning/phases/01-no-login-vertical-skeleton/01-RESEARCH.md:79-80`
- `.planning/research/ARCHITECTURE.md:103-113`
- `.planning/research/ARCHITECTURE.md:130-135`
- `.planning/research/ARCHITECTURE.md:244-255`

**Copy this pattern:**
- `routes/generate.py` should use a typed request model and a dependency or helper that enforces the rights gate before any stub work runs.
- `stub_generation.py` should return metadata only, not audio.
- The structured result must include provider type, voice id, rights check result, placeholder result metadata, compact provider trace, and timing (`started_at`, `ended_at`, `duration_ms`).
- `contracts.py` should define `Protocol` or ABC-style interfaces for VAD, STT, TTS, and S2S so later model swaps do not touch the UI contract.
- `services/api/tests` and `services/speech-worker/tests` should only validate contract shape and blocked/allowed behavior, not real synthesis.

**Reference pattern from research:**
```python
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
```

```python
from typing import Protocol


class TTSProvider(Protocol):
    def synthesize(self, text: str, voice_id: str) -> bytes: ...
```

## Shared Patterns

### Root route owns the studio

**Source:** `.planning/research/ARCHITECTURE.md:191-209`

**Apply to:** `apps/web/app/layout.tsx`, `apps/web/app/page.tsx`, `apps/web/components/studio-shell.tsx`, `apps/web/tests/root-route.spec.ts`

- `layout.tsx` wraps the document.
- `page.tsx` renders the studio directly at `/`.
- No landing page detour, no auth gate, no Phase 2 controls.

### Rights are enforced server-side

**Source:** `.planning/research/ARCHITECTURE.md:211-242`

**Apply to:** `services/api/app/routes/generate.py`, `services/api/app/services/rights_gate.py`, `services/api/tests/test_generate_rights_gate.py`

- Client state is not authoritative.
- Unapproved or incomplete voice profiles must be rejected with the exact blocked-generation message.
- The route returns 403 for blocked requests and only reaches the stub path after validation passes.

### Provider contracts stay swappable

**Source:** `.planning/research/ARCHITECTURE.md:244-255`

**Apply to:** `services/speech-worker/providers/contracts.py`, `services/speech-worker/tests/test_provider_contracts.py`

- Use `Protocol` or ABC boundaries.
- Keep VAD, STT, TTS, and S2S interchangeable.
- Do not hard-code one model repo into the studio surface.

## No Analog Found

| File group | Reason |
|---|---|
| `apps/web/*` | No source tree exists yet; only planning artifacts are present. |
| `services/api/*` | No source tree exists yet; backend files are greenfield. |
| `packages/shared/*` | Shared persona and schema files are new. |
| `services/speech-worker/*` | Provider contracts are new. |
| `tests/*` | No existing test harness exists to mirror. |

## Metadata

**Analog search scope:** repository root plus `.planning/`
**Files scanned:** 4 planning docs, 0 source files
**Pattern extraction date:** 2026-06-30
