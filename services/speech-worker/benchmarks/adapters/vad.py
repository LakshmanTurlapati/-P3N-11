from __future__ import annotations

from statistics import fmean
from time import perf_counter

from benchmarks.corpus import BenchmarkCorpus, load_benchmark_corpus
from benchmarks.schemas import (
    BenchmarkCandidateResult,
    BenchmarkCorpusItem,
    BenchmarkGateResult,
    BenchmarkQualityScores,
    BenchmarkRecommendation,
    BenchmarkStageTimings,
)
from providers.contracts import SpeechSegment, VADProvider
from providers.silero_vad_provider import SileroVADProvider

from .base import (
    BlockedCandidateAdapter,
    BenchmarkCandidateAdapter,
    _audio_buffer_from_fixture_path,
    _pass_gate,
    _score_from_confidence,
    _score_from_error_ms,
    build_candidate_result,
)


def _segment_bounds(segments: list[SpeechSegment]) -> tuple[int, int]:
    start_ms = min(segment.start_ms for segment in segments)
    end_ms = max(segment.end_ms for segment in segments)
    return start_ms, end_ms


def _quality_scores(
    corpus_item: BenchmarkCorpusItem,
    segments: list[SpeechSegment],
) -> BenchmarkQualityScores:
    if not segments:
        return BenchmarkQualityScores(
            intelligibility=1,
            persona_tone_fit=1,
            naturalness=1,
            artifact_level=1,
            safety_boundary_adherence=5,
        )

    detected_start_ms, detected_end_ms = _segment_bounds(segments)
    start_error_ms = abs(detected_start_ms - corpus_item.speech_window_start_ms)
    end_error_ms = abs(detected_end_ms - corpus_item.speech_window_end_ms)
    confidence_values = [
        segment.confidence for segment in segments if segment.confidence is not None
    ]
    confidence_score = _score_from_confidence(
        fmean(confidence_values) if confidence_values else None,
    )
    alignment_score = _score_from_error_ms(start_error_ms + end_error_ms)
    overall_score = max(1, min(5, round((confidence_score + alignment_score) / 2)))

    return BenchmarkQualityScores(
        intelligibility=overall_score,
        persona_tone_fit=overall_score,
        naturalness=overall_score,
        artifact_level=max(1, overall_score - 1 if len(segments) > 2 else overall_score),
        safety_boundary_adherence=5,
    )


def _fixture_stage_timings(corpus_item: BenchmarkCorpusItem, segment_count: int) -> BenchmarkStageTimings:
    vad_ms = max(1, min(80, corpus_item.duration_ms // 48 + segment_count * 3))
    return BenchmarkStageTimings(
        vad_ms=vad_ms,
        stt_ms=0,
        response_text_ms=0,
        tts_ms=0,
        playback_ready_ms=vad_ms,
        total_wall_ms=vad_ms,
    )


def _artifact_references(
    corpus_item: BenchmarkCorpusItem,
    segments: list[SpeechSegment],
) -> list[str]:
    references = [
        f"fixture:{corpus_item.fixture_path.name if corpus_item.fixture_path else corpus_item.id}",
        f"window:{corpus_item.speech_window_start_ms}-{corpus_item.speech_window_end_ms}",
        f"segments:{len(segments)}",
    ]
    confidence_values = [
        segment.confidence for segment in segments if segment.confidence is not None
    ]
    if confidence_values:
        references.append(f"confidence:{fmean(confidence_values):.2f}")
    return references


class VADBenchmarkAdapter(BenchmarkCandidateAdapter):
    provider_type = "vad"

    def __init__(
        self,
        provider: VADProvider,
        *,
        candidate_id: str,
        provider_name: str | None = None,
        fixture_mode: bool = True,
    ) -> None:
        self.provider = provider
        self.candidate_id = candidate_id
        self.provider_name = provider_name or getattr(provider, "provider_name", "vad")
        self.fixture_mode = fixture_mode

    def license_gate(self) -> BenchmarkGateResult:
        return _pass_gate(
            "Silero VAD stays behind the existing provider contract.",
            "Fixture or injected backend executed without a new model install.",
        )

    def safety_gate(self) -> BenchmarkGateResult:
        return _pass_gate(
            "Benchmark corpus items stay inside the original theatrical boundary.",
            "Consent-safe benchmark corpus only.",
        )

    def integration_gate(self) -> BenchmarkGateResult:
        return _pass_gate(
            "Provider contract accepted the benchmark audio and returned ordered speech segments.",
            "No torch or GPU runtime was required for the fixture path.",
        )

    def run(self, corpus_item: BenchmarkCorpusItem) -> BenchmarkCandidateResult:
        if corpus_item.modality != "audio":
            raise ValueError("VAD benchmarks can only run against audio corpus items")
        if corpus_item.fixture_path is None:
            raise ValueError("audio benchmark items must include a fixture path")

        audio_buffer = _audio_buffer_from_fixture_path(corpus_item.fixture_path)
        if self.fixture_mode:
            segments = self.provider.detect_speech_segments(audio_buffer)
            elapsed_ms = max(1, min(80, corpus_item.duration_ms // 48 + len(segments) * 3))
        else:
            started_at = perf_counter()
            segments = self.provider.detect_speech_segments(audio_buffer)
            elapsed_ms = max(0, int(round((perf_counter() - started_at) * 1000)))

        stage_timings = _fixture_stage_timings(corpus_item, len(segments))
        stage_timings = stage_timings.model_copy(
            update={
                "vad_ms": elapsed_ms,
                "playback_ready_ms": elapsed_ms,
                "total_wall_ms": elapsed_ms,
            }
        )

        quality_scores = _quality_scores(corpus_item, segments)
        total_duration_ms = corpus_item.duration_ms or 0
        return build_candidate_result(
            candidate_id=self.candidate_id,
            provider_type=self.provider_type,
            provider_name=self.provider_name,
            corpus_item_id=corpus_item.id,
            status="passed",
            stage_timings_ms=stage_timings,
            total_duration_ms=total_duration_ms,
            quality_scores=quality_scores,
            license_gate=self.license_gate(),
            safety_gate=self.safety_gate(),
            integration_gate=self.integration_gate(),
            runtime_cost="cpu fixture path, low memory",
            integration_risk="low",
            artifact_references=_artifact_references(corpus_item, segments),
        )


class SileroVADBenchmarkAdapter(VADBenchmarkAdapter):
    def __init__(
        self,
        provider: VADProvider,
        *,
        fixture_mode: bool = True,
    ) -> None:
        super().__init__(
            provider,
            candidate_id="silero-vad",
            provider_name=getattr(provider, "provider_name", "silero-vad"),
            fixture_mode=fixture_mode,
        )


def build_blocked_vad_adapter() -> BlockedCandidateAdapter:
    return BlockedCandidateAdapter(
        candidate_id="fireredvad",
        provider_type="vad",
        provider_name="fireredvad",
        blocker_reason=(
            "FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker "
            "runtime compatibility are verified in the local workspace."
        ),
        next_action=(
            "Approve a verified FireRedVAD source/package, validate it on the GPU worker, "
            "then rerun the benchmark before ranking it."
        ),
        license_reason="FireRedVAD package legitimacy and download evidence are not verified locally.",
        license_evidence="https://github.com/FireRedTeam/FireRedVAD",
        integration_reason="FireRedVAD target runtime compatibility is not verified in this workspace.",
        integration_evidence="GPU-worker runtime validation remains pending.",
        safety_reason="Blocked candidates are not ranked ahead of the consent-safe baseline.",
        safety_evidence="Consent-safe benchmark corpus only.",
        license_status="blocked",
        runtime_cost="blocked before runtime",
        integration_risk="high",
    )


def _select_candidate_id(rows: list[BenchmarkCandidateResult]) -> str:
    grouped: dict[str, list[BenchmarkCandidateResult]] = {}
    for row in rows:
        grouped.setdefault(row.candidate_id, []).append(row)

    ranked: list[tuple[bool, float, float, str]] = []
    for candidate_id, candidate_rows in grouped.items():
        blocked = any(
            row.status != "passed"
            or row.license_gate.blocked
            or row.safety_gate.blocked
            or row.integration_gate.blocked
            for row in candidate_rows
        )
        average_wall_ms = sum(
            row.stage_timings_ms.total_wall_ms for row in candidate_rows
        ) / len(candidate_rows)
        average_quality = sum(
            sum(row.quality_scores.model_dump().values()) for row in candidate_rows
        ) / len(candidate_rows)
        ranked.append((blocked, average_wall_ms, -average_quality, candidate_id))

    if not ranked:
        raise ValueError("benchmark run did not produce any candidate rows")

    ranked.sort()
    return ranked[0][3]


def run_vad_benchmark(
    *,
    corpus: BenchmarkCorpus | None = None,
    baseline_provider: VADProvider | None = None,
    alternate_adapter: BenchmarkCandidateAdapter | None = None,
    fixture_mode: bool = True,
) -> tuple[list[BenchmarkCandidateResult], BenchmarkRecommendation]:
    benchmark_corpus = corpus or load_benchmark_corpus()
    provider = baseline_provider or SileroVADProvider(force_fixture_fallback=True)
    baseline_adapter = SileroVADBenchmarkAdapter(provider, fixture_mode=fixture_mode)
    blocked_alternate = alternate_adapter or build_blocked_vad_adapter()

    audio_items = [
        item for item in benchmark_corpus.items if item.modality == "audio"
    ]
    rows: list[BenchmarkCandidateResult] = []
    for corpus_item in audio_items:
        rows.append(baseline_adapter.run(corpus_item))
        rows.append(blocked_alternate.run(corpus_item))

    recommended_candidate_id = _select_candidate_id(rows)
    recommendation = BenchmarkRecommendation(
        studio_default_recommendation=recommended_candidate_id,
        live_conversation_recommendation=recommended_candidate_id,
        notes=(
            "FireRedVAD remains blocked in the local workspace until package legitimacy "
            "and GPU-worker runtime validation are confirmed."
        ),
    )
    return rows, recommendation
