from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import asr

app = FastAPI(
    title="Voice-output API",
    description="Backend API for the Voice-output intelligent voice input MVP.",
    version="0.1.0",
)

app.include_router(asr.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
