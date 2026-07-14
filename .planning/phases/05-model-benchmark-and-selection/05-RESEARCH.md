# Phase 5: Model Benchmark and Selection - Research

**Researched:** 2026-07-13
**Domain:** Speech model benchmarking, provider selection, and benchmark corpus/reporting
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)
- A visual benchmark dashboard - not in Phase 5; use file-based reports and structured results first.
- Aggressive default provider migration - only switch defaults if low-risk; otherwise defer provider migration hardening.
- Running every end-to-end speech model - defer broad execution unless setup is feasible without derailing VAD/TTS benchmarks.
- Deployment hardening, GPU service separation, health checks, and beta setup documentation - belongs to Phase 6.
</user_constraints>

## Project Constraints (from AGENTS.md)

- Preserve the consented/original voice boundary. Do not plan around exact Loki/Tom Hiddleston imitation.
- Keep v1 no-login, studio-first, and cloud GPU oriented. Do not assume local-only deployment.
- Keep speech components behind provider interfaces so model swaps do not rewrite the product.
- Optimize for latency and quality together, not just one dimension.
- Keep rights/consent metadata authoritative before generation.
- Use GSD workflow discipline for file changes; do not treat this phase as ad hoc repo editing.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BEN-01 | Fixed benchmark input set for voice quality, latency, and reliability | Corpus shape, repo-manifest fixture pattern, rough speech-window metadata, and tone coverage in Summary / Architecture Patterns |
| BEN-02 | Compare at least two VAD candidates or configurations | VAD candidate docs, provider contract shape, package-legitimacy audit, and Common Pitfalls |
| BEN-03 | Compare at least two TTS or voice-cloning candidates | TTS candidate docs, provider contract shape, package-legitimacy audit, and Standard Stack |
| BEN-04 | Record findings for feasible end-to-end speech-to-speech candidates | End-to-end scan notes, hardware/runtime availability, and Common Pitfalls |
| BEN-05 | Produce recommendation report with quality, latency, GPU/runtime cost, license fit, and integration risk | Summary, State of the Art, Sources, and Package Legitimacy Audit |
</phase_requirements>

## Summary

Phase 5 should stay backend/file-based. The current repo already defines the key seams the benchmark harness needs: provider protocols for VAD/STT/TTS/S2S, stage-timing fields on generation/conversation/audio-turn records, and repo-backed object storage patterns for audio artifacts [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/conversation.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/conversation_jobs.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py].

The most actionable comparison set is Silero vs FireRedVAD for VAD and CosyVoice vs Qwen3-TTS for TTS. FireRedVAD and qwen-tts are official PyPI packages but both were flagged `SUS` by the package gate because downloads are unknown, so the planner must add `checkpoint:human-verify` before any install [VERIFIED: package-legitimacy check] [CITED: https://github.com/FireRedTeam/FireRedVAD] [CITED: https://github.com/QwenLM/Qwen3-TTS]. OpenVoice and F5-TTS remain useful fallbacks, but F5-TTS weights are CC-BY-NC and OpenVoice is repo-based with a heavier dependency stack [CITED: https://github.com/SWivid/F5-TTS] [CITED: https://github.com/myshell-ai/OpenVoice].

End-to-end speech-to-speech work should remain findings-first. Moshi and MiniCPM-o 4.5 look like the best first scan targets because they have clear streaming/full-duplex docs and bounded runtime stories; Chroma and Qwen3-Omni should stay as heavier/late-scan candidates because Chroma needs CUDA 12.6 and Qwen3-Omni is a 30B-A3B-class stack with open streaming issues in the repo [CITED: https://github.com/kyutai-labs/moshi] [CITED: https://github.com/OpenBMB/MiniCPM-V] [CITED: https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma] [CITED: https://github.com/QwenLM/Qwen3-Omni] [CITED: https://github.com/QwenLM/Qwen3-TTS]. The local benchmark environment is not enough for real model runs: `.venv` is Python 3.11.12 and pytest 9.1.1, but torch, ffmpeg, and GPU access are missing [VERIFIED: shell check].

**Primary recommendation:** build a file-based benchmark harness under `services/speech-worker/benchmarks`, compare Silero vs FireRedVAD and CosyVoice vs Qwen3-TTS, and keep end-to-end models as a small findings-first scan behind human verification checkpoints.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Benchmark corpus manifest, fixtures, and result files | Database / Storage | API / Backend | Corpus and outputs are repo/filesystem assets; the backend runner consumes them [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/audio_turn_jobs.py]. |
| Candidate execution and scoring | API / Backend | Database / Storage | Provider adapters and timing capture belong in worker/backend code, not the browser [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py]. |
| Markdown/JSON/CSV report generation | API / Backend | Database / Storage | Reports should serialize benchmark results, not infer them in the UI [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py] [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/conversation.py]. |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pytest` | 9.1.1 [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | Test and benchmark runner | Already installed in the repo venv and used by current speech tests. |
| `pydantic` | 2.13.4 [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | Corpus/result schema validation | Current app and job records already use Pydantic for strict shape checks. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `silero` baseline provider | existing repo provider [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/silero_vad_provider.py] | Baseline VAD comparison | Use as the benchmark baseline with deterministic fixture fallback. |
| `CosyVoice` baseline checkout | `third_party/CosyVoice` / `Fun-CosyVoice3-0.5B-2512` [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/cosyvoice_provider.py] | Baseline TTS comparison | Use as the current product baseline and timing anchor. |
| `fireredvad` | 0.0.2 [CITED: https://github.com/FireRedTeam/FireRedVAD] [WARNING: flagged as suspicious - verify before using.] | Alternate VAD candidate | Use when comparing a newer streaming/non-streaming VAD with stronger accuracy claims. |
| `qwen-tts` | 0.1.1 [CITED: https://github.com/QwenLM/Qwen3-TTS] [WARNING: flagged as suspicious - verify before using.] | Alternate TTS / voice-cloning candidate | Use when comparing a modern streaming TTS/clone package with explicit voice-design controls. |
| `ffmpeg` | system binary [VERIFIED: shell check] | Audio normalization / conversion | Install in the benchmark host; the current workspace does not have it. |

**Version verification:** `pip index versions` confirmed `qwen-tts` 0.1.1, `fireredvad` 0.0.2, and `f5-tts` 1.1.21 exist on PyPI; package-legitimacy checks flagged `qwen-tts` and `fireredvad` as `SUS` because download data is unknown [VERIFIED: pip index versions] [VERIFIED: package-legitimacy check].

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `fireredvad` | `TEN VAD` | Smaller footprint and cross-platform support, but extra license conditions and a less direct package story [CITED: https://github.com/TEN-framework/ten-vad]. |
| `qwen-tts` | `OpenVoice` | MIT and style-control friendly, but repo-based integration with a heavier dependency stack [CITED: https://github.com/myshell-ai/OpenVoice]. |
| `qwen-tts` | `F5-TTS` | MIT code, but pretrained weights are CC-BY-NC, so license fit is weaker for the benchmark shortlist [CITED: https://github.com/SWivid/F5-TTS]. |

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `qwen-tts` | PyPI | ~5 mo [VERIFIED: pip index versions] | unknown [VERIFIED: package-legitimacy check] | `https://github.com/Qwen/Qwen3-TTS` [CITED: https://github.com/QwenLM/Qwen3-TTS] | `SUS` [VERIFIED: package-legitimacy check] | Flagged - planner must add checkpoint |
| `fireredvad` | PyPI | ~4 mo [VERIFIED: pip index versions] | unknown [VERIFIED: package-legitimacy check] | `https://github.com/FireRedTeam/FireRedVAD` [CITED: https://github.com/FireRedTeam/FireRedVAD] | `SUS` [VERIFIED: package-legitimacy check] | Flagged - planner must add checkpoint |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `qwen-tts`, `fireredvad`

## Architecture Patterns

### System Architecture Diagram

```text
Repo corpus manifest + consent-safe fixtures
  -> benchmark runner (Python/pytest)
    -> provider adapter under test (VAD / TTS / S2S)
      -> candidate runtime (baseline repo checkout or package install)
      -> metrics capture (quality rubric, stage timings, failures, cost, license, risk)
      -> JSON/CSV rows + Markdown report
        -> planner decision
```

### Recommended Project Structure

```text
services/speech-worker/
  benchmarks/
    corpus/
    adapters/
    runs/
    reports/
```

### Pattern 1: Fixed Corpus, Candidate-Specific Adapters
**What:** One canonical corpus, many adapters.  
**When to use:** Always for Phase 5.  
**Example:**
```python
# Source: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py
class VADProvider(Protocol):
    provider_name: str
    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]: ...

class TTSProvider(Protocol):
    provider_name: str
    def synthesize(self, text: str, voice_id: str, *, tone: str | None = None) -> SpeechArtifact: ...
```

### Pattern 2: Reuse Existing Timing Semantics
**What:** Mirror the current `generation`, `audio-turn`, and `conversation` stage timing fields in benchmark output.  
**When to use:** Whenever a benchmark path has stage timings.  
**Example:**
```python
# Source: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/conversation.py
class ConversationTurnTiming(BaseModel):
    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)
    speech_end_to_transcript_ms: int | None = Field(default=None, ge=0)
    response_text_ms: int | None = Field(default=None, ge=0)
    tts_complete_ms: int | None = Field(default=None, ge=0)
    playback_start_ms: int | None = Field(default=None, ge=0)
```

### Anti-Patterns to Avoid
- **Ad hoc cherry-picked clips:** results become subjective and non-repeatable.
- **Candidate-specific preprocessing in the corpus:** keep adapters responsible for any model quirks.
- **Benchmarking without stage timings:** total time alone hides the bottleneck.
- **Mixing license review into prose only:** keep license/weight terms in the report and audit table.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Speech boundary scoring | Custom silence classifier | Provider adapters + fixed corpus | Candidate contracts already exist and are swappable. |
| Audio normalization | One-off signal scripts | `ffmpeg` / current `normalize_audio` helper | Keeps format conversion consistent across candidates. |
| Result serialization | Free-form notes only | Pydantic JSON + CSV/Markdown outputs | Reruns need machine-readable rows. |
| Rights/licensing checks | Prose-only approval | Explicit audit rows + blocked-candidate notes | License fit is a hard gate in this phase. |

**Key insight:** benchmark selection is mostly a reproducibility problem. If the corpus, preprocessing, and timing fields are not fixed, model quality comparisons will not survive reruns.

## Common Pitfalls

### Pitfall 1: Different preprocessing per candidate
**What goes wrong:** one model gets cleaner inputs than another.  
**How to avoid:** keep corpus inputs canonical and move model-specific prep into adapters.

### Pitfall 2: License confusion
**What goes wrong:** code license is treated as model-weight license.  
**How to avoid:** audit code, weights, and package terms separately.

### Pitfall 3: Real-model runs in the wrong environment
**What goes wrong:** torch/GPU/ffmpeg assumptions fail on the local host.  
**How to avoid:** treat this workspace as fixture-test only; run real benchmarks on a GPU host.

### Pitfall 4: End-to-end scans consume the whole phase
**What goes wrong:** Chroma/Qwen3-Omni experiments delay VAD/TTS comparisons.  
**How to avoid:** record findings-first notes and stop after the first feasible proof.

## Code Examples

### Existing provider seams
```python
# Source: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py
@runtime_checkable
class SpeechToSpeechProvider(Protocol):
    provider_name: str
    def transform(self, audio: AudioBuffer, voice_id: str, *, tone: str | None = None) -> SpeechArtifact: ...
```

### Existing timing fields to mirror
```python
# Source: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py
class GenerationTiming(BaseModel):
    started_at: datetime
    ended_at: datetime
    duration_ms: int = Field(ge=0)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Cherry-picked listening tests | Fixed corpus + rubric + machine-readable results | 2026-07-13 | Reproducible model selection. |
| Single-provider assumption | Provider-backed benchmark adapters | 2026-07-13 | Lower lock-in and easier swaps. |
| Total wall time only | Stage + total timings | 2026-07-13 | Clearer bottleneck analysis. |

**Deprecated/outdated:**
- Ad hoc audio comparisons without a manifest or rubric: too subjective for Phase 5.

## Assumptions Log

> If this table is empty, all claims in this research were verified or cited.

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Resolved Planning Decisions

1. **Corpus count for the first manifest: RESOLVED.**
   - Decision: start with at least 6 corpus items.
   - Required coverage: at least 3 text prompt items covering `measured`, `cutting`, and `grandiose`; at least 2 WAV-backed audio items covering clean and noisy conditions; at least 1 expected-failure item.
   - Rationale: this is small enough for fast fixture tests while covering the locked clean/noisy, short/long, tone, reliability, and safety-note dimensions from D-01 through D-04.

2. **End-to-end scan budget: RESOLVED.**
   - Decision: run at most 1 end-to-end speech-to-speech candidate in Phase 05, and only after the VAD/TTS harness and report scaffolding are stable.
   - Default behavior: record findings/blockers for at least 3 S2S candidates without broad runtime execution.
   - Rationale: D-08 makes S2S findings-first and explicitly says not to derail VAD/TTS benchmarks. A runnable proof is allowed only when setup is already approved and cheap; otherwise precise blocker evidence is sufficient.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python venv | benchmark runner/tests | ✓ [VERIFIED: shell check] | 3.11.12 | Use `./.venv/bin/python`. |
| pytest | validation | ✓ [VERIFIED: shell check] | 9.1.1 | None. |
| ffmpeg | audio normalization | ✗ [VERIFIED: shell check] | — | WAV-only corpus + current fallback, or install ffmpeg in the benchmark host. |
| torch | real model benchmarks | ✗ [VERIFIED: shell check] | — | No local fallback for real candidate runs; use a GPU host with matched PyTorch. |
| nvidia-smi / GPU | real model benchmarks | ✗ [VERIFIED: shell check] | — | Use rented GPU infrastructure or a CUDA-capable CI runner. |
| uv | convenience installs | ✗ [VERIFIED: shell check] | — | Use the existing venv and `python -m pip`. |

**Missing dependencies with no fallback:**
- `torch`
- GPU access (`nvidia-smi`)

**Missing dependencies with fallback:**
- `ffmpeg`
- `uv`

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] |
| Config file | `pyproject.toml` |
| Quick run command | `./.venv/bin/python -m pytest services/speech-worker/tests/test_provider_contracts.py services/speech-worker/tests/test_audio_normalization.py services/speech-worker/tests/test_audio_turn_providers.py services/speech-worker/tests/test_cosyvoice_provider.py -q` |
| Full suite command | `./.venv/bin/python -m pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|-----------|-----------|-------------------|-------------|
| BEN-01 | Corpus manifest loads, fixture metadata validates, and rough speech-window tags round-trip | unit | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py -q` | ❌ Wave 0 |
| BEN-02 | Two VAD candidates/configs run against the same corpus and emit comparable rows | integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_vad.py -q` | ❌ Wave 0 |
| BEN-03 | Two TTS/voice-cloning candidates run against the same corpus and emit comparable rows | integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_tts.py -q` | ❌ Wave 0 |
| BEN-04 | Findings-first S2S scan records setup/runtime/license blockers or runnable evidence | integration/manual | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_s2s.py -q` | ❌ Wave 0 |
| BEN-05 | Markdown report plus JSON/CSV outputs serialize the comparison cleanly | unit | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_report.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** quick run command above.
- **Per wave merge:** full suite command above.
- **Phase gate:** full suite green before `$gsd-verify-work`.

### Wave 0 Gaps
- `services/speech-worker/benchmarks/` package does not exist yet.
- `services/speech-worker/tests/test_benchmark_corpus.py` is missing.
- `services/speech-worker/tests/test_benchmark_vad.py` is missing.
- `services/speech-worker/tests/test_benchmark_tts.py` is missing.
- `services/speech-worker/tests/test_benchmark_s2s.py` is missing.
- `services/speech-worker/tests/test_benchmark_report.py` is missing.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 5 is internal and no-login. |
| V3 Session Management | no | No user session state is part of the benchmark harness. |
| V4 Access Control | no | Keep the harness repo-local; no external API surface is introduced. |
| V5 Input Validation | yes | Pydantic corpus/result schemas and path sanitization. |
| V6 Cryptography | no | Do not hand-roll crypto; use existing storage/security primitives if needed. |

### Known Threat Patterns for backend benchmark tooling

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal in fixture/result names | Tampering | Normalize with `Path(...).name` and keep outputs inside the benchmark root. |
| Malformed audio or candidate outputs | DoS | Validate WAV/container shape before scoring; fail fast. |
| Untrusted model text in Markdown reports | Tampering / spoofing | Escape output and treat model text as data, not report markup. |

## Sources

### Primary (HIGH confidence)
- [services/speech-worker/providers/contracts.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py) - provider contracts for VAD/STT/TTS/S2S.
- [services/speech-worker/providers/silero_vad_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/silero_vad_provider.py) - existing baseline VAD and fixture fallback.
- [services/speech-worker/providers/cosyvoice_provider.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/cosyvoice_provider.py) - existing baseline TTS and tone steering.
- [services/api/app/schemas/generation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/generation.py) - generation timing/result schema.
- [services/api/app/schemas/conversation.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/conversation.py) - conversation stage timing schema.
- [services/api/app/schemas/audio_turn.py](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/schemas/audio_turn.py) - VAD metadata schema.
- [pyproject.toml](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml) - pytest and pydantic versions.

### Secondary (MEDIUM confidence)
- https://github.com/FireRedTeam/FireRedVAD - FireRedVAD docs and feature claims.
- https://github.com/QwenLM/Qwen3-TTS - Qwen3-TTS docs and feature claims.
- https://github.com/TEN-framework/ten-vad - TEN VAD docs and license caveats.
- https://github.com/myshell-ai/OpenVoice - OpenVoice docs and license.
- https://github.com/SWivid/F5-TTS - F5-TTS docs and weight-license caveat.
- https://github.com/kyutai-labs/moshi - Moshi docs.
- https://github.com/OpenBMB/MiniCPM-V - MiniCPM-o docs and license.
- https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma - Chroma docs and issue signals.
- https://github.com/QwenLM/Qwen3-Omni - Qwen3-Omni docs and issue signals.

### Tertiary (LOW confidence)
- GitHub issue threads on `FlashLabs-Chroma` and `Qwen3-Omni` indicating setup/streaming/runtime friction.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - existing repo schemas/tests are stable, but the new candidate packages are fresh and SUS-flagged.
- Architecture: HIGH - current code already defines the backend/worker boundaries and timing fields.
- Pitfalls: HIGH - the main failure modes are already visible in the codebase and official docs.

**Research date:** 2026-07-13
**Valid until:** 2026-07-20
