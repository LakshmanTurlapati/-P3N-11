from __future__ import annotations

from pathlib import Path

from .corpus import FIXTURES_DIR, MANIFEST_PATH, REPORTS_DIR, RUNS_DIR, load_benchmark_corpus
from .adapters import (
    BenchmarkAdapterStatus,
    BenchmarkCandidateAdapter,
    BlockedCandidateAdapter,
    CosyVoiceBenchmarkAdapter,
    SileroVADBenchmarkAdapter,
    TTSBenchmarkAdapter,
    VADBenchmarkAdapter,
    run_provider_benchmarks,
    run_tts_benchmark,
    run_vad_benchmark,
)
from .reporting import write_benchmark_report
from .schemas import BenchmarkCorpus, BenchmarkCorpusItem

__all__ = [
    "BenchmarkAdapterStatus",
    "BenchmarkCandidateAdapter",
    "BlockedCandidateAdapter",
    "BenchmarkCorpus",
    "BenchmarkCorpusItem",
    "CosyVoiceBenchmarkAdapter",
    "FIXTURES_DIR",
    "MANIFEST_PATH",
    "REPORTS_DIR",
    "RUNS_DIR",
    "SileroVADBenchmarkAdapter",
    "TTSBenchmarkAdapter",
    "VADBenchmarkAdapter",
    "run_provider_benchmarks",
    "run_tts_benchmark",
    "run_vad_benchmark",
    "load_benchmark_corpus",
    "write_benchmark_report",
]


def package_root() -> Path:
    return Path(__file__).resolve().parent
