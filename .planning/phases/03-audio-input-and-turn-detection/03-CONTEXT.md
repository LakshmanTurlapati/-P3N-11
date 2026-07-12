# Phase 3: Audio Input and Turn Detection - Context

**Gathered:** 2026-07-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 adds spoken input to the existing no-login studio. It extends the Phase 2 text-generation surface with browser microphone recording, audio upload, audio-turn job state, VAD-based turn segmentation, STT transcription, and transcript inspection. The captured transcript can be reviewed and then used as generation text in the existing studio flow.

This phase does not add live conversation responses, persona LLM output, interruption handling, streaming audio transport, automatic end-of-turn listening, multi-provider benchmarks, accounts, durable transcript/audio history, or a saved clip library.

</domain>

<decisions>
## Implementation Decisions

### Input Capture
- **D-01:** Add spoken-input controls beside the current generation text composer instead of creating a separate page or hiding text/audio behind a mode switcher.
- **D-02:** The spoken-input controls should support manual Record and Stop actions plus uploaded audio files.
- **D-03:** Stopping a recording or selecting an upload should automatically create an audio-turn job and run VAD plus STT. Do not require a separate Transcribe click.
- **D-04:** Captured audio should be stored as a session-scoped job artifact through the existing local object-store pattern. Do not add a durable audio library or page-refresh restoration in Phase 3.
- **D-05:** Audio capture must include first-class browser states for mic permission denial, unavailable devices, recording in progress, upload validation, queued/running transcription, success, and failure.

### VAD Behavior
- **D-06:** Run VAD over the stopped recording or uploaded clip after capture, then treat the best combined speech region as one turn for transcription.
- **D-07:** Keep the first turn model lenient for the internal MVP: if VAD finds any meaningful speech segment, continue to STT and show short/low-confidence warnings instead of blocking aggressively.
- **D-08:** Use a Silero or Silero-compatible baseline behind the existing `VADProvider` interface, with deterministic fixture/stub fallback for local tests.
- **D-09:** Leave TEN VAD, FireRedVAD, and multi-provider VAD comparisons to Phase 5 benchmark work.
- **D-10:** Show compact VAD metadata near the transcript: provider name, segment start/end, speech duration, and confidence when available. Do not build a detailed VAD debug dashboard in Phase 3.

### Transcript Inspection
- **D-11:** Show STT output in an editable transcript review field. The transcript should not overwrite the generation text until the user chooses to use it.
- **D-12:** Provide a clear action to use the reviewed transcript as the generation text for the existing text-to-speech flow.
- **D-13:** Use a faster-whisper-compatible STT baseline behind the existing `STTProvider` interface, with deterministic fixture/stub fallback for local tests.
- **D-14:** Do not use browser-native `SpeechRecognition` as the primary Phase 3 STT path because it bypasses the backend/worker provider boundary.
- **D-15:** Add a compact spoken-turns list near the composer. It should show queued/running/succeeded/failed state, transcript text, VAD metadata, provider metadata, and the Use as generation text action.
- **D-16:** Keep spoken input attempts separate from generated output attempts. Do not fold transcription jobs into the existing recent generation attempts list.
- **D-17:** For failed or weak turns, support re-recording or re-uploading rather than mutating the same job into a retry. Successful transcripts remain editable before use.

### the agent's Discretion
- **D-18:** The user selected the recommended options throughout the discussion. Downstream agents may choose exact endpoint names, schema names, component boundaries, and deterministic fixture mechanics as long as the decisions above are preserved.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` - Defines the current product direction, Phase 3 starting point, rights/persona constraints, no-login studio-first shape, and current Phase 2 completion state.
- `.planning/REQUIREMENTS.md` - Maps Phase 3 to AUD-01 through AUD-04: mic/upload input, VAD speech boundaries, STT transcription, and transcript inspection.
- `.planning/ROADMAP.md` - Defines the Phase 3 goal, success criteria, and planned slices: browser microphone/upload input, VAD provider baseline, and STT/transcript inspection.
- `.planning/STATE.md` - Captures current phase position and accumulated Phase 1/2 decisions that affect audio input.

### Prior Phase Handoff
- `.planning/phases/02-consented-studio-generation/02-CONTEXT.md` - Locks the queued generation job shape, session-scoped attempts, local object-store pattern, and minimal studio controls that Phase 3 should extend.
- `.planning/phases/01-no-login-vertical-skeleton/01-CONTEXT.md` - Locks the direct root studio route, Vesper Glass identity boundary, server-owned rights gate, and provider-interface posture.
- `.planning/phases/02-consented-studio-generation/02-06-SUMMARY.md` - Summarizes live backend browser verification, same-origin polling, local CosyVoice fixture, and current audio playback test patterns relevant to Phase 3 browser tests.

### Research and Architecture
- `.planning/research/ARCHITECTURE.md` - Defines the web/API/worker split, audio input flow, live conversation flow boundary, provider adapter boundary, metadata store, and object storage role.
- `.planning/research/STACK.md` - Recommends Web Audio API/MediaRecorder for mic capture, Silero VAD as the baseline, faster-whisper as the STT baseline, and FFmpeg/audio normalization support.
- `.planning/research/PITFALLS.md` - Calls out web mic permission states, over/under-aggressive VAD, realtime latency traps, and the need to prove turn boundaries before live mode.
- `.planning/research/FEATURES.md` - Defines audio input, VAD/turn detection, provider abstraction, and transcript-producing speech-to-speech input as expected v1 capabilities.

No separate Phase 3 SPEC.md exists as of this discussion.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `apps/web/components/studio-shell.tsx` - Current client component owns the root studio UI, text composer, tone presets, generation submission, status polling, current clip, and recent generation attempts. Phase 3 should extend this surface with mic/upload controls and a separate spoken-turns list near the composer.
- `apps/web/app/globals.css` - Existing studio styles define form groups, action buttons, cards, attempt lists, responsive behavior, and metadata layouts that can be reused for spoken-turn cards.
- `apps/web/next.config.ts` - Next.js already rewrites `/generate`, `/generations/:path*`, and `/voices/:path*` to the FastAPI API. Add audio-turn routes to the same same-origin rewrite pattern.
- `services/api/app/routes/generate.py` - Existing route pattern creates jobs, dispatches background processing, exposes job status, and serves controlled audio URLs. Phase 3 should mirror this pattern for audio-turn transcription jobs.
- `services/api/app/services/generation_jobs.py` - Existing SQLite-backed job service and `LocalObjectStore` provide the pattern for persisted job JSON, controlled artifact paths, and status transitions.
- `services/api/app/schemas/generation.py` - Existing Pydantic schemas use strict `extra="forbid"` validation, explicit status enums, provider trace metadata, timing fields, and attempt records. Audio-turn schemas should follow this style.
- `services/speech-worker/providers/contracts.py` - Existing `AudioBuffer`, `SpeechSegment`, `TranscriptResult`, `VADProvider`, and `STTProvider` protocols are the intended provider boundary for this phase.
- `services/speech-worker/audio/normalization.py` - Existing audio normalization helper and WAV fallback are relevant for recorded/uploaded audio conversion before VAD/STT provider calls.
- `apps/web/tests/studio-generation.spec.ts` - Current Playwright tests verify same-origin live backend polling, status transitions, retry behavior, and audio URL assertions. Phase 3 should add similarly focused browser coverage for mic/upload, audio-turn status, transcript review, and Use as generation text.
- `services/speech-worker/tests/test_provider_contracts.py` - Existing provider-contract test already covers dummy VAD and STT swappability and should be extended or mirrored with real baseline/fallback tests.

### Established Patterns
- The root route `/` remains the direct studio. Do not add a landing page or separate audio-only route for Phase 3.
- Server/provider boundaries are authoritative. Browser code should not import model-specific VAD/STT logic or use browser-native STT as the primary path.
- Jobs expose `queued`, `running`, `succeeded`, and `failed` states and are stored through SQLite-backed JSON records.
- Browser-visible attempts are session-scoped. Phase 3 should keep spoken turns visible in-session without adding accounts, saved transcript history, or durable libraries.
- Local deterministic fixtures are acceptable for tests, but provider adapters should still prove the intended real baseline path behind the provider interface.

### Integration Points
- Web: add mic/upload controls beside the generation text composer, plus a spoken-turns list with transcript review and Use as generation text action.
- API: add audio-turn/transcription job routes that accept recorded/uploaded audio, create a job, expose status, and return transcript/VAD metadata.
- Worker: implement Silero-compatible VAD and faster-whisper-compatible STT adapters behind `VADProvider` and `STTProvider`, with deterministic fallbacks for tests.
- Storage: store captured audio as controlled job artifacts through the local object-store pattern; avoid raw filesystem path exposure.
- Tests: add API tests for upload/capture job creation, VAD/STT metadata, provider fallback, failure states, and transcript schema; add Playwright tests for upload or mocked MediaRecorder flows and transcript handoff into generation text.

</code_context>

<specifics>
## Specific Ideas

- Place spoken input controls near the current generation text area so text and audio feel like two ways to feed the same studio audition flow.
- Label the spoken input list as a compact "Spoken turns" or equivalent transcript-focused surface.
- The primary transcript action should be phrased around using the transcript as generation text, not auto-generating speech immediately.
- VAD metadata should be useful for inspection but compact enough to keep the studio from becoming a debug console.

</specifics>

<deferred>
## Deferred Ideas

- Automatic end-of-turn listening while recording - belongs to Phase 4 live conversation mode.
- Multiple detected turns from one recording - defer until the single-turn capture path works reliably or until conversation mode needs it.
- Interruption handling and speaking/listening live states - belongs to Phase 4.
- TEN VAD, FireRedVAD, and multi-provider VAD comparison - belongs to Phase 5 benchmark work.
- Browser-native `SpeechRecognition` as the primary STT path - rejected for Phase 3 because it bypasses the backend provider boundary.
- Retrying VAD/STT against the same stored audio artifact - useful later for provider debugging, but Phase 3 should prefer re-record/re-upload and editable transcripts.
- Durable transcript/audio history, saved clips, and user libraries - deferred beyond v1 no-login studio scope.

</deferred>

---

*Phase: 3-Audio Input and Turn Detection*
*Context gathered: 2026-07-03*
