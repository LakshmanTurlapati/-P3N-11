---
phase: "01-no-login-vertical-skeleton"
verified: "2026-07-01T01:46:20Z"
status: passed
score: "7/7 must-haves verified"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 1: No-Login Vertical Skeleton - Verification Report

**Phase Goal:** User can open the studio directly at `/`, see Vesper Glass as an original rights-bounded voice, and trigger a metadata-only rights-gated generation result card proving the web-to-API speech boundary.

**Verified:** 2026-07-01T01:46:20Z

**Status:** passed

**Re-verification:** No

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User can open `/` directly and land in the studio without a login or landing detour. | ✓ VERIFIED | [apps/web/app/page.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/page.tsx:1) renders `StudioShell` directly; [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:85) is the first visible surface; [apps/web/tests/root-route.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/root-route.spec.ts:3) asserts the root route opens the studio. |
| 2 | The first studio surface shows Vesper Glass as an original theatrical voice profile with an approval badge and boundary note. | ✓ VERIFIED | [apps/web/lib/voice-registry.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/lib/voice-registry.ts:13) defines the render-only Vesper Glass seed; [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:121) renders the approval badge and card; [services/api/app/voice_registry/bundled_voice.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py:5) carries the server-owned original-theatrical boundary copy; [services/api/tests/test_voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_voice_profile.py:10) verifies the boundary language and rights fields. |
| 3 | The first studio surface omits Phase 2 controls. | ✓ VERIFIED | [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:102) only renders voice selector, badge, voice card, and one generate button; [apps/web/tests/root-route.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/root-route.spec.ts:16) asserts there are no text inputs, tone presets, retry, playback, or mic controls. |
| 4 | The server exposes a rights-annotated Vesper Glass record and blocks missing or unapproved profiles with the exact safety message. | ✓ VERIFIED | [services/api/app/schemas/voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py:10) defines strict rights/style models; [services/api/app/voice_registry/bundled_voice.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py:5) defines `VESPER_GLASS_PROFILE`; [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py:22) enforces the rights gate; [services/api/app/routes/voices.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/voices.py:12) exposes the registry route; [services/api/app/main.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py:8) mounts it; [services/api/tests/test_rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_rights_gate.py:39) and [services/api/tests/test_rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_rights_gate.py:65) verify the exact 403 message for unapproved and incomplete profiles. |
| 5 | The generation path returns metadata only, including provider type, voice id, rights check, result metadata, compact provider trace, and timing, with no audio payload. | ✓ VERIFIED | [services/api/app/schemas/generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py:13) defines the strict generation models; [services/api/app/services/stub_generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py:17) builds the metadata-only result; [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py:13) returns that result model; [services/api/tests/test_generate_stub.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generate_stub.py:15) verifies the response shape and asserts `audio` and `playback_url` are absent. |
| 6 | `StudioShell` posts the selected Vesper Glass voice id to `/generate` and renders the structured metadata result card. | ✓ VERIFIED | [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:47) posts `{ voice_id }` to `/generate` and renders provider type, rights check, metadata, trace, and timing; [apps/web/tests/studio-generation.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/studio-generation.spec.ts:3) intercepts the request and asserts the card content. |
| 7 | Provider contracts exist for VAD, STT, TTS, and speech-to-speech candidates behind the worker boundary. | ✓ VERIFIED | [services/speech-worker/providers/contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py:38) defines the four `Protocol` interfaces; [services/speech-worker/tests/test_provider_contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/tests/test_provider_contracts.py:69) verifies the interfaces are swappable and shape-driven. |

**Score:** 7/7 truths verified (0 present-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| [apps/web/app/page.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/page.tsx) | Direct root route | VERIFIED | Renders `StudioShell` at `/` with no detour. |
| [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx) | Voice-first studio shell and generation card | VERIFIED | Selector, approval badge, voice card, generate action, and structured metadata result card. |
| [apps/web/lib/voice-registry.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/lib/voice-registry.ts) | Render-only Vesper Glass display seed | VERIFIED | Single bundled seed with original-theatrical boundary copy. |
| [apps/web/app/layout.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/layout.tsx) | Root HTML wrapper | VERIFIED | App Router shell with studio metadata. |
| [apps/web/app/globals.css](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/globals.css) | Theatrical shell and result-card styling | VERIFIED | Restraint-focused visual system for the studio and result card. |
| [apps/web/playwright.config.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/playwright.config.ts) | Browser smoke runner | VERIFIED | Builds and starts the app for Playwright against `127.0.0.1:3000`. |
| [apps/web/tests/root-route.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/root-route.spec.ts) | Root-route smoke test | VERIFIED | Checks direct studio entry and absence of Phase 2 controls. |
| [apps/web/tests/studio-generation.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/studio-generation.spec.ts) | Browser generation contract test | VERIFIED | Proves the request body and result-card contract. |
| [apps/web/package.json](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json) | Web scripts and dependencies | VERIFIED | `dev`, `build`, and `test` scripts present. |
| [apps/web/tsconfig.json](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tsconfig.json) | Web TypeScript config | VERIFIED | Strict App Router setup with Next path aliases. |
| [services/api/app/schemas/voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py) | Rights/style voice schema | VERIFIED | Strict, `extra="forbid"` model with rights metadata. |
| [services/api/app/voice_registry/bundled_voice.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py) | Bundled Vesper Glass record | VERIFIED | Server-owned voice registry entry. |
| [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py) | Rights gate helper | VERIFIED | Blocks missing/unapproved metadata with one exact message. |
| [services/api/app/routes/voices.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/voices.py) | Voice registry route | VERIFIED | Returns the server-owned voice profile(s). |
| [services/api/app/main.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/main.py) | API router mounting | VERIFIED | Includes the voice registry and generation routers. |
| [services/api/app/schemas/generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py) | Generation schema | VERIFIED | Request, result, trace, and timing models with no audio field. |
| [services/api/app/services/stub_generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py) | Metadata-only stub service | VERIFIED | Builds the structured result card payload. |
| [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py) | Generation route | VERIFIED | Rights-gated and metadata-only. |
| [services/api/tests/test_voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_voice_profile.py) | Voice schema and boundary tests | VERIFIED | Confirms required rights/style fields and boundary language. |
| [services/api/tests/test_rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_rights_gate.py) | Rights-gate tests | VERIFIED | Confirms blocked and approved outcomes. |
| [services/api/tests/test_generate_stub.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generate_stub.py) | Generation response tests | VERIFIED | Confirms structured metadata only and exact blocked-path message. |
| [services/speech-worker/providers/contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py) | Provider interfaces | VERIFIED | Typed VAD, STT, TTS, and speech-to-speech protocols. |
| [services/speech-worker/tests/test_provider_contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/tests/test_provider_contracts.py) | Provider contract tests | VERIFIED | Confirms the interfaces are swappable and behavior-shaped. |
| [pyproject.toml](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml) | Python test scaffold | VERIFIED | Declares FastAPI, Pydantic, pytest, and package discovery for the approved venv path. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| [apps/web/app/page.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/page.tsx:1) | [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:35) | Root page renders the studio component directly. | WIRED | `HomePage` returns `StudioShell` at `/`. |
| [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:5) | [apps/web/lib/voice-registry.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/lib/voice-registry.ts:13) | Studio reads the render-only Vesper Glass display seed. | WIRED | Voice identity, boundary note, and badge text stay aligned to one local seed. |
| [apps/web/tests/root-route.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/root-route.spec.ts:3) | [apps/web/app/page.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/app/page.tsx:1) | Playwright checks the root route renders the studio-first surface and omits Phase 2 controls. | WIRED | Smoke test covers the route contract. |
| [services/api/app/schemas/voice_profile.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/voice_profile.py:10) | [services/api/app/voice_registry/bundled_voice.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/voice_registry/bundled_voice.py:5) | Bundled Vesper Glass data must satisfy the same rights fields as the schema. | WIRED | The registry record validates against the strict schema. |
| [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py:53) | [services/api/app/routes/voices.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/voices.py:12) | Route exposes the server-owned record while the gate enforces approval before generation. | WIRED | The API is authoritative for rights checks. |
| [services/api/tests/test_rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_rights_gate.py:34) | [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py:53) | Tests assert blocked and approved outcomes against the exact safety gate. | WIRED | Covers both approved and rejected paths. |
| [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py:13) | [services/api/app/services/stub_generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py:17) | The route delegates the allowed path to the stub service after rights checks pass. | WIRED | Metadata-only assembly happens after server approval. |
| [services/api/app/services/stub_generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py:17) | [services/speech-worker/providers/contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py:38) | The stub service emits provider trace and timing data shaped by the provider boundary. | WIRED | Keeps future provider swaps behind a narrow contract. |
| [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:47) | [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py:13) | The single studio generation action posts the selected Vesper Glass voice to the API and renders the structured metadata card. | WIRED | The UI contract matches the `/generate` API contract. |
| [apps/web/tests/studio-generation.spec.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/tests/studio-generation.spec.ts:3) | [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:47) | The browser test proves the trigger/result-card loop without introducing Phase 2 controls. | WIRED | Route interception checks the request and response shape. |
| [services/api/tests/test_generate_stub.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/tests/test_generate_stub.py:15) | [services/api/app/routes/generate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/routes/generate.py:13) | Tests assert the allowed and blocked responses stay metadata-only. | WIRED | Confirms the safety gate and no-audio payload contract. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| [apps/web/components/studio-shell.tsx](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx:35) | `selectedVoice`, `generationResult` | `selectedVoice` starts from the intentional render-only seed in [apps/web/lib/voice-registry.ts](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/lib/voice-registry.ts:13); `generationResult` comes from `fetch("/generate")`, which the API route resolves from the server registry and stub service. | Yes for the generation card; the local voice seed is intentionally static display copy. | ✓ VERIFIED |
| [services/api/app/services/stub_generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/stub_generation.py:17) | `GenerationResult` | `VOICE_REGISTRY[request.voice_id]` after `ensure_voice_allowed(profile)` and strict Pydantic model assembly. | Yes | ✓ VERIFIED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Direct-root studio shell and no-login surface | `pnpm --dir apps/web build` | Passed | ✓ PASS |
| Root-route smoke verification | `pnpm --dir apps/web exec playwright test tests/root-route.spec.ts` | Passed | ✓ PASS |
| Studio generation browser contract | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | Passed | ✓ PASS |
| API rights, schema, and stub generation checks | `.venv/bin/python -m pytest services/api/tests/test_voice_profile.py services/api/tests/test_rights_gate.py services/api/tests/test_generate_stub.py -q` | 11 passed | ✓ PASS |
| Worker provider contract checks | `.venv/bin/python -m pytest services/speech-worker/tests/test_provider_contracts.py -q` | Passed | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| GOV-01 | 01-02 | User can only generate with a voice profile that has explicit rights metadata. | SATISFIED | `VoiceProfile`/`VoiceRights` require rights fields; `ensure_voice_allowed` blocks incomplete metadata; `test_rights_gate.py` covers approved and rejected paths. |
| GOV-02 | 01-02 | System blocks generation requests for voice profiles that are not approved for generation. | SATISFIED | `rights_gate.py` returns 403 with the exact blocked-path message; `test_generate_stub.py` verifies the response body. |
| GOV-03 | 01-01 and 01-02 | First bundled voice profile is described as an original theatrical voice, not Loki, Tom Hiddleston, or any other unlicensed identity. | SATISFIED | `voice-registry.ts`, `bundled_voice.py`, and the schema tests keep the copy inside the original-theatrical boundary. |
| STUD-01 | 01-01 | User can open a no-login web studio. | SATISFIED | `page.tsx` renders the studio directly and the root-route smoke test passes. |
| STUD-02 | 01-01 | User can select the bundled original theatrical voice profile. | SATISFIED | The studio renders the bundled Vesper Glass selector and the profile card on first paint. |
| PIPE-01 | 01-03 | System exposes provider interfaces for VAD, STT, TTS, and speech-to-speech candidates. | SATISFIED | `services/speech-worker/providers/contracts.py` defines the four protocols and the provider contract test exercises them. |

The phase-1 requirement traceability in [`.planning/REQUIREMENTS.md`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/.planning/REQUIREMENTS.md) already maps all six IDs to Phase 1 and marks them complete; no orphaned Phase 1 requirement IDs remain.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| [services/api/app/services/rights_gate.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/rights_gate.py:18) | 18 | `return []` | Info | Defensive normalization for malformed input in `_text_items`; not a stub and not user-visible. |

No TODO/FIXME/XXX debt markers were found in the modified phase files.

### Gaps Summary

None. The phase-1 goal is achieved in the codebase and the automated checks passed.

---

_Verified: 2026-07-01T01:46:20Z_
_Verifier: the agent (gsd-verifier)_
