# Project Research Summary

**Project:** Theatrical Voice Studio
**Domain:** Consented voice cloning and speech-to-speech voice studio
**Researched:** 2026-06-30
**Confidence:** MEDIUM

## Executive Summary

The product should be built as a modular realtime voice web app, not as a thin wrapper around one speech model. The safest and most durable approach is a Next.js studio UI, a Python API/control plane, isolated GPU speech workers, and provider interfaces for VAD, STT, TTS, and end-to-end speech-to-speech candidates.

The first working milestone should prove a vertical path from web input to generated audio playback while enforcing consent/license metadata on voice profiles. Live conversation can then build on the same voice registry and provider contracts by adding mic capture, VAD, STT, LLM response generation, TTS, and interruption handling.

The main risks are unauthorized impersonation, model lock-in, realtime latency, and licensing surprises. These should be handled by defining the first voice as an original theatrical archetype, requiring rights metadata for all cloned voices, benchmarking model candidates with repeatable samples, and isolating model runtimes behind adapters.

## Key Findings

### Recommended Stack

Use a split web/API/worker architecture. Next.js and React should own the no-login studio and live conversation UI. FastAPI/Python should own voice profile validation, job/session APIs, and speech workers. Pipecat or LiveKit Agents should be evaluated for the realtime pipeline because both are designed for voice agents; LiveKit is especially relevant where WebRTC, turn detection, and interruption handling are central.

**Core technologies:**
- Next.js and React: studio UI, conversation UI, and internal web app shell.
- FastAPI and Python: backend API, provider contracts, GPU worker orchestration.
- Pipecat or LiveKit Agents: realtime voice-agent orchestration.
- faster-whisper: first STT baseline.
- Silero VAD: first VAD baseline; benchmark TEN VAD and FireRedVAD.
- F5-TTS, CosyVoice, and OpenVoice: first TTS/voice cloning candidates.
- Chroma, MiniCPM-o, Qwen3-Omni, and Moshi: end-to-end speech-to-speech benchmark candidates.

### Expected Features

**Must have (table stakes):**
- Consent/license metadata for every voice profile.
- One original theatrical voice profile.
- Text input to generated speech.
- Tone preset selection.
- Audio playback and generation status.
- Mic input, VAD, STT, and spoken response for conversation mode.
- Provider abstraction for model swapping.

**Should have (competitive):**
- Interruption-aware live conversation.
- Benchmark records for voice quality, latency, GPU cost, and license fit.
- Multi-voice-ready registry even while only one voice ships.

**Defer (v2+):**
- User accounts and saved personal libraries.
- Detailed tone sliders.
- Batch generation.
- Public API.

### Architecture Approach

Build a thin vertical skeleton first: web UI -> API -> voice rights check -> provider adapter -> generated audio playback. Then replace the stub/simple provider with real TTS, add audio input and VAD, and finally add live conversation. Keep model workers isolated so F5-TTS, CosyVoice, OpenVoice, Fish Speech, Step-Audio, Qwen, MiniCPM, or Chroma experiments do not destabilize the core app.

**Major components:**
1. Web studio and conversation client - input, mic capture, playback, and controls.
2. App API/control plane - voice registry, consent checks, jobs, sessions.
3. Speech worker - STT, VAD, TTS, and end-to-end model adapters.
4. Audio/object storage - reference clips and generated outputs.
5. Benchmark harness - repeatable model evaluation and selection.

### Critical Pitfalls

1. **Unauthorized impersonation** - avoid by using original voice profiles or consented/licensed references only.
2. **Model lock-in** - avoid with provider interfaces and benchmark-driven selection.
3. **Realtime latency** - avoid by measuring full user-turn-to-audio latency and tuning VAD/interruption.
4. **Subjective model choice** - avoid with fixed benchmark prompts and saved output comparisons.
5. **GPU dependency conflicts** - avoid by isolating model workers.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: No-Login Vertical Skeleton
**Rationale:** Prove the web/API/audio playback path and consent model before real model complexity.
**Delivers:** Studio shell, voice registry, rights-gated voice profile, provider contracts, stub/generated sample audio.
**Addresses:** Product shell, consent metadata, provider abstraction.
**Avoids:** Unauthorized voice use and model lock-in.

### Phase 2: Consented Studio Generation
**Rationale:** Text-to-speech studio output is the simplest useful voice-generation loop.
**Delivers:** First real TTS provider, tone presets, generation jobs, playback.
**Uses:** FastAPI worker, TTS provider adapter, object storage.
**Implements:** Studio workflow.

### Phase 3: Audio Input and Turn Detection
**Rationale:** Speech-to-speech requires robust input before live conversation.
**Delivers:** Mic/audio input, VAD baseline, STT baseline, segmentation metrics.
**Uses:** Web Audio/MediaRecorder, faster-whisper, Silero VAD.

### Phase 4: Live Conversation Mode
**Rationale:** Combines the validated components into the voicebot behavior the user asked for.
**Delivers:** Turn-based or streaming conversation, persona-safe LLM response, spoken output, interruption.
**Implements:** Speech-to-speech interaction.

### Phase 5: Model Benchmark and Selection
**Rationale:** Quality, latency, license, and cost need evidence before scaling voices.
**Delivers:** Benchmark harness and recommendation across VAD, TTS, and end-to-end candidates.
**Uses:** F5-TTS, CosyVoice, OpenVoice, Fish Speech, Qwen3-TTS, Chroma, MiniCPM-o, Qwen3-Omni, Moshi as candidates where feasible.

### Phase 6: Cloud GPU Deployment and Internal Beta Hardening
**Rationale:** The target is cloud web app on rented GPUs, not local scripts.
**Delivers:** Deployable services, worker health checks, storage, basic observability, safety enforcement.
**Implements:** Cloud-ready internal demo.

### Phase Ordering Rationale

- Consent and provider contracts must come before real voice generation.
- Studio generation should precede live conversation because it validates output quality with fewer moving parts.
- Audio input and VAD should precede live conversation because turn-taking is its own risk.
- Model benchmarking should happen after at least one baseline works, so comparisons use the app's real provider contracts.
- Cloud hardening should come after the full loop exists, so deployment work targets the real architecture.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** TTS provider install/runtime/license details.
- **Phase 3:** VAD thresholds and browser audio capture behavior.
- **Phase 4:** Pipecat vs LiveKit transport decision.
- **Phase 5:** Benchmark methodology and candidate model compatibility.
- **Phase 6:** Rented GPU deployment target and cost controls.

Phases with standard patterns:
- **Phase 1:** Web/API skeleton, provider interface, and metadata model are established patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Official docs support the candidates, but exact model runtime compatibility needs implementation-time verification. |
| Features | HIGH | User decisions plus standard voice studio/conversation expectations are clear. |
| Architecture | MEDIUM | Modular app/worker architecture is clear; Pipecat vs LiveKit should be decided by prototype. |
| Pitfalls | HIGH | Voice rights, lock-in, latency, and dependency conflicts are predictable risks. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **Provider choice:** Benchmark real TTS/VAD/S2S candidates before committing to one.
- **GPU host:** Pick a rented GPU target during deployment planning.
- **Voice reference source:** Need consented/licensed audio or an original synthetic seed before real cloning.
- **Latency targets:** Define acceptable end-to-end latency during Phase 4 planning.

## Sources

### Primary (HIGH confidence)

- https://github.com/pipecat-ai/pipecat - Realtime voice and multimodal agent framework.
- https://docs.livekit.io/agents/ - Realtime voice agent SDK, turn detection, interruptions, STT-LLM-TTS.
- https://github.com/SYSTRAN/faster-whisper - STT baseline, performance, VAD filter.
- https://github.com/snakers4/silero-vad - VAD speed and footprint.
- https://github.com/ten-framework/ten-vad - Realtime VAD alternative.
- https://github.com/FireRedTeam/FireRedVAD - VAD/AED alternative and benchmark claims.
- https://github.com/SWivid/F5-TTS - TTS candidate and license note.
- https://github.com/FunAudioLLM/CosyVoice - TTS candidate.
- https://github.com/myshell-ai/openvoice - Voice cloning/style control candidate.
- https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma - End-to-end spoken dialogue candidate.
- https://github.com/OpenBMB/MiniCPM-V - MiniCPM-o 4.5 speech candidate.
- https://github.com/QwenLM/Qwen3-Omni - Qwen3-Omni speech candidate.

### Secondary (MEDIUM confidence)

- https://github.com/fishaudio/fish-speech - Strong TTS candidate with nonstandard research license.
- https://github.com/stepfun-ai/Step-Audio - Speech interaction and TTS candidate; repo notes maintenance moved to newer Step-Audio projects.
- https://github.com/kyutai-labs/moshi - Full-duplex speech-text framework candidate.
- https://github.com/Plachtaa/seed-vc - Real-time voice conversion candidate, GPL-3.0 license.

---
*Research completed: 2026-06-30*
*Ready for roadmap: yes*
