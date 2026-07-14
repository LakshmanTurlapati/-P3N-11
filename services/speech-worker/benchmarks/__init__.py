from __future__ import annotations

from pathlib import Path

from .corpus import FIXTURES_DIR, MANIFEST_PATH, REPORTS_DIR, RUNS_DIR, load_benchmark_corpus
from .schemas import BenchmarkCorpus, BenchmarkCorpusItem

__all__ = [
    "BenchmarkCorpus",
    "BenchmarkCorpusItem",
    "FIXTURES_DIR",
    "MANIFEST_PATH",
    "REPORTS_DIR",
    "RUNS_DIR",
    "load_benchmark_corpus",
]


def package_root() -> Path:
    return Path(__file__).resolve().parent
