# Pitfalls Research

**Domain:** Consented voice cloning and realtime speech-to-speech web app
**Researched:** 2026-06-30
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Unauthorized Voice or Character Impersonation

**What goes wrong:**
The product starts by cloning a known character or actor voice and becomes legally and ethically fragile before the technical MVP is even validated.

**Why it happens:**
It is tempting to optimize for a recognizable demo instead of an ownable voice direction.

**How to avoid:**
Require voice profile rights metadata, block unapproved profiles in the backend, and define the first voice as an original theatrical archetype.

**Warning signs:**
Prompts or UI copy say "Loki voice", "Tom voice", or "sounds exactly like" rather than describing original voice traits.

**Phase to address:**
Phase 1.

---

### Pitfall 2: Model Lock-In Before Benchmarks

**What goes wrong:**
The app couples its UI, API, and audio formats to one model repository, then quality, license, latency, or GPU cost forces a rewrite.

**Why it happens:**
Open voice demos often ship with one-off scripts that are faster to copy than to adapt cleanly.

**How to avoid:**
Define provider interfaces first and test multiple TTS, VAD, STT, and end-to-end candidates against the same sample set.

**Warning signs:**
Frontend code imports model-specific concepts, or generation job schema only fits one provider.

**Phase to address:**
Phases 1, 2, and 5.

---

### Pitfall 3: Realtime Conversation Feels Slow or Awkward

**What goes wrong:**
The product technically responds, but turn detection, STT, LLM, and TTS latency make conversation feel broken.

**Why it happens:**
Teams measure model quality in isolation instead of end-to-end time from user speech end to audible response.

**How to avoid:**
Track end-to-end latency, time to first audio, interruption success, VAD false starts, and clipped speech from the beginning.

**Warning signs:**
Good clip quality but no measured conversation latency, or frequent "sorry, I missed that" behavior.

**Phase to address:**
Phases 3 and 4.

---

### Pitfall 4: Voice Quality Tests Are Purely Subjective

**What goes wrong:**
Model selection changes based on whichever sample sounded best most recently.

**Why it happens:**
Voice quality is hard to automate and demos can be cherry-picked.

**How to avoid:**
Use a fixed prompt/reference sample set, record latency and failures, and add human notes with repeatable rubrics.

**Warning signs:**
No saved benchmark inputs, no generated outputs kept for comparison, and no license column.

**Phase to address:**
Phase 5.

---

### Pitfall 5: GPU Worker Dependency Conflicts

**What goes wrong:**
One model requires a CUDA/Python/PyTorch stack that breaks another model.

**Why it happens:**
Speech model repos often pin dependencies tightly and may not share runtime assumptions.

**How to avoid:**
Run model providers in isolated worker images when necessary and keep the app API model-agnostic.

**Warning signs:**
One requirements file tries to install every candidate model at once.

**Phase to address:**
Phases 2 and 6.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Stub audio provider | Fast vertical skeleton | No real quality validation | Acceptable in Phase 1 only |
| Local filesystem audio storage | Simple development | Breaks cloud deployment and sharing | Acceptable before Phase 6 |
| Hard-coded first voice | Faster UI | Slows multi-voice expansion | Acceptable only behind voice registry |
| Manual benchmark notes | Fast first comparison | Harder trend analysis | Acceptable before benchmark schema exists |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| VAD | Treating silence detection as binary and universal | Tune thresholds and compare on target mic/noise conditions |
| STT | Waiting for full audio file before transcription | Use chunked or streaming strategy when conversation latency matters |
| TTS | Ignoring license differences between code and weights | Track model code license and model weight license separately |
| Web mic | Building without permission/error states | Treat permission denial and unavailable devices as first-class UI states |
| GPU deployment | Shipping the web app and models in one image | Separate web, API, and worker images |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Synchronous generation | UI spinner hangs or request times out | Use job IDs, progress, and cancellation | Any slow TTS or cold GPU |
| Over-aggressive VAD | User gets cut off mid-sentence | Tune min speech/silence durations and keep pre-roll | Normal conversational pauses |
| Under-aggressive VAD | Bot waits too long to respond | Benchmark end-of-turn latency | Live conversation mode |
| Cold model loads | First generation is extremely slow | Warm workers and expose readiness checks | Cloud GPU deployment |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Accepting untracked reference audio | Unauthorized voice use | Require voice profile rights metadata |
| Returning raw storage paths | Artifact leakage | Use signed URLs or controlled serving |
| No rate limits in cloud beta | GPU cost abuse | Add limits before external access |
| Logging full audio/transcripts carelessly | Privacy exposure | Redact or make retention explicit |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No feedback during generation | User thinks the app froze | Show job state and allow retry |
| Persona text explains itself in-app | Feels like a prompt editor, not a product | Use concise tone presets and keep prompt details behind settings |
| Live mode overlaps user speech | User loses trust quickly | Add interruption and clear speaking/listening states |
| Tone presets do not audibly differ | Controls feel fake | Benchmark presets with fixed test lines |

## "Looks Done But Isn't" Checklist

- [ ] **Voice profile:** Has rights metadata and backend enforcement, not just a label.
- [ ] **Studio generation:** Handles errors, loading, retry, playback, and audio storage.
- [ ] **VAD:** Tested on pauses, background noise, and short utterances.
- [ ] **Conversation:** Measures end-to-end latency and interruption behavior.
- [ ] **Model selection:** Includes license, GPU memory, and latency, not only output quality.
- [ ] **Cloud deployment:** Has health checks and warm model strategy.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Unauthorized voice direction | HIGH | Rename voice, remove unsafe prompts/samples, add consent gate, regenerate outputs |
| Model lock-in | HIGH | Extract provider interface, migrate current provider behind adapter, add tests |
| Bad realtime latency | MEDIUM | Profile each stage, tune VAD, stream TTS where possible, reduce model size |
| Dependency conflict | MEDIUM | Split worker images and use provider service boundary |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Unauthorized voice use | Phase 1 | Generation is blocked unless voice profile is approved |
| Model lock-in | Phase 1 and 2 | Provider contracts exist and at least one provider implementation uses them |
| Realtime latency | Phase 3 and 4 | Conversation metrics recorded for sample turns |
| Subjective model choice | Phase 5 | Benchmark report compares candidates with fixed inputs |
| Dependency conflicts | Phase 6 | Worker deployment isolates model runtime |

## Sources

- https://github.com/SWivid/F5-TTS - Code vs pretrained model license distinction.
- https://github.com/myshell-ai/openvoice - Voice cloning and style control claims.
- https://github.com/fishaudio/fish-speech - Research license and legal disclaimer.
- https://github.com/SYSTRAN/faster-whisper - STT/VAD integration and CUDA constraints.
- https://github.com/snakers4/silero-vad - VAD speed and ONNX/JIT footprint.
- https://github.com/ten-framework/ten-vad - Low-latency VAD claims.
- https://github.com/FireRedTeam/FireRedVAD - VAD/AED support and benchmark claims.
- https://docs.livekit.io/agents/ - Turn detection and interruption as core realtime voice concerns.

---
*Pitfalls research for: Theatrical Voice Studio*
*Researched: 2026-06-30*
