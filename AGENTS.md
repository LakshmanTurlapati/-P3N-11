<!-- GSD:project-start source:PROJECT.md -->

## Project

**Theatrical Voice Studio**

Theatrical Voice Studio is a web app for consented voice cloning and speech-to-speech voice generation. The first product direction is a studio-first workflow where an internal user can generate and test a customizable, theatrical trickster-style voice, with live conversation mode included in v1 rather than deferred indefinitely.

The first voice should feel measured, theatrical, charming, icy, philosophical, cynical, and edged with honey-coated sarcasm, but it must be an original voice profile rather than a clone of Marvel's Loki, Tom Hiddleston, or any other unlicensed real performer or protected character voice.

**Core Value:** Users can speak or write an input and receive a high-quality spoken response in a controllable, consented character voice with low enough latency to feel conversational.

### Constraints

- **Voice rights**: Only consented or licensed reference voices may be cloned - this avoids building around unauthorized impersonation.
- **Persona boundary**: The first voice may evoke a theatrical trickster archetype but must not claim to be or exactly sound like Marvel's Loki, Tom Hiddleston, or another protected/unlicensed identity.
- **Deployment**: v1 targets a cloud web app using rented GPU infrastructure - local-only assumptions should not leak into the architecture.
- **Authentication**: v1 is no-login - prioritize the core speech and generation loop over accounts and user libraries.
- **UI scope**: v1 studio controls are minimal - voice, input, tone preset, generate, and live conversation controls are enough for the first proof.
- **Architecture**: Speech components must sit behind provider interfaces - future voices and model swaps should not require rewriting the product.
- **Latency and quality**: v1 must balance conversational latency, voice quality, and future scale instead of optimizing only one dimension.
- **Safety and auditability**: Voice profiles should carry rights/consent metadata before they can be used for generation.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Next.js | 16.2.x stable, verify latest patch during implementation | Web studio UI and lightweight API routes | Current stable React framework with strong support for interactive web apps, server components, and deployment ergonomics. |
| React | 19.2.x | UI components | Current React docs target 19.2; it pairs with current Next.js. |
| TypeScript | Current stable | UI and API type safety | Keeps voice profile, generation job, and provider contract data shapes explicit. |
| FastAPI | 0.138.x | Python backend and speech worker API | Modern Python API framework; suitable for async job orchestration and GPU worker endpoints. |
| Python | 3.10-3.12 for model workers; verify per model | Speech model runtime | Many open speech repos still pin older Python/PyTorch/CUDA ranges; pick the newest version each selected model supports. |
| Pipecat or LiveKit Agents | Current stable | Realtime voice-agent orchestration | Both target realtime voice agents. Pipecat emphasizes composable pipelines and many provider integrations; LiveKit Agents includes STT-LLM-TTS pipelines, turn detection, interruption handling, and WebRTC. |
| faster-whisper | Current stable | Baseline STT | Faster Whisper uses CTranslate2 and reports up to 4x speed improvements over OpenAI Whisper with lower memory use. |
| Silero VAD | Current stable | Baseline speech/silence detection | Small, fast, CPU-friendly VAD. Good default before benchmarking TEN VAD and FireRedVAD. |
| F5-TTS, CosyVoice, OpenVoice | Current model releases | Initial TTS and voice cloning candidates | Cover zero-shot/few-shot voice cloning, voice style control, and open-source experimentation. |
| Object storage | S3-compatible | Generated clip and reference audio storage | Audio artifacts should not live only in app server memory or local disk. |
| PostgreSQL or SQLite first | Current stable | Voice metadata, consent records, jobs | SQLite is enough for no-login local/internal MVP; Postgres becomes preferred before multi-user cloud use. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Web Audio API / MediaRecorder | Browser-native | Mic capture and playback | Required for no-login browser speech input and generated clip playback. |
| WebRTC | Browser-native or LiveKit transport | Low-latency media transport | Use when live conversation mode needs interruption and streaming audio. |
| Celery, Dramatiq, or arq | Current stable | Background GPU jobs | Use once generation latency exceeds normal HTTP request budgets. |
| Pydantic | FastAPI-compatible | Runtime validation | Voice profile, job request, and model provider schemas. |
| PyTorch | Model-compatible | Speech model inference | Required by most open TTS, STT, and speech-to-speech candidates. Pin per selected model. |
| ONNX Runtime | Model-compatible | Lightweight VAD or optimized inference | Useful for Silero VAD and possibly future optimized models. |
| FFmpeg | Current stable | Audio normalization and format conversion | Needed for uploaded reference clips, mic recordings, and generated output normalization. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Docker / Docker Compose | Reproducible app and worker services | Keep GPU worker image separate from web app image. |
| uv | Python dependency management | Good fit for Python services and reproducible lockfiles. |
| pnpm | Frontend package management | Fast, deterministic installs for Next.js apps. |
| Playwright | Browser verification | Needed for microphone permission flows and studio UI smoke tests. |
| pytest | Python tests | Use for provider contract tests, VAD segmentation tests, and job API tests. |

## Installation

# Frontend

# Backend

# Model runtime examples, pin per chosen provider

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Pipecat | LiveKit Agents | Use LiveKit first if WebRTC rooms, interruption handling, and deployed realtime transport are more important than local pipeline flexibility. |
| LiveKit Agents | Pipecat | Use Pipecat first if provider experimentation and Python pipeline composition matter most. |
| Modular STT-LLM-TTS | Chroma, MiniCPM-o, Qwen3-Omni, Moshi end-to-end speech models | Use end-to-end first only if benchmarks show materially lower latency and enough voice/persona control. |
| faster-whisper | OpenAI Whisper reference implementation | Use reference Whisper for compatibility or baseline validation, not for production latency. |
| Silero VAD | TEN VAD or FireRedVAD | Use TEN or FireRed if benchmarking shows lower false turns and better interruption behavior in the target audio conditions. |
| F5-TTS / CosyVoice / OpenVoice | Fish Speech / Step-Audio / Qwen3-TTS | Use if license, quality, streaming behavior, or style control wins the benchmark. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Exact Marvel Loki or Tom Hiddleston voice cloning | Unauthorized impersonation risk and weak product ownership | Original theatrical voice or licensed/consented reference voice |
| One hard-coded speech provider | Model quality and licenses are moving quickly | Provider interface plus benchmark harness |
| Browser-only speech synthesis | Cannot deliver high-quality custom voice cloning | Server-side speech model provider |
| Long synchronous HTTP generation requests | GPU inference can exceed request timeouts and blocks UI feedback | Job model with progress events or streaming responses |
| Saving consent only in prose docs | Future voices need enforceable metadata | Voice profile schema with rights and consent fields |

## Stack Patterns by Variant

- Use Next.js, FastAPI, local SQLite, object storage directory, faster-whisper, Silero VAD, and one TTS provider.
- Because this proves the interaction loop while keeping deployment complexity low.
- Use Next.js app, FastAPI control plane, GPU worker service, Postgres, S3-compatible storage, queue, and WebRTC transport.
- Because generation jobs, reference audio, and live mic sessions need isolation and observability.
- Put that model behind a separate worker image and provider adapter.
- Because open speech repositories often require different CUDA, PyTorch, Python, or license constraints.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| faster-whisper | CUDA 12 / cuDNN 9 for latest CTranslate2 | Official README notes current CTranslate2 CUDA constraints. |
| F5-TTS pretrained weights | CC-BY-NC model license | Code is MIT, but pretrained models are non-commercial due to training data. |
| OpenVoice V2 | MIT license | Commercially friendlier candidate for cloning/style control. |
| Fish Speech | Fish Audio Research License | Review before product use. |
| Step-Audio weights | Separate Hugging Face model licenses | Repository code is Apache 2.0, but model weights require separate license checks. |
| MiniCPM-o 4.5 / Qwen3-Omni / Chroma | Apache 2.0 repos | Still benchmark hosting cost, memory, and output controllability before using as the base. |

## Sources

- https://nextjs.org/docs - Next.js latest docs and version context.
- https://react.dev/versions - React latest version.
- https://fastapi.tiangolo.com/release-notes/ - FastAPI latest release context.
- https://github.com/pipecat-ai/pipecat - Pipecat capabilities, services, and license.
- https://docs.livekit.io/agents/ - LiveKit Agents realtime voice AI capabilities.
- https://github.com/SYSTRAN/faster-whisper - Faster Whisper performance and VAD integration.
- https://github.com/snakers4/silero-vad - Silero VAD speed and footprint.
- https://github.com/ten-framework/ten-vad - TEN VAD claims and realtime frame-level detection.
- https://github.com/FireRedTeam/FireRedVAD - FireRedVAD streaming/non-streaming and 100+ language support.
- https://github.com/SWivid/F5-TTS - F5-TTS license and official implementation.
- https://github.com/FunAudioLLM/CosyVoice - CosyVoice 3.0 model direction.
- https://github.com/myshell-ai/openvoice - OpenVoice cloning, style control, and MIT license.
- https://github.com/fishaudio/fish-speech - Fish Speech model capabilities and license notice.
- https://github.com/FlashLabs-AI-Corp/FlashLabs-Chroma - Chroma end-to-end speech-to-speech.
- https://github.com/OpenBMB/MiniCPM-V - MiniCPM-o 4.5 speech and model license.
- https://github.com/QwenLM/Qwen3-Omni - Qwen3-Omni realtime multimodal speech.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
