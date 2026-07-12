from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from services.api.app.schemas.generation import (
    GenerationJobStatus,
    GenerationResult,
    GenerationRightsCheck,
    GenerationRequest,
    GenerationTiming,
    ProviderTraceEntry,
)
from services.api.app.schemas.voice_profile import VoiceProfile

STUB_PROVIDER_TYPE = "prototype-baseline-stub"


def build_stub_generation_result(
    profile: VoiceProfile,
    request: GenerationRequest,
) -> GenerationResult:
    started_at = datetime.now(UTC)
    ended_at = started_at + timedelta(milliseconds=18)

    return GenerationResult(
        provider_type=STUB_PROVIDER_TYPE,
        job_id=f"job-{uuid4().hex[:12]}",
        status=GenerationJobStatus.QUEUED,
        voice_id=profile.id,
        text=request.text,
        tone_preset=request.tone_preset,
        rights_check=GenerationRightsCheck(
            status="approved",
            approved_for_generation=True,
            message="Rights gate approved the bundled voice profile.",
        ),
        provider_trace=[
            ProviderTraceEntry(
                stage="rights-gate",
                provider="server-registry",
                detail="Bundled Vesper Glass profile passed the approval check.",
            ),
            ProviderTraceEntry(
                stage="job-queue",
                provider="api-control-plane",
                detail="Queued a prototype baseline job with the submitted text and tone preset.",
            ),
            ProviderTraceEntry(
                stage="provider-boundary",
                provider=STUB_PROVIDER_TYPE,
                detail="Speech-worker contracts stay swappable behind the prototype baseline stub.",
            ),
        ],
        timing=GenerationTiming(
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=18,
        ),
    )
