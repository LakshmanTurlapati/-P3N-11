from __future__ import annotations

from datetime import UTC, datetime, timedelta

from services.api.app.schemas.generation import (
    GenerationResult,
    GenerationResultMetadata,
    GenerationRightsCheck,
    GenerationTiming,
    ProviderTraceEntry,
)
from services.api.app.schemas.voice_profile import VoiceProfile

STUB_PROVIDER_TYPE = "metadata-only-stub"


def build_stub_generation_result(profile: VoiceProfile) -> GenerationResult:
    started_at = datetime.now(UTC)
    ended_at = started_at + timedelta(milliseconds=18)

    return GenerationResult(
        provider_type=STUB_PROVIDER_TYPE,
        voice_id=profile.id,
        rights_check=GenerationRightsCheck(
            status="approved",
            approved_for_generation=True,
            message="Rights gate approved the bundled voice profile.",
        ),
        result_metadata=GenerationResultMetadata(
            status="metadata-only",
            summary="Metadata-only stub generation completed without audio playback.",
            artifact_label="Structured studio result card",
            provider_note="Phase 1 keeps the stub provider inline in the API control plane.",
        ),
        provider_trace=[
            ProviderTraceEntry(
                stage="rights-gate",
                provider="server-registry",
                detail="Bundled Vesper Glass profile passed the approval check.",
            ),
            ProviderTraceEntry(
                stage="provider-boundary",
                provider=STUB_PROVIDER_TYPE,
                detail="Speech-worker contracts stay swappable behind the metadata stub.",
            ),
            ProviderTraceEntry(
                stage="result-assembly",
                provider="api-control-plane",
                detail="Returned structured metadata only with no audio payload.",
            ),
        ],
        timing=GenerationTiming(
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=18,
        ),
    )
