# Architecture Research

**Domain:** Realtime voice AI web app with studio generation
**Researched:** 2026-06-30
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```text
+-----------------------------------------------------------+
| Web Client                                                |
| Next.js studio UI, mic capture, playback, live session UI |
+-------------------------+---------------------------------+
                          |
                          | HTTPS / WebSocket / WebRTC
                          v
+-----------------------------------------------------------+
| App API / Control Plane                                   |
| Voice registry, consent checks, job API, session API       |
+-------------------------+---------------------------------+
                          |
          +---------------+----------------+
          |                                |
          v                                v
+----------------------+        +--------------------------+
| Metadata Store       |        | Audio Object Store       |
| voices, jobs, rights |        | refs, generated clips    |
+----------------------+        +--------------------------+
          |
          v
+-----------------------------------------------------------+
| GPU Speech Worker Layer                                   |
| Provider adapters: STT, VAD, TTS, S2S, benchmark runner    |
+-------------------------+---------------------------------+
                          |
                          v
+-----------------------------------------------------------+
| Model Backends                                             |
| faster-whisper, Silero/TEN/FireRed, F5/Cosy/OpenVoice,     |
| Chroma/MiniCPM/Qwen/Moshi benchmark candidates             |
+-----------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Web studio | Text/audio input, tone preset, generated playback | Next.js + React |
| Live conversation UI | Mic permission, audio capture, interruption controls | Browser MediaRecorder/Web Audio plus WebRTC or WebSocket |
| App API | Voice profile CRUD, consent enforcement, generation jobs | FastAPI or Next.js API plus Python worker API |
| Provider contracts | Normalize STT, VAD, TTS, and S2S model calls | Python interfaces and typed schemas |
| Speech worker | Runs GPU model inference and audio normalization | Python, PyTorch, FFmpeg, queue worker |
| Benchmark runner | Measures latency, quality notes, stability, and license fit | Python scripts plus stored benchmark records |
| Metadata store | Voice profiles, jobs, generation metadata, rights records | SQLite for internal demo; Postgres for cloud beta |
| Object storage | Reference audio and generated clips | S3-compatible bucket or local storage for dev |

## Recommended Project Structure

```text
apps/
  web/
    app/
      studio/
      conversation/
    components/
    lib/api/
services/
  api/
    app/
      routes/
      schemas/
      voice_registry/
      jobs/
  speech-worker/
    providers/
      stt/
      vad/
      tts/
      s2s/
    benchmarks/
    audio/
packages/
  shared/
    schemas/
    persona/
infra/
  docker/
  deploy/
```

### Structure Rationale

- **apps/web:** Keeps the product UI separate from GPU/model runtime concerns.
- **services/api:** Owns consent checks, voice metadata, and job/session orchestration.
- **services/speech-worker:** Allows fragile model dependencies to live in isolated Python environments.
- **packages/shared:** Keeps request/response schemas and persona presets consistent.
- **infra:** Keeps cloud GPU deployment explicit from the first milestone.

## Architectural Patterns

### Pattern 1: Provider Adapter Boundary

**What:** Each STT, VAD, TTS, and speech-to-speech model implements a common provider contract.
**When to use:** Always, because model choice is unsettled.
**Trade-offs:** Adds interface design upfront but prevents rewriting the app for each model.

```python
class TTSProvider:
    def synthesize(self, request: TTSRequest) -> TTSResult:
        raise NotImplementedError
```

### Pattern 2: Rights-Gated Voice Profiles

**What:** Voice generation requests reference a voice profile that includes consent/license metadata.
**When to use:** Before any real voice cloning.
**Trade-offs:** Adds fields and validation, but keeps the product out of unsafe cloning flows.

```typescript
type VoiceProfile = {
  id: string;
  displayName: string;
  rightsStatus: "original" | "licensed" | "consented";
  approvedForGeneration: boolean;
};
```

### Pattern 3: Thin Vertical Skeleton Before Model Quality Work

**What:** Build UI -> API -> provider interface -> generated audio playback with a stub or simple provider first.
**When to use:** Phase 1.
**Trade-offs:** Early output may not sound impressive, but integration risks surface quickly.

## Data Flow

### Studio Generation Flow

```text
User enters text/audio + tone preset
    -> Web client submits generation request
    -> API validates voice rights and creates job
    -> Speech worker runs STT if needed, then LLM/TTS provider
    -> Audio stored in object storage
    -> API returns job result and playback URL
    -> User plays generated clip
```

### Live Conversation Flow

```text
User opens conversation mode
    -> Browser captures mic stream
    -> VAD segments speech and detects turn end
    -> STT provider transcribes user turn
    -> LLM generates persona-safe response text
    -> TTS provider streams or returns speech audio
    -> Client plays response and allows interruption
```

### Benchmark Flow

```text
Benchmark sample set
    -> Provider adapter under test
    -> Metrics capture: latency, quality notes, errors, cost, license
    -> Benchmark report
    -> Recommended provider selection
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1 internal users | Local SQLite, single GPU worker, local object storage is fine. |
| Internal beta | Add queue, cloud object storage, GPU worker health checks, and benchmark records. |
| External users | Add accounts, per-user libraries, rate limits, billing controls, and abuse monitoring. |

### Scaling Priorities

1. **First bottleneck:** GPU inference latency. Fix with queues, batching where safe, and model-specific worker pools.
2. **Second bottleneck:** Live audio transport. Fix with WebRTC/LiveKit and cancellation-aware pipeline design.
3. **Third bottleneck:** Audio artifact lifecycle. Fix with object storage, retention policy, and metadata indexing.

## Anti-Patterns

### Anti-Pattern 1: Model-Centric App Design

**What people do:** Build directly around one model repo's scripts.
**Why it's wrong:** The UI and product get locked to one dependency stack and license.
**Do this instead:** Wrap each model in a provider adapter.

### Anti-Pattern 2: Treating Consent as a UI Checkbox Only

**What people do:** Ask for consent in UI but do not enforce it server-side.
**Why it's wrong:** Unsafe or unapproved voices can be generated through direct API calls.
**Do this instead:** Enforce `approvedForGeneration` in backend request validation.

### Anti-Pattern 3: Realtime Mode Before Turn Boundaries Work

**What people do:** Stream everything before VAD, buffering, and interruption are reliable.
**Why it's wrong:** Users experience awkward pauses, clipped turns, or overlapping speech.
**Do this instead:** Prove VAD and turn-taking with clear metrics before deep realtime polish.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| GPU host | Worker deployment | Keep model image separate from web app. |
| S3-compatible storage | Signed URLs | Do not serve generated audio only from local disk. |
| LiveKit or WebRTC transport | Session token and stream | Needed if WebSocket audio proves too limited for interruption. |
| LLM provider | Text response adapter | Persona prompt should define original voice style and safety boundary. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Web UI to API | HTTP for studio, WebSocket/WebRTC for live | Keep studio and live flows separate but share voice profiles. |
| API to worker | Queue or internal HTTP | Queue is safer for long generation jobs. |
| Worker to model providers | Local Python calls or subprocess | Isolate incompatible model dependencies if needed. |
| API to storage | Signed URL references | Store metadata separately from audio blobs. |

## Sources

- https://github.com/pipecat-ai/pipecat - Realtime voice and multimodal pipeline patterns.
- https://docs.livekit.io/agents/ - Realtime voice SDK handles STT-LLM-TTS, turn detection, interruptions.
- https://github.com/SYSTRAN/faster-whisper - STT and VAD integration considerations.
- https://github.com/myshell-ai/openvoice - Voice style control candidate.
- https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma - End-to-end spoken dialogue candidate.
- https://github.com/OpenBMB/MiniCPM-V - Full-duplex and speech generation benchmark candidate.
- https://github.com/QwenLM/Qwen3-Omni - Realtime natural speech generation candidate.

---
*Architecture research for: Theatrical Voice Studio*
*Researched: 2026-06-30*
