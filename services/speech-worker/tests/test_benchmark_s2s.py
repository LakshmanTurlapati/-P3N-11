from __future__ import annotations

from benchmarks.s2s_findings import SpeechToSpeechFinding, SpeechToSpeechScan, build_s2s_findings


EXPECTED_CANDIDATES = {
    "moshi",
    "minicpm-o-4.5",
    "chroma",
    "qwen3-omni",
}


def test_build_s2s_findings_records_multiple_blocked_candidates_with_complete_evidence() -> None:
    scan = build_s2s_findings()

    assert isinstance(scan, SpeechToSpeechScan)
    assert len(scan.findings) >= 3

    candidate_ids = {finding.candidate_id for finding in scan.findings}
    assert candidate_ids & EXPECTED_CANDIDATES

    for finding in scan.findings:
        assert isinstance(finding, SpeechToSpeechFinding)
        assert finding.candidate_id
        assert finding.candidate_name
        assert finding.status in {"blocked", "runnable"}
        assert finding.license_summary
        assert finding.hardware_runtime_needs
        assert finding.streaming_latency_posture
        assert finding.voice_control_fit
        assert finding.integration_risk
        assert finding.attempted_setup_evidence

        if finding.status == "blocked":
            assert finding.blocker_reason
            assert finding.next_action
        else:
            assert finding.blocker_reason is None
            assert finding.next_action is None
            assert finding.gpu_run_command or finding.external_evidence_ref

