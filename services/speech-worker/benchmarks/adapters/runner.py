from __future__ import annotations

from pathlib import Path

from benchmarks.corpus import BenchmarkCorpus, REPORTS_DIR, load_benchmark_corpus
from benchmarks.recommendation import build_provider_recommendation
from benchmarks.reporting import write_benchmark_report
from benchmarks.s2s_findings import build_s2s_findings
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
    s2s_scan = build_s2s_findings()
    s2s_rows = s2s_scan.candidate_rows()

    combined_rows = [*vad_rows, *tts_rows, *s2s_rows]
    recommendation = build_provider_recommendation(
        vad_rows=vad_rows,
        tts_rows=tts_rows,
        s2s_scan=s2s_scan,
    )

    write_benchmark_report(
        combined_rows,
        recommendation,
        output_dir=output_dir or REPORTS_DIR,
        s2s_scan=s2s_scan,
    )
    return combined_rows, recommendation
