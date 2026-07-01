from __future__ import annotations

from fastapi import FastAPI

from services.api.app.routes.voices import router as voices_router

app = FastAPI(title="Theatrical Voice Studio API")
app.include_router(voices_router)

