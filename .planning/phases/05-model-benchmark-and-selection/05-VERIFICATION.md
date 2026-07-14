---
phase: 05-model-benchmark-and-selection
verified: 2026-07-14T17:29:13Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 05: Model Benchmark and Selection Verification Report

**Phase Goal:** As a studio operator, I want to compare speech model candidates with fixed inputs and provider-safe benchmark evidence, so that I can choose baseline providers for conversational voice generation.

**Verified:** 2026-07-14T17:29:13Z

**Status:** passed

**Re-verification:** No

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | The repo contains a fixed benchmark corpus with consent-safe text prompts, audio cases, short and long coverage, expected failures, tone cases, and reviewer-facing safety notes. | VERIFIED | `services/speech-worker/benchmarks/corpus/manifest.json:4,14,24,34,49,64,79`; `services/speech-worker/benchmarks/corpus.py:43`; `services/speech-worker/tests/test_benchmark_corpus.py:38` |
| 2 | Corpus loading enforces fixture containment and modality-specific metadata so audio rows cannot escape `corpus/fixtures` and text rows cannot smuggle audio-only fields. | VERIFIED | `services/speech-worker/benchmarks/corpus.py:16,26,33,43`; `services/speech-worker/benchmarks/schemas.py:12,45,80`; `services/speech-worker/tests/test_benchmark_corpus.py:38` |
| 3 | Benchmark schemas and report serialization carry safety/license/integration gates, 1-5 quality rubric fields, stage/total timings, and JSON/CSV/Markdown outputs from the same candidate rows. | VERIFIED | `services/speech-worker/benchmarks/schemas.py:97,108,133,143,199`; `services/speech-worker/benchmarks/reporting.py:30,61,84,119,163,204,224,247,301,305,308,311,314,317,320,323,326,329`; `services/speech-worker/tests/test_benchmark_report.py:275` |
| 4 | The benchmark package fixes concrete scoring thresholds and named runner/output surfaces instead of leaving metric thresholds or report file paths abstract. | VERIFIED | `services/speech-worker/benchmarks/adapters/base.py:47,59`; `services/speech-worker/benchmarks/reporting.py:13,14,15,247`; `services/speech-worker/benchmarks/adapters/runner.py:16`; `services/speech-worker/benchmarks/runner.py:3`; `services/speech-worker/benchmarks/__init__.py:5,29` |
| 5 | The VAD benchmark compares the Silero baseline against a blocked FireRedVAD alternate behind `VADProvider`, and blocked candidates are emitted with exact evidence instead of fake metrics. | VERIFIED | `services/speech-worker/benchmarks/adapters/vad.py:98,176,191,245`; `services/speech-worker/benchmarks/adapters/runner.py:16,28,40,44,50`; `services/speech-worker/tests/test_benchmark_vad.py:24`; `services/speech-worker/benchmarks/reports/model-benchmark-results.json` |
| 6 | The TTS benchmark compares the CosyVoice baseline against a blocked Qwen3-TTS alternate behind `TTSProvider`, and blocked candidates are emitted with exact evidence instead of fake metrics. | VERIFIED | `services/speech-worker/benchmarks/adapters/tts.py:96,178,193,255`; `services/speech-worker/benchmarks/adapters/runner.py:16,34,40,44,50`; `services/speech-worker/tests/test_benchmark_tts.py:49`; `services/speech-worker/benchmarks/reports/model-benchmark-results.json` |
| 7 | The findings-first S2S scan records Moshi, MiniCPM-o 4.5, FlashLabs Chroma, and Qwen3-Omni with license, hardware/runtime, streaming/latency, voice-control, integration risk, blocker, and next-action fields. | VERIFIED | `services/speech-worker/benchmarks/s2s_findings.py:31,126,142,203`; `services/speech-worker/tests/test_benchmark_s2s.py:14`; `services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md:56,108` |
| 8 | Recommendation logic keeps current defaults unless a candidate is runnable, licensed, safe, integration-safe, and evidence-backed, while still emitting separate studio and live-conversation recommendations. | VERIFIED | `services/speech-worker/benchmarks/recommendation.py:12,51,86,179`; `services/speech-worker/tests/test_benchmark_report.py:80,136`; `services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md:3,123` |
| 9 | The final report includes the required Gate Matrix, Quality Rubric, Latency And Runtime, Blocked Candidates, and Default Switch Decision sections, and the checked-in JSON/CSV/Markdown artifacts match that shape. | VERIFIED | `services/speech-worker/benchmarks/reporting.py:247,301,305,308,311,314,317,320,323,326,329`; `services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md:3,12,64,86,108,123`; `services/speech-worker/benchmarks/reports/model-benchmark-results.csv`; `services/speech-worker/benchmarks/reports/model-benchmark-results.json` |

**Score:** 9/9 truths verified

## Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `services/speech-worker/benchmarks/__init__.py` | Public benchmark surface exports corpus, adapters, runner, recommendation, findings, and report helpers | VERIFIED | Exports `run_provider_benchmarks`, `load_benchmark_corpus`, `build_provider_recommendation`, `build_s2s_findings`, and the adapter classes |
| `services/speech-worker/benchmarks/corpus.py` | Manifest loader with fixture containment checks | VERIFIED | Resolves manifest paths and rejects fixtures outside `corpus/fixtures` |
| `services/speech-worker/benchmarks/schemas.py` | Corpus, gate, quality, candidate, and recommendation schemas | VERIFIED | Defines the exact BEN-01..05 result models and validation rules |
| `services/speech-worker/benchmarks/reporting.py` | JSON/CSV/Markdown writer | VERIFIED | Emits the checked-in result files and escapes Markdown candidate text |
| `services/speech-worker/benchmarks/adapters/vad.py` | Silero baseline plus blocked VAD alternate | VERIFIED | Produces baseline rows and a FireRedVAD blocked-candidate row |
| `services/speech-worker/benchmarks/adapters/tts.py` | CosyVoice baseline plus blocked TTS alternate | VERIFIED | Produces baseline rows and a Qwen3-TTS blocked-candidate row |
| `services/speech-worker/benchmarks/adapters/runner.py` | Combined benchmark runner | VERIFIED | Runs VAD, TTS, and S2S data into one report pass |
| `services/speech-worker/benchmarks/runner.py` | Public runner shim | VERIFIED | Re-exports `run_provider_benchmarks` from the adapter runner path |
| `services/speech-worker/benchmarks/s2s_findings.py` | Findings-first S2S scan | VERIFIED | Records blocked Moshi, MiniCPM-o 4.5, Chroma, and Qwen3-Omni evidence rows |
| `services/speech-worker/benchmarks/recommendation.py` | Conservative recommendation builder | VERIFIED | Keeps current defaults unless hard gates and evidence pass |
| `services/speech-worker/benchmarks/corpus/manifest.json` | Canonical benchmark corpus | VERIFIED | Contains the measured, cutting, and grandiose text cases plus audio fixtures |
| `services/speech-worker/benchmarks/corpus/fixtures/clean-short.wav` | Consent-safe clean fixture | VERIFIED | Present and consumed by the corpus loader |
| `services/speech-worker/benchmarks/corpus/fixtures/noisy-short.wav` | Consent-safe noisy fixture | VERIFIED | Present and consumed by the corpus loader |
| `services/speech-worker/benchmarks/runs/.gitkeep` | Benchmark run-output placeholder | VERIFIED | Present as the checked-in run directory placeholder |
| `services/speech-worker/benchmarks/reports/.gitkeep` | Benchmark report-output placeholder | VERIFIED | Present as the checked-in report directory placeholder |
| `services/speech-worker/benchmarks/reports/model-benchmark-results.json` | Structured benchmark output | VERIFIED | Matches the current candidate row and recommendation shape |
| `services/speech-worker/benchmarks/reports/model-benchmark-results.csv` | Tabular benchmark output | VERIFIED | Carries the same candidate ids and gate fields as the JSON file |
| `services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md` | Human-readable recommendation report | VERIFIED | Includes the required benchmark, findings, and default-switch sections |
| `services/speech-worker/tests/test_benchmark_corpus.py` | Corpus contract tests | VERIFIED | Confirms tone coverage, fixture containment, and protected-term exclusions |
| `services/speech-worker/tests/test_benchmark_vad.py` | VAD benchmark tests | VERIFIED | Confirms baseline and blocked-alternate rows for the same audio corpus |
| `services/speech-worker/tests/test_benchmark_tts.py` | TTS benchmark tests | VERIFIED | Confirms baseline and blocked-alternate rows for the same text corpus |
| `services/speech-worker/tests/test_benchmark_s2s.py` | S2S findings tests | VERIFIED | Confirms multi-candidate blocked evidence rows with required fields |
| `services/speech-worker/tests/test_benchmark_report.py` | Recommendation/report tests | VERIFIED | Confirms conservative switching and Markdown/JSON/CSV output shape |

## Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `services/speech-worker/benchmarks/corpus/manifest.json` | `load_benchmark_corpus()` | Manifest-driven loader with fixture containment checks | WIRED | `corpus.py:16,26,43` loads the manifest and validates every fixture-backed item |
| `load_benchmark_corpus()` | VAD/TTS benchmark adapters | Shared corpus passed into `run_vad_benchmark()` and `run_tts_benchmark()` | WIRED | `adapters/runner.py:26,28,34`; `adapters/vad.py:245`; `adapters/tts.py:255` |
| `VADProvider` / `TTSProvider` contracts | Benchmark adapters | Existing provider interfaces wrap Silero and CosyVoice | WIRED | `providers/contracts.py`; `adapters/vad.py:98`; `adapters/tts.py:96` |
| Candidate rows | `write_benchmark_report()` | Same rows serialized to JSON, CSV, and Markdown | WIRED | `reporting.py:247,261,295,301,302` and the checked-in report artifacts |
| `SpeechToSpeechScan` | `build_provider_recommendation()` | Findings feed conservative recommendation logic | WIRED | `recommendation.py:165,179,211`; `s2s_findings.py:126,203` |
| Quality scores and gate results | Recommendation decision | Hard-gate checks and scoring thresholds | WIRED | `recommendation.py:42,51,78,86,102,120,130,152` |

## Data-Flow Trace

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| Benchmark corpus items | `BenchmarkCorpusItem` | `manifest.json` -> `load_benchmark_corpus()` | Yes | FLOWING |
| VAD/TTS candidate rows | `BenchmarkCandidateResult` | `run_vad_benchmark()` / `run_tts_benchmark()` | Yes | FLOWING |
| S2S finding rows | `SpeechToSpeechFinding` | `build_s2s_findings()` | Yes | FLOWING |
| Recommendation output | `BenchmarkRecommendation` | Candidate rows + findings -> `build_provider_recommendation()` | Yes | FLOWING |
| Final report files | JSON / CSV / Markdown | `write_benchmark_report()` | Yes | FLOWING |

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| BEN-01 | 05-01 | Fixed benchmark input set for voice quality, latency, and reliability | SATISFIED | `manifest.json:4,14,24,34,49,64,79`; `corpus.py:16,26,43`; `test_benchmark_corpus.py:38` |
| BEN-02 | 05-02 | At least two VAD candidates or configurations compared | SATISFIED | `vad.py:98,176,191,245`; `test_benchmark_vad.py:24`; `model-benchmark-results.json` |
| BEN-03 | 05-02 | At least two TTS or voice-cloning candidates compared | SATISFIED | `tts.py:96,178,193,255`; `test_benchmark_tts.py:49`; `model-benchmark-results.json` |
| BEN-04 | 05-03 | Feasible end-to-end speech-to-speech candidates recorded findings | SATISFIED | `s2s_findings.py:31,126,203`; `test_benchmark_s2s.py:14`; `model-benchmark-recommendation.md:56` |
| BEN-05 | 05-01, 05-02, 05-03 | Recommendation report includes quality, latency, GPU/runtime cost, license fit, and integration risk | SATISFIED | `reporting.py:247,301,305,308,311,314,317,320,323,326,329`; `recommendation.py:179`; `test_benchmark_report.py:80,136,275` |

All BEN IDs from the plan frontmatter are present in `.planning/REQUIREMENTS.md:51,52,53,54,55` and mapped to Phase 5 in the requirements trace at `.planning/REQUIREMENTS.md:130,131,132,133,134`.

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Benchmark corpus, VAD, TTS, S2S, and report contracts | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py services/speech-worker/tests/test_benchmark_vad.py services/speech-worker/tests/test_benchmark_tts.py services/speech-worker/tests/test_benchmark_s2s.py services/speech-worker/tests/test_benchmark_report.py -q` | `7 passed in 0.10s` | PASS |

## Probe Execution

No probes were declared for Phase 05.

## Anti-Patterns Found

None detected in the benchmark package or benchmark tests. The grep scans found no unresolved `TBD`, `FIXME`, `XXX`, `TODO`, placeholder, or empty-handler stubs in the phase code paths.

## Gaps Summary

No blocking gaps remain. The benchmark corpus, adapters, findings scan, recommendation logic, checked-in outputs, and benchmark-specific tests all line up with the Phase 05 goal and BEN-01 through BEN-05.

_Verified: 2026-07-14T17:29:13Z_
_Verifier: the agent (gsd-verifier)_
