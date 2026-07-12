---
phase: 03-audio-input-and-turn-detection
plan: 03
subsystem: full-stack
tags: [stt, faster-whisper, playwright, nextjs, fastapi, audio-turns]

# Dependency graph
requires:
  - phase: 03-02
    provides: VAD segmentation, audio normalization, and session-scoped spoken-turn capture
provides:
  - Faster-whisper-compatible STT provider behind `STTProvider`
  - Transcript language/confidence persisted on audio-turn job records
  - Editable transcript review with explicit `Use as generation text` handoff
  - Deterministic fallback fixtures for backend and browser validation
affects:
  - phase 04 live conversation mode
  - generation composer handoff flow
  - audio-turn verification harness

# Tech tracking
tech-stack:
  added: [faster-whisper-compatible worker adapter, Playwright fallback fixture env, transcript review UI]
  patterns: [provider-backed STT boundary, session-scoped transcript persistence, explicit no-overwrite handoff]

key-files:
  created:
    - services/speech-worker/providers/faster_whisper_stt_provider.py
  modified:
    - services/speech-worker/providers/__init__.py
    - services/speech-worker/tests/test_audio_turn_providers.py
    - services/api/app/services/audio_turn_runtime.py
    - services/api/app/schemas/audio_turn.py
    - services/api/app/services/audio_turn_jobs.py
    - services/api/tests/test_audio_turn_jobs.py
    - apps/web/components/studio-shell.tsx
    - apps/web/app/globals.css
    - apps/web/playwright.config.ts
    - apps/web/tests/audio-input.spec.ts

key-decisions:
  - "Use a faster-whisper-compatible STT provider behind STTProvider with deterministic fixture fallback so the worker/runtime boundary stays intact."
  - "Persist transcript language and confidence on the same session-scoped audio-turn record that stores VAD metadata."
  - "Keep transcript review separate from the generation composer and require an explicit Use as generation text action to copy the transcript."

patterns-established:
  - "Pattern 1: STT providers return text, language, and confidence through a worker adapter and can swap between real and fixture backends."
  - "Pattern 2: Audio-turn job records carry VAD metadata plus transcript metadata in the same session-scoped state."
  - "Pattern 3: Spoken-turn review uses an editable transcript field and an explicit handoff button rather than auto-overwriting generation input."

requirements-completed: [AUD-03, AUD-04]

coverage:
  - id: D1
    description: "Faster-whisper-compatible STT provider transcribes the segmented turn and persists transcript language/confidence on the audio-turn job record."
    requirement: AUD-03
    verification:
      - kind: integration
        ref: "./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_turn_providers.py services/api/tests/test_audio_turn_jobs.py -q"
        status: pass
    human_judgment: false
  - id: D2
    description: "Editable spoken-turn transcript review copies into the generation composer only when the user clicks Use as generation text."
    requirement: AUD-04
    verification:
      - kind: automated_ui
        ref: "pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts -g \"transcript|Use as generation text\""
        status: pass
      - kind: automated_ui
        ref: "pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts"
        status: pass
    human_judgment: false

duration: 29 min
completed: 2026-07-12
status: complete
---

# Phase 03: Audio Input and Turn Detection Summary

**Provider-backed STT with persisted transcript metadata and explicit copy-to-composer review flow**

## Performance

- **Duration:** 29 min
- **Started:** 2026-07-12T16:58:09Z
- **Completed:** 2026-07-12T17:26:45Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments
- Added a faster-whisper-compatible STT provider behind `STTProvider`, with deterministic fixture fallback and speech-window transcription.
- Persisted transcript text, language, confidence, and provider metadata on the same session-scoped audio-turn record as the VAD data.
- Added editable transcript review cards and an explicit `Use as generation text` action so the composer only changes on demand.

## Task Commits

Each task was committed atomically:

1. **Task 1: Approve the faster-whisper baseline runtime and fallback shape** - `approved` (human-verify checkpoint)
2. **Task 2: Implement the faster-whisper-compatible STT provider and transcript persistence** - `ea495e0` (feat)
3. **Task 3: Wire transcript review and explicit generation-text handoff** - `6137e41` (feat)

**Plan metadata:** pending final docs commit

## Files Created/Modified
- `services/speech-worker/providers/faster_whisper_stt_provider.py` - Faster-whisper-compatible STT adapter with fixture fallback
- `services/speech-worker/providers/__init__.py` - Lazy export for the new STT provider
- `services/speech-worker/tests/test_audio_turn_providers.py` - Backend coverage for injected backend and fixture fallback
- `services/api/app/services/audio_turn_runtime.py` - Crops to the VAD speech window and persists STT metadata
- `services/api/app/schemas/audio_turn.py` - Adds transcript language/confidence fields to audio-turn records
- `services/api/app/services/audio_turn_jobs.py` - Stores STT provider and transcript metadata on job attempts
- `services/api/tests/test_audio_turn_jobs.py` - Verifies transcript persistence and speech-window cropping
- `apps/web/components/studio-shell.tsx` - Editable transcript review and explicit handoff UI
- `apps/web/app/globals.css` - Styles for the transcript review block
- `apps/web/playwright.config.ts` - Forces deterministic STT fixture mode for browser validation
- `apps/web/tests/audio-input.spec.ts` - Browser regression for transcript editing and copy-to-composer behavior

## Decisions Made
- Use a faster-whisper-compatible STT provider behind `STTProvider` with deterministic fixture fallback so the worker/runtime boundary stays intact.
- Persist transcript language and confidence on the same session-scoped audio-turn record that stores VAD metadata.
- Keep transcript review separate from the generation composer and require an explicit `Use as generation text` action to copy the transcript.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] Added deterministic STT fixture env for browser validation**
- **Found during:** Task 3
- **Issue:** The Playwright transcript-handoff test needed deterministic STT fallback behavior so the browser run would not depend on a live worker package path.
- **Fix:** Set `THEATRICAL_VOICE_STUDIO_STT_FIXTURE=1` in `apps/web/playwright.config.ts` webServer env.
- **Files modified:** `apps/web/playwright.config.ts`
- **Verification:** `pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts -g "transcript|Use as generation text"` and `pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts`
- **Committed in:** `6137e41` (part of task 3 commit)

**Total deviations:** 1 auto-fixed (Rule 3)
**Impact on plan:** The change kept browser verification deterministic and did not alter the user-facing slice.

## Issues Encountered
- `formatProviderLabel()` initially only accepted generation job records, so the shared studio label helper had to be widened to accept audio-turn provider shapes as well. That was fixed in the task 3 UI commit and verified by the Playwright run.
- The existing `.planning/config.json` change was left untouched because it predated this work and was unrelated to the phase execution.

## Next Phase Readiness
The studio now has provider-backed transcription, editable transcript review, and explicit handoff into generation. Phase 04 can build on the same session-scoped turn history for live conversation without reworking the audio-turn persistence shape.

---
*Phase: 03-audio-input-and-turn-detection*
*Completed: 2026-07-12*

## Self-Check: PASSED

- Confirmed the summary file and shipped code files exist on disk.
- Confirmed task commits `ea495e0` and `6137e41` are present in git history.
