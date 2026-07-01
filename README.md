# Op3n-11

*A consent-based voice cloning and text-to-speech platform.*

## What This Is

Op3n-11 lets a user create a verified, authorized clone of their own voice and generate natural speech from text. It follows the workflow ElevenLabs popularized, but every clone requires proof of consent, not just a checkbox.

## Status

This project is in the planning stage. No application code has been written yet. Requirements, architecture, and an eight-phase roadmap are complete in `.planning/`, and Phase 1 (safety, legal, and data governance) is next.

## Core Features (v1)

- Sign up and manage a personal workspace
- Record or upload a voice sample
- Verify consent by reading a random spoken phrase aloud
- Create a reusable voice clone after verification passes
- Generate, preview, regenerate, and download speech from text
- Audit trail covering every consent, clone, and generation event
- Admin review queue to flag and disable misused clones

## Tech Stack

Next.js, React, and TypeScript on the frontend. PostgreSQL with Drizzle ORM for data. Clerk for auth. AWS S3 and KMS for encrypted storage. Trigger.dev for background jobs. A FastAPI gateway in Python wraps the voice provider (Azure Personal Voice or Cartesia) so the underlying model can be replaced later without touching the app.

## Safety

Voice likeness carries real misuse risk. Consent verification, audit logging, and admin review are core requirements, not later additions. Unauthorized cloning and impersonation workflows are explicitly out of scope.

## Roadmap

v1 covers cloning and generation only. Broader parity work such as dubbing, agents, APIs, and a marketplace is planned for v2 and beyond.

---

By Akhila Susarla, Lakshman Turlapati
