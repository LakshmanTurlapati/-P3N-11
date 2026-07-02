# Roadmap: Theatrical Voice Studio

## Overview

The v1 milestone builds a no-login internal web app that proves the full voice workflow without committing too early to one speech model. The roadmap starts with a thin vertical skeleton and rights-gated voice registry, then adds real studio generation, audio input, live conversation, benchmark-driven model selection, and cloud GPU deployment hardening.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: No-Login Vertical Skeleton** - Prove the web/API/audio path and consent-safe voice registry. (completed 2026-07-01)
- [ ] **Phase 2: Consented Studio Generation** - Generate playable speech from text with one real provider and tone presets.
- [ ] **Phase 3: Audio Input and Turn Detection** - Add mic/audio input, VAD, STT, and transcript inspection.
- [ ] **Phase 4: Live Conversation Mode** - Combine speech input, persona response, TTS output, and interruption handling.
- [ ] **Phase 5: Model Benchmark and Selection** - Compare VAD, TTS, and end-to-end speech candidates with repeatable metrics.
- [ ] **Phase 6: Cloud GPU Deployment and Internal Beta Hardening** - Make the app deployable and debuggable on rented GPU infrastructure.

## Phase Details

### Phase 1: No-Login Vertical Skeleton

**Goal**: User can open the web studio, select the bundled original theatrical voice, and trigger a rights-gated generation path through provider interfaces.
**Mode:** mvp
**UI hint**: yes
**Depends on**: Nothing (first phase)
**Requirements**: [GOV-01, GOV-02, GOV-03, STUD-01, STUD-02, PIPE-01]
**Success Criteria** (what must be TRUE):

  1. User can open a no-login web studio.
  2. User can see and select the bundled original theatrical voice profile.
  3. System blocks generation unless the selected voice profile is approved for generation.
  4. Provider contracts exist for VAD, STT, TTS, and speech-to-speech candidates.
  5. The first voice is described as an original theatrical voice, not as a protected character or actor clone.

**Plans**: 3/3 plans complete

Plans:

- [x] 01-01-PLAN.md
- [x] 01-02-PLAN.md
- [x] 01-03-PLAN.md

**Wave 1**

- [x] 01-01: Web studio shell and no-login routing
- [x] 01-02: Voice profile schema and consent enforcement

**Wave 2**

- [x] 01-03: Speech provider interfaces and stub generation path

### Phase 2: Consented Studio Generation

**Goal**: User can enter text, choose a tone preset, generate speech through a real provider, and play the resulting audio.
**Mode:** mvp
**UI hint**: yes
**Depends on**: Phase 1
**Requirements**: [GOV-04, STUD-03, STUD-04, STUD-05, STUD-06, STUD-07, PIPE-02, PIPE-03, PIPE-04]
**Success Criteria** (what must be TRUE):

  1. User can enter text and select a tone preset.
  2. User can generate speech through at least one real TTS or voice-cloning provider.
  3. User can play generated audio in the browser.
  4. User sees loading, success, error, and retry states.
  5. Generated audio is stored with provider, voice, tone, and timing metadata.

**Plans**: 3/4 plans executed

Plans:

- [x] 02-01-PLAN.md
- [x] 02-02-PLAN.md
- [x] 02-03-PLAN.md
- [ ] 02-04-PLAN.md

**Wave 1**

- [x] 02-01: Studio text input, tone presets, and generation UX

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02: First real TTS provider adapter and audio normalization
- [ ] 02-03: Generation job metadata, storage, playback, and retry behavior

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 02-04: Browser playback surface and session-scoped retry

### Phase 3: Audio Input and Turn Detection

**Goal**: User can provide spoken input, system can detect speech boundaries, transcribe the turn, and expose the transcript.
**Mode:** mvp
**UI hint**: yes
**Depends on**: Phase 2
**Requirements**: [AUD-01, AUD-02, AUD-03, AUD-04]
**Success Criteria** (what must be TRUE):

  1. User can provide microphone or uploaded audio input.
  2. System can detect speech boundaries through a VAD provider.
  3. System can transcribe spoken input through an STT provider.
  4. User can inspect the recognized transcript.
  5. The audio input path shares the same provider and job architecture as studio generation.

**Plans**: 3 plans

Plans:

- [ ] 03-01: Browser microphone and audio upload input
- [ ] 03-02: VAD provider baseline and turn segmentation
- [ ] 03-03: STT provider baseline and transcript inspection

### Phase 4: Live Conversation Mode

**Goal**: User can speak to the voicebot and receive a spoken response in the selected original voice and tone, with interruption support.
**Mode:** mvp
**UI hint**: yes
**Depends on**: Phase 3
**Requirements**: [CONV-01, CONV-02, CONV-03, CONV-04, CONV-05]
**Success Criteria** (what must be TRUE):

  1. User can start live conversation mode from the web app.
  2. User speech produces a spoken response using the selected voice and tone.
  3. Response text follows the original theatrical persona boundary.
  4. User can interrupt or cancel a response and continue the conversation.
  5. System records end-to-end latency for conversation turns.

**Plans**: 3 plans

Plans:

- [ ] 04-01: Conversation session state and UI controls
- [ ] 04-02: Persona-safe LLM response and speech output loop
- [ ] 04-03: Interruption handling and turn latency metrics

### Phase 5: Model Benchmark and Selection

**Goal**: Team can compare speech model candidates with fixed inputs and choose baseline providers using evidence.
**Mode:** mvp
**UI hint**: no
**Depends on**: Phase 4
**Requirements**: [BEN-01, BEN-02, BEN-03, BEN-04, BEN-05]
**Success Criteria** (what must be TRUE):

  1. Fixed benchmark input set exists for voice quality, latency, and reliability.
  2. At least two VAD candidates or configurations are compared.
  3. At least two TTS or voice-cloning candidates are compared.
  4. Feasible end-to-end speech-to-speech candidates have recorded findings.
  5. Recommendation report includes quality, latency, GPU/runtime cost, license fit, and integration risk.

**Plans**: 3 plans

Plans:

- [ ] 05-01: Benchmark corpus, metrics schema, and report format
- [ ] 05-02: VAD and TTS candidate benchmark adapters
- [ ] 05-03: End-to-end speech model findings and provider recommendation

### Phase 6: Cloud GPU Deployment and Internal Beta Hardening

**Goal**: Internal user can run or deploy the no-login web app as separate web, API, and speech-worker services on rented GPU infrastructure.
**Mode:** mvp
**UI hint**: no
**Depends on**: Phase 5
**Requirements**: [DEP-01, DEP-02, DEP-03, DEP-04, DEP-05]
**Success Criteria** (what must be TRUE):

  1. Web, API/control-plane, and speech-worker services can run separately.
  2. Reference audio and generated clips persist outside the app process.
  3. API and speech-worker readiness health checks exist.
  4. Generation errors and latency are logged for internal debugging.
  5. Setup documentation explains how to run or deploy on rented GPU infrastructure.

**Plans**: 3 plans

Plans:

- [ ] 06-01: Service separation and deployment configuration
- [ ] 06-02: Audio persistence, health checks, and observability
- [ ] 06-03: Internal beta setup documentation and safety audit

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. No-Login Vertical Skeleton | 3/3 | Complete    | 2026-07-01 |
| 2. Consented Studio Generation | 3/4 | In Progress|  |
| 3. Audio Input and Turn Detection | 0/3 | Not started | - |
| 4. Live Conversation Mode | 0/3 | Not started | - |
| 5. Model Benchmark and Selection | 0/3 | Not started | - |
| 6. Cloud GPU Deployment and Internal Beta Hardening | 0/3 | Not started | - |
