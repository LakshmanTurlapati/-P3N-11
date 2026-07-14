from __future__ import annotations

from collections import defaultdict
from statistics import fmean
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .schemas import BenchmarkCandidateResult, BenchmarkRecommendation
from .s2s_findings import SpeechToSpeechScan

CURRENT_STUDIO_DEFAULT = "cosyvoice"
CURRENT_LIVE_CONVERSATION_DEFAULT = "silero-vad"


class RecommendationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    workflow: Literal["studio", "live_conversation", "default_switch"]
    decision: Literal["keep-current-defaults", "switch-defaults"]
    candidate_id: str | None = None
    candidate_name: str | None = None
    reason: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)

    @field_validator("candidate_id", "candidate_name", "reason")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        return cleaned_value

    @field_validator("evidence")
    @classmethod
    def _normalize_evidence(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


def _candidate_quality_score(candidate: BenchmarkCandidateResult) -> float:
    scores = candidate.quality_scores.model_dump()
    return fmean(scores.values())


def _candidate_evidence_score(candidate: BenchmarkCandidateResult) -> int:
    return len(candidate.artifact_references)


def should_switch_default_provider(candidate: BenchmarkCandidateResult) -> bool:
    if candidate.status != "passed":
        return False
    if (
        candidate.license_gate.blocked
        or candidate.safety_gate.blocked
        or candidate.integration_gate.blocked
    ):
        return False
    if candidate.stage_timings_ms.total_wall_ms <= 0:
        return False
    if candidate.total_duration_ms <= 0:
        return False
    if not candidate.runtime_cost.strip() or not candidate.integration_risk.strip():
        return False
    if not candidate.artifact_references:
        return False
    return True


def _group_candidates(rows: list[BenchmarkCandidateResult]) -> dict[str, list[BenchmarkCandidateResult]]:
    grouped: dict[str, list[BenchmarkCandidateResult]] = defaultdict(list)
    for row in rows:
        grouped[row.candidate_id].append(row)
    return grouped


def _candidate_rank(rows: list[BenchmarkCandidateResult]) -> tuple[float, float, int, str]:
    average_quality = fmean(_candidate_quality_score(row) for row in rows)
    average_latency = fmean(row.stage_timings_ms.total_wall_ms for row in rows)
    evidence_score = sum(_candidate_evidence_score(row) for row in rows)
    provider_name = rows[0].provider_name
    return (average_quality, -average_latency, evidence_score, provider_name)


def _select_recommendation(
    *,
    rows: list[BenchmarkCandidateResult],
    current_default_candidate_id: str,
    workflow: Literal["studio", "live_conversation"],
) -> RecommendationDecision:
    if not rows:
        return RecommendationDecision(
            workflow=workflow,
            decision="keep-current-defaults",
            candidate_id=current_default_candidate_id,
            candidate_name=current_default_candidate_id,
            reason="No benchmark rows were provided, so the current default remains unchanged.",
            evidence=[],
        )

    grouped_rows = _group_candidates(rows)
    eligible_groups: dict[str, list[BenchmarkCandidateResult]] = {}
    blocked_evidence: list[str] = []
    for candidate_id, candidate_rows in grouped_rows.items():
        if all(should_switch_default_provider(row) for row in candidate_rows):
            eligible_groups[candidate_id] = candidate_rows
        else:
            blocked_evidence.extend(
                row.blocker_reason
                or row.integration_gate.evidence
                or row.license_gate.evidence
                for row in candidate_rows
                if row.status != "passed"
                or row.license_gate.blocked
                or row.safety_gate.blocked
                or row.integration_gate.blocked
            )

    current_default_rows = eligible_groups.get(current_default_candidate_id)
    current_default_score = (
        _candidate_rank(current_default_rows) if current_default_rows is not None else None
    )

    alternate_candidates = {
        candidate_id: candidate_rows
        for candidate_id, candidate_rows in eligible_groups.items()
        if candidate_id != current_default_candidate_id
    }
    if alternate_candidates:
        best_alternate_id, best_alternate_rows = max(
            alternate_candidates.items(),
            key=lambda item: _candidate_rank(item[1]),
        )
        best_alternate_score = _candidate_rank(best_alternate_rows)
        if current_default_score is None or best_alternate_score > current_default_score:
            best_alternate = best_alternate_rows[0]
            return RecommendationDecision(
                workflow=workflow,
                decision="switch-defaults",
                candidate_id=best_alternate.candidate_id,
                candidate_name=best_alternate.provider_name,
                reason=(
                    f"{best_alternate.provider_name} cleared all hard gates and outscored the "
                    f"current default on quality and latency evidence."
                ),
                evidence=best_alternate.artifact_references,
            )

    current_candidate_rows = current_default_rows or grouped_rows.get(current_default_candidate_id)
    current_candidate = current_candidate_rows[0] if current_candidate_rows else rows[0]
    return RecommendationDecision(
        workflow=workflow,
        decision="keep-current-defaults",
        candidate_id=current_candidate.candidate_id,
        candidate_name=current_candidate.provider_name,
        reason=(
            f"Keep {current_candidate.provider_name} as the {workflow.replace('_', ' ')} default "
            "until an alternate clears the hard gates and provides stronger benchmark evidence."
        ),
        evidence=blocked_evidence or current_candidate.artifact_references,
    )


def _s2s_notes(scan: SpeechToSpeechScan | None) -> str:
    if scan is None or not scan.findings:
        return "No S2S findings were supplied for the recommendation report."

    blocked_summary = "; ".join(
        f"{finding.candidate_name}: {finding.blocker_reason}" for finding in scan.findings
    )
    return (
        "End-to-end S2S candidates remain findings-first only. "
        f"Blocked scan evidence: {blocked_summary}. "
        "Phase 6 GPU-host validation is required before any S2S migration is reconsidered."
    )


def build_provider_recommendation(
    *,
    vad_rows: list[BenchmarkCandidateResult],
    tts_rows: list[BenchmarkCandidateResult],
    s2s_scan: SpeechToSpeechScan | None = None,
) -> BenchmarkRecommendation:
    live_decision = _select_recommendation(
        rows=vad_rows,
        current_default_candidate_id=CURRENT_LIVE_CONVERSATION_DEFAULT,
        workflow="live_conversation",
    )
    studio_decision = _select_recommendation(
        rows=tts_rows,
        current_default_candidate_id=CURRENT_STUDIO_DEFAULT,
        workflow="studio",
    )

    default_switch_decision = "keep-current-defaults"
    default_switch_reason = (
        "No alternate candidate cleared the hard gates and evidence thresholds; "
        "keep the current studio and live conversation defaults until Phase 6 GPU-host validation."
    )
    if (
        studio_decision.decision == "switch-defaults"
        and live_decision.decision == "switch-defaults"
    ):
        default_switch_decision = "switch-defaults"
        default_switch_reason = (
            "Both the studio and live conversation candidates cleared the hard gates with "
            "stronger benchmark evidence than the current defaults."
        )

    return BenchmarkRecommendation(
        studio_default_recommendation=studio_decision.candidate_id or CURRENT_STUDIO_DEFAULT,
        live_conversation_recommendation=live_decision.candidate_id or CURRENT_LIVE_CONVERSATION_DEFAULT,
        default_switch_decision=default_switch_decision,
        default_switch_reason=default_switch_reason,
        notes=f"{studio_decision.reason} {live_decision.reason} {_s2s_notes(s2s_scan)}",
    )

