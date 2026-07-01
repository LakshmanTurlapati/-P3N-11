# Theatrical Voice Studio

## What This Is

Theatrical Voice Studio is a web app for consented voice cloning and speech-to-speech voice generation. The first product direction is a studio-first workflow where an internal user can generate and test a customizable, theatrical trickster-style voice, with live conversation mode included in v1 rather than deferred indefinitely.

The first voice should feel measured, theatrical, charming, icy, philosophical, cynical, and edged with honey-coated sarcasm, but it must be an original voice profile rather than a clone of Marvel's Loki, Tom Hiddleston, or any other unlicensed real performer or protected character voice.

## Core Value

Users can speak or write an input and receive a high-quality spoken response in a controllable, consented character voice with low enough latency to feel conversational.

## Requirements

### Validated

- [x] Phase 1 validated a no-login studio route at `/` with Vesper Glass visible as an original, rights-bounded theatrical profile.
- [x] Phase 1 validated server-owned voice rights metadata, backend approval gating, and metadata-only stub generation before any real synthesis provider is introduced.
- [x] Phase 1 validated typed provider interfaces for VAD, STT, TTS, and speech-to-speech candidates.

### Active

- [ ] Build a cloud-hosted web app MVP for internal experimentation.
- [x] Provide a no-login first version focused on the speech loop and generation workflow.
- [ ] Support a minimal studio workflow: choose a voice, provide text or audio input, choose a tone preset, and generate speech.
- [ ] Include live conversation mode in v1 with microphone input, voice activity detection, interruption handling, and spoken responses.
- [ ] Use only consented or licensed reference voices for cloning.
- [ ] Start with one original theatrical trickster voice profile, then keep the architecture ready for multiple voices.
- [ ] Support customizable tone rather than a single fixed persona prompt.
- [ ] Build around open-source or open-weight speech components where practical, with rented GPU deployment in mind.
- [ ] Benchmark model choices instead of hard-coding the product around a single speech stack too early.

### Out of Scope

- Exact Marvel Loki, Tom Hiddleston, or other unlicensed voice imitation - the product should create an original, ownable voice direction and only clone voices with explicit rights and consent.
- User accounts, persistent user libraries, and saved clip history in the first pass - v1 should stay no-login and focus on proving the speech loop.
- Advanced studio controls such as detailed sliders, batch generation, and A/B comparison in the first UI - start with minimal controls before expanding.
- A pure text-to-speech-only studio with no conversation path - live speech-to-speech interaction is part of the v1 product direction.

## Context

The desired experience is similar in spirit to ElevenLabs: a user can interact with a voicebot or generation surface and hear a convincing, stylized voice response. The product should begin with one carefully designed voice and later scale to a catalog of voices and additional features.

The working product shape is studio-first, not chat-only. The studio should let the user test the voice with text or spoken input and a tone preset. Conversation mode should still be part of v1: the user speaks to the bot, silence/turn detection identifies when to respond, an LLM produces a reply in the selected persona/tone, and TTS or speech-to-speech output returns the voice response.

Initial model strategy should be modular. A practical baseline is a real-time voice-agent framework such as Pipecat or LiveKit, STT through Whisper or faster-whisper, response generation through an LLM, VAD through Silero first with TEN VAD and FireRedVAD benchmarked, and TTS/voice cloning through candidates such as F5-TTS, CosyVoice, OpenVoice, Fish Speech, Step-Audio, or similar open-source systems. End-to-end speech models such as Chroma, MiniCPM-o, Qwen Omni, and Moshi should be treated as benchmark candidates rather than assumed foundations until latency, controllability, hosting cost, and voice quality are tested.

The voice style prompt can describe an original persona with traits such as measured theatrical delivery, polished sarcasm, charm with cold edges, philosophical cynicism, and manipulative logic. It should not instruct the model to impersonate a copyrighted character or a real actor.

## Current State

Phase 1 is complete as of 2026-07-01. The app has a direct no-login studio shell, a server-owned Vesper Glass rights profile, backend rights enforcement, typed speech provider interfaces, and a metadata-only generation result card. Phase 2 starts from that skeleton and adds text input, tone presets, a real generation provider, playback, retry states, and generated-audio metadata.

## Constraints

- **Voice rights**: Only consented or licensed reference voices may be cloned - this avoids building around unauthorized impersonation.
- **Persona boundary**: The first voice may evoke a theatrical trickster archetype but must not claim to be or exactly sound like Marvel's Loki, Tom Hiddleston, or another protected/unlicensed identity.
- **Deployment**: v1 targets a cloud web app using rented GPU infrastructure - local-only assumptions should not leak into the architecture.
- **Authentication**: v1 is no-login - prioritize the core speech and generation loop over accounts and user libraries.
- **UI scope**: v1 studio controls are minimal - voice, input, tone preset, generate, and live conversation controls are enough for the first proof.
- **Architecture**: Speech components must sit behind provider interfaces - future voices and model swaps should not require rewriting the product.
- **Latency and quality**: v1 must balance conversational latency, voice quality, and future scale instead of optimizing only one dimension.
- **Safety and auditability**: Voice profiles should carry rights/consent metadata before they can be used for generation.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build an original theatrical trickster voice, not an exact Loki/Tom Hiddleston clone | The user wants the style and attitude, but the product should avoid unauthorized voice or character impersonation | - Pending |
| Start as a web app | The user selected web app as the first MVP shape | - Pending |
| Make the product studio-first with conversation mode in v1 | The user selected studio-first and live conversation mode as part of v1 | - Pending |
| Deploy on rented cloud GPUs | The user selected cloud web deployment using open-source models | - Pending |
| Require consented/licensed reference voices | The user selected consented/licensed voice references only | - Pending |
| Keep v1 no-login | The user selected a fast no-login demo focused on the speech loop | - Pending |
| Use minimal studio controls in v1 | The user selected minimal studio controls for the first version | - Pending |
| Use a modular benchmark-first model strategy | The user asked the agent to decide; modularity reduces lock-in while still enabling a working baseline | - Pending |
| Keep Phase 1 generation metadata-only | The first vertical skeleton should prove web-to-API shape and rights gating before introducing real synthesis latency, playback, or storage | Implemented in Phase 1 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-01 after Phase 1 completion*
