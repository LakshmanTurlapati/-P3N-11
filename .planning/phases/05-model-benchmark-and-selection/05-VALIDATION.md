---
phase: 05
slug: model-benchmark-and-selection
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-07-13
---

# Phase 05 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py services/speech-worker/tests/test_benchmark_vad.py services/speech-worker/tests/test_benchmark_tts.py services/speech-worker/tests/test_benchmark_s2s.py services/speech-worker/tests/test_benchmark_report.py -q` |
| **Full suite command** | `./.venv/bin/python -m pytest -q` |
| **Estimated runtime** | ~30 seconds for fixture-only benchmark tests; real GPU/model runs are manual or externally hosted |

---

## Sampling Rate

- **After every task commit:** Run `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py services/speech-worker/tests/test_benchmark_vad.py services/speech-worker/tests/test_benchmark_tts.py services/speech-worker/tests/test_benchmark_s2s.py services/speech-worker/tests/test_benchmark_report.py -q`
- **After every plan wave:** Run `./.venv/bin/python -m pytest -q`
- **Before `$gsd-verify-work`:** Full suite must be green in the local fixture path, with any GPU-only benchmark runs documented in the report as executed externally or blocked with evidence.
- **Max feedback latency:** 60 seconds for fixture tests.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | BEN-01 | T-05-01 | Fixture paths stay under the benchmark corpus root | unit | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_corpus.py -q` | no - W0 | pending |
| 05-01-02 | 01 | 1 | BEN-05 | T-05-03 | Report text treats model/provider output as data, not trusted Markdown | unit | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_report.py -q` | no - W0 | pending |
| 05-02-01 | 02 | 2 | BEN-02 | T-05-02 | Malformed audio fixtures fail fast without unbounded candidate execution | integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_vad.py -q` | no - W0 | pending |
| 05-02-02 | 02 | 2 | BEN-03 | T-05-02 | TTS benchmark adapters emit explicit blockers when runtime dependencies are unavailable | integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_tts.py -q` | no - W0 | pending |
| 05-03-01 | 03 | 3 | BEN-04 | T-05-03 | End-to-end findings record setup/runtime/license blockers instead of ranking unsupported models | integration/manual | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_s2s.py -q` | no - W0 | pending |
| 05-03-02 | 03 | 3 | BEN-05 | T-05-03 | Recommendation output includes quality, latency, GPU/runtime cost, license fit, and integration risk fields | unit | `./.venv/bin/python -m pytest services/speech-worker/tests/test_benchmark_report.py -q` | no - W0 | pending |

---

## Wave 0 Requirements

- [ ] `services/speech-worker/tests/test_benchmark_corpus.py` - stubs and assertions for BEN-01 corpus manifest loading, consent-safe fixture metadata, and rough speech-window tags.
- [ ] `services/speech-worker/tests/test_benchmark_vad.py` - shared-corpus comparison assertions for BEN-02 VAD candidate rows.
- [ ] `services/speech-worker/tests/test_benchmark_tts.py` - shared-corpus comparison assertions for BEN-03 TTS/voice-cloning candidate rows.
- [ ] `services/speech-worker/tests/test_benchmark_s2s.py` - findings-first assertions for BEN-04 end-to-end candidate evidence or blockers.
- [ ] `services/speech-worker/tests/test_benchmark_report.py` - JSON/CSV/Markdown report assertions for BEN-05.
- [ ] `services/speech-worker/benchmarks/` - benchmark package, corpus manifest, adapters, report writer, and deterministic fixture path.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Subjective theatrical voice quality rubric | BEN-03, BEN-05 | Human review is required for intelligibility, tone fit, naturalness, artifact level, and safety-boundary adherence | Run the TTS benchmark on a GPU-capable host, score generated clips 1-5 using the report rubric, and record reviewer scores in the Markdown and machine-readable results. |
| Real GPU/runtime cost for candidate models | BEN-03, BEN-04, BEN-05 | Local workspace lacks torch, ffmpeg, and GPU access | Run candidate setup on the target GPU host or document the exact setup blocker, command attempted, error, license issue, and next action in the report. |
| Default provider switch decision | BEN-05 | The phase may recommend defaults, but should switch only when low-risk and license-safe | Confirm the recommendation report marks the winner runnable, license-safe, and non-disruptive before changing any app defaults. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification.
- [ ] Wave 0 covers all missing benchmark test files.
- [ ] No watch-mode flags appear in verification commands.
- [ ] Fixture-path feedback latency stays under 60 seconds.
- [ ] `nyquist_compliant: true` remains set in frontmatter.

**Approval:** pending
