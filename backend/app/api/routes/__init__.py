"""Route modules for the CourtIQ API."""

from app.api.routes.analytics import router as analytics_router
from app.api.routes.games import router as games_router
from app.api.routes.players import router as players_router
from app.api.routes.teams import router as teams_router
from app.api.routes.uploads import router as uploads_router

__all__ = [
    "analytics_router",
    "games_router",
    "players_router",
    "teams_router",
    "uploads_router",
]
