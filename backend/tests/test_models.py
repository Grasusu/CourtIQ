"""Model metadata tests."""

from app.core.database import Base
from app import models  # noqa: F401


def test_model_metadata_contains_mvp_tables():
    assert set(Base.metadata.tables.keys()) >= {
        "teams",
        "players",
        "games",
        "player_game_stats",
    }
