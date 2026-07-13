from __future__ import annotations

from fastapi import FastAPI

from services.api.app.routes.conversation import router as conversation_router
from services.api.app.routes.audio_turns import router as audio_turns_router
from services.api.app.routes.generate import router as generate_router
from services.api.app.routes.voices import router as voices_router

app = FastAPI(title="Theatrical Voice Studio API")
app.include_router(conversation_router)
app.include_router(audio_turns_router)
app.include_router(generate_router)
app.include_router(voices_router)
