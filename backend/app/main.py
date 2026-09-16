from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    analytics_router,
    auth_router,
    demo_router,
    games_router,
    players_router,
    teams_router,
    uploads_router,
)
from app import models  # noqa: F401


def _cors_origins() -> list[str]:
    configured_origins = getenv("CORS_ALLOWED_ORIGINS")
    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]


app = FastAPI(title="CourtIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(teams_router)
app.include_router(players_router)
app.include_router(games_router)
app.include_router(uploads_router)
app.include_router(analytics_router)
app.include_router(demo_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
