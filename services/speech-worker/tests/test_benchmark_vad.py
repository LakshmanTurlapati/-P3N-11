from __future__ import annotations

from benchmarks.adapters.vad import run_vad_benchmark
from benchmarks.corpus import load_benchmark_corpus
from benchmarks.schemas import BenchmarkCandidateResult
from providers.contracts import AudioBuffer, SpeechSegment
from providers.silero_vad_provider import SileroVADProvider


class FakeSileroBackend:
    provider_name = "silero-vad"

    def __init__(self) -> None:
        self.calls: list[AudioBuffer] = []

    def detect_speech_segments(self, audio: AudioBuffer) -> list[SpeechSegment]:
        self.calls.append(audio)
        return [
            SpeechSegment(start_ms=100, end_ms=420, confidence=0.84),
            SpeechSegment(start_ms=560, end_ms=920, confidence=0.76),
        ]


def test_run_vad_benchmark_emits_baseline_and_blocked_alternate_rows() -> None:
    corpus = load_benchmark_corpus()
    backend = FakeSileroBackend()
    baseline_provider = SileroVADProvider(backend=backend)

    rows, recommendation = run_vad_benchmark(
        corpus=corpus,
        baseline_provider=baseline_provider,
        fixture_mode=True,
    )

    audio_items = [item for item in corpus.items if item.modality == "audio"]
    row_dicts = [row.model_dump() for row in rows]

    assert len(rows) == len(audio_items) * 2
    assert all(isinstance(row, BenchmarkCandidateResult) for row in rows)
    assert {row.provider_type for row in rows} == {"vad"}
    assert {row.candidate_id for row in rows} == {"silero-vad", "fireredvad"}
    assert len(backend.calls) == len(audio_items)

    required_fields = {
        "candidate_id",
        "provider_type",
        "provider_name",
        "status",
        "corpus_item_id",
        "stage_timings_ms",
        "total_duration_ms",
        "license_gate",
        "safety_gate",
        "integration_gate",
        "runtime_cost",
        "integration_risk",
        "blocker_reason",
        "next_action",
    }

    for row, row_dict in zip(rows, row_dicts, strict=True):
        assert required_fields.issubset(row_dict)
        assert row.stage_timings_ms.total_wall_ms >= 0
        assert row.total_duration_ms >= 0
        assert row.provider_name in {"silero-vad", "fireredvad"}

    baseline_rows = [row for row in rows if row.candidate_id == "silero-vad"]
    blocked_rows = [row for row in rows if row.candidate_id == "fireredvad"]

    assert baseline_rows
    assert blocked_rows
    assert all(row.status == "passed" for row in baseline_rows)
    assert all(not row.license_gate.blocked for row in baseline_rows)
    assert all(row.blocker_reason is None for row in baseline_rows)
    assert all(row.next_action is None for row in baseline_rows)

    assert all(row.status == "blocked" for row in blocked_rows)
    assert all(row.license_gate.blocked for row in blocked_rows)
    assert all(row.integration_gate.blocked for row in blocked_rows)
    assert all(row.blocker_reason for row in blocked_rows)
    assert all(row.next_action for row in blocked_rows)

    blocked_recommendations = {
        row.candidate_id for row in rows if row.license_gate.blocked
    }
    assert recommendation.studio_default_recommendation not in blocked_recommendations
    assert recommendation.live_conversation_recommendation not in blocked_recommendations
    assert recommendation.studio_default_recommendation == "silero-vad"
    assert recommendation.live_conversation_recommendation == "silero-vad"
