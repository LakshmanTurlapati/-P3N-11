# Phase 3: Audio Input and Turn Detection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-07-03T21:41:50Z
**Phase:** 3-Audio Input and Turn Detection
**Areas discussed:** Input capture, VAD behavior, Transcript inspection

---

## Input Capture

### Spoken Input Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Audio input beside text | Add mic/upload controls near the current generation text box, then let the transcript fill or replace that text. | yes |
| Separate transcript card | Add a distinct audio/transcription panel below generation, with its own job state and transcript history. | |
| Mode switcher | Use a Text / Audio segmented control so the main composer shows only one input mode at a time. | |
| Other | Freeform preference. | |

**User's choice:** Audio input beside text.
**Notes:** Keeps spoken input tied to the existing studio flow.

### Recording Controls

| Option | Description | Selected |
|--------|-------------|----------|
| Manual start/stop + upload | User clicks Record, clicks Stop, and can also upload an audio file. | yes |
| Push-to-hold recording | User holds a button while speaking, release ends the take. | |
| Auto-capture after mic enable | Once mic permission is granted, the app listens and segments automatically. | |
| Other | Freeform preference. | |

**User's choice:** Manual start/stop + upload.
**Notes:** Avoids drifting into live conversation behavior.

### Post-Capture Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-transcribe immediately | Stopping a recording or selecting a file creates an audio turn job and runs VAD plus STT right away. | yes |
| Wait for Transcribe click | Capture the audio first, then require a separate Transcribe action. | |
| Preview audio first | Show a small playback preview before any VAD/STT job starts. | |
| Other | Freeform preference. | |

**User's choice:** Auto-transcribe immediately.
**Notes:** Proves the spoken-input loop directly.

### Captured Audio Retention

| Option | Description | Selected |
|--------|-------------|----------|
| Session-scoped artifact only | Store the captured clip through the existing local object-store pattern for the job, expose metadata/transcript in the current session, and do not create a durable library. | yes |
| Keep only transcript | Discard captured audio after VAD/STT and retain just recognized text. | |
| Visible audio preview retained | Keep a small playback preview for each captured turn in the UI. | |
| Other | Freeform preference. | |

**User's choice:** Session-scoped artifact only.
**Notes:** Matches Phase 2 session-scoped attempts and avoids saved-library scope.

---

## VAD Behavior

### Segmentation Model

| Option | Description | Selected |
|--------|-------------|----------|
| Whole captured clip first | Run VAD over the stopped recording/upload, identify speech segments, and transcribe the best combined speech region. | yes |
| Split into multiple turns | If VAD finds multiple speech regions, show them as separate transcript turns. | |
| End-of-turn simulation | While recording, show listening/speaking/silence state and auto-stop after silence. | |
| Other | Freeform preference. | |

**User's choice:** Whole captured clip first.
**Notes:** Proves VAD/STT without treating Phase 3 as live conversation.

### Usable Turn Rule

| Option | Description | Selected |
|--------|-------------|----------|
| Lenient internal MVP | Accept a turn if VAD finds any meaningful speech segment, and show low confidence/short duration as warnings instead of blocking. | yes |
| Strict minimums | Require minimum speech duration and confidence before STT runs; otherwise ask the user to re-record. | |
| Always transcribe | Run STT on the whole clip even if VAD is uncertain, with VAD metadata shown separately. | |
| Other | Freeform preference. | |

**User's choice:** Lenient internal MVP.
**Notes:** Warnings are preferred over aggressive blocking.

### VAD Provider Posture

| Option | Description | Selected |
|--------|-------------|----------|
| Silero baseline behind provider interface | Implement a Silero or Silero-compatible baseline, with fixture/stub fallback for local tests. | yes |
| Pure stub provider first | Implement only a deterministic VAD stub in Phase 3 and defer real VAD until benchmarks. | |
| Compare multiple VADs now | Add Silero plus TEN or FireRed in this phase. | |
| Other | Freeform preference. | |

**User's choice:** Silero baseline behind provider interface.
**Notes:** TEN/FireRed comparison remains Phase 5 benchmark scope.

### Visible VAD Metadata

| Option | Description | Selected |
|--------|-------------|----------|
| Compact transcript metadata | Show segment start/end, duration, confidence when available, and provider name near the transcript. | yes |
| Detailed segment table | Show every segment with thresholds, sample rate, and normalization details. | |
| Warnings only | Show transcript text plus warnings for weak/no speech, hiding normal VAD metadata. | |
| Other | Freeform preference. | |

**User's choice:** Compact transcript metadata.
**Notes:** Keep inspection useful without building a debug dashboard.

---

## Transcript Inspection

### Transcript Handoff

| Option | Description | Selected |
|--------|-------------|----------|
| Review then use | Show the transcript in an editable review field, with a clear action to copy/use it as the generation text. | yes |
| Auto-fill generation text | Immediately replace the generation text box with the transcript. | |
| Transcript stays separate | Show transcript only in an audio-turn card; user manually copies if desired. | |
| Other | Freeform preference. | |

**User's choice:** Review then use.
**Notes:** AUD-04 requires transcript inspection before or during speech-to-speech generation.

### STT Provider Posture

| Option | Description | Selected |
|--------|-------------|----------|
| faster-whisper baseline behind provider interface | Implement a faster-whisper-compatible STT baseline with deterministic test fallback. | yes |
| Deterministic stub only | Ship a fake STT provider now and defer real transcription setup. | |
| Browser SpeechRecognition first | Use browser-native speech recognition for speed. | |
| Other | Freeform preference. | |

**User's choice:** faster-whisper baseline behind provider interface.
**Notes:** Preserves the server/worker provider boundary.

### Transcript Job State

| Option | Description | Selected |
|--------|-------------|----------|
| Audio turns list | Add a compact spoken turns/transcript list near the composer, showing queued/running/succeeded/failed, transcript text, VAD metadata, and a Use as generation text action. | yes |
| Inline composer state only | Show a single active transcript status below the mic controls. | |
| Fold into recent attempts | Combine transcription and generation attempts into one mixed history. | |
| Other | Freeform preference. | |

**User's choice:** Audio turns list.
**Notes:** Spoken input attempts stay separate from generated output attempts.

### Failure And Correction

| Option | Description | Selected |
|--------|-------------|----------|
| Retry capture, edit transcript | Failed/weak turns can be re-recorded or re-uploaded, and successful transcripts are editable before use. | yes |
| Retry transcription job | Keep the same audio artifact and allow rerunning VAD/STT. | |
| Manual transcript fallback | If STT fails, show an empty editable transcript field the user can fill manually. | |
| Other | Freeform preference. | |

**User's choice:** Retry capture, edit transcript.
**Notes:** Handles STT errors without adding same-artifact job mutation.

---

## the agent's Discretion

- Exact endpoint names, schema names, component boundaries, and fixture mechanics can be selected during planning/implementation.

## Deferred Ideas

- Automatic end-of-turn listening, interruption support, and live speaking/listening states.
- Multi-turn splitting from one captured clip.
- TEN/FireRed VAD comparison.
- Browser-native `SpeechRecognition` as the primary STT path.
- Same-audio VAD/STT retry.
- Durable transcript/audio history.
