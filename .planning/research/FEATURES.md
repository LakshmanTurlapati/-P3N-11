# Feature Research

**Domain:** Consented voice cloning and speech-to-speech voice studio
**Researched:** 2026-06-30
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Voice profile selection | A voice product needs a chosen output voice | LOW | Start with one original voice but model the data for many. |
| Consent/license metadata | Voice cloning without rights tracking is unsafe | MEDIUM | Require source, owner, usage scope, and approval status. |
| Text input to speech | Baseline ElevenLabs-like studio behavior | MEDIUM | First generation path should be reliable before realtime mode. |
| Audio input to speech response | User asked for speech-to-speech | HIGH | Needs mic capture, upload/streaming, STT or speech model, and TTS. |
| Tone preset control | User wants customizable tone | MEDIUM | Start with presets, defer sliders. |
| Generated audio playback | Users must hear and evaluate outputs | LOW | Include visible loading, playback, and retry. |
| VAD/turn detection | Live conversation needs silence detection | MEDIUM | Benchmark Silero, TEN VAD, and FireRedVAD. |
| Provider abstraction | Speech model choices are uncertain | MEDIUM | Interface around STT, VAD, TTS, and end-to-end candidates. |
| Basic safety boundary | Product must not impersonate unlicensed people/characters | MEDIUM | UI and backend should enforce voice profile rights checks. |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Original theatrical persona controls | Ownable voice direction, not a legally fragile clone | MEDIUM | Use tone presets and persona prompts. |
| Live conversation with interruption | Feels more like a voicebot than clip generation | HIGH | Requires careful transport, VAD, buffering, and cancellation. |
| Open-source model benchmark dashboard | Lets the product improve as models change | HIGH | Capture latency, quality notes, license, GPU cost, and stability. |
| Multi-voice-ready architecture | Enables future voice catalog | MEDIUM | Voice registry and provider adapters from day one. |
| End-to-end model bakeoff | May reduce latency or improve expressiveness later | HIGH | Benchmark Chroma, MiniCPM-o, Qwen3-Omni, and Moshi after modular baseline. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Exact celebrity or character clone | Seems like a fast wow demo | Legal, ethical, and platform trust risk | Original archetype or licensed/consented voice |
| Full account system in v1 | Feels product-like | Slows core speech validation | No-login internal demo first |
| Dozens of tone sliders immediately | Looks powerful | Hard to validate and tune before model behavior is known | Small set of tone presets |
| Single model lock-in | Simpler implementation | Model licenses, quality, and latency can change fast | Provider interface and benchmark suite |
| Batch generation in v1 | Useful for creators | Not needed for internal speech-loop validation | Add after studio loop works |

## Feature Dependencies

```text
Consent metadata
    requires -> Voice profile registry
        enables -> Studio generation
        enables -> Live conversation

Provider interfaces
    enables -> TTS provider swap
    enables -> VAD benchmark
    enables -> End-to-end model benchmark

Mic capture
    requires -> VAD/turn detection
        requires -> STT or speech-understanding provider
            enables -> Conversation response

Tone presets
    enhances -> Studio generation
    enhances -> Conversation response
```

### Dependency Notes

- **Voice profile registry requires consent metadata:** A voice should not be usable unless its rights status is known.
- **Studio generation requires at least one TTS provider:** Conversation can reuse this output provider later.
- **Conversation requires mic capture, VAD, STT, LLM, and TTS:** Build these incrementally, not as one untestable block.
- **Benchmarking requires provider interfaces:** Otherwise every model test becomes a rewrite.

## MVP Definition

### Launch With (v1)

- [ ] No-login web app shell - fastest path for internal experimentation.
- [ ] One original theatrical voice profile with consent-safe metadata - proves voice catalog shape.
- [ ] Text-to-speech studio generation with tone preset - proves core output quality.
- [ ] Audio input path with VAD and STT - proves speech-to-speech input.
- [ ] Live conversation mode with interruption handling - proves voicebot behavior.
- [ ] Provider abstraction and benchmark records - prevents early model lock-in.
- [ ] Cloud GPU deployment path - matches intended deployment environment.

### Add After Validation (v1.x)

- [ ] Saved clip history - add when generated outputs are worth keeping.
- [ ] Detailed tone sliders - add after preset behavior is measurable.
- [ ] Additional consented voices - add once first voice workflow is sound.
- [ ] A/B model comparison UI - add after benchmark harness exists.

### Future Consideration (v2+)

- [ ] User accounts and libraries - needed for external users, not internal v1.
- [ ] Team voice approvals - useful when many licensed voices exist.
- [ ] Batch generation - useful for creator workflows.
- [ ] Public API - useful once the provider contracts stabilize.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| No-login web shell | HIGH | LOW | P1 |
| Consent metadata | HIGH | MEDIUM | P1 |
| Text-to-speech studio | HIGH | MEDIUM | P1 |
| Tone presets | HIGH | MEDIUM | P1 |
| Mic capture and VAD | HIGH | MEDIUM | P1 |
| Live conversation loop | HIGH | HIGH | P1 |
| Benchmark harness | MEDIUM | HIGH | P1 |
| Saved history | MEDIUM | MEDIUM | P2 |
| Multi-voice catalog | HIGH | MEDIUM | P2 |
| Accounts | MEDIUM | HIGH | P3 |
| Batch generation | MEDIUM | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | ElevenLabs-style products | Open-source voice agent frameworks | Our Approach |
|---------|---------------------------|------------------------------------|--------------|
| Voice generation studio | Strong text-to-speech and voice management | Usually not productized | Minimal studio first, then expand. |
| Voice cloning | Strong closed-source quality | Model quality varies by project | Use consented voices and benchmark candidates. |
| Live conversation | Offered by some commercial tools | Pipecat/LiveKit provide orchestration | Build a modular live mode with provider adapters. |
| Tone/persona control | Often prompt or style based | Depends on model | Start with tone presets and enforce original persona boundary. |
| Model transparency | Low | High | Use research docs and benchmark records as product assets. |

## Sources

- https://github.com/pipecat-ai/pipecat - Voice-agent pipeline and provider ecosystem.
- https://docs.livekit.io/agents/ - Turn detection, interruption, and STT-LLM-TTS pipeline support.
- https://github.com/myshell-ai/openvoice - Tone color cloning and style control.
- https://github.com/FunAudioLLM/CosyVoice - Zero-shot multilingual TTS and prosody direction.
- https://github.com/SWivid/F5-TTS - Zero-shot TTS candidate and license constraint.
- https://github.com/SYSTRAN/faster-whisper - STT baseline and VAD integration.
- https://github.com/snakers4/silero-vad - Baseline VAD.
- https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma - End-to-end speech-to-speech benchmark candidate.

---
*Feature research for: Theatrical Voice Studio*
*Researched: 2026-06-30*
