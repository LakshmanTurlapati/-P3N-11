# Phase 3: Audio Input and Turn Detection - Research

**Researched:** 2026-07-03
**Domain:** Browser audio capture, VAD/STT provider pipeline, transcript review
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Add spoken-input controls beside the current generation text composer instead of creating a separate page or hiding text/audio behind a mode switcher.
- **D-02:** The spoken-input controls should support manual Record and Stop actions plus uploaded audio files.
- **D-03:** Stopping a recording or selecting an upload should automatically create an audio-turn job and run VAD plus STT. Do not require a separate Transcribe click.
- **D-04:** Captured audio should be stored as a session-scoped job artifact through the existing local object-store pattern. Do not add a durable audio library or page-refresh restoration in Phase 3.
- **D-05:** Audio capture must include first-class browser states for mic permission denial, unavailable devices, recording in progress, upload validation, queued/running transcription, success, and failure.
- **D-06:** Run VAD over the stopped recording or uploaded clip after capture, then treat the best combined speech region as one turn for transcription.
- **D-07:** Keep the first turn model lenient for the internal MVP: if VAD finds any meaningful speech segment, continue to STT and show short/low-confidence warnings instead of blocking aggressively.
- **D-08:** Use a Silero or Silero-compatible baseline behind the existing `VADProvider` interface, with deterministic fixture/stub fallback for local tests.
- **D-09:** Leave TEN VAD, FireRedVAD, and multi-provider VAD comparisons to Phase 5 benchmark work.
- **D-10:** Show compact VAD metadata near the transcript: provider name, segment start/end, speech duration, and confidence when available. Do not build a detailed VAD debug dashboard in Phase 3.
- **D-11:** Show STT output in an editable transcript review field. The transcript should not overwrite the generation text until the user chooses to use it.
- **D-12:** Provide a clear action to use the reviewed transcript as the generation text for the existing text-to-speech flow.
- **D-13:** Use a faster-whisper-compatible STT baseline behind the existing `STTProvider` interface, with deterministic fixture/stub fallback for local tests.
- **D-14:** Do not use browser-native `SpeechRecognition` as the primary Phase 3 STT path because it bypasses the backend/worker provider boundary.
- **D-15:** Add a compact spoken-turns list near the composer. It should show queued/running/succeeded/failed state, transcript text, VAD metadata, provider metadata, and the Use as generation text action.
- **D-16:** Keep spoken input attempts separate from generated output attempts. Do not fold transcription jobs into the existing recent generation attempts list.
- **D-17:** For failed or weak turns, support re-recording or re-uploading rather than mutating the same job into a retry. Successful transcripts remain editable before use.

### the agent's Discretion
- **D-18:** The user selected the recommended options throughout the discussion. Downstream agents may choose exact endpoint names, schema names, component boundaries, and deterministic fixture mechanics as long as the decisions above are preserved.

### Deferred Ideas (OUT OF SCOPE)
- Automatic end-of-turn listening while recording - belongs to Phase 4 live conversation mode.
- Multiple detected turns from one recording - defer until the single-turn capture path works reliably or until conversation mode needs it.
- Interruption handling and speaking/listening live states - belongs to Phase 4.
- TEN VAD, FireRedVAD, and multi-provider VAD comparison - belongs to Phase 5 benchmark work.
- Browser-native `SpeechRecognition` as the primary STT path - rejected for Phase 3 because it bypasses the backend provider boundary.
- Retrying VAD/STT against the same stored audio artifact - useful later for provider debugging, but Phase 3 should prefer re-record/re-upload and editable transcripts.
- Durable transcript/audio history, saved clips, and user libraries - deferred beyond v1 no-login studio scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUD-01 | User can provide spoken input through the browser microphone or an uploaded audio clip. | Use browser-native `getUserMedia` + `MediaRecorder` for capture, preserve first-class mic/upload states, and wire the upload into the same queued job path as generation. |
| AUD-02 | System can detect speech boundaries using a VAD provider. | Keep VAD behind `VADProvider`, use a Silero-compatible baseline, normalize audio to worker-friendly mono WAV, and keep metadata compact and lenient. |
| AUD-03 | System can transcribe user speech through an STT provider. | Keep STT behind `STTProvider`, use a faster-whisper-compatible baseline, and return transcript results as editable review text. |
| AUD-04 | User can see or inspect the recognized transcript before or during speech-to-speech generation. | Render an editable transcript review field and a clear Use as generation text action; do not auto-overwrite the generation composer. |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Keep the app as a no-login, studio-first web product with the root route opening the studio directly.
- Preserve the original theatrical voice boundary and server-side rights enforcement; do not drift toward protected-character imitation.
- Keep speech components behind provider interfaces so future model swaps do not require product rewrites.
- Target cloud GPU deployment, not local-only assumptions.
- Use the GSD workflow for file-changing work; do not make direct repo edits outside a GSD workflow.
- Preserve the minimal v1 studio scope: voice, input, tone preset, generate, and live conversation controls.
- Prefer `rg` for searches and `apply_patch` for manual file edits; avoid destructive git operations unless explicitly requested.

## Summary

Phase 3 should be planned as a browser-capture -> queued audio-turn job -> worker VAD/STT -> editable transcript review -> explicit copy-to-generation loop. The current repo already has the right seams to extend: SQLite-backed job records plus a local object store in [`services/api/app/services/generation_jobs.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py#L102), provider protocols in [`services/speech-worker/providers/contracts.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py#L7), same-origin rewrites in [`apps/web/next.config.ts`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts#L5), and a session-scoped attempt list in [`apps/web/components/studio-shell.tsx`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx#L316).

For browser capture, use `navigator.mediaDevices.getUserMedia()` plus `MediaRecorder` and treat MIME support as runtime-dependent. MDN shows the stop-based recorder flow and `MediaRecorder.isTypeSupported()` checks, which matters because Phase 3 should support manual Record/Stop and uploaded clips without assuming one browser codec. Keep the capture UI focused on first-class permission denial, missing-device, validation, and recording states rather than a separate audio page. [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder] [CITED: https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API]

For speech processing, keep VAD and STT separate. The official Silero VAD README shows a baseline loader/reader/timestamp flow, supports 8 kHz and 16 kHz audio, and documents PyTorch or ONNX Runtime paths; the faster-whisper README shows `WhisperModel.transcribe()` returning generator segments and also offers a built-in Silero VAD filter. Phase 3 should still keep VAD as its own provider so the UI can show compact segment metadata and the backend can stay swappable. [CITED: https://github.com/snakers4/silero-vad] [CITED: https://github.com/SYSTRAN/faster-whisper]

The workspace has the browser/runtime scaffolding but not the speech stack yet: `ffmpeg` is missing, the repo venv does not currently have `silero-vad`, `faster-whisper`, `torch`, `torchaudio`, or `ctranslate2`, and the package-legitimacy gate marked the audio packages as SUS because of unknown-download or too-new signals. The planner should therefore include install/setup checkpoints before implementation, not assume the worker image is speech-ready. [VERIFIED: local env] [VERIFIED: package-legitimacy check]

**Primary recommendation:** Mirror the generation job path with a new audio-turn job service and UI surface, normalize captured audio to mono WAV in the backend, use Silero VAD and faster-whisper behind provider interfaces, and make transcript handoff explicit with a Use as generation text action.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Browser microphone capture and audio upload | Browser / Client | API / Backend | Permission prompts, device selection, recording, and file picking belong in the browser; the backend only validates and ingests the resulting blob. |
| Audio-turn job creation, polling, and artifact serving | API / Backend | Database / Storage | The existing queued-job pattern already lives on the backend with SQLite and a local object store; Phase 3 should mirror it. |
| VAD speech-boundary detection | API / Backend | Database / Storage | VAD must stay behind the provider boundary so the app can swap models later without changing the UI contract. |
| STT transcription and transcript assembly | API / Backend | Database / Storage | STT is server-side inference, not a browser responsibility, and the transcript must land in persisted job state. |
| Editable transcript review and Use as generation text | Browser / Client | API / Backend | The transcript must stay editable in the UI until the user explicitly copies it into the generation composer and submits a new generation job. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | `16.2.9` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Web studio UI and same-origin rewrites | Already powers the root studio and the browser-to-API rewrite pattern; keep the existing pin out of this phase's scope. |
| React | `19.2.7` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | UI components | Current repo pin for the app shell and studio surface. |
| React DOM | `19.2.7` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | Client rendering | Pairs with React 19.2.7 in the existing app. |
| TypeScript | `6.0.3` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/package.json] | UI and API type safety | Keeps transcript, job, and provider payloads explicit. |
| FastAPI | `0.138.2` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | API/control plane | Already backs the current generation and voice routes. |
| Pydantic | `2.13.4` [CITED: /Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/pyproject.toml] | Runtime validation | Existing schemas already use strict `extra="forbid"` and explicit validators. |
| MediaDevices.getUserMedia / MediaRecorder / Web Audio API | Browser-native | Mic capture, stop-based recording, and playback | MDN documents the exact browser primitives Phase 3 needs for manual Record/Stop plus upload. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `silero-vad` [WARNING: package-legitimacy check flagged SUS; human-verify before install.] | `6.2.1` | Baseline speech-boundary detection | Use for the first VAD provider; the official repo documents 8 kHz / 16 kHz support and timestamp extraction. |
| `faster-whisper` [WARNING: package-legitimacy check flagged SUS; human-verify before install.] | `1.2.1` | Baseline STT | Use for the first transcription provider; the official repo exposes generator segments and a WhisperModel API. |
| FFmpeg | system binary | Audio normalization and format conversion | Use for uploaded/recorded audio that is not already worker-friendly mono WAV. |

**Registry note:** current registry checks showed React, React DOM, and TypeScript matching the repo pins, while Next, FastAPI, Pydantic, `silero-vad`, and `faster-whisper` were flagged SUS by the package-legitimacy gate. Do not bundle framework churn or package upgrades into Phase 3.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Separate VAD provider | `faster-whisper`'s built-in `vad_filter` | Easier wiring, but it hides VAD metadata and couples segmentation to STT, which is the opposite of this phase's provider-boundary goal. |
| Backend STT provider | Browser `SpeechRecognition` | Simpler in the browser, but it bypasses the worker/provider boundary and makes future model swaps harder. |
| MediaRecorder | Custom Web Audio PCM/WAV encoding | More deterministic output, but much more code and more browser-specific maintenance. |

**Installation:**
```bash
# Human-verify first; the package-gate marked the speech packages as SUS.
pip install silero-vad==6.2.1 faster-whisper==1.2.1
```

## Package Legitimacy Audit

> Required because this phase will install speech packages in the worker environment. The gate was run before writing this section.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `silero-vad` | PyPI | Published 2026-02-24 (~4 months) | unknown | https://github.com/snakers4/silero-vad | SUS | Flagged - planner must add `checkpoint:human-verify` before install |
| `faster-whisper` | PyPI | Published 2025-10-31 (~8 months) | unknown | https://github.com/SYSTRAN/faster-whisper | SUS | Flagged - planner must add `checkpoint:human-verify` before install |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `silero-vad`, `faster-whisper`

## Architecture Patterns

### System Architecture Diagram

```text
Browser mic Record/Stop or audio upload
    -> client validation (permission/device/mime/size)
    -> POST audio blob to API
    -> queued audio-turn job record + session-scoped artifact path
    -> worker normalizes audio to mono WAV
    -> VADProvider segments speech (lenient first-turn policy)
    -> if speech is meaningful
          -> STTProvider transcribes the turn
       else
          -> mark weak turn + warn the user, do not auto-block aggressively
    -> API persists transcript + compact VAD metadata
    -> browser shows editable transcript review
    -> user clicks Use as generation text
    -> existing generation job path
```

### Recommended Project Structure
```text
apps/
  web/
    app/
    components/
    tests/
services/
  api/
    app/
      routes/
      schemas/
      services/
  speech-worker/
    audio/
    providers/
    tests/
```

### Pattern 1: Audio-Turn Jobs Mirror Generation Jobs
**What:** Create queued jobs on stop/upload, persist a job record, then poll until VAD/STT completes.
**When to use:** Always for Phase 3 audio input.
**Example:** The current generation path already does this in [`services/api/app/services/generation_jobs.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py#L172) and [`services/api/app/services/generation_runtime.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py#L125).

### Pattern 2: Lenient First-Turn Segmentation
**What:** Accept short or low-confidence speech segments, warn instead of blocking, and prefer re-record/re-upload over retrying the same audio artifact.
**When to use:** The first internal MVP turn path.
**Example:** Keep the VAD provider output compact: provider name, start/end, speech duration, confidence.

### Pattern 3: Explicit Transcript Handoff
**What:** Render the transcript in an editable review field and require an explicit Use as generation text action.
**When to use:** Always in Phase 3.
**Example:** The composer should not overwrite itself until the user confirms the handoff.

### Anti-Patterns to Avoid
- **Separate audio page:** it fragments the studio flow and fights the locked no-separate-page decision.
- **SpeechRecognition as the primary STT path:** it bypasses the worker/provider boundary.
- **Auto-copy transcript into the composer:** it removes the review step and makes errors harder to catch.
- **Hard-coded codec assumptions:** browser capture formats vary; normalize server-side.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Mic capture and record/stop state handling | Custom media stack | `getUserMedia` + `MediaRecorder` | The browser already gives you the permission prompt, media stream, and Blob-based recording flow. |
| Audio normalization | Custom decoder/converter | FFmpeg helper | The existing worker helper already normalizes to mono WAV and handles non-WAV inputs. |
| Speech boundary detection | Silence heuristics in the browser | Silero-compatible `VADProvider` | First-turn leniency and future model swaps are easier behind the provider boundary. |
| STT transcription | Browser `SpeechRecognition` | faster-whisper-compatible `STTProvider` | The backend/worker boundary stays intact and testable. |
| Transcript reuse | Auto-mutating the composer | Explicit Use as generation text action | Keeps the transcript editable and preserves review intent. |

**Key insight:** audio input is deceptively multi-problem: permissions, codecs, storage, turn boundaries, and transcription are separate concerns. Reuse the job/provider/storage pattern instead of building a one-off "upload and hope" path.

## Common Pitfalls

### Pitfall 1: Treating Browser Codecs as Uniform
**What goes wrong:** the browser produces a codec/container the worker can't read.
**Why it happens:** MediaRecorder support varies, and MIME support is runtime-dependent.
**How to avoid:** check `MediaRecorder.isTypeSupported()` and normalize server-side.
**Warning signs:** upload validation passes but VAD/STT fails on some browsers.

### Pitfall 2: Assuming Track Constraints Are Portable
**What goes wrong:** the code tries to force a sample rate or other audio setting the browser ignores.
**Why it happens:** `MediaTrackSettings.sampleRate` is limited-availability and browser support varies.
**How to avoid:** treat browser capture settings as hints, not guarantees, and normalize in the worker.
**Warning signs:** one browser records fine while another silently changes the format.

### Pitfall 3: Over-Aggressive First-Turn VAD
**What goes wrong:** short or noisy turns are dropped instead of reviewed.
**Why it happens:** threshold tuning is too strict for the first MVP.
**How to avoid:** warn on weak segments, keep the transcript editable, and favor re-record/re-upload.
**Warning signs:** users repeatedly see empty or failed turns for ordinary speech.

### Pitfall 4: Client-Side STT Bypasses the Architecture
**What goes wrong:** the feature works in one browser but becomes impossible to swap or test consistently.
**Why it happens:** browser-native speech APIs are tempting shortcuts.
**How to avoid:** keep STT behind `STTProvider` and run it in the backend/worker boundary.
**Warning signs:** UI code imports speech-model logic or turns transcript generation into a browser-only feature.

### Pitfall 5: Overwriting the Composer Automatically
**What goes wrong:** the transcript becomes a silent mutation instead of a reviewed input.
**Why it happens:** the UI tries to be too helpful.
**How to avoid:** keep transcript review editable and require an explicit handoff action.
**Warning signs:** the generation text changes before the user clicks Use as generation text.

## Code Examples

Verified patterns from official sources:

### Browser Capture Flow
```ts
// Source: MDN getUserMedia + MediaRecorder
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const recorder = new MediaRecorder(stream);
const chunks: Blob[] = [];
recorder.ondataavailable = (event) => chunks.push(event.data);
recorder.stop();
```
[MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)  
[MDN MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)

### Silero-Compatible VAD Flow
```python
# Source: official Silero VAD README
vad = load_vad_model()
waveform = read_audio(audio_path)
segments = get_speech_timestamps(waveform, vad, return_seconds=True)
```
[Silero VAD README](https://github.com/snakers4/silero-vad)

### faster-whisper STT Flow
```python
# Source: official faster-whisper README
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, info = model.transcribe(audio_path, beam_size=5)
for segment in segments:
    transcript.append((segment.start, segment.end, segment.text))
```
[faster-whisper README](https://github.com/SYSTRAN/faster-whisper)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Browser `SpeechRecognition` as primary STT | Backend `STTProvider` behind the worker boundary | Rejected in Phase 3 context | Keeps the speech stack swappable and testable. |
| STT-only VAD heuristics | Separate `VADProvider` plus compact metadata | Phase 3 design decision | Makes turn boundaries inspectable and benchmarkable later. |
| Synchronous mic transcription | Queued audio-turn job with polling | Follows the existing generation-job pattern | Prevents the UI from blocking on slow speech inference. |
| Browser-format assumptions | Server-side normalization to mono WAV | Existing worker helper and Phase 3 capture flow | Avoids browser codec drift. |

**Deprecated/outdated:**
- Browser-native `SpeechRecognition` as the primary STT path.
- Hard-coded audio codec assumptions in the client.
- Auto-copying transcript text into the generation composer.

## Assumptions Log

> All claims in this research were verified or cited - no user confirmation needed.

## Open Questions (RESOLVED)

1. **Resolved: Phase 3 will include the FFmpeg setup/install step now, while tests keep a WAV-only deterministic fallback.**
   - What we know: the current worker helper normalizes non-WAV inputs with FFmpeg, and this workspace does not have an `ffmpeg` binary.
   - Decision: plan the FFmpeg install/setup step now; keep a WAV-only fallback for tests.
2. **Resolved: the worker will use the `torch`/`torchaudio` Silero path first.**
   - What we know: the official Silero README supports both paths, and this workspace has neither installed.
   - Decision: choose the `torch`/`torchaudio` path first because it matches the official helper flow and the existing file-based normalization pattern.

These decisions are locked for Phase 3 planning. Future execution should treat FFmpeg setup and the `torch`/`torchaudio` Silero path as the approved baseline, with deterministic fixtures kept for local tests.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-----------|-----------|---------|----------|
| Node.js | Web app build/test | ✓ | 24.2.0 | — |
| pnpm | Web package manager | ✓ | 10.30.3 | — |
| `.venv` Python | API/worker runtime | ✓ | Python 3.11.12 | Use the repo venv instead of system Python 3.13.5 |
| pytest | API/worker tests | ✓ | 9.1.1 in `.venv` | `./.venv/bin/python -m pytest` |
| uvicorn | FastAPI server for Playwright | ✓ | 0.49.0 in `.venv` | `./.venv/bin/python -m uvicorn` |
| Playwright | Browser verification | ✓ | 1.61.1 via `apps/web/node_modules/.bin/playwright` | `cd apps/web && pnpm test` |
| uv | Python dependency management | ✗ | — | Use the current `.venv` + `pip` fallback already accepted by the project. |
| FFmpeg | Audio normalization | ✗ | — | Add FFmpeg to the worker image in this phase; keep a WAV-only fallback for tests. |
| Speech runtime packages | Silero/STT worker stack | ✗ | `silero-vad`, `faster-whisper`, `torch`, `torchaudio`, `ctranslate2` are not installed in `.venv` | Install them in the worker venv/image after human verify; use the approved `torch`/`torchaudio` Silero path and deterministic fixtures. |

**Missing dependencies with no fallback:**
- none - the phase can proceed once the planner adds the worker/runtime install step and completes the FFmpeg setup step.

**Missing dependencies with fallback:**
- FFmpeg - a WAV-only fallback exists for tests, but it is not enough for arbitrary browser blobs.
- Speech runtime packages - install in the worker venv/image; use the approved `torch`/`torchaudio` Silero path and the deterministic fixture fallback.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 9.1.1` for API/worker tests and `@playwright/test 1.61.1` for browser verification |
| Config file | `pyproject.toml` and `apps/web/playwright.config.ts` |
| Quick run command | `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -x` |
| Full suite command | `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && cd apps/web && pnpm test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|-----------|-----------|-------------------|-------------|
| AUD-01 | Capture mic audio or accept an uploaded clip, validate permission/device/upload states, and create the first audio-turn job on stop/upload. | browser/e2e | `cd apps/web && pnpm exec playwright test tests/audio-input.spec.ts -g "mic|upload"` | ❌ Wave 0 |
| AUD-02 | Detect speech boundaries with a VAD provider and persist compact VAD metadata. | unit/integration | `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -k "vad" -x` | ❌ Wave 0 |
| AUD-03 | Transcribe the turn through an STT provider and keep the transcript editable. | unit/integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_turn_providers.py -k "stt" -x` | ❌ Wave 0 |
| AUD-04 | Show the transcript for review and move it into generation only on explicit Use as generation text action. | browser/e2e | `cd apps/web && pnpm exec playwright test tests/audio-input.spec.ts -g "transcript|Use as generation text"` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -x`
- **Per wave merge:** `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && cd apps/web && pnpm test`
- **Phase gate:** Full suite green before `gsd-verify-work`

### Wave 0 Gaps
- `services/api/tests/test_audio_turn_jobs.py` - audio-turn queue/status/metadata coverage
- `services/speech-worker/tests/test_audio_turn_providers.py` - Silero-compatible VAD and faster-whisper adapter coverage
- `apps/web/tests/audio-input.spec.ts` - mic/upload capture, transcript review, and Use-as-generation-text coverage
- `services/api/tests/conftest.py` - audio-turn fixtures mirroring the generation-job fixtures

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 3 remains no-login. |
| V3 Session Management | yes | Session-scoped audio-turn jobs, opaque job IDs, and controlled playback URLs. |
| V4 Access Control | yes | Server-side rights gate plus controlled artifact serving through same-origin routes. |
| V5 Input Validation | yes | Strict Pydantic schemas, file-type/size checks, and worker-side audio normalization. |
| V6 Cryptography | no | No new cryptographic primitive is needed in this phase. |

### Known Threat Patterns for Browser Audio + STT

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed audio uploads or oversized blobs | Tampering / DoS | Validate MIME/size, normalize on the backend, and queue work instead of processing synchronously. |
| Transcript injection into UI or composer | Tampering / XSS | Render transcript as text, not HTML, and require explicit Use as generation text action. |
| Raw path leakage for stored audio | Information disclosure | Serve audio through controlled URLs and keep the object-store path server-side only. |
| Voice/profile bypass through direct API calls | Spoofing / Elevation | Keep the rights gate server-side and keep the browser seed render-only. |

## Sources

### Primary (HIGH confidence)
- [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia) - browser mic permission + capture primitives.
- [MDN MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder) - recorder constructor, MIME support checks, and baseline availability.
- [MDN MediaStream Recording API](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API) - stop-based Blob capture flow.
- [Silero VAD README](https://github.com/snakers4/silero-vad) - loader/read_audio/timestamp flow, sample-rate support, runtime requirements, release history.
- [faster-whisper README](https://github.com/SYSTRAN/faster-whisper) - WhisperModel.transcribe, generator segments, VAD filter, and model/runtime behavior.
- [`services/api/app/services/generation_jobs.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_jobs.py) - queued job records, SQLite persistence, local object store, retry pattern.
- [`services/api/app/services/generation_runtime.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/api/app/services/generation_runtime.py) - provider helper, worker-root boundary, background dispatch, artifact duration handling.
- [`services/speech-worker/providers/contracts.py`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/services/speech-worker/providers/contracts.py) - VAD/STT/TTS/provider interfaces.
- [`apps/web/components/studio-shell.tsx`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/components/studio-shell.tsx) - session-scoped attempt list, status polling, retry cache pattern, current clip surface.
- [`apps/web/next.config.ts`](/Users/akhilasusarla/conductor/workspaces/p3n-11/calgary/apps/web/next.config.ts) - same-origin rewrite pattern.

### Secondary (MEDIUM confidence)
- `npm view` / package-legitimacy checks for `next`, `react`, `react-dom`, `@playwright/test`, and `typescript`.
- `pip index versions` / package-legitimacy checks for `fastapi`, `pydantic`, `silero-vad`, `faster-whisper`, `torch`, `torchaudio`, `ctranslate2`, and `onnxruntime`.
- Local environment probes for `.venv`, `pnpm`, `playwright`, and `ffmpeg`.

### Tertiary (LOW confidence)
- none - no low-confidence training-only claims were needed for this research.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - browser APIs and repo seams are clear, but the speech packages are flagged SUS and the worker runtime is not yet provisioned.
- Architecture: HIGH - the current codebase already supplies the job/service/provider patterns Phase 3 should extend.
- Pitfalls: HIGH - MDN and official repo docs align with the repo's current generation pattern and the locked phase decisions.

**Research date:** 2026-07-03
**Valid until:** 2026-08-02
