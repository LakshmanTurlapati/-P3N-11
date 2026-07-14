---
phase: 05-model-benchmark-and-selection
plan: 02
subsystem: testing
tags: [benchmarking, speech, provider-contracts, pytest, json, csv]

dependency-graph:
  requires:
    - phase: 05-01
      provides: fixed benchmark corpus, result schema, and report writer
    - phase: 02-consented-studio-generation
      provides: CosyVoice baseline provider contract and original voice boundary
    - phase: 03-audio-input-and-turn-detection
      provides: Silero-compatible VAD provider contract and fixture fallback pattern
  provides:
    - provider-contract benchmark adapters for Silero VAD and CosyVoice TTS
    - blocked-candidate rows for FireRedVAD and Qwen3-TTS evidence paths
    - deterministic fixture-mode benchmark runner and combined JSON/CSV/Markdown report artifacts
  affects:
    - phase 05-03
    - future GPU-worker validation of approved alternate candidates

tech-stack:
  added:
    - provider-contract benchmark adapters
    - blocked-candidate evidence rows with next-action metadata
    - fixture-mode runner with combined JSON/CSV/Markdown outputs
  patterns:
    - baseline-plus-blocked candidate comparison
    - fixture-only provider injection for local tests
    - recommendation selection that excludes blocked candidates

key-files:
  created:
    - services/speech-worker/benchmarks/adapters/__init__.py
    - services/speech-worker/benchmarks/adapters/base.py
    - services/speech-worker/benchmarks/adapters/runner.py
    - services/speech-worker/benchmarks/adapters/tts.py
    - services/speech-worker/benchmarks/adapters/vad.py
    - services/speech-worker/benchmarks/runner.py
    - services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md
    - services/speech-worker/benchmarks/reports/model-benchmark-results.csv
    - services/speech-worker/benchmarks/reports/model-benchmark-results.json
    - services/speech-worker/tests/test_benchmark_tts.py
    - services/speech-worker/tests/test_benchmark_vad.py
  modified:
    - services/speech-worker/benchmarks/__init__.py
    - services/speech-worker/benchmarks/reporting.py
    - services/speech-worker/tests/test_benchmark_report.py
    - services/speech-worker/benchmarks/schemas.py

key-decisions:
  - "Use Silero VAD as the runnable baseline and keep FireRedVAD blocked in the local workspace until package legitimacy and GPU runtime validation are proven."
  - "Treat the approved Qwen3-TTS source checkout and weights as the alternate TTS candidate, but keep it blocked from local runtime execution until GPU-worker evidence is captured."
  - "Keep benchmark execution fixture-only with fake backends and select recommendations only from runnable baselines."

patterns-established:
  - "Provider-backed benchmark adapters stay behind the existing speech-worker contracts."
  - "Blocked candidates carry blocker_reason, next_action, and evidence URLs instead of fake runtime metrics."
  - "Combined benchmark reports serialize the same candidate rows to JSON, CSV, and Markdown."

requirements-completed: [BEN-02, BEN-03, BEN-05]

coverage:
  - id: D1
    description: "Runnable Silero VAD baseline plus blocked FireRedVAD evidence rows behind the provider contract."
    requirement: "BEN-02"
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_benchmark_vad.py#test_run_vad_benchmark_emits_baseline_and_blocked_alternate_rows"
        status: pass
    human_judgment: false
  - id: D2
    description: "Runnable CosyVoice baseline plus approved-but-unrun Qwen3-TTS evidence rows behind the provider contract."
    requirement: "BEN-03"
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_benchmark_tts.py#test_run_tts_benchmark_emits_baseline_and_blocked_alternate_rows"
        status: pass
    human_judgment: false
  - id: D3
    description: "Combined JSON/CSV/Markdown benchmark outputs and recommendation selection for the two workflow paths."
    requirement: "BEN-05"
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_benchmark_report.py#test_write_benchmark_report_serializes_quality_latency_cost_and_risk_fields"
        status: pass
      - kind: other
        ref: "services/speech-worker/benchmarks/reports/model-benchmark-results.json"
        status: pass
    human_judgment: false

metrics:
  duration: 13m
  completed: 2026-07-14
status: complete
---

# Phase 05: Model Benchmark and Selection Summary

**Provider-contract benchmark adapters with deterministic baseline rows, blocked alternates, and combined report artifacts for the next recommendation phase.**

## Performance

- **Duration:** 13m
- **Started:** 2026-07-14T16:13:34Z
- **Completed:** 2026-07-14T16:26:57Z
- **Tasks:** 4
- **Files modified:** 13

## Accomplishments

- Added `VADBenchmarkAdapter` and `TTSBenchmarkAdapter` baselines that wrap the existing Silero and CosyVoice provider contracts.
- Recorded blocked FireRedVAD rows and approved-but-unrun Qwen3-TTS rows with `blocker_reason`, `next_action`, and evidence URLs.
- Generated deterministic `model-benchmark-results.json`, `.csv`, and Markdown recommendation files from fixture-mode runs.
- Kept local benchmark execution independent of torch, ffmpeg, and GPU runtime dependencies.
- Resolved the two checkpoint tasks without local installs: VAD stayed conservatively blocked and TTS was approved for the Qwen3-TTS path but deferred from runtime execution.

## Task Commits

Each task was committed atomically:

1. **Task 3: Pin VAD and TTS benchmark behavior with fixture tests**
   - Commit: `b9bce08`
   - Result: Added failing tests that required benchmark adapter imports, blocked-candidate rows, and non-recommended blocked candidates.

2. **Task 4: Implement provider-contract benchmark adapters and runner rows**
   - Commit: `fd44733`
   - Result: Added the benchmark adapter layer, combined runner, and generated benchmark artifacts.

## Deviations from Plan

### Post-completion Correction

**1. [Plan Artifact Fix] Restored the planned benchmark runner module path**
- **Found during:** Post-completion spot-check before wave 3
- **Issue:** The phase output listed `services/speech-worker/benchmarks/runner.py`, but the implementation only exposed `run_provider_benchmarks` from `services/speech-worker/benchmarks/adapters/runner.py`.
- **Fix:** Added `services/speech-worker/benchmarks/runner.py` as a compatibility shim that re-exports `run_provider_benchmarks` from the adapters implementation, and added a regression test that imports the public module path.
- **Files modified:** `services/speech-worker/benchmarks/runner.py`, `services/speech-worker/tests/test_benchmark_report.py`, `.planning/phases/05-model-benchmark-and-selection/05-02-SUMMARY.md`
- **Commit:** `fix(05-02): restore planned benchmark runner module path`

## Self-Check: PASSED

- Verified `.planning/phases/05-model-benchmark-and-selection/05-02-SUMMARY.md` exists.
- Verified `services/speech-worker/benchmarks/reports/model-benchmark-results.json` exists.
- Verified `services/speech-worker/benchmarks/reports/model-benchmark-results.csv` exists.
- Verified `services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md` exists.
- Verified task commits `b9bce08` and `fd44733` exist in git history.
