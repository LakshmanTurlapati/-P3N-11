<div align="center">

# Op3n-11

*A consent-based voice cloning and text-to-speech platform.*

![Status](https://img.shields.io/badge/status-planning-lightgrey?style=for-the-badge)

</div>

---

## The Problem

Voice cloning tools are spreading fast, and most treat consent as a checkbox. A user ticks a box, uploads a sample, and the clone activates. There is no proof the voice in the sample belongs to the person creating the clone, and no durable record if something goes wrong.

## The Solution

Op3n-11 lets a user create a verified, authorized clone of their own voice and generate natural speech from text. It follows the workflow ElevenLabs popularized, but every clone requires proof of consent: the user reads a random spoken phrase aloud, and that recording is verified before the clone activates. Every consent event, clone, and generation is written to an audit trail.

## Status

This project is in the planning stage. No application code exists yet. Requirements, architecture, and an eight-phase roadmap are complete in `.planning/`, and Phase 1 (safety, legal, and data governance) is next.

## Core Features (v1)

| Feature | Description |
|---|---|
| **Workspace** | Sign up, log in, and manage a personal voice workspace. |
| **Sample Intake** | Record or upload a voice sample for cloning. |
| **Consent Verification** | Read a random spoken phrase aloud before a clone can activate. |
| **Voice Cloning** | Create a reusable personal voice clone once verification passes. |
| **Generation** | Enter text and generate speech using an authorized cloned voice. |
| **History** | Preview, regenerate, download, and manage generated audio. |
| **Audit Trail** | Every consent, clone, and generation event is logged. |
| **Admin Review** | Flag and disable misused voice clones. |

## Tech Stack

| Layer | Choices |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui |
| Auth | Clerk |
| Data | PostgreSQL, Drizzle ORM, pgvector |
| Storage | AWS S3, KMS, CloudTrail |
| Jobs | Trigger.dev, Upstash Redis |
| Voice Gateway | FastAPI, Python, Azure Personal Voice or Cartesia |

The voice gateway sits behind its own abstraction, so the underlying provider or model can be replaced later without touching the app.

## Safety

Voice likeness carries real misuse risk. Consent verification, audit logging, and admin review are core requirements, not later additions. Unauthorized cloning and impersonation workflows are explicitly out of scope.

## Roadmap

v1 covers cloning and generation only. Broader parity work such as dubbing, agents, APIs, and a marketplace is planned for v2 and beyond.

---

<div align="center">

By Akhila Susarla, Lakshman Turlapati

</div>
