# Walking Skeleton - Theatrical Voice Studio

**Phase:** 1
**Generated:** 2026-06-30

## Capability Proven End-to-End

The user can open `/`, select Vesper Glass, trigger a rights-gated stub generation request, and receive a structured backend metadata result card in the studio.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Next.js App Router for `apps/web` plus FastAPI for `services/api` | The studio shell needs route-driven rendering, while the control plane needs typed request validation and server-side rights enforcement. |
| Data layer | Server-owned voice registry read plus structured stub/timing metadata write; no persistent database in Phase 1 | This proves the read/write shape needed for later phases without adding storage just to satisfy the skeleton. |
| Auth | No-login Phase 1 with server-side rights gating | Matches the product direction and keeps consent enforcement authoritative on the backend. |
| Provider boundary | Python `Protocol` / ABC contracts for VAD, STT, TTS, and speech-to-speech | Future model swaps should replace adapters, not the studio contract. |
| Deployment target | Cloud web app architecture with local full-stack development as the Phase 1 proving ground | Keeps the rented-GPU direction explicit while still allowing the skeleton to run during development. |
| Directory layout | `apps/web`, `services/api`, `services/speech-worker`, `packages/shared`, `infra` | Separates the studio, control plane, worker boundary, shared contracts, and deployment assets from the start. |

## Stack Touched in Phase 1

- [ ] Project scaffold (framework, build, lint, test runner)
- [ ] Routing - direct `/` studio surface
- [ ] Data layer - server-owned voice registry read plus structured stub/timing metadata write
- [ ] UI - voice selector, approval badge, Vesper Glass profile card, stub generation button, and structured result card
- [ ] Deployment - local full-stack run command or dev environment that exercises web + API

## Out of Scope

> Anything not included in the skeleton stays deferred so later slices do not have to renegotiate Phase 1 decisions.

- Accounts, saved clip libraries, or any other login flow
- Text input, tone presets, retry UX, or audio playback controls
- Mic capture, audio upload, VAD, STT, or live conversation controls
- Benchmark harnesses, model comparisons, or provider selection reports
- Public API exposure or team approval workflows
- Exact Marvel Loki, Tom Hiddleston, or any other unlicensed identity cloning

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without changing these architectural decisions:

- Phase 2: Text-driven studio generation with one real speech provider and browser playback
- Phase 3: Browser microphone input, VAD, STT, and transcript inspection
- Phase 4: Live conversation mode with interruption handling
- Phase 5: Provider benchmark and model selection evidence
- Phase 6: Cloud GPU deployment hardening and internal beta observability
