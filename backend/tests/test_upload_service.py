"""Upload import service tests."""

from pathlib import Path

from sqlalchemy import func, select

from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.services.analytics_service import get_player_analytics
from app.services.analytics_service import get_team_analytics
from app.services.upload_service import import_box_score_csv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_import_box_score_csv_creates_games_players_and_stats(db_session):
    team = Team(name="CourtIQ Demo", season="2025-26")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    csv_path = PROJECT_ROOT / "sample_data" / "demo_game_1.csv"
    result = import_box_score_csv(db_session, team.id, csv_path)

    assert result.rows_processed == 3
    assert result.games_created == 1
    assert result.players_created == 3
    assert result.stats_created == 3
    assert result.stats_updated == 0

    assert db_session.scalar(select(func.count()).select_from(Game)) == 1
    assert db_session.scalar(select(func.count()).select_from(Player)) == 3
    assert db_session.scalar(select(func.count()).select_from(PlayerGameStats)) == 3


def test_import_box_score_csv_updates_existing_player_game_stats(db_session):
    team = Team(name="CourtIQ Demo", season="2025-26")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    csv_path = PROJECT_ROOT / "sample_data" / "demo_game_1.csv"
    import_box_score_csv(db_session, team.id, csv_path)
    second_result = import_box_score_csv(db_session, team.id, csv_path)

    assert second_result.games_created == 0
    assert second_result.players_created == 0
    assert second_result.stats_created == 0
    assert second_result.stats_updated == 3

    assert db_session.scalar(select(func.count()).select_from(PlayerGameStats)) == 3


def test_player_analytics_after_multi_game_import(db_session):
    team = Team(name="CourtIQ Demo", season="2025-26")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    csv_path = PROJECT_ROOT / "sample_data" / "demo_multi_game.csv"
    import_box_score_csv(db_session, team.id, csv_path)

    alex = db_session.scalar(select(Player).where(Player.name == "Alex"))
    analytics = get_player_analytics(db_session, alex.id)

    assert analytics is not None
    assert analytics.games_played == 6
    assert analytics.average_points == 20.67
    assert analytics.best_game is not None
    assert analytics.best_game.points == 26
    assert "Alex is averaging" in analytics.summary


def test_team_analytics_after_multi_game_import(db_session):
    team = Team(name="CourtIQ Demo", season="2025-26")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    csv_path = PROJECT_ROOT / "sample_data" / "demo_multi_game.csv"
    import_box_score_csv(db_session, team.id, csv_path)

    analytics = get_team_analytics(db_session, team.id)

    assert analytics is not None
    assert analytics.games_played == 6
    assert analytics.roster_size == 1
    assert analytics.average_team_points == 20.67
    assert analytics.top_scorers[0].player_name == "Alex"
    assert len(analytics.game_trends) == 6
