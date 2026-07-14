from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Sequence

from .corpus import REPORTS_DIR
from .schemas import BenchmarkCandidateResult, BenchmarkRecommendation

RESULTS_JSON_FILENAME = "model-benchmark-results.json"
RESULTS_CSV_FILENAME = "model-benchmark-results.csv"
RECOMMENDATION_MD_FILENAME = "model-benchmark-recommendation.md"


def _escape_markdown_text(value: str) -> str:
    escaped_value = value.replace("\\", "\\\\")
    for raw_character in ("|", "*", "_", "`", "<", ">"):
        escaped_value = escaped_value.replace(raw_character, f"\\{raw_character}")
    return escaped_value


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
        "failure_blocker": candidate.failure_blocker or "",
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
        "| Candidate | Provider | License | Safety | Integration |",
        "| --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    _escape_markdown_text(candidate.provider_name),
                    _escape_markdown_text(candidate.license_gate.status),
                    _escape_markdown_text(candidate.safety_gate.status),
                    _escape_markdown_text(candidate.integration_gate.status),
                )
            )
            + " |"
        )
    return lines


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


def _blocked_rows(candidates: Sequence[BenchmarkCandidateResult]) -> list[str]:
    blocked_candidates = [
        candidate
        for candidate in candidates
        if candidate.status == "blocked"
        or candidate.license_gate.blocked
        or candidate.safety_gate.blocked
        or candidate.integration_gate.blocked
    ]
    lines = [
        "| Candidate | Blocker | Evidence |",
        "| --- | --- | --- |",
    ]
    if not blocked_candidates:
        lines.append("| None | None | None |")
        return lines

    for candidate in blocked_candidates:
        blocker = candidate.failure_blocker or candidate.integration_gate.reason
        evidence = candidate.integration_gate.evidence
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown_text(candidate.candidate_id),
                    _escape_markdown_text(blocker),
                    _escape_markdown_text(evidence),
                )
            )
            + " |"
        )
    return lines


def _recommendation_section(recommendation: BenchmarkRecommendation) -> list[str]:
    lines = [
        "| Workflow | Recommendation |",
        "| --- | --- |",
        "| Studio default | "
        + _escape_markdown_text(recommendation.studio_default_recommendation)
        + " |",
        "| Live conversation | "
        + _escape_markdown_text(recommendation.live_conversation_recommendation)
        + " |",
    ]
    if recommendation.notes:
        lines.append("")
        lines.append(_escape_markdown_text(recommendation.notes))
    return lines


def write_benchmark_report(
    candidate_rows: Sequence[BenchmarkCandidateResult],
    recommendation: BenchmarkRecommendation,
    *,
    output_dir: str | Path | None = None,
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
        "failure_blocker",
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

    markdown_lines = [
        "# Model Benchmark Recommendation",
        "",
        "## Gate Matrix",
        *_gate_matrix_rows(candidate_rows),
        "",
        "## Quality Rubric",
        *_quality_rows(candidate_rows),
        "",
        "## Latency And Runtime",
        *_latency_rows(candidate_rows),
        "",
        "## Recommendation",
        *_recommendation_section(recommendation),
        "",
        "## Blocked Candidates",
        *_blocked_rows(candidate_rows),
    ]
    markdown_path.write_text("\n".join(markdown_lines).rstrip() + "\n")
