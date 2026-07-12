# Requirements: Theatrical Voice Studio

**Defined:** 2026-06-30
**Core Value:** Users can speak or write an input and receive a high-quality spoken response in a controllable, consented character voice with low enough latency to feel conversational.

## v1 Requirements

Requirements for the initial internal no-login web app. Each maps to exactly one roadmap phase.

### Governance

- [x] **GOV-01**: User can only generate with a voice profile that has explicit rights metadata.
- [x] **GOV-02**: System blocks generation requests for voice profiles that are not approved for generation.
- [x] **GOV-03**: First bundled voice profile is described as an original theatrical trickster voice, not as Marvel Loki, Tom Hiddleston, or any other unlicensed identity.
- [x] **GOV-04**: User can attach or record consent/license notes for a voice reference before that voice is used for cloning.

### Studio

- [x] **STUD-01**: User can open a no-login web studio.
- [x] **STUD-02**: User can select the bundled original theatrical voice profile.
- [x] **STUD-03**: User can enter text to synthesize into speech.
- [x] **STUD-04**: User can choose a tone preset for generation.
- [x] **STUD-05**: User can submit a generation request and see loading, success, and error states.
- [x] **STUD-06**: User can play the generated audio in the browser.
- [x] **STUD-07**: User can retry a failed generation without refreshing the app.

### Speech Pipeline

- [x] **PIPE-01**: System exposes provider interfaces for VAD, STT, TTS, and speech-to-speech candidates.
- [x] **PIPE-02**: System can synthesize speech through at least one real TTS or voice-cloning provider adapter.
- [x] **PIPE-03**: System stores generated audio with metadata that includes provider, voice profile, tone preset, and generation timing.
- [x] **PIPE-04**: System can normalize uploaded, recorded, or generated audio into formats accepted by the selected providers.

### Audio Input

- [x] **AUD-01**: User can provide spoken input through the browser microphone or an uploaded audio clip.
- [x] **AUD-02**: System can detect speech boundaries using a VAD provider.
- [x] **AUD-03**: System can transcribe user speech through an STT provider.
- [x] **AUD-04**: User can see or inspect the recognized transcript before or during speech-to-speech generation.

### Conversation

- [ ] **CONV-01**: User can start a live conversation mode from the web app.
- [ ] **CONV-02**: User can speak a turn and receive a spoken response using the selected voice and tone.
- [ ] **CONV-03**: System response text follows the original theatrical persona boundary without claiming to be a protected character or real person.
- [ ] **CONV-04**: User can interrupt or cancel a spoken response and continue the conversation.
- [ ] **CONV-05**: System records basic end-to-end conversation latency for each turn.

### Benchmarks

- [ ] **BEN-01**: System includes a fixed benchmark input set for voice quality, latency, and reliability comparisons.
- [ ] **BEN-02**: System can compare at least two VAD candidates or configurations using the benchmark set.
- [ ] **BEN-03**: System can compare at least two TTS or voice-cloning candidates using the benchmark set.
- [ ] **BEN-04**: System can record findings for end-to-end speech-to-speech candidates such as Chroma, MiniCPM-o, Qwen Omni, or Moshi when feasible.
- [ ] **BEN-05**: System produces a recommendation report that includes quality, latency, GPU/runtime cost, license fit, and integration risk.

### Deployment

- [ ] **DEP-01**: System can run as separate web, API/control-plane, and speech-worker services.
- [ ] **DEP-02**: System can persist reference audio and generated clips outside the application process.
- [ ] **DEP-03**: System exposes health checks for API and speech-worker readiness.
- [ ] **DEP-04**: System logs generation errors and latency in a way that supports internal debugging.
- [ ] **DEP-05**: Internal user can follow setup documentation to run or deploy the v1 web app on a rented GPU environment.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Accounts and Libraries

- **ACCT-01**: User can create an account.
- **ACCT-02**: User can save generated clips to a personal library.
- **ACCT-03**: User can organize multiple voice profiles in a personal workspace.

### Advanced Studio

- **ADV-01**: User can adjust detailed tone sliders such as sarcasm, warmth, pace, and intensity.
- **ADV-02**: User can batch-generate multiple lines.
- **ADV-03**: User can compare model outputs side by side in the studio UI.

### Public Platform

- **PLAT-01**: Developer can call a public API to create voice generations.
- **PLAT-02**: Admin can manage rate limits and usage quotas.
- **PLAT-03**: Team can run approval workflows for new voice profiles.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Exact Marvel Loki, Tom Hiddleston, or other unlicensed voice imitation | The product must use original or consented/licensed voices only. |
| Full user account system in v1 | User chose no-login first version focused on the speech loop. |
| Saved clip history in v1 | Useful later, but not required to validate generation and conversation. |
| Detailed tone sliders in v1 | User chose minimal controls first; presets are enough for validation. |
| Batch generation in v1 | Not needed for the internal MVP. |
| Public API in v1 | Provider contracts should stabilize before external API support. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-01 | Phase 1 | Complete |
| GOV-02 | Phase 1 | Complete |
| GOV-03 | Phase 1 | Complete |
| GOV-04 | Phase 2 | Complete |
| STUD-01 | Phase 1 | Complete |
| STUD-02 | Phase 1 | Complete |
| STUD-03 | Phase 2 | Complete |
| STUD-04 | Phase 2 | Complete |
| STUD-05 | Phase 2 | Complete |
| STUD-06 | Phase 2 | Complete |
| STUD-07 | Phase 2 | Complete |
| PIPE-01 | Phase 1 | Complete |
| PIPE-02 | Phase 2 | Complete |
| PIPE-03 | Phase 2 | Complete |
| PIPE-04 | Phase 2 | Complete |
| AUD-01 | Phase 3 | Complete |
| AUD-02 | Phase 3 | Complete |
| AUD-03 | Phase 3 | Complete |
| AUD-04 | Phase 3 | Complete |
| CONV-01 | Phase 4 | Pending |
| CONV-02 | Phase 4 | Pending |
| CONV-03 | Phase 4 | Pending |
| CONV-04 | Phase 4 | Pending |
| CONV-05 | Phase 4 | Pending |
| BEN-01 | Phase 5 | Pending |
| BEN-02 | Phase 5 | Pending |
| BEN-03 | Phase 5 | Pending |
| BEN-04 | Phase 5 | Pending |
| BEN-05 | Phase 5 | Pending |
| DEP-01 | Phase 6 | Pending |
| DEP-02 | Phase 6 | Pending |
| DEP-03 | Phase 6 | Pending |
| DEP-04 | Phase 6 | Pending |
| DEP-05 | Phase 6 | Pending |

**Coverage:**

- v1 requirements: 34 total
- Mapped to phases: 34
- Unmapped: 0

---
*Requirements defined: 2026-06-30*
*Last updated: 2026-06-30 after roadmap creation*
