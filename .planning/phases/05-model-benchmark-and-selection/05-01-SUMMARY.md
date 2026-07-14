---
phase: 05-model-benchmark-and-selection
plan: 01
subsystem: testing
tags: [benchmarking, corpus, reporting, pydantic, pytest, markdown]
dependency-graph:
  requires:
    - phase: 02-consented-studio-generation
      provides: original voice id, tone presets, and controlled playback baseline
    - phase: 04-live-conversation-mode
      provides: stage timing semantics and conversation latency fields to mirror
  provides:
    - fixed benchmark corpus manifest with consent-safe text/audio fixtures
    - validated benchmark corpus loader and corpus item schema
    - benchmark result schemas and JSON/CSV/Markdown report writer
  affects:
    - phase 05-02 VAD/TTS candidate adapters
    - phase 05-03 end-to-end findings and recommendation
tech-stack:
  added:
    - pydantic benchmark schemas
    - manifest-driven benchmark corpus loading
    - JSON/CSV/Markdown report serialization
  patterns:
    - path-contained fixture resolution
    - file-based benchmark outputs
    - Markdown escaping for untrusted provider/model text
key-files:
  created:
    - services/speech-worker/benchmarks/__init__.py
    - services/speech-worker/benchmarks/corpus.py
    - services/speech-worker/benchmarks/reporting.py
    - services/speech-worker/benchmarks/schemas.py
    - services/speech-worker/benchmarks/corpus/manifest.json
    - services/speech-worker/benchmarks/corpus/fixtures/clean-short.wav
    - services/speech-worker/benchmarks/corpus/fixtures/noisy-short.wav
    - services/speech-worker/benchmarks/reports/.gitkeep
    - services/speech-worker/benchmarks/runs/.gitkeep
    - services/speech-worker/tests/test_benchmark_corpus.py
    - services/speech-worker/tests/test_benchmark_report.py
  modified:
    - services/speech-worker/benchmarks/__init__.py
    - services/speech-worker/benchmarks/schemas.py
    - services/speech-worker/benchmarks/reporting.py
key-decisions:
  - "Use a small fixed corpus with three tone-preserving text prompts and three audio paths worth of consent-safe rows backed by two tiny WAV fixtures."
  - "Keep fixture paths resolved and containment-checked under services/speech-worker/benchmarks/corpus/fixtures."
  - "Emit benchmark results as JSON, CSV, and escaped Markdown so later adapters can compare reruns without a dashboard."
patterns-established:
  - "Manifest-driven benchmark loading with Pydantic validation"
  - "Escaped Markdown report rendering for candidate/provider text"
  - "Machine-readable and human-readable outputs share the same candidate rows"
requirements-completed: [BEN-01, BEN-05]
status: complete
---
# Phase 05 Plan 01: Benchmark Corpus and Report Foundation Summary

One-line summary: Manifest-driven benchmark corpus and escaped report pipeline for consent-safe voice candidate selection.

## Outcome

This plan established the reproducible base for Phase 05 benchmarking without running any real model comparisons. The repo now has a locked corpus manifest, validated corpus loader, schema models for benchmark results, and a report writer that emits JSON, CSV, and Markdown from the same candidate rows.

## Completed Tasks

| Task | Commit | Result |
| --- | --- | --- |
| Task 1: Pin the corpus and report contracts with failing tests | `e54aeb7` | Added red tests that pinned corpus tone coverage, audio metadata, path containment, protected-name exclusions, and report serialization fields. |
| Task 2: Implement the benchmark corpus package and manifest | `cfd7d94` | Added the benchmark package, corpus schemas, manifest loader, consent-safe WAV fixtures, and output directory placeholders. |
| Task 3: Implement structured report serialization | `6568e2c` | Added benchmark result schemas and a serializer that writes escaped Markdown plus JSON and CSV outputs. |

## Verification

- `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py -q` passed.
- `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_report.py -q` passed.
- `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py services/speech-worker/tests/test_benchmark_report.py -q` passed.
- `./.venv/bin/python -m pytest -q` passed with 41 tests.

## Deviations from Plan

None - plan executed exactly as written.

## Notes

- The benchmark corpus uses `vesper-glass` as the consent-safe internal voice id for all rows.
- The report writer escapes provider and candidate names in Markdown so untrusted text cannot break the recommendation tables.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/05-model-benchmark-and-selection/05-01-SUMMARY.md`.
- Commits `e54aeb7`, `cfd7d94`, and `6568e2c` exist in the repository history.
- Verification commands passed: phase-specific benchmark tests and `./.venv/bin/python -m pytest -q`.
