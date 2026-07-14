from __future__ import annotations

from pathlib import Path

from benchmarks.corpus import BenchmarkCorpus, REPORTS_DIR, load_benchmark_corpus
from benchmarks.reporting import write_benchmark_report
from benchmarks.schemas import BenchmarkCandidateResult, BenchmarkRecommendation
from providers.contracts import TTSProvider, VADProvider

from .tts import run_tts_benchmark
from .vad import run_vad_benchmark


def run_provider_benchmarks(
    *,
    corpus: BenchmarkCorpus | None = None,
    vad_provider: VADProvider | None = None,
    tts_provider: TTSProvider | None = None,
    vad_alternate_adapter=None,
    tts_alternate_adapter=None,
    fixture_mode: bool = True,
    output_dir: str | Path | None = None,
) -> tuple[list[BenchmarkCandidateResult], BenchmarkRecommendation]:
    benchmark_corpus = corpus or load_benchmark_corpus()

    vad_rows, vad_recommendation = run_vad_benchmark(
        corpus=benchmark_corpus,
        baseline_provider=vad_provider,
        alternate_adapter=vad_alternate_adapter,
        fixture_mode=fixture_mode,
    )
    tts_rows, tts_recommendation = run_tts_benchmark(
        corpus=benchmark_corpus,
        baseline_provider=tts_provider,
        alternate_adapter=tts_alternate_adapter,
        fixture_mode=fixture_mode,
    )

    combined_rows = [*vad_rows, *tts_rows]
    recommendation = BenchmarkRecommendation(
        studio_default_recommendation=tts_recommendation.studio_default_recommendation,
        live_conversation_recommendation=vad_recommendation.live_conversation_recommendation,
        notes=(
            "Studio generation follows the runnable CosyVoice baseline while live "
            "conversation follows the runnable Silero VAD baseline. FireRedVAD stays "
            "blocked until package legitimacy and GPU-worker validation are confirmed, "
            "and Qwen3-TTS stays blocked until the approved GPU-worker path is exercised."
        ),
    )

    write_benchmark_report(
        combined_rows,
        recommendation,
        output_dir=output_dir or REPORTS_DIR,
    )
    return combined_rows, recommendation
