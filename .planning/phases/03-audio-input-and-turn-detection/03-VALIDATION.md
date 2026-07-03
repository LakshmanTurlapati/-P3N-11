---
phase: 03
slug: audio-input-and-turn-detection
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-03
---

# Phase 03 - Validation Strategy

Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | `pytest 9.1.1` for API/worker tests and `@playwright/test 1.61.1` for browser verification |
| Config file | `pyproject.toml`, `apps/web/playwright.config.ts` |
| Quick run command | `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -x` |
| Full suite command | `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && pnpm --dir apps/web exec playwright test` |
| Estimated runtime | about 90 seconds for the focused API/worker checks; longer once browser capture coverage is added |

## Sampling Rate

- After every task commit: run the smallest relevant automated command for the files changed, with `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -x` as the default backend check.
- After every plan wave: run `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests && pnpm --dir apps/web exec playwright test`.
- Before `$gsd-verify-work`: full pytest and Playwright suites must be green, and the transcript handoff path must be browser-verified.
- Max feedback latency: 90 seconds for non-browser checks.

## Per-Task Verification Map

| Requirement | Expected Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|-------------------|-----------|-------------------|-------------|--------|
| AUD-01 | User can record microphone audio or upload an audio clip, and stop/upload creates an audio-turn job automatically. | browser/API | `pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts -g "mic|upload"` and `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py -k "create" -x` | no - Wave 0 | pending |
| AUD-02 | VAD runs through `VADProvider`, selects one lenient best speech region, and persists provider/start/end/duration/confidence metadata. | unit/integration | `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py services/speech-worker/tests/test_audio_turn_providers.py -k "vad" -x` | no - Wave 0 | pending |
| AUD-03 | STT runs through `STTProvider`, persists transcript/provider metadata, and supports deterministic fallback fixtures. | unit/integration | `./.venv/bin/python -m pytest services/api/tests/test_audio_turn_jobs.py services/speech-worker/tests/test_audio_turn_providers.py -k "stt" -x` | no - Wave 0 | pending |
| AUD-04 | Browser shows an editable transcript review field and only copies it into the generation composer after an explicit Use as generation text action. | browser/e2e | `pnpm --dir apps/web exec playwright test tests/audio-input.spec.ts -g "transcript|Use as generation text"` | no - Wave 0 | pending |

## Wave 0 Requirements

- [ ] `services/api/tests/test_audio_turn_jobs.py` - covers audio-turn queue/status transitions, upload validation, artifact storage, transcript payloads, and compact VAD metadata.
- [ ] `services/speech-worker/tests/test_audio_turn_providers.py` - covers Silero-compatible VAD and faster-whisper-compatible STT adapters with deterministic fallback fixtures.
- [ ] `apps/web/tests/audio-input.spec.ts` - covers mic/upload states, queued/running/succeeded/failed audio turns, transcript editing, and Use as generation text.
- [ ] `services/api/tests/conftest.py` - shared audio-turn fixtures mirroring existing generation-job fixtures if needed.
- [ ] Framework install: none for pytest or Playwright. Human-verify and install speech runtime packages before provider integration work.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `silero-vad` and `faster-whisper` package legitimacy and runtime install | AUD-02, AUD-03 | Research package gate marked both speech packages SUS, and model/runtime install can vary by host/GPU image | Before installing, review source repo and registry metadata, then run the focused provider tests with deterministic fixtures enabled. |
| Microphone permission denial and unavailable-device state | AUD-01 | Browser/device permission prompts are environment-dependent and hard to fully assert in CI | In a browser run, deny microphone permission and confirm the studio shows the denied state without creating an audio-turn job. |
| Real captured browser blob normalization | AUD-01, AUD-02, AUD-03 | FFmpeg is missing in this workspace, and browser codec output varies | Record a short clip in the browser, submit it, and confirm the backend either normalizes it to mono WAV or reports a clear validation/setup error. |

## Security Domain

| Ref | Threat | Expected Mitigation |
|-----|--------|---------------------|
| T-03-01 | Oversized or malformed audio upload causes synchronous worker failure or denial of service | Validate MIME/size, store as a queued job artifact, normalize in the worker, and return failed job state instead of blocking the request. |
| T-03-02 | Raw artifact paths leak through the API or browser | Keep object-store paths server-side and expose only controlled same-origin job/status/audio routes. |
| T-03-03 | Transcript content injects markup into the studio UI | Render transcripts as text in form controls, never as HTML, and require explicit Use as generation text. |
| T-03-04 | Browser-only STT bypasses provider auditability | Keep transcription behind `STTProvider`; do not use browser-native `SpeechRecognition` as the primary path. |

## Validation Sign-Off

- [ ] All plan tasks have automated verification commands or Wave 0 dependencies.
- [ ] Sampling continuity: no three consecutive tasks without automated verification.
- [ ] Wave 0 covers all missing test references.
- [ ] No watch-mode flags are used in verification commands.
- [ ] Feedback latency stays under 90 seconds for non-browser checks.
- [ ] `nyquist_compliant: true` is set after the above checks are satisfied.

**Approval:** pending
