from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from benchmarks.adapters.base import build_candidate_result
from benchmarks.schemas import (
    BenchmarkCandidateResult,
    BenchmarkGateResult,
    BenchmarkQualityScores,
    BenchmarkStageTimings,
)

SpeechToSpeechStatus = Literal["blocked", "runnable"]


def _pass_gate(reason: str, evidence: str) -> BenchmarkGateResult:
    return BenchmarkGateResult(status="pass", reason=reason, evidence=evidence, blocked=False)


def _blocked_gate(reason: str, evidence: str) -> BenchmarkGateResult:
    return BenchmarkGateResult(
        status="blocked",
        reason=reason,
        evidence=evidence,
        blocked=True,
    )


class SpeechToSpeechFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    candidate_id: str = Field(min_length=1)
    candidate_name: str = Field(min_length=1)
    status: SpeechToSpeechStatus
    license_summary: str = Field(min_length=1)
    hardware_runtime_needs: str = Field(min_length=1)
    streaming_latency_posture: str = Field(min_length=1)
    voice_control_fit: str = Field(min_length=1)
    integration_risk: str = Field(min_length=1)
    attempted_setup_evidence: str = Field(min_length=1)
    blocker_reason: str | None = None
    next_action: str | None = None
    gpu_run_command: str | None = None
    external_evidence_ref: str | None = None
    quality_scores: BenchmarkQualityScores
    stage_timings_ms: BenchmarkStageTimings
    total_duration_ms: int = Field(ge=0)
    license_gate: BenchmarkGateResult
    safety_gate: BenchmarkGateResult
    integration_gate: BenchmarkGateResult
    runtime_cost: str = Field(min_length=1)
    artifact_references: list[str] = Field(default_factory=list)

    @field_validator(
        "candidate_id",
        "candidate_name",
        "license_summary",
        "hardware_runtime_needs",
        "streaming_latency_posture",
        "voice_control_fit",
        "integration_risk",
        "attempted_setup_evidence",
        "blocker_reason",
        "next_action",
        "gpu_run_command",
        "external_evidence_ref",
        "runtime_cost",
    )
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @field_validator("artifact_references")
    @classmethod
    def _normalize_artifact_references(cls, value: list[str]) -> list[str]:
        return [reference.strip() for reference in value if reference and reference.strip()]

    @model_validator(mode="after")
    def _validate_status_consistency(self) -> "SpeechToSpeechFinding":
        if self.status == "blocked":
            if not self.blocker_reason or not self.next_action:
                raise ValueError("blocked S2S findings must include blocker_reason and next_action")
            if self.gpu_run_command is not None or self.external_evidence_ref is not None:
                raise ValueError("blocked S2S findings must not include external execution evidence")
        else:
            if self.blocker_reason is not None or self.next_action is not None:
                raise ValueError("runnable S2S findings must not include blocker metadata")
            if not (self.gpu_run_command or self.external_evidence_ref):
                raise ValueError("runnable S2S findings must include a GPU run command or evidence ref")
        return self

    def to_candidate_result(self) -> BenchmarkCandidateResult:
        return build_candidate_result(
            candidate_id=self.candidate_id,
            provider_type="s2s",
            provider_name=self.candidate_name,
            corpus_item_id=f"s2s-{self.candidate_id}",
            status="blocked" if self.status == "blocked" else "passed",
            stage_timings_ms=self.stage_timings_ms,
            total_duration_ms=self.total_duration_ms,
            quality_scores=self.quality_scores,
            license_gate=self.license_gate,
            safety_gate=self.safety_gate,
            integration_gate=self.integration_gate,
            runtime_cost=self.runtime_cost,
            integration_risk=self.integration_risk,
            blocker_reason=self.blocker_reason,
            next_action=self.next_action,
            artifact_references=self.artifact_references
            or [
                self.attempted_setup_evidence,
                self.license_summary,
                self.hardware_runtime_needs,
                self.streaming_latency_posture,
            ],
        )


class SpeechToSpeechScan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: list[SpeechToSpeechFinding]

    @model_validator(mode="after")
    def _validate_findings(self) -> "SpeechToSpeechScan":
        candidate_ids = [finding.candidate_id for finding in self.findings]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("speech-to-speech finding candidate_ids must be unique")
        return self

    def candidate_rows(self) -> list[BenchmarkCandidateResult]:
        return [finding.to_candidate_result() for finding in self.findings]


def _blocked_finding(
    *,
    candidate_id: str,
    candidate_name: str,
    license_summary: str,
    hardware_runtime_needs: str,
    streaming_latency_posture: str,
    voice_control_fit: str,
    integration_risk: str,
    attempted_setup_evidence: str,
    blocker_reason: str,
    next_action: str,
    quality_scores: tuple[int, int, int, int, int],
    runtime_cost: str,
    artifact_references: list[str],
) -> SpeechToSpeechFinding:
    return SpeechToSpeechFinding(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        status="blocked",
        license_summary=license_summary,
        hardware_runtime_needs=hardware_runtime_needs,
        streaming_latency_posture=streaming_latency_posture,
        voice_control_fit=voice_control_fit,
        integration_risk=integration_risk,
        attempted_setup_evidence=attempted_setup_evidence,
        blocker_reason=blocker_reason,
        next_action=next_action,
        quality_scores=BenchmarkQualityScores(
            intelligibility=quality_scores[0],
            persona_tone_fit=quality_scores[1],
            naturalness=quality_scores[2],
            artifact_level=quality_scores[3],
            safety_boundary_adherence=quality_scores[4],
        ),
        stage_timings_ms=BenchmarkStageTimings(
            vad_ms=0,
            stt_ms=0,
            response_text_ms=0,
            tts_ms=0,
            playback_ready_ms=0,
            total_wall_ms=0,
        ),
        total_duration_ms=0,
        license_gate=_pass_gate(
            "License and repo documentation were reviewed.",
            license_summary,
        ),
        safety_gate=_pass_gate(
            "The scan stays inside the consented original-voice boundary.",
            "No protected-character or real-performer imitation is planned.",
        ),
        integration_gate=_blocked_gate(
            "A capable GPU host is required before ranking this candidate.",
            attempted_setup_evidence,
        ),
        runtime_cost=runtime_cost,
        artifact_references=artifact_references,
    )


def build_s2s_findings() -> SpeechToSpeechScan:
    findings = [
        _blocked_finding(
            candidate_id="moshi",
            candidate_name="Moshi",
            license_summary=(
                "Repo docs indicate a promising open stack, but the model/runtime path has not been "
                "validated in the local benchmark workspace."
            ),
            hardware_runtime_needs=(
                "Capable GPU host with streaming/full-duplex speech runtime and low-latency transport."
            ),
            streaming_latency_posture=(
                "Best first scan target because the docs describe clear streaming/full-duplex behavior."
            ),
            voice_control_fit=(
                "Strong conversational fit if external execution proves stable and interruptible."
            ),
            integration_risk="medium",
            attempted_setup_evidence=(
                "Research notes cite clear streaming/full-duplex docs, but `.venv` lacks torch, ffmpeg, and GPU access."
            ),
            blocker_reason=(
                "No sanctioned GPU-host execution or package verification has been captured in this workspace."
            ),
            next_action=(
                "Run a sanctioned GPU-host scan and attach the external evidence reference before ranking Moshi."
            ),
            quality_scores=(3, 3, 3, 3, 4),
            runtime_cost="gpu host, bounded streaming runtime",
            artifact_references=[
                "https://github.com/kyutai-labs/moshi",
                "local workspace lacks torch, ffmpeg, and GPU access",
            ],
        ),
        _blocked_finding(
            candidate_id="minicpm-o-4.5",
            candidate_name="MiniCPM-o 4.5",
            license_summary=(
                "Repo docs and model notes are available, but no external GPU-host benchmark evidence has been captured."
            ),
            hardware_runtime_needs=(
                "GPU host with a bounded runtime envelope for full-duplex multimodal speech."
            ),
            streaming_latency_posture=(
                "Clear streaming/full-duplex documentation, but the local workspace cannot validate it."
            ),
            voice_control_fit=(
                "Good candidate for live turn-taking if the external host keeps latency bounded."
            ),
            integration_risk="medium",
            attempted_setup_evidence=(
                "Research notes describe clear streaming/full-duplex docs and a bounded runtime story, but no GPU-host run is captured."
            ),
            blocker_reason=(
                "The candidate remains findings-only until a capable GPU host produces benchmark evidence."
            ),
            next_action=(
                "Capture an external evidence reference from a capable GPU host or keep MiniCPM-o blocked."
            ),
            quality_scores=(3, 3, 3, 2, 4),
            runtime_cost="gpu host, moderate memory footprint",
            artifact_references=[
                "https://github.com/OpenBMB/MiniCPM-V",
                "no GPU-host evidence captured",
            ],
        ),
        _blocked_finding(
            candidate_id="chroma",
            candidate_name="FlashLabs Chroma",
            license_summary=(
                "The repo is visible, but the heavier runtime and CUDA dependency story makes it a late-scan candidate."
            ),
            hardware_runtime_needs="CUDA 12.6 GPU host with a heavier inference envelope than the baseline slice.",
            streaming_latency_posture=(
                "Interesting speech-to-speech profile, but too much runtime friction for the local benchmark host."
            ),
            voice_control_fit=(
                "Moderate conversational fit once the CUDA 12.6 runtime can be exercised on the correct worker."
            ),
            integration_risk="high",
            attempted_setup_evidence=(
                "Phase research flags CUDA 12.6 and the local workspace lacks GPU access for a real run."
            ),
            blocker_reason=(
                "Chroma is too heavy for this workspace and needs a different GPU host before it can be ranked."
            ),
            next_action=(
                "Defer until a CUDA 12.6 worker is available and the benchmark slice can absorb the run."
            ),
            quality_scores=(2, 2, 2, 2, 4),
            runtime_cost="cuda 12.6 GPU host, heavier memory footprint",
            artifact_references=[
                "https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma",
                "CUDA 12.6 runtime unavailable locally",
            ],
        ),
        _blocked_finding(
            candidate_id="qwen3-omni",
            candidate_name="Qwen3-Omni",
            license_summary=(
                "Official repo/docs are available, but the 30B-A3B-class stack needs a much larger runtime envelope."
            ),
            hardware_runtime_needs="Large GPU host with substantial memory headroom and streaming support.",
            streaming_latency_posture=(
                "Open streaming issues keep it as a late-scan candidate rather than a local benchmark target."
            ),
            voice_control_fit=(
                "Potentially strong multimodal fit, but still unproven in this benchmark slice."
            ),
            integration_risk="high",
            attempted_setup_evidence=(
                "Research notes call out the 30B-A3B class and open streaming issues; the local host has no GPU runtime."
            ),
            blocker_reason=(
                "The phase should not absorb a Qwen3-Omni run until larger GPU-host evidence exists."
            ),
            next_action=(
                "Revisit only after smaller S2S candidates or a Phase 6 GPU host make the runtime plausible."
            ),
            quality_scores=(2, 2, 2, 1, 4),
            runtime_cost="30B-A3B-class GPU host, high memory footprint",
            artifact_references=[
                "https://github.com/QwenLM/Qwen3-Omni",
                "open streaming issues noted in research",
            ],
        ),
    ]
    return SpeechToSpeechScan(findings=findings)

