from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import fmean
from typing import Sequence

from .corpus import REPORTS_DIR
from .s2s_findings import SpeechToSpeechFinding, SpeechToSpeechScan
from .schemas import BenchmarkCandidateResult, BenchmarkRecommendation

RESULTS_JSON_FILENAME = "model-benchmark-results.json"
RESULTS_CSV_FILENAME = "model-benchmark-results.csv"
RECOMMENDATION_MD_FILENAME = "model-benchmark-recommendation.md"


def _escape_markdown_text(value: str) -> str:
    escaped_value = value.replace("\\", "\\\\")
    for raw_character in ("|", "*", "_", "`", "<", ">"):
        escaped_value = escaped_value.replace(raw_character, f"\\{raw_character}")
    return escaped_value


def _average_quality(candidate: BenchmarkCandidateResult) -> str:
    scores = candidate.quality_scores.model_dump()
    return f"{fmean(scores.values()):.2f}"


def _candidate_to_csv_row(candidate: BenchmarkCandidateResult) -> dict[str, str]:
    return {
        "candidate_id": candidate.candidate_id,
        "provider_type": candidate.provider_type,
        "provider_name": candidate.provider_name,
        "corpus_item_id": candidate.corpus_item_id,
        "status": candidate.status,
        "total_wall_ms": str(candidate.stage_timings_ms.total_wall_ms),
        "license_gate_status": candidate.license_gate.status,
        "license_gate_reason": candidate.license_gate.reason,
        "safety_gate_status": candidate.safety_gate.status,
        "integration_gate_status": candidate.integration_gate.status,
        "runtime_cost": candidate.runtime_cost,
        "integration_risk": candidate.integration_risk,
        "blocker_reason": candidate.blocker_reason or "",
        "next_action": candidate.next_action or "",
        "quality_intelligibility": str(candidate.quality_scores.intelligibility),
        "quality_persona_tone_fit": str(candidate.quality_scores.persona_tone_fit),
        "quality_naturalness": str(candidate.quality_scores.naturalness),
        "quality_artifact_level": str(candidate.quality_scores.artifact_level),
        "quality_safety_boundary_adherence": str(candidate.quality_scores.safety_boundary_adherence),
        "vad_ms": str(candidate.stage_timings_ms.vad_ms),
        "stt_ms": str(candidate.stage_timings_ms.stt_ms),
        "response_text_ms": str(candidate.stage_timings_ms.response_text_ms),
        "tts_ms": str(candidate.stage_timings_ms.tts_ms),
        "playback_ready_ms": str(candidate.stage_timings_ms.playback_ready_ms),
        "total_duration_ms": str(candidate.total_duration_ms),
        "artifact_references": json.dumps(candidate.artifact_references, ensure_ascii=False),
    }


def _gate_matrix_rows(candidates: Sequence[BenchmarkCandidateResult]) -> list[str]:
    lines = [
        "| Candidate | Provider | Status | License | Safety | Integration |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    _escape_markdown_text(candidate.provider_name),
                    _escape_markdown_text(candidate.status),
                    _escape_markdown_text(candidate.license_gate.status),
                    _escape_markdown_text(candidate.safety_gate.status),
                    _escape_markdown_text(candidate.integration_gate.status),
                )
            )
            + " |"
        )
    return lines


def _comparison_rows(
    candidates: Sequence[BenchmarkCandidateResult],
    *,
    provider_type: str,
) -> list[str]:
    rows = [candidate for candidate in candidates if candidate.provider_type == provider_type]
    lines = [
        "| Candidate | Provider | Corpus Item | Status | Quality | Total Wall | Runtime Cost | License Fit | Integration Risk |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not rows:
        lines.append("| None | None | None | None | None | None | None | None | None |")
        return lines

    for candidate in rows:
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    _escape_markdown_text(candidate.provider_name),
                    _escape_markdown_text(candidate.corpus_item_id),
                    _escape_markdown_text(candidate.status),
                    _average_quality(candidate),
                    str(candidate.stage_timings_ms.total_wall_ms),
                    _escape_markdown_text(candidate.runtime_cost),
                    _escape_markdown_text(candidate.license_gate.status),
                    _escape_markdown_text(candidate.integration_risk),
                )
            )
            + " |"
        )
    return lines


def _s2s_findings_rows(scan: SpeechToSpeechScan | None) -> list[str]:
    lines = [
        "| Candidate | Status | License Summary | Hardware / Runtime | Streaming / Latency | Voice Control Fit | Integration Risk | Attempted Setup Evidence | Blocker | Next Action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if scan is None or not scan.findings:
        lines.append("| None | None | None | None | None | None | None | None | None | None |")
        return lines

    for finding in scan.findings:
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(finding.candidate_name),
                    _escape_markdown_text(finding.status),
                    _escape_markdown_text(finding.license_summary),
                    _escape_markdown_text(finding.hardware_runtime_needs),
                    _escape_markdown_text(finding.streaming_latency_posture),
                    _escape_markdown_text(finding.voice_control_fit),
                    _escape_markdown_text(finding.integration_risk),
                    _escape_markdown_text(finding.attempted_setup_evidence),
                    _escape_markdown_text(finding.blocker_reason or ""),
                    _escape_markdown_text(finding.next_action or ""),
                )
            )
            + " |"
        )
    return lines


def _blocked_attempted_setup(
    candidate: BenchmarkCandidateResult,
    s2s_lookup: dict[str, SpeechToSpeechFinding],
) -> str:
    if candidate.provider_type == "s2s":
        finding = s2s_lookup.get(candidate.candidate_id)
        if finding is not None:
            return finding.attempted_setup_evidence
    if candidate.artifact_references:
        return candidate.artifact_references[0]
    return candidate.integration_gate.evidence


def _blocked_rows(
    candidates: Sequence[BenchmarkCandidateResult],
    *,
    s2s_lookup: dict[str, SpeechToSpeechFinding],
) -> list[str]:
    blocked_candidates = [
        candidate
        for candidate in candidates
        if candidate.status == "blocked"
        or candidate.license_gate.blocked
        or candidate.safety_gate.blocked
        or candidate.integration_gate.blocked
    ]
    lines = [
        "| Candidate | Provider | Blocker | Attempted Setup | Next Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    if not blocked_candidates:
        lines.append("| None | None | None | None | None |")
        return lines

    for candidate in blocked_candidates:
        blocker = candidate.blocker_reason or candidate.integration_gate.reason
        next_action = candidate.next_action or candidate.integration_gate.evidence
        attempted_setup = _blocked_attempted_setup(candidate, s2s_lookup)
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    _escape_markdown_text(candidate.provider_type),
                    _escape_markdown_text(blocker),
                    _escape_markdown_text(attempted_setup),
                    _escape_markdown_text(next_action),
                )
            )
            + " |"
        )
    return lines


def _recommendation_rows(recommendation: BenchmarkRecommendation) -> list[str]:
    lines = [
        "| Workflow | Recommendation |",
        "| --- | --- |",
        "| Studio default | "
        + _escape_markdown_text(recommendation.studio_default_recommendation)
        + " |",
        "| Live conversation | "
        + _escape_markdown_text(recommendation.live_conversation_recommendation)
        + " |",
        "| Default switch | "
        + _escape_markdown_text(recommendation.default_switch_decision)
        + " |",
    ]
    if recommendation.notes:
        lines.append("")
        lines.append(_escape_markdown_text(recommendation.notes))
    return lines


def _default_switch_rows(recommendation: BenchmarkRecommendation) -> list[str]:
    lines = [
        "| Decision | Reason | Next Step |",
        "| --- | --- | --- |",
        "| "
        + " | ".join(
            (
                _escape_markdown_text(recommendation.default_switch_decision),
                _escape_markdown_text(
                    recommendation.default_switch_reason
                    or "No alternate candidate cleared the hard gates.",
                ),
                _escape_markdown_text(
                    "Phase 6 GPU-host validation or an approved external evidence run is required "
                    "before any default switch is considered.",
                ),
            )
        )
        + " |",
    ]
    return lines


def write_benchmark_report(
    candidate_rows: Sequence[BenchmarkCandidateResult],
    recommendation: BenchmarkRecommendation,
    *,
    output_dir: str | Path | None = None,
    s2s_scan: SpeechToSpeechScan | None = None,
) -> None:
    report_dir = Path(output_dir) if output_dir is not None else REPORTS_DIR
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / RESULTS_JSON_FILENAME
    csv_path = report_dir / RESULTS_CSV_FILENAME
    markdown_path = report_dir / RECOMMENDATION_MD_FILENAME

    payload = {
        "candidates": [candidate.model_dump(mode="json") for candidate in candidate_rows],
        "recommendation": recommendation.model_dump(mode="json"),
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

    csv_headers = [
        "candidate_id",
        "provider_type",
        "provider_name",
        "corpus_item_id",
        "status",
        "total_wall_ms",
        "license_gate_status",
        "license_gate_reason",
        "safety_gate_status",
        "integration_gate_status",
        "runtime_cost",
        "integration_risk",
        "blocker_reason",
        "next_action",
        "quality_intelligibility",
        "quality_persona_tone_fit",
        "quality_naturalness",
        "quality_artifact_level",
        "quality_safety_boundary_adherence",
        "vad_ms",
        "stt_ms",
        "response_text_ms",
        "tts_ms",
        "playback_ready_ms",
        "total_duration_ms",
        "artifact_references",
    ]
    with csv_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        for candidate in candidate_rows:
            writer.writerow(_candidate_to_csv_row(candidate))

    s2s_lookup = {finding.candidate_id: finding for finding in s2s_scan.findings} if s2s_scan else {}
    markdown_lines = [
        "# Model Benchmark Recommendation",
        "",
        "## Executive Recommendation",
        *_recommendation_rows(recommendation),
        "",
        "## Gate Matrix",
        *_gate_matrix_rows(candidate_rows),
        "",
        "## VAD Comparison",
        *_comparison_rows(candidate_rows, provider_type="vad"),
        "",
        "## TTS And Voice-Cloning Comparison",
        *_comparison_rows(candidate_rows, provider_type="tts"),
        "",
        "## End-to-End Speech Findings",
        *_s2s_findings_rows(s2s_scan),
        "",
        "## Quality Rubric",
        *_quality_rows(candidate_rows),
        "",
        "## Latency And Runtime",
        *_latency_rows(candidate_rows),
        "",
        "## Blocked Candidates",
        *_blocked_rows(candidate_rows, s2s_lookup=s2s_lookup),
        "",
        "## Default Switch Decision",
        *_default_switch_rows(recommendation),
    ]
    markdown_path.write_text("\n".join(markdown_lines).rstrip() + "\n")


def _quality_rows(candidates: Sequence[BenchmarkCandidateResult]) -> list[str]:
    lines = [
        "| Candidate | Intelligibility | Persona Tone Fit | Naturalness | Artifact Level | Safety Boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        scores = candidate.quality_scores
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    str(scores.intelligibility),
                    str(scores.persona_tone_fit),
                    str(scores.naturalness),
                    str(scores.artifact_level),
                    str(scores.safety_boundary_adherence),
                )
            )
            + " |"
        )
    return lines


def _latency_rows(candidates: Sequence[BenchmarkCandidateResult]) -> list[str]:
    lines = [
        "| Candidate | VAD | STT | Response Text | TTS | Playback Ready | Total Wall | Runtime Cost |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        timings = candidate.stage_timings_ms
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    str(timings.vad_ms),
                    str(timings.stt_ms),
                    str(timings.response_text_ms),
                    str(timings.tts_ms),
                    str(timings.playback_ready_ms),
                    str(timings.total_wall_ms),
                    _escape_markdown_text(candidate.runtime_cost),
                )
            )
            + " |"
        )
    return lines

