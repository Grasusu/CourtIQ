from contextlib import asynccontextmanager

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
from app.core.database import Base, engine
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CourtIQ API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
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
