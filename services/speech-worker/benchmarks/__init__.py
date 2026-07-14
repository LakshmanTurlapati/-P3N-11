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
from .recommendation import (
    CURRENT_LIVE_CONVERSATION_DEFAULT,
    CURRENT_STUDIO_DEFAULT,
    RecommendationDecision,
    build_provider_recommendation,
    should_switch_default_provider,
)
from .reporting import write_benchmark_report
from .s2s_findings import SpeechToSpeechFinding, SpeechToSpeechScan, build_s2s_findings
from .schemas import BenchmarkCorpus, BenchmarkCorpusItem

__all__ = [
    "BenchmarkAdapterStatus",
    "BenchmarkCandidateAdapter",
    "BlockedCandidateAdapter",
    "BenchmarkCorpus",
    "BenchmarkCorpusItem",
    "CosyVoiceBenchmarkAdapter",
    "FIXTURES_DIR",
    "CURRENT_LIVE_CONVERSATION_DEFAULT",
    "CURRENT_STUDIO_DEFAULT",
    "MANIFEST_PATH",
    "REPORTS_DIR",
    "RUNS_DIR",
    "RecommendationDecision",
    "SileroVADBenchmarkAdapter",
    "SpeechToSpeechFinding",
    "SpeechToSpeechScan",
    "TTSBenchmarkAdapter",
    "VADBenchmarkAdapter",
    "build_provider_recommendation",
    "build_s2s_findings",
    "should_switch_default_provider",
    "run_provider_benchmarks",
    "run_tts_benchmark",
    "run_vad_benchmark",
    "load_benchmark_corpus",
    "write_benchmark_report",
]


def package_root() -> Path:
    return Path(__file__).resolve().parent
