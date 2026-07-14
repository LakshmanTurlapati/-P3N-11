---
phase: 05-model-benchmark-and-selection
plan: 03
subsystem: benchmarking
tags: [speech, benchmark, recommendation, vad, tts, s2s]

requires:
  - phase: 05-01
    provides: benchmark corpus, result schemas, and report serialization
  - phase: 05-02
    provides: runnable VAD/TTS baselines and blocked-alternate benchmark rows
provides:
  - findings-first S2S scan records for Moshi, MiniCPM-o 4.5, FlashLabs Chroma, and Qwen3-Omni
  - conservative recommendation builder with keep-current-defaults gating
  - expanded Markdown, JSON, and CSV benchmark artifacts with S2S-aware sections
affects: [phase 06 cloud GPU deployment and internal beta hardening, future benchmark reruns]

tech-stack:
  added: [Pydantic recommendation model, S2S findings scan, S2S-inclusive report renderer]
  patterns: [findings-first blocker reporting, conservative default-switch gating, shared candidate-row serialization]

key-files:
  created:
    - services/speech-worker/benchmarks/recommendation.py
    - services/speech-worker/benchmarks/s2s_findings.py
    - services/speech-worker/tests/test_benchmark_s2s.py
  modified:
    - services/speech-worker/benchmarks/__init__.py
    - services/speech-worker/benchmarks/adapters/runner.py
    - services/speech-worker/benchmarks/reporting.py
    - services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md
    - services/speech-worker/benchmarks/reports/model-benchmark-results.csv
    - services/speech-worker/benchmarks/reports/model-benchmark-results.json
    - services/speech-worker/benchmarks/schemas.py
    - services/speech-worker/tests/test_benchmark_report.py

key-decisions:
  - "Keep end-to-end S2S candidates findings-first and blocked in the local workspace until a sanctioned GPU-host run exists."
  - "Preserve CosyVoice and Silero VAD as the current studio/live defaults and set the default-switch decision to keep-current-defaults."
  - "Surface blocked candidate attempted-setup evidence and next actions in the report instead of ranking unsupported models."
  - "Render report sections separately for executive summary, VAD, TTS, S2S findings, blocked candidates, and default-switch decisions."

patterns-established:
  - "Findings-first S2S scan: document blockers and evidence, do not infer runnable status from research notes alone."
  - "Conservative recommendation gating: switch only when status, license, safety, integration, and evidence are all clear."
  - "Shared benchmark serialization: the same candidate rows feed JSON, CSV, and markdown report sections."

requirements-completed: [BEN-04, BEN-05]

coverage:
  - id: D1
    description: "Blocked Moshi, MiniCPM-o 4.5, Chroma, and Qwen3-Omni findings are recorded with explicit runtime and next-action evidence."
    requirement: BEN-04
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_benchmark_s2s.py::test_build_s2s_findings_records_multiple_blocked_candidates_with_complete_evidence"
        status: pass
    human_judgment: false
  - id: D2
    description: "Recommendation building keeps CosyVoice and Silero VAD as defaults and refuses blocked alternate candidates."
    requirement: BEN-05
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_benchmark_report.py::test_should_switch_default_provider_requires_complete_evidence_and_passed_gates"
        status: pass
      - kind: unit
        ref: "services/speech-worker/tests/test_benchmark_report.py::test_build_provider_recommendation_keeps_current_defaults_and_blocks_alternates"
        status: pass
    human_judgment: false
  - id: D3
    description: "Markdown, JSON, and CSV benchmark artifacts were regenerated with S2S-aware comparison and blocked-candidate sections."
    requirement: BEN-05
    verification:
      - kind: integration
        ref: "PYTHONPATH=services/speech-worker ./.venv/bin/python - <<'PY' ... run_provider_benchmarks() ..."
        status: pass
    human_judgment: false

duration: 34 min
completed: 2026-07-14
status: complete
---

# Phase 05: Model Benchmark and Selection Summary

The benchmark phase now includes a findings-first S2S scan and a conservative recommendation layer that keeps CosyVoice and Silero VAD as the current defaults while documenting blocked Moshi, MiniCPM-o 4.5, FlashLabs Chroma, and Qwen3-Omni evidence in the report artifacts.

## Performance

- **Duration:** 34 min
- **Started:** 2026-07-14T16:30:03Z
- **Completed:** 2026-07-14T17:04:09Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Added a structured `SpeechToSpeechFinding` / `SpeechToSpeechScan` model and a findings-first scan for Moshi, MiniCPM-o 4.5, FlashLabs Chroma, and Qwen3-Omni.
- Added `build_provider_recommendation()` and `should_switch_default_provider()` so blocked candidates cannot promote defaults without full gate and evidence coverage.
- Expanded the benchmark report to render Executive Recommendation, VAD Comparison, TTS And Voice-Cloning Comparison, End-to-End Speech Findings, Blocked Candidates, and Default Switch Decision sections.
- Regenerated the benchmark JSON, CSV, and markdown artifacts so the checked-in outputs match the new S2S-aware report shape.

## Task Commits

| Task | Commit | Files |
| ---- | ------ | ----- |
| 1 | `cba872a` | `services/speech-worker/tests/test_benchmark_report.py`, `services/speech-worker/tests/test_benchmark_s2s.py` |
| 2 | `297095b` | `services/speech-worker/benchmarks/s2s_findings.py`, `services/speech-worker/benchmarks/__init__.py` |
| 3 | `13c1375` | `services/speech-worker/benchmarks/recommendation.py`, `services/speech-worker/benchmarks/schemas.py`, `services/speech-worker/benchmarks/reporting.py`, `services/speech-worker/benchmarks/adapters/runner.py`, `services/speech-worker/benchmarks/__init__.py`, `services/speech-worker/benchmarks/reports/model-benchmark-recommendation.md`, `services/speech-worker/benchmarks/reports/model-benchmark-results.csv`, `services/speech-worker/benchmarks/reports/model-benchmark-results.json`, `services/speech-worker/tests/test_benchmark_report.py` |

## Verification

- `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_s2s.py services/speech-worker/tests/test_benchmark_report.py -q`
- `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py services/speech-worker/tests/test_benchmark_vad.py services/speech-worker/tests/test_benchmark_tts.py services/speech-worker/tests/test_benchmark_s2s.py services/speech-worker/tests/test_benchmark_report.py -q`
- `PYTHONPATH=services/speech-worker ./.venv/bin/python - <<'PY' ... run_provider_benchmarks() ... PY`

## Deviations from Plan

None. The implementation stayed within the findings-first, report-first scope of the plan.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/05-model-benchmark-and-selection/05-03-SUMMARY.md`.
- Task commit hashes `cba872a`, `297095b`, and `13c1375` are present in git history.
- Benchmark verification passed for corpus, VAD, TTS, S2S, and report tests.
