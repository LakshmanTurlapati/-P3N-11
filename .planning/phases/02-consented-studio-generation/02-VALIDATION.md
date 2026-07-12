---
phase: 02
slug: consented-studio-generation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-01
---

# Phase 02 - Validation Strategy

Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | `pytest 9.1.1` for Python services and `@playwright/test 1.61.1` for browser flows |
| Config file | `pyproject.toml`, `apps/web/playwright.config.ts` |
| Quick run command | `./.venv/bin/python -m pytest services/api/tests/test_rights_gate.py services/api/tests/test_voice_profile.py services/api/tests/test_generate_stub.py services/speech-worker/tests/test_provider_contracts.py -q && pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` |
| Full suite command | `./.venv/bin/python -m pytest services/api/tests services/speech-worker/tests -q && pnpm --dir apps/web exec playwright test` |
| Estimated runtime | about 60 seconds for the quick suite, longer when browser and provider integration tests are enabled |

## Sampling Rate

- After every task commit: run the quick command above.
- After every plan wave: run the full suite above.
- Before `$gsd-verify-work`: full suite must be green, plus one configured real provider smoke test must produce playable audio.
- Max feedback latency: 90 seconds for non-provider checks.

## Per-Task Verification Map

| Requirement | Expected Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|-------------------|-----------|-------------------|-------------|--------|
| GOV-04 | Consent/license notes remain backend-owned and generation remains rights-gated | unit/integration | `./.venv/bin/python -m pytest services/api/tests/test_voice_profile.py services/api/tests/test_rights_gate.py -q` | yes | pending |
| STUD-03 | Text input submits generation text to the backend | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | yes | pending |
| STUD-04 | `Measured`, `Cutting`, and `Grandiose` render and map to generation metadata | e2e/unit | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | yes | pending |
| STUD-05 | Loading, success, error, and retry states render from job status | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | yes | pending |
| STUD-06 | Generated audio renders as a playable browser audio element from a controlled URL | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | yes | pending |
| STUD-07 | Retry reuses the last text, voice, and tone after failure | e2e | `pnpm --dir apps/web exec playwright test tests/studio-generation.spec.ts` | yes | pending |
| PIPE-02 | Real provider adapter synthesizes playable audio behind `TTSProvider` | integration/manual smoke | `./.venv/bin/python -m pytest services/speech-worker/tests/test_cosyvoice_provider.py -q` | no - Wave 0 | pending |
| PIPE-03 | Generated audio metadata includes provider, voice profile, tone preset, and timing | integration/API | `./.venv/bin/python -m pytest services/api/tests/test_generation_jobs.py -q` | no - Wave 0 | pending |
| PIPE-04 | Generated audio is normalized into accepted playback/provider formats | integration | `./.venv/bin/python -m pytest services/speech-worker/tests/test_audio_normalization.py -q` | no - Wave 0 | pending |

## Wave 0 Requirements

- [ ] `services/api/tests/test_generation_jobs.py` - covers `queued`, `running`, `succeeded`, `failed`, retry, and metadata persistence.
- [ ] `services/speech-worker/tests/test_cosyvoice_provider.py` - covers the real provider adapter and playable-audio contract.
- [ ] `services/speech-worker/tests/test_audio_normalization.py` - covers normalized generated-audio output shape and accepted sample format.
- [ ] `apps/web/tests/studio-generation.spec.ts` - extend existing coverage for text input, tone selection, playback, and retry assertions.
- [ ] `services/api/tests/conftest.py` - add shared fixtures if the job store or object-store abstraction needs them.
- [ ] Framework install: none. Existing pytest and Playwright infrastructure covers the phase.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A configured real provider produces playable audio locally or in the intended runtime | PIPE-02 | Model install and checkpoint licensing require human verification before use | Run the chosen provider smoke test with a licensed/allowed voice profile and confirm a playable audio file is produced through the job flow. |
| Tone presets produce audible or metadata-observable differences | STUD-04 | Early baseline providers may not expose stable style controls | Generate the same fixed sentence with all three presets and confirm the stored metadata differs; if audio is materially identical, record that as a provider limitation rather than hiding it. |

## Validation Sign-Off

- [ ] All plan tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no three consecutive tasks without automated verification.
- [ ] Wave 0 covers all missing test references.
- [ ] No watch-mode flags are used in verification commands.
- [ ] Feedback latency stays under 90 seconds for non-provider checks.
- [ ] `nyquist_compliant: true` is set after the above checks are satisfied.

**Approval:** pending
