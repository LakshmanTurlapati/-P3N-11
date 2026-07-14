from __future__ import annotations

from pathlib import Path

from benchmarks.adapters.tts import run_tts_benchmark
from benchmarks.corpus import load_benchmark_corpus
from benchmarks.schemas import BenchmarkCandidateResult
from providers.contracts import SpeechArtifact, TTSProvider
from providers.cosyvoice_provider import CosyVoiceTTSProvider


class FakeCosyVoiceBackend:
    def __init__(self, sample_rate_hz: int = 24_000) -> None:
        self.sample_rate = sample_rate_hz
        self.calls: list[dict[str, object]] = []

    def inference_zero_shot(
        self,
        text: str,
        prompt_text: str,
        prompt_audio_path: str,
        *,
        stream: bool = False,
    ):
        self.calls.append(
            {
                "text": text,
                "prompt_text": prompt_text,
                "prompt_audio_path": prompt_audio_path,
                "stream": stream,
            }
        )
        sample_count = max(2_400, len(text) * 80)
        yield {"tts_speech": [0.0] * sample_count}


def _build_provider(tmp_path: Path, backend: FakeCosyVoiceBackend) -> CosyVoiceTTSProvider:
    repo_root = tmp_path / "CosyVoice"
    model_dir = repo_root / "pretrained_models" / "Fun-CosyVoice3-0.5B"
    prompt_audio_path = repo_root / "asset" / "zero_shot_prompt.wav"
    return CosyVoiceTTSProvider(
        repo_root=repo_root,
        model_dir=model_dir,
        prompt_audio_path=prompt_audio_path,
        backend=backend,
    )


def test_run_tts_benchmark_emits_baseline_and_blocked_alternate_rows(
    tmp_path: Path,
) -> None:
    corpus = load_benchmark_corpus()
    backend = FakeCosyVoiceBackend()
    baseline_provider = _build_provider(tmp_path, backend)

    rows, recommendation = run_tts_benchmark(
        corpus=corpus,
        baseline_provider=baseline_provider,
        fixture_mode=True,
    )

    text_items = [item for item in corpus.items if item.modality == "text"]
    row_dicts = [row.model_dump() for row in rows]

    assert len(rows) == len(text_items) * 2
    assert all(isinstance(row, BenchmarkCandidateResult) for row in rows)
    assert {row.provider_type for row in rows} == {"tts"}
    assert {row.candidate_id for row in rows} == {
        "cosyvoice",
        "qwen3-tts-12hz-0.6b-customvoice",
    }
    assert len(backend.calls) == len(text_items)

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
        assert row.provider_name in {"cosyvoice", "qwen3-tts"}

    baseline_rows = [row for row in rows if row.candidate_id == "cosyvoice"]
    blocked_rows = [row for row in rows if row.candidate_id == "qwen3-tts-12hz-0.6b-customvoice"]

    assert baseline_rows
    assert blocked_rows
    assert all(row.status == "passed" for row in baseline_rows)
    assert all(not row.license_gate.blocked for row in baseline_rows)
    assert all(row.blocker_reason is None for row in baseline_rows)
    assert all(row.next_action is None for row in baseline_rows)

    assert all(row.status == "blocked" for row in blocked_rows)
    assert all(not row.license_gate.blocked for row in blocked_rows)
    assert all(row.integration_gate.blocked for row in blocked_rows)
    assert all(row.blocker_reason for row in blocked_rows)
    assert all(row.next_action for row in blocked_rows)

    for item, call in zip(text_items, backend.calls, strict=True):
        assert call["text"] == item.text
        assert item.tone in str(call["prompt_text"]).lower()
        assert call["stream"] is False

    blocked_recommendations = {
        row.candidate_id for row in rows if row.license_gate.blocked
    }
    assert recommendation.studio_default_recommendation not in blocked_recommendations
    assert recommendation.live_conversation_recommendation not in blocked_recommendations
    assert recommendation.studio_default_recommendation == "cosyvoice"
    assert recommendation.live_conversation_recommendation == "cosyvoice"
