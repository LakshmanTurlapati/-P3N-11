# Phase 5: Model Benchmark and Selection - Context

**Gathered:** 2026-07-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 5 creates the evidence base for model selection. It should add a repeatable benchmark corpus, metrics/results schema, candidate adapters or documented blockers, and a recommendation report that compares VAD, TTS/voice-cloning, and feasible end-to-end speech-to-speech candidates against quality, latency, reliability, runtime cost, license fit, and integration risk.

This phase does not add a benchmark dashboard, user accounts, saved libraries, deployment hardening, detailed studio controls, public APIs, or a full provider migration unless the benchmark winner is clearly low-risk and already fits the existing provider contracts.

</domain>

<decisions>
## Implementation Decisions

### Benchmark Corpus Shape
- **D-01:** Use a balanced benchmark suite. The corpus should cover theatrical text prompts, clean and noisy spoken turns, short and longer clips, expected failure cases, voice quality, latency, and reliability.
- **D-02:** Store benchmark inputs as a repo manifest plus small consent-safe fixtures. Text prompts and a few short WAV fixtures should live in the repo; generated/noise variants may be created deterministically.
- **D-03:** Audio fixtures should include transcript text plus rough speech-window ground truth: approximate speech start/end, duration, and noise/condition tags. Do not require sample-perfect segment labels in this phase.
- **D-04:** Persona and tone coverage should include fixed cases for the existing `measured`, `cutting`, and `grandiose` presets, with expected safety/persona notes for reviewers and the report.

### Candidate Set And Evidence Depth
- **D-05:** Benchmark existing Silero VAD against one real alternate VAD candidate behind `VADProvider`. The exact alternate, such as TEN VAD or FireRedVAD, is left to research/planning based on install and runtime fit.
- **D-06:** Benchmark existing CosyVoice TTS against one additional feasible TTS or voice-cloning candidate behind `TTSProvider`. The additional candidate should be chosen for license and runtime feasibility.
- **D-07:** Include candidates in the recommendation only when they have runnable benchmark harness evidence or a clearly documented setup/runtime/license blocker. Do not rank candidates from vague research notes alone.
- **D-08:** Treat end-to-end speech-to-speech candidates as a findings-first feasibility scan. Record license, hardware/runtime needs, streaming/latency posture, voice-control fit, and integration risk for candidates such as Chroma, MiniCPM-o, Qwen Omni, or Moshi; run one only if it does not derail the VAD/TTS benchmarks.

### Scoring And Report Format
- **D-09:** Use a balanced gate matrix. Candidates must pass minimum safety, license, and integration gates before quality, latency, reliability, and runtime cost are compared.
- **D-10:** Capture subjective voice quality with a small 1-5 reviewer rubric for intelligibility, persona/tone fit, naturalness, artifact level, and safety-boundary adherence.
- **D-11:** Report both stage and total timings where the path supports them: VAD, STT, response text when relevant, TTS, playback-ready, and total wall time.
- **D-12:** Produce both a human-readable Markdown recommendation report and machine-readable results such as JSON or CSV for reruns and future comparison.

### Selection Outcome
- **D-13:** Recommend first and switch defaults only if low-risk. Phase 5 may update app defaults only when the winner is runnable, license-safe, and does not destabilize existing studio or conversation flows.
- **D-14:** Allow separate recommendations by workflow path. Live conversation may prefer a lower-latency provider while studio generation may prefer a higher-quality provider; keep app defaults conservative.
- **D-15:** Treat license and consent fit as a hard gate. Exclude or block recommendation of candidates whose code, model weights, or usage terms do not fit the internal MVP or consent-safe voice generation.
- **D-16:** Keep promising failures in the report as blocked candidates with the exact blocker, attempted setup evidence, and the next action needed to unblock them.

### the agent's Discretion
- **D-17:** Downstream agents may choose exact fixture counts, manifest/result schema names, runner CLI names, benchmark output paths, metric threshold values, and the specific alternate VAD/TTS candidates as long as the decisions above are preserved.
- **D-18:** If an alternate candidate fails setup or licensing review, downstream agents should document the blocker and keep the recommendation conservative rather than inventing metrics or forcing a risky default switch.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope And Requirements
- `.planning/PROJECT.md` - Defines the benchmark-first model strategy, consented/original voice boundary, cloud GPU direction, provider-interface posture, and current Phase 4 completion state.
- `.planning/REQUIREMENTS.md` - Maps Phase 5 to BEN-01 through BEN-05: benchmark corpus, VAD comparison, TTS/cloning comparison, end-to-end findings, and recommendation report.
- `.planning/ROADMAP.md` - Defines Phase 5 goal, success criteria, and planned slices: benchmark corpus/report, VAD/TTS adapters, end-to-end findings, and provider recommendation.
- `.planning/STATE.md` - Captures current project position, accumulated decisions, and blockers/concerns affecting model compatibility and license checks.

### Prior Phase Handoff
- `.planning/phases/04-live-conversation-mode/04-CONTEXT.md` - Locks live conversation timing, turn-based response loop, interruption behavior, and the fact that multi-provider comparison belongs to Phase 5.
- `.planning/phases/03-audio-input-and-turn-detection/03-CONTEXT.md` - Locks the Silero-compatible VAD baseline, faster-whisper-compatible STT baseline, transcript metadata, and VAD comparison deferral to Phase 5.
- `.planning/phases/02-consented-studio-generation/02-CONTEXT.md` - Locks the CosyVoice baseline, queued generation jobs, controlled playback, tone presets, local object-store pattern, and provider-interface constraints.

### Research And Architecture
- `.planning/research/STACK.md` - Lists current stack assumptions and candidate speech components, including faster-whisper, Silero VAD, TEN VAD, FireRedVAD, F5-TTS, CosyVoice, OpenVoice, Fish Speech, Step-Audio, Chroma, MiniCPM-o, and Qwen3-Omni.
- `.planning/research/ARCHITECTURE.md` - Defines the web/API/worker split, provider adapter boundary, storage role, and speech pipeline architecture that benchmarks must preserve.
- `.planning/research/PITFALLS.md` - Captures model lock-in, latency, VAD false turns, provider dependency conflicts, license risk, and runtime/deployment pitfalls relevant to benchmark design.
- `.planning/research/FEATURES.md` - Defines expected v1 speech features and the role of provider abstraction, live conversation, and model benchmarking.

### Code References
- `services/speech-worker/providers/contracts.py` - Defines the `VADProvider`, `STTProvider`, `TTSProvider`, and `SpeechToSpeechProvider` contracts the benchmark adapters should preserve.
- `services/speech-worker/providers/silero_vad_provider.py` - Current Silero-compatible VAD baseline and deterministic fixture fallback.
- `services/speech-worker/providers/cosyvoice_provider.py` - Current CosyVoice TTS baseline, tone prompt steering, and WAV normalization path.
- `services/api/app/services/audio_turn_runtime.py` - Current VAD/STT runtime, audio normalization, speech-window extraction, provider metadata, and failure behavior.
- `services/api/app/services/generation_runtime.py` - Current TTS runtime, provider loading, generated artifact duration, and failure behavior.
- `services/api/app/services/conversation_runtime.py` - Current conversation pipeline and stage timing fields that benchmark timing should align with.
- `services/speech-worker/tests/test_provider_contracts.py` - Existing provider swappability test pattern.
- `services/speech-worker/tests/test_audio_turn_providers.py` - Existing Silero/faster-whisper provider test and fixture patterns.
- `services/speech-worker/tests/test_cosyvoice_provider.py` - Existing CosyVoice provider test and normalization expectations.

No separate Phase 5 SPEC.md exists as of this discussion.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `services/speech-worker/providers/contracts.py` - The benchmark harness can use existing provider protocols instead of creating provider-specific call sites.
- `services/speech-worker/providers/silero_vad_provider.py` - Existing VAD baseline with fixture fallback can be the first benchmark target and adapter reference.
- `services/speech-worker/providers/cosyvoice_provider.py` - Existing TTS baseline with tone steering can be the first TTS benchmark target and adapter reference.
- `services/api/app/services/audio_turn_runtime.py` - Existing audio normalization, VAD metadata summarization, and speech-window extraction can inform fixture preparation and VAD/STT metrics.
- `services/api/app/services/generation_runtime.py` - Existing TTS artifact duration and provider metadata can inform benchmark timing/result fields.
- `services/api/app/services/conversation_runtime.py` - Existing conversation stage timings provide names and semantics for latency reporting.
- `services/speech-worker/tests/test_provider_contracts.py`, `services/speech-worker/tests/test_audio_turn_providers.py`, and `services/speech-worker/tests/test_cosyvoice_provider.py` - Existing provider test fixtures show how to keep local validation deterministic while preserving real provider boundaries.

### Established Patterns
- Provider contracts are the boundary. Benchmark work should not introduce model-specific logic into the web UI or API schemas.
- Deterministic fixtures are acceptable for local tests, but benchmark candidates should either run through the harness or be recorded as blocked with evidence.
- Existing jobs and conversation turns already record provider names, status, duration, and stage timing metadata. Benchmark result schemas should align with these fields rather than invent unrelated terminology.
- Controlled artifacts and local object-store patterns already exist for generated audio and captured turns. Benchmark fixtures/results should avoid exposing raw internal filesystem paths through app routes.
- The root studio remains no-login and minimal. Phase 5 has `UI hint: no`; benchmark output should be files/reports, not a new dashboard.

### Integration Points
- Benchmark corpus: add manifest and small fixtures under a repo path chosen during planning.
- Benchmark runner: call VAD/TTS/SpeechToSpeech providers through existing contracts and capture structured results.
- VAD candidates: reuse Silero baseline and add one alternate provider adapter or documented blocker.
- TTS/cloning candidates: reuse CosyVoice baseline and add one feasible additional provider adapter or documented blocker.
- Report artifacts: generate a Markdown recommendation report plus JSON/CSV results for future reruns.
- Tests: add focused contract/runner tests proving corpus loading, result schema validation, provider invocation, blocked-candidate recording, and report generation.

</code_context>

<specifics>
## Specific Ideas

- The benchmark corpus should exercise the existing `measured`, `cutting`, and `grandiose` tone presets rather than introducing new studio controls.
- The recommendation should make it clear when live conversation and studio generation prefer different providers.
- Candidate evidence should distinguish runnable benchmark metrics from blocked setup/license/runtime findings.
- End-to-end speech-to-speech candidates should be investigated without letting them consume the whole phase unless one is clearly feasible.

</specifics>

<deferred>
## Deferred Ideas

- A visual benchmark dashboard - not in Phase 5; use file-based reports and structured results first.
- Aggressive default provider migration - only switch defaults if low-risk; otherwise defer provider migration hardening.
- Running every end-to-end speech model - defer broad execution unless setup is feasible without derailing VAD/TTS benchmarks.
- Deployment hardening, GPU service separation, health checks, and beta setup documentation - belongs to Phase 6.

</deferred>

---

*Phase: 5-Model Benchmark and Selection*
*Context gathered: 2026-07-13*
