from __future__ import annotations

import csv
import json
from pathlib import Path

from benchmarks.reporting import write_benchmark_report
from benchmarks.schemas import (
    BenchmarkCandidateResult,
    BenchmarkGateResult,
    BenchmarkQualityScores,
    BenchmarkRecommendation,
    BenchmarkStageTimings,
)


def _build_candidate_result() -> BenchmarkCandidateResult:
    return BenchmarkCandidateResult(
        candidate_id="candidate|alpha",
        provider_type="tts",
        provider_name="cosyvoice|baseline",
        corpus_item_id="text-measured-01",
        status="blocked",
        stage_timings_ms=BenchmarkStageTimings(
            vad_ms=12,
            stt_ms=23,
            response_text_ms=34,
            tts_ms=210,
            playback_ready_ms=250,
            total_wall_ms=290,
        ),
        total_duration_ms=290,
        quality_scores=BenchmarkQualityScores(
            intelligibility=5,
            persona_tone_fit=4,
            naturalness=4,
            artifact_level=2,
            safety_boundary_adherence=5,
        ),
        license_gate=BenchmarkGateResult(
            status="pass",
            reason="model weights are compatible with the internal MVP",
            evidence="license review completed",
            blocked=False,
        ),
        safety_gate=BenchmarkGateResult(
            status="pass",
            reason="original theatrical profile stays inside the project boundary",
            evidence="manifest and prompt text stay consent-safe",
            blocked=False,
        ),
        integration_gate=BenchmarkGateResult(
            status="blocked",
            reason="ffmpeg not available in the local fixture environment",
            evidence="local workspace has no system ffmpeg binary",
            blocked=True,
        ),
        runtime_cost="single GPU class, moderate memory footprint",
        integration_risk="moderate",
        failure_blocker="ffmpeg missing in the local workspace",
        artifact_references=["benchmarks/runs/candidate|alpha.wav"],
    )


def test_write_benchmark_report_serializes_quality_latency_cost_and_risk_fields(tmp_path: Path) -> None:
    candidate = _build_candidate_result()
    recommendation = BenchmarkRecommendation(
        studio_default_recommendation="candidate|alpha",
        live_conversation_recommendation="candidate|alpha",
    )

    write_benchmark_report(
        [candidate],
        recommendation,
        output_dir=tmp_path,
    )

    json_path = tmp_path / "model-benchmark-results.json"
    csv_path = tmp_path / "model-benchmark-results.csv"
    markdown_path = tmp_path / "model-benchmark-recommendation.md"

    assert json_path.exists()
    assert csv_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text())
    assert payload["recommendation"]["studio_default_recommendation"] == "candidate|alpha"
    assert payload["recommendation"]["live_conversation_recommendation"] == "candidate|alpha"

    row = payload["candidates"][0]
    assert row["candidate_id"] == "candidate|alpha"
    assert row["provider_name"] == "cosyvoice|baseline"
    assert row["quality_scores"]["intelligibility"] == 5
    assert row["stage_timings_ms"]["total_wall_ms"] == 290
    assert row["total_duration_ms"] == 290
    assert row["license_gate"]["status"] == "pass"
    assert row["safety_gate"]["status"] == "pass"
    assert row["integration_gate"]["status"] == "blocked"
    assert row["runtime_cost"] == "single GPU class, moderate memory footprint"
    assert row["integration_risk"] == "moderate"

    csv_rows = list(csv.DictReader(csv_path.read_text().splitlines()))
    assert csv_rows[0]["candidate_id"] == "candidate|alpha"
    assert csv_rows[0]["provider_type"] == "tts"
    assert csv_rows[0]["provider_name"] == "cosyvoice|baseline"
    assert csv_rows[0]["status"] == "blocked"
    assert csv_rows[0]["total_wall_ms"] == "290"
    assert csv_rows[0]["license_gate_status"] == "pass"
    assert csv_rows[0]["integration_risk"] == "moderate"

    markdown = markdown_path.read_text()
    assert "## Gate Matrix" in markdown
    assert "## Quality Rubric" in markdown
    assert "## Latency And Runtime" in markdown
    assert "## Recommendation" in markdown
    assert "## Blocked Candidates" in markdown
    assert "candidate|alpha" not in markdown
    assert "candidate\\|alpha" in markdown
    assert "cosyvoice|baseline" not in markdown
    assert "cosyvoice\\|baseline" in markdown
