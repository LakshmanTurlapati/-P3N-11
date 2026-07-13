# Phase 5: Model Benchmark and Selection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-07-13
**Phase:** 5-Model Benchmark and Selection
**Areas discussed:** Benchmark corpus shape, Candidate set and evidence depth, Scoring and report format, Selection outcome

---

## Benchmark Corpus Shape

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| How broad should the first corpus be? | Balanced suite; Minimal smoke set; Stress-heavy suite; Other | Balanced suite |
| How should inputs be stored and sourced? | Repo manifest plus small fixtures; External corpus directory; Generated-only fixtures; Other | Repo manifest plus small fixtures |
| What ground truth should audio fixtures include? | Transcript plus rough speech window; Exact segment labels; No ground truth; Other | Transcript plus rough speech window |
| How should persona and tone quality be represented? | Tone coverage cases; Neutral quality only; Extensive style rubric; Other | Tone coverage cases |

**User's choice:** Selected the recommended option for each question.
**Notes:** The corpus should balance quality, latency, and reliability evidence without requiring a large curated dataset or exact timestamp labeling.

---

## Candidate Set And Evidence Depth

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| How should VAD candidates be handled? | Compare baseline plus configurations; Two real VAD adapters; Three-way VAD comparison; Other | Two real VAD adapters |
| How should TTS/voice-cloning candidates be handled? | Current baseline plus one cloning candidate; Current baseline plus two cloning candidates; Report-only for alternates; Other | Current baseline plus one cloning candidate |
| What evidence depth should recommendation candidates need? | Runnable adapter evidence; Research evidence is enough; Strict benchmark-only; Other | Runnable adapter evidence |
| How should end-to-end speech-to-speech models be handled? | Findings-first feasibility scan; Run one end-to-end model; Defer entirely; Other | Findings-first feasibility scan |

**User's choice:** The user delegated the VAD choice with "do whichever is best"; the recommended two-real-adapter path was selected. The user selected the recommended options for the remaining questions.
**Notes:** Candidates should either run through the benchmark harness or have an exact documented blocker. End-to-end models should not derail the VAD/TTS benchmark work.

---

## Scoring And Report Format

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| What should be the primary decision rule? | Balanced gate matrix; Latency-first; Quality-first; Other | Balanced gate matrix |
| How should subjective voice quality be captured? | Small reviewer rubric; Narrative notes only; Automated proxies only; Other | Small reviewer rubric |
| How should latency be reported? | Stage and total timings; Total time only; Interactive target only; Other | Stage and total timings |
| What format should the recommendation report use? | Markdown report plus machine-readable results; Markdown only; Data-first only; Other | Markdown report plus machine-readable results |

**User's choice:** Selected the recommended option for each question.
**Notes:** The report should combine human-readable conclusions with structured data so benchmark reruns can be compared later.

---

## Selection Outcome

| Question | Options Considered | Selected |
|----------|--------------------|----------|
| Should Phase 5 change app defaults if a better fit is found? | Recommend first, switch only if low-risk; Recommendation only; Switch winner aggressively; Other | Recommend first, switch only if low-risk |
| What if winners differ by workflow? | Separate recommendations by path; One overall winner; No default recommendation; Other | Separate recommendations by path |
| How should licensing and consent affect selection? | Hard gate; Warning only; Defer legal judgment; Other | Hard gate |
| How should blockers be represented? | Blocked with next action; Drop blocked candidates; Rank blocked candidates anyway; Other | Blocked with next action |

**User's choice:** Selected the recommended option for each question.
**Notes:** Licensing and consent fit are non-negotiable gates. Conservative defaults are preferred unless a winner is clearly runnable, safe, and low-risk.

---

## the agent's Discretion

- The user delegated the VAD selection approach to the agent. The locked approach is Silero plus one real alternate VAD adapter behind `VADProvider`, with the exact alternate chosen during research/planning.
- Downstream agents may choose exact fixture counts, schema filenames, benchmark runner names, output paths, metric thresholds, and alternate model candidates as long as the decisions in CONTEXT.md are preserved.

## Deferred Ideas

- Visual benchmark dashboard.
- Aggressive default provider migration.
- Broad execution of every end-to-end speech model.
- Deployment hardening and rented-GPU beta setup documentation.
