---
phase: 02-consented-studio-generation
plan: 02
subsystem: speech-worker
tags: [cosyvoice, tts, ffmpeg, python, pytest]

# Dependency graph
requires:
  - phase: 01-no-login-vertical-skeleton
    provides: phase-1 rights gate, provider contract, and the studio shell seam for real synthesis
provides:
  - approved CosyVoice 0.5B baseline adapter behind `TTSProvider`
  - FFmpeg-backed audio normalization helper for generated clips
  - worker-surface export for the CosyVoice provider
affects:
  - 02-03 job persistence and playback URLs
  - 02-04 browser audio playback and retry
  - 03-01 turn-detection and speech-input slices

# Tech tracking
tech-stack:
  added:
    - none
  patterns:
    - lazy repo-checkout loading for optional model runtimes
    - tone-steered prompt composition with a safe baseline voice default
    - FFmpeg-backed WAV normalization before later storage or playback

key-files:
  created:
    - services/speech-worker/audio/normalization.py
    - services/speech-worker/providers/cosyvoice_provider.py
    - services/speech-worker/tests/test_audio_normalization.py
    - services/speech-worker/tests/test_cosyvoice_provider.py
  modified:
    - services/speech-worker/providers/__init__.py

key-decisions:
  - "Use the approved official CosyVoice repo checkout and the Fun-CosyVoice3-0.5B-2512 0.5B checkpoint as the baseline."
  - "Keep tone steering in prompt text rather than adding provider-specific knobs or sliders."
  - "Normalize generated audio to mono WAV via FFmpeg before the worker hands it to later storage or playback code."

patterns-established:
  - "Pattern 1: TTS providers stay behind the shared `TTSProvider` protocol and load the external model lazily."
  - "Pattern 2: Real provider output is assembled into a complete WAV clip first, then normalized through a worker helper."
  - "Pattern 3: Approved baseline voice selection stays explicit (`vesper-glass`) while tone remains preset-driven."

requirements-completed: [PIPE-02, PIPE-04]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "CosyVoiceTTSProvider returns a playable baseline clip behind the worker TTS contract and threads tone steering through the repo-checkout prompt path."
    requirement: PIPE-02
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_cosyvoice_provider.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "normalize_audio converts generated output into a mono WAV clip with preserved metadata through an FFmpeg-backed worker helper."
    requirement: PIPE-04
    verification:
      - kind: unit
        ref: "services/speech-worker/tests/test_audio_normalization.py"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-02
status: complete
---

# Phase 2: Consented Studio Generation Summary

CosyVoice 0.5B is now wired into the worker behind the shared provider contract, and generated audio is normalized to a playable WAV clip before it leaves the worker boundary.

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-02T18:00:00Z
- **Completed:** 2026-07-02T18:19:19Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Captured the approved CosyVoice baseline from the checkpoint resolution and encoded it as a lazy worker adapter that defaults to the official `FunAudioLLM/CosyVoice` repo checkout and `Fun-CosyVoice3-0.5B-2512` checkpoint path.
- Added `normalize_audio` so generated clips are converted into mono WAV output with preserved metadata via FFmpeg before the browser or storage layer sees them.
- Added focused worker tests that pin the baseline provider contract, tone steering, and the normalization behavior without depending on the real model runtime in CI.

## Task Commits

Each task was completed atomically or, for the resolved checkpoint, explicitly approved before implementation:

1. **Task 1: Approve the baseline CosyVoice checkpoint and install path** - resolved at checkpoint, no repository changes
2. **Task 2: Add failing worker tests for the real provider and normalization helper** - `aeada85` (`test`)
3. **Task 3: Implement the CosyVoice provider adapter and audio normalization helper** - `b632b19` (`feat`)

## Files Created/Modified

- `services/speech-worker/audio/normalization.py` - FFmpeg-backed audio normalization helper
- `services/speech-worker/providers/cosyvoice_provider.py` - CosyVoice 0.5B baseline adapter
- `services/speech-worker/providers/__init__.py` - worker export surface for the new provider
- `services/speech-worker/tests/test_audio_normalization.py` - normalization contract coverage
- `services/speech-worker/tests/test_cosyvoice_provider.py` - provider wiring and tone-steering coverage

## Decisions Made

- Use the official `FunAudioLLM/CosyVoice` repo checkout with the `Fun-CosyVoice3-0.5B-2512` baseline instead of a PyPI install path.
- Keep `vesper-glass` as the explicit approved worker voice key for this phase and steer tone through prompt text.
- Normalize audio to mono WAV in the worker so later storage and playback code always receive a consistent clip shape.

## Deviations from Plan

None - plan executed exactly as written. The only additional hardening was clearer runtime error messaging when the approved repo checkout or FFmpeg is missing.

## Issues Encountered

- The workspace does not contain the approved CosyVoice checkout, model weights, or `torch`/`torchaudio`, so a live real-model smoke test could not be executed here.
- The worker code now fails with actionable messages if those runtime prerequisites are absent, and the behavior is covered by unit tests with injected fakes.

## User Setup Required

None in-repo. A real worker runtime still needs the approved CosyVoice checkout, checkpoint assets, and FFmpeg available in the deployment environment.

## Next Phase Readiness

- The worker now exposes a real CosyVoice baseline adapter behind `TTSProvider`.
- Audio is normalized before it leaves the worker helper, so the storage and playback slice can consume one clip shape.
- Phase 2 can build the job/store and browser playback layers on top of this worker seam without revisiting the provider selection decision.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/02-consented-studio-generation/02-02-SUMMARY.md`.
- Task commits verified in git history: `aeada85` and `b632b19`.
