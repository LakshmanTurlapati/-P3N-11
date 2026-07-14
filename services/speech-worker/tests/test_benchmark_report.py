from __future__ import annotations

import csv
import json
from pathlib import Path

from benchmarks.adapters.base import build_candidate_result
from benchmarks.recommendation import build_provider_recommendation, should_switch_default_provider
from benchmarks.reporting import write_benchmark_report
from benchmarks.s2s_findings import build_s2s_findings
from benchmarks.schemas import (
    BenchmarkCandidateResult,
    BenchmarkGateResult,
    BenchmarkQualityScores,
    BenchmarkRecommendation,
    BenchmarkStageTimings,
)


def _gate(status: str, reason: str, evidence: str) -> BenchmarkGateResult:
    return BenchmarkGateResult(
        status=status,  # type: ignore[arg-type]
        reason=reason,
        evidence=evidence,
        blocked=status == "blocked",
    )


def _candidate(
    *,
    candidate_id: str,
    provider_type: str,
    provider_name: str,
    corpus_item_id: str,
    status: str,
    stage_timings_ms: BenchmarkStageTimings,
    total_duration_ms: int,
    quality_scores: BenchmarkQualityScores,
    runtime_cost: str,
    integration_risk: str,
    license_status: str = "pass",
    safety_status: str = "pass",
    integration_status: str = "pass",
    blocker_reason: str | None = None,
    next_action: str | None = None,
    artifact_references: list[str] | None = None,
) -> BenchmarkCandidateResult:
    return build_candidate_result(
        candidate_id=candidate_id,
        provider_type=provider_type,
        provider_name=provider_name,
        corpus_item_id=corpus_item_id,
        status=status,
        stage_timings_ms=stage_timings_ms,
        total_duration_ms=total_duration_ms,
        quality_scores=quality_scores,
        license_gate=_gate(
            license_status,
            "license gate passed" if license_status == "pass" else "license blocked",
            "license evidence" if license_status == "pass" else "license blocker evidence",
        ),
        safety_gate=_gate(
            safety_status,
            "safety gate passed" if safety_status == "pass" else "safety blocked",
            "safety evidence" if safety_status == "pass" else "safety blocker evidence",
        ),
        integration_gate=_gate(
            integration_status,
            "integration gate passed" if integration_status == "pass" else "integration blocked",
            "integration evidence" if integration_status == "pass" else "integration blocker evidence",
        ),
        runtime_cost=runtime_cost,
        integration_risk=integration_risk,
        blocker_reason=blocker_reason,
        next_action=next_action,
        artifact_references=artifact_references or [],
    )


def test_should_switch_default_provider_requires_complete_evidence_and_passed_gates() -> None:
    runnable_candidate = _candidate(
        candidate_id="runnable|baseline",
        provider_type="tts",
        provider_name="cosyvoice|baseline",
        corpus_item_id="text-measured-01",
        status="passed",
        stage_timings_ms=BenchmarkStageTimings(
            vad_ms=0,
            stt_ms=0,
            response_text_ms=0,
            tts_ms=145,
            playback_ready_ms=150,
            total_wall_ms=150,
        ),
        total_duration_ms=157,
        quality_scores=BenchmarkQualityScores(
            intelligibility=5,
            persona_tone_fit=5,
            naturalness=5,
            artifact_level=5,
            safety_boundary_adherence=5,
        ),
        runtime_cost="single GPU class, moderate memory footprint",
        integration_risk="low",
        artifact_references=["fixture:text-measured-01", "timings:150ms"],
    )

    assert should_switch_default_provider(runnable_candidate) is True

    blocked_license = runnable_candidate.model_copy(
        update={"license_gate": _gate("blocked", "blocked", "blocked license")},
    )
    blocked_safety = runnable_candidate.model_copy(
        update={"safety_gate": _gate("blocked", "blocked", "blocked safety")},
    )
    blocked_integration = runnable_candidate.model_copy(
        update={"integration_gate": _gate("blocked", "blocked", "blocked integration")},
    )
    missing_evidence = runnable_candidate.model_copy(update={"artifact_references": []})
    zero_runtime = runnable_candidate.model_copy(
        update={
            "stage_timings_ms": runnable_candidate.stage_timings_ms.model_copy(
                update={"tts_ms": 0, "playback_ready_ms": 0, "total_wall_ms": 0},
            ),
            "total_duration_ms": 0,
        },
    )

    assert should_switch_default_provider(blocked_license) is False
    assert should_switch_default_provider(blocked_safety) is False
    assert should_switch_default_provider(blocked_integration) is False
    assert should_switch_default_provider(missing_evidence) is False
    assert should_switch_default_provider(zero_runtime) is False


def test_build_provider_recommendation_keeps_current_defaults_and_blocks_alternates() -> None:
    vad_rows = [
        _candidate(
            candidate_id="silero-vad",
            provider_type="vad",
            provider_name="silero-vad",
            corpus_item_id="audio-clean-short-01",
            status="passed",
            stage_timings_ms=BenchmarkStageTimings(
                vad_ms=22,
                stt_ms=0,
                response_text_ms=0,
                tts_ms=0,
                playback_ready_ms=22,
                total_wall_ms=22,
            ),
            total_duration_ms=920,
            quality_scores=BenchmarkQualityScores(
                intelligibility=4,
                persona_tone_fit=4,
                naturalness=4,
                artifact_level=4,
                safety_boundary_adherence=5,
            ),
            runtime_cost="cpu fixture path, low memory",
            integration_risk="low",
            artifact_references=["fixture:clean-short.wav", "window:120-760"],
        ),
        _candidate(
            candidate_id="fireredvad",
            provider_type="vad",
            provider_name="fireredvad",
            corpus_item_id="audio-clean-short-01",
            status="blocked",
            stage_timings_ms=BenchmarkStageTimings(
                vad_ms=0,
                stt_ms=0,
                response_text_ms=0,
                tts_ms=0,
                playback_ready_ms=0,
                total_wall_ms=0,
            ),
            total_duration_ms=0,
            quality_scores=BenchmarkQualityScores(
                intelligibility=1,
                persona_tone_fit=1,
                naturalness=1,
                artifact_level=1,
                safety_boundary_adherence=1,
            ),
            runtime_cost="blocked before runtime",
            integration_risk="high",
            license_status="blocked",
            integration_status="blocked",
            blocker_reason="FireRedVAD is blocked until package legitimacy and GPU validation are verified.",
            next_action="Approve a verified FireRedVAD package, validate it on the GPU worker, and rerun.",
            artifact_references=["https://github.com/FireRedTeam/FireRedVAD"],
        ),
    ]
    tts_rows = [
        _candidate(
            candidate_id="cosyvoice",
            provider_type="tts",
            provider_name="cosyvoice",
            corpus_item_id="text-measured-01",
            status="passed",
            stage_timings_ms=BenchmarkStageTimings(
                vad_ms=0,
                stt_ms=0,
                response_text_ms=0,
                tts_ms=145,
                playback_ready_ms=150,
                total_wall_ms=150,
            ),
            total_duration_ms=157,
            quality_scores=BenchmarkQualityScores(
                intelligibility=5,
                persona_tone_fit=5,
                naturalness=5,
                artifact_level=5,
                safety_boundary_adherence=5,
            ),
            runtime_cost="single GPU class, moderate memory footprint",
            integration_risk="low",
            artifact_references=["voice:vesper-glass", "tone:measured"],
        ),
        _candidate(
            candidate_id="qwen3-tts-12hz-0.6b-customvoice",
            provider_type="tts",
            provider_name="qwen3-tts",
            corpus_item_id="text-measured-01",
            status="blocked",
            stage_timings_ms=BenchmarkStageTimings(
                vad_ms=0,
                stt_ms=0,
                response_text_ms=0,
                tts_ms=0,
                playback_ready_ms=0,
                total_wall_ms=0,
            ),
            total_duration_ms=0,
            quality_scores=BenchmarkQualityScores(
                intelligibility=1,
                persona_tone_fit=1,
                naturalness=1,
                artifact_level=1,
                safety_boundary_adherence=1,
            ),
            runtime_cost="blocked before runtime",
            integration_risk="high",
            integration_status="blocked",
            blocker_reason="Qwen3-TTS is approved on source/license grounds but remains blocked until GPU evidence is captured.",
            next_action="Run the approved Qwen3-TTS checkout on the GPU worker and rerun the benchmark.",
            artifact_references=["https://github.com/QwenLM/Qwen3-TTS"],
        ),
    ]
    s2s_scan = build_s2s_findings()

    recommendation = build_provider_recommendation(
        vad_rows=vad_rows,
        tts_rows=tts_rows,
        s2s_scan=s2s_scan,
    )

    blocked_candidate_ids = {
        row.candidate_id
        for row in (*vad_rows, *tts_rows)
        if row.license_gate.blocked or row.safety_gate.blocked or row.integration_gate.blocked
    }
    blocked_candidate_ids.update(finding.candidate_id for finding in s2s_scan.findings)

    assert recommendation.studio_default_recommendation == "cosyvoice"
    assert recommendation.live_conversation_recommendation == "silero-vad"
    assert recommendation.default_switch_decision == "keep-current-defaults"
    assert recommendation.default_switch_reason
    assert recommendation.studio_default_recommendation not in blocked_candidate_ids
    assert recommendation.live_conversation_recommendation not in blocked_candidate_ids


def test_write_benchmark_report_serializes_new_sections_and_candidate_fields(
    tmp_path: Path,
) -> None:
    s2s_scan = build_s2s_findings()
    s2s_rows = [finding.to_candidate_result() for finding in s2s_scan.findings]
    vad_row = _candidate(
        candidate_id="candidate|vad",
        provider_type="vad",
        provider_name="silero-vad|baseline",
        corpus_item_id="audio-clean-short-01",
        status="passed",
        stage_timings_ms=BenchmarkStageTimings(
            vad_ms=22,
            stt_ms=0,
            response_text_ms=0,
            tts_ms=0,
            playback_ready_ms=22,
            total_wall_ms=22,
        ),
        total_duration_ms=920,
        quality_scores=BenchmarkQualityScores(
            intelligibility=4,
            persona_tone_fit=4,
            naturalness=4,
            artifact_level=4,
            safety_boundary_adherence=5,
        ),
        runtime_cost="cpu fixture path, low memory",
        integration_risk="low",
        artifact_references=["fixture:clean-short.wav", "window:120-760"],
    )
    tts_row = _candidate(
        candidate_id="candidate|tts",
        provider_type="tts",
        provider_name="cosyvoice|baseline",
        corpus_item_id="text-measured-01",
        status="blocked",
        stage_timings_ms=BenchmarkStageTimings(
            vad_ms=0,
            stt_ms=0,
            response_text_ms=0,
            tts_ms=140,
            playback_ready_ms=145,
            total_wall_ms=145,
        ),
        total_duration_ms=157,
        quality_scores=BenchmarkQualityScores(
            intelligibility=5,
            persona_tone_fit=5,
            naturalness=5,
            artifact_level=5,
            safety_boundary_adherence=5,
        ),
        runtime_cost="single GPU class, moderate memory footprint",
        integration_risk="moderate",
        integration_status="blocked",
        blocker_reason="ffmpeg is missing in the local workspace",
        next_action="Install ffmpeg on the GPU worker and rerun the benchmark",
        artifact_references=["attempted setup: local ffmpeg check failed"],
    )
    recommendation = BenchmarkRecommendation(
        studio_default_recommendation="cosyvoice",
        live_conversation_recommendation="silero-vad",
        default_switch_decision="keep-current-defaults",
        default_switch_reason="No alternate candidate cleared the hard gates.",
        notes="Blocked candidates stay visible in the report.",
    )

    write_benchmark_report(
        [vad_row, tts_row, *s2s_rows],
        recommendation,
        output_dir=tmp_path,
        s2s_scan=s2s_scan,
    )

    json_path = tmp_path / "model-benchmark-results.json"
    csv_path = tmp_path / "model-benchmark-results.csv"
    markdown_path = tmp_path / "model-benchmark-recommendation.md"

    assert json_path.exists()
    assert csv_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text())
    assert payload["recommendation"]["studio_default_recommendation"] == "cosyvoice"
    assert payload["recommendation"]["live_conversation_recommendation"] == "silero-vad"
    assert payload["recommendation"]["default_switch_decision"] == "keep-current-defaults"

    payload_candidate_ids = {candidate["candidate_id"] for candidate in payload["candidates"]}
    assert payload_candidate_ids == {vad_row.candidate_id, tts_row.candidate_id, *{finding.candidate_id for finding in s2s_scan.findings}}

    csv_rows = list(csv.DictReader(csv_path.read_text().splitlines()))
    assert {row["candidate_id"] for row in csv_rows} == payload_candidate_ids
    assert any(row["provider_type"] == "s2s" for row in csv_rows)

    markdown = markdown_path.read_text()
    for heading in (
        "## Executive Recommendation",
        "## Gate Matrix",
        "## VAD Comparison",
        "## TTS And Voice-Cloning Comparison",
        "## End-to-End Speech Findings",
        "## Quality Rubric",
        "## Latency And Runtime",
        "## Blocked Candidates",
        "## Default Switch Decision",
    ):
        assert heading in markdown

    assert "candidate\\|vad" in markdown
    assert "cosyvoice\\|baseline" in markdown
    assert "attempted setup: local ffmpeg check failed" in markdown
    assert s2s_scan.findings[0].attempted_setup_evidence.replace("`", "\\`") in markdown
    assert s2s_scan.findings[0].blocker_reason in markdown
    assert s2s_scan.findings[0].next_action in markdown
