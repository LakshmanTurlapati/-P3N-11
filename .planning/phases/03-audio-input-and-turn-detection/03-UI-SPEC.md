---
phase: 3
slug: audio-input-and-turn-detection
status: draft
shadcn_initialized: false
preset: none
created: 2026-07-07
---

# Phase 3 - UI Design Contract

Visual and interaction contract for audio input, turn detection, and transcript review. Keep the existing single-page studio shell, preserve the custom CSS system, and extend the current workflow rather than introducing a new page or mode switch.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | none |
| Font | Iowan Old Style for display and headings, Avenir Next for body, with Georgia and Arial fallbacks |

Reuse the existing 24px card radius, translucent borders, and full-width action buttons from the current studio shell. The new audio controls should read as part of the same studio stack, not a new product surface.

---

## Interaction Contract

| Rule | Contract |
|------|----------|
| Surface structure | Keep `/` as the studio entry point and add audio input inside the existing studio shell. Do not add a separate audio route, modal flow, or mode switcher. |
| Desktop layout | Place the spoken-input card beside the generation composer on desktop. The generation composer remains the primary visual anchor; the spoken-input card is the secondary capture surface, and the spoken-turns list is tertiary review history. On mobile, stack spoken input above the composer and keep the turn list underneath both. |
| Capture flow | Record starts capture and Stop ends it. Stopping a recording or finishing an upload immediately creates an audio-turn job. There is no separate Transcribe button. |
| Transcript flow | Show the transcript in an editable review field. Do not overwrite the generation composer until the user clicks `Use as generation text`. |
| Turn visibility | Keep spoken turns session-scoped and separate from the generation attempt list. Use the existing attempt-card shape for turn cards, with transcript text plus compact VAD metadata fields: provider name, segment start and end, speech duration, and confidence when available. Failed or weak turns stay visible and prompt re-record or re-upload rather than retrying the same audio job. |
| Status feedback | Show queued, running, succeeded, and failed states plus a live recording timer or level indicator. Compact VAD metadata must sit next to the transcript, not in a separate debug page. |
| Accessibility | Every audio control needs a visible text label, a keyboard focus state, and screen-reader-readable status text. |

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, inline padding |
| sm | 8px | Compact element spacing |
| md | 16px | Default element spacing |
| lg | 24px | Section padding |
| xl | 32px | Layout gaps |
| 2xl | 48px | Major section breaks |
| 3xl | 64px | Page-level spacing |

Exceptions: 44px minimum touch target for any icon-only mic or stop control; otherwise none.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 16px | 400 | 1.5 |
| Label | 12px | 700 | 1.2 |
| Heading | 28px | 400 | 1.2 |
| Display | 52px | 400 | 0.95 |

Use body text for transcript copy, metadata, helper text, and form fields. Reserve the display size for the studio title only.

---

## Color

Keep the existing 60/30/10 split from the dark studio shell.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | #0B0908 | Page background, outer shell, and dark canvas |
| Secondary (30%) | #151110 | Cards, transcript surfaces, side panels, and turn list containers |
| Accent (10%) | #D6A06A | Primary Record/Stop control, `Generate voice`, `Use as generation text`, selected tone chips, selected or ready turn badges, live recording indicators, focus rings, and success emphasis on transcript handoff |
| Destructive | #F5B9A8 | Permission denied, invalid upload, failed turn labels, and error banners only |

Destructive reserved for error states and destructive actions only.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | Record turn |
| Active CTA | Stop recording |
| Secondary CTA | Upload audio |
| Transcript action | Use as generation text |
| Recovery CTA | Re-record |
| Alternate recovery CTA | Re-upload |
| Empty state heading | No spoken turns yet |
| Empty state body | Record a line or upload audio to create an editable transcript, then use it as generation text. |
| Queued state | Queued |
| Recording state | Recording... |
| Processing state | Transcribing turn... |
| Success state | Transcript ready |
| Permission denied state | Mic access is blocked. Allow microphone access in the browser or upload audio instead. |
| Upload validation state | That file is not supported. Upload a valid audio file and try again. |
| Weak turn note | Audio was captured, but the turn is thin or noisy. Review the transcript or record again. |
| Error state | We could not process this turn. Allow microphone access or upload a supported audio file, then record again. |
| Destructive confirmation | None |

The transcript review field must remain editable after transcription. The handoff action copies text into the composer without submitting the generation form.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registries | none | not applicable |

No third-party registries were declared, so no additional safety vetting is required.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved
