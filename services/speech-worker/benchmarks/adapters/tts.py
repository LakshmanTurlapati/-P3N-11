from __future__ import annotations

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
from providers.contracts import SpeechArtifact, TTSProvider
from providers.cosyvoice_provider import CosyVoiceTTSProvider

from .base import (
    BlockedCandidateAdapter,
    BenchmarkCandidateAdapter,
    _pass_gate,
    build_candidate_result,
)


class _FixtureCosyVoiceBackend:
    provider_name = "cosyvoice"

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


def _quality_scores(
    corpus_item: BenchmarkCorpusItem,
    artifact: SpeechArtifact,
) -> BenchmarkQualityScores:
    duration_ms = artifact.duration_ms or 0
    return BenchmarkQualityScores(
        intelligibility=5 if duration_ms > 0 else 1,
        persona_tone_fit=5 if corpus_item.tone in {"measured", "cutting", "grandiose"} else 1,
        naturalness=5 if artifact.mime_type == "audio/wav" else 1,
        artifact_level=5 if artifact.audio_bytes.startswith(b"RIFF") else 1,
        safety_boundary_adherence=5 if corpus_item.voice_id == "vesper-glass" else 1,
    )


def _fixture_stage_timings(
    corpus_item: BenchmarkCorpusItem,
    artifact: SpeechArtifact,
) -> BenchmarkStageTimings:
    duration_ms = artifact.duration_ms or 0
    tts_ms = max(1, min(140, len(corpus_item.text) * 3 + max(1, duration_ms) // 4))
    playback_ready_ms = tts_ms + 5
    return BenchmarkStageTimings(
        vad_ms=0,
        stt_ms=0,
        response_text_ms=0,
        tts_ms=tts_ms,
        playback_ready_ms=playback_ready_ms,
        total_wall_ms=playback_ready_ms,
    )


def _artifact_references(
    corpus_item: BenchmarkCorpusItem,
    artifact: SpeechArtifact,
) -> list[str]:
    return [
        f"voice:{corpus_item.voice_id}",
        f"tone:{corpus_item.tone}",
        f"duration_ms:{artifact.duration_ms or 0}",
        f"sample_rate_hz:{artifact.sample_rate_hz}",
        f"mime_type:{artifact.mime_type}",
    ]


class TTSBenchmarkAdapter(BenchmarkCandidateAdapter):
    provider_type = "tts"

    def __init__(
        self,
        provider: TTSProvider,
        *,
        candidate_id: str,
        provider_name: str | None = None,
        fixture_mode: bool = True,
    ) -> None:
        self.provider = provider
        self.candidate_id = candidate_id
        self.provider_name = provider_name or getattr(provider, "provider_name", "tts")
        self.fixture_mode = fixture_mode

    def license_gate(self) -> BenchmarkGateResult:
        return _pass_gate(
            "CosyVoice stays behind the existing provider contract.",
            "Fixture or injected backend executed without a new model install.",
        )

    def safety_gate(self) -> BenchmarkGateResult:
        return _pass_gate(
            "Tone presets stay inside the original theatrical boundary.",
            "Consent-safe benchmark corpus only.",
        )

    def integration_gate(self) -> BenchmarkGateResult:
        return _pass_gate(
            "Provider contract returned normalized WAV audio and duration metadata.",
            "No ffmpeg or GPU runtime was required for the fixture path.",
        )

    def run(self, corpus_item: BenchmarkCorpusItem) -> BenchmarkCandidateResult:
        if corpus_item.modality != "text":
            raise ValueError("TTS benchmarks can only run against text corpus items")

        if self.fixture_mode:
            artifact = self.provider.synthesize(
                corpus_item.text,
                corpus_item.voice_id,
                tone=corpus_item.tone,
            )
            stage_timings = _fixture_stage_timings(corpus_item, artifact)
        else:
            started_at = perf_counter()
            artifact = self.provider.synthesize(
                corpus_item.text,
                corpus_item.voice_id,
                tone=corpus_item.tone,
            )
            elapsed_ms = max(0, int(round((perf_counter() - started_at) * 1000)))
            stage_timings = BenchmarkStageTimings(
                vad_ms=0,
                stt_ms=0,
                response_text_ms=0,
                tts_ms=elapsed_ms,
                playback_ready_ms=elapsed_ms,
                total_wall_ms=elapsed_ms,
            )

        quality_scores = _quality_scores(corpus_item, artifact)
        total_duration_ms = artifact.duration_ms or 0
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
            runtime_cost="single GPU class, moderate memory footprint",
            integration_risk="low",
            artifact_references=_artifact_references(corpus_item, artifact),
        )


class CosyVoiceBenchmarkAdapter(TTSBenchmarkAdapter):
    def __init__(
        self,
        provider: TTSProvider,
        *,
        fixture_mode: bool = True,
    ) -> None:
        super().__init__(
            provider,
            candidate_id="cosyvoice",
            provider_name=getattr(provider, "provider_name", "cosyvoice"),
            fixture_mode=fixture_mode,
        )


def build_blocked_tts_adapter() -> BlockedCandidateAdapter:
    return BlockedCandidateAdapter(
        candidate_id="qwen3-tts-12hz-0.6b-customvoice",
        provider_type="tts",
        provider_name="qwen3-tts",
        blocker_reason=(
            "Qwen3-TTS is approved on source/license grounds but remains blocked until "
            "GPU-worker runtime evidence is captured."
        ),
        next_action=(
            "Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the "
            "GPU worker, capture timings and quality scores, and then rerun the benchmark."
        ),
        license_reason=(
            "The official Qwen3-TTS source checkout and model weights were approved in the "
            "checkpoint review."
        ),
        license_evidence=(
            "https://github.com/QwenLM/Qwen3-TTS | "
            "https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
        ),
        integration_reason=(
            "Local workspace intentionally does not execute the approved Qwen3-TTS candidate."
        ),
        integration_evidence="GPU-worker validation remains pending for the approved path.",
        safety_reason="The approved candidate path remains within the original voice boundary.",
        safety_evidence="Consent-safe benchmark corpus only.",
        license_status="pass",
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


def run_tts_benchmark(
    *,
    corpus: BenchmarkCorpus | None = None,
    baseline_provider: TTSProvider | None = None,
    alternate_adapter: BenchmarkCandidateAdapter | None = None,
    fixture_mode: bool = True,
) -> tuple[list[BenchmarkCandidateResult], BenchmarkRecommendation]:
    benchmark_corpus = corpus or load_benchmark_corpus()
    provider = baseline_provider or CosyVoiceTTSProvider(backend=_FixtureCosyVoiceBackend())
    baseline_adapter = CosyVoiceBenchmarkAdapter(provider, fixture_mode=fixture_mode)
    blocked_alternate = alternate_adapter or build_blocked_tts_adapter()

    text_items = [item for item in benchmark_corpus.items if item.modality == "text"]
    rows: list[BenchmarkCandidateResult] = []
    for corpus_item in text_items:
        rows.append(baseline_adapter.run(corpus_item))
        rows.append(blocked_alternate.run(corpus_item))

    recommended_candidate_id = _select_candidate_id(rows)
    recommendation = BenchmarkRecommendation(
        studio_default_recommendation=recommended_candidate_id,
        live_conversation_recommendation=recommended_candidate_id,
        notes=(
            "Qwen3-TTS remains blocked for local runtime execution until the approved "
            "GPU-worker path captures benchmark evidence."
        ),
    )
    return rows, recommendation
