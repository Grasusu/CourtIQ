"""Upload import service tests."""

from pathlib import Path

from sqlalchemy import func, select

from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.models.upload_job import UploadJob
from app.models.user import User
from app.services.analytics_service import get_player_analytics
from app.services.analytics_service import get_team_analytics
from app.services.upload_service import create_upload_job, import_box_score_csv, process_upload_job_in_session


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


def test_process_upload_job_updates_status_and_counts(db_session):
    user = User(email="coach@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    team = Team(name="CourtIQ Demo", season="2025-26", owner_id=user.id)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    csv_path = PROJECT_ROOT / "sample_data" / "demo_game_1.csv"
    job = create_upload_job(db_session, team.id, "demo_game_1.csv", csv_path, owner_id=user.id)
    processed_job = process_upload_job_in_session(db_session, job.id)

    assert processed_job is not None
    assert processed_job.status == "completed"
    assert processed_job.rows_processed == 3
    assert processed_job.games_created == 1
    assert processed_job.players_created == 3
    assert processed_job.stats_created == 3
    assert processed_job.error_message is None
    assert db_session.scalar(select(func.count()).select_from(UploadJob)) == 1


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
