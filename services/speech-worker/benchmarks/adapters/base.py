from __future__ import annotations

import io
import wave
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Sequence

from benchmarks.corpus import FIXTURES_DIR
from benchmarks.schemas import (
    BenchmarkCandidateResult,
    BenchmarkCorpusItem,
    BenchmarkGateResult,
    BenchmarkQualityScores,
    BenchmarkStageTimings,
)
from providers.contracts import AudioBuffer

BLOCKED_RISK = "high"
RUNNABLE_RISK = "low"


class BenchmarkAdapterStatus(str, Enum):
    RUNNABLE = "runnable"
    BLOCKED = "blocked"


def _pass_gate(reason: str, evidence: str) -> BenchmarkGateResult:
    return BenchmarkGateResult(
        status="pass",
        reason=reason,
        evidence=evidence,
        blocked=False,
    )


def _blocked_gate(reason: str, evidence: str) -> BenchmarkGateResult:
    return BenchmarkGateResult(
        status="blocked",
        reason=reason,
        evidence=evidence,
        blocked=True,
    )


def _score_from_error_ms(error_ms: int) -> int:
    if error_ms <= 40:
        return 5
    if error_ms <= 90:
        return 4
    if error_ms <= 160:
        return 3
    if error_ms <= 260:
        return 2
    return 1


def _score_from_confidence(confidence: float | None) -> int:
    if confidence is None:
        return 3
    if confidence >= 0.9:
        return 5
    if confidence >= 0.8:
        return 4
    if confidence >= 0.65:
        return 3
    if confidence >= 0.5:
        return 2
    return 1


def _audio_buffer_from_fixture_path(fixture_path: Path) -> AudioBuffer:
    resolved_path = Path(fixture_path).resolve()
    fixtures_root = FIXTURES_DIR.resolve()
    if not resolved_path.is_relative_to(fixtures_root):
        raise ValueError(
            f"benchmark audio fixture must live under {fixtures_root}, got {resolved_path}",
        )

    with wave.open(str(resolved_path), "rb") as wav_file:
        return AudioBuffer(
            pcm16=wav_file.readframes(wav_file.getnframes()),
            sample_rate_hz=wav_file.getframerate(),
            channels=wav_file.getnchannels(),
            mime_type="audio/wav",
        )


def build_candidate_result(
    *,
    candidate_id: str,
    provider_type: str,
    provider_name: str,
    corpus_item_id: str,
    status: str,
    stage_timings_ms: BenchmarkStageTimings,
    total_duration_ms: int,
    quality_scores: BenchmarkQualityScores,
    license_gate: BenchmarkGateResult,
    safety_gate: BenchmarkGateResult,
    integration_gate: BenchmarkGateResult,
    runtime_cost: str,
    integration_risk: str,
    blocker_reason: str | None = None,
    next_action: str | None = None,
    artifact_references: Sequence[str] | None = None,
) -> BenchmarkCandidateResult:
    return BenchmarkCandidateResult(
        candidate_id=candidate_id,
        provider_type=provider_type,
        provider_name=provider_name,
        corpus_item_id=corpus_item_id,
        status=status,  # type: ignore[arg-type]
        stage_timings_ms=stage_timings_ms,
        total_duration_ms=total_duration_ms,
        quality_scores=quality_scores,
        license_gate=license_gate,
        safety_gate=safety_gate,
        integration_gate=integration_gate,
        runtime_cost=runtime_cost,
        integration_risk=integration_risk,
        blocker_reason=blocker_reason,
        next_action=next_action,
        artifact_references=list(artifact_references or ()),
    )


class BenchmarkCandidateAdapter(ABC):
    candidate_id: str
    provider_type: str
    provider_name: str

    @property
    def status(self) -> BenchmarkAdapterStatus:
        if (
            self.license_gate().blocked
            or self.safety_gate().blocked
            or self.integration_gate().blocked
        ):
            return BenchmarkAdapterStatus.BLOCKED
        return BenchmarkAdapterStatus.RUNNABLE

    @abstractmethod
    def license_gate(self) -> BenchmarkGateResult:
        raise NotImplementedError

    @abstractmethod
    def safety_gate(self) -> BenchmarkGateResult:
        raise NotImplementedError

    @abstractmethod
    def integration_gate(self) -> BenchmarkGateResult:
        raise NotImplementedError

    @abstractmethod
    def run(self, corpus_item: BenchmarkCorpusItem) -> BenchmarkCandidateResult:
        raise NotImplementedError


class BlockedCandidateAdapter(BenchmarkCandidateAdapter):
    def __init__(
        self,
        *,
        candidate_id: str,
        provider_type: str,
        provider_name: str,
        blocker_reason: str,
        next_action: str,
        license_reason: str,
        license_evidence: str,
        integration_reason: str,
        integration_evidence: str,
        safety_reason: str,
        safety_evidence: str,
        license_status: str = "blocked",
        runtime_cost: str = "blocked before runtime",
        integration_risk: str = BLOCKED_RISK,
    ) -> None:
        self.candidate_id = candidate_id
        self.provider_type = provider_type
        self.provider_name = provider_name
        self.blocker_reason = blocker_reason
        self.next_action = next_action
        self.license_status = license_status
        self.license_reason = license_reason
        self.license_evidence = license_evidence
        self.integration_reason = integration_reason
        self.integration_evidence = integration_evidence
        self.safety_reason = safety_reason
        self.safety_evidence = safety_evidence
        self.runtime_cost = runtime_cost
        self.integration_risk = integration_risk

    def _validate_corpus_item(self, corpus_item: BenchmarkCorpusItem) -> None:
        expected_modality = self.provider_type
        if expected_modality == "vad" and corpus_item.modality != "audio":
            raise ValueError("blocked VAD candidate can only benchmark audio corpus items")
        if expected_modality == "tts" and corpus_item.modality != "text":
            raise ValueError("blocked TTS candidate can only benchmark text corpus items")

    def license_gate(self) -> BenchmarkGateResult:
        status = "pass" if self.license_status == "pass" else "blocked"
        return BenchmarkGateResult(
            status=status,
            reason=self.license_reason,
            evidence=self.license_evidence,
            blocked=status == "blocked",
        )

    def safety_gate(self) -> BenchmarkGateResult:
        return _pass_gate(self.safety_reason, self.safety_evidence)

    def integration_gate(self) -> BenchmarkGateResult:
        return _blocked_gate(self.integration_reason, self.integration_evidence)

    def run(self, corpus_item: BenchmarkCorpusItem) -> BenchmarkCandidateResult:
        self._validate_corpus_item(corpus_item)
        return build_candidate_result(
            candidate_id=self.candidate_id,
            provider_type=self.provider_type,
            provider_name=self.provider_name,
            corpus_item_id=corpus_item.id,
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
            license_gate=self.license_gate(),
            safety_gate=self.safety_gate(),
            integration_gate=self.integration_gate(),
            runtime_cost=self.runtime_cost,
            integration_risk=self.integration_risk,
            blocker_reason=self.blocker_reason,
            next_action=self.next_action,
            artifact_references=[
                self.license_evidence,
                self.integration_evidence,
                self.next_action,
            ],
        )
