"""CSV import service for box-score uploads."""

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.validators import BoxScoreRow, parse_box_score_csv
from app.core.database import SessionLocal
from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.models.upload_job import UploadJob
from app.schemas.upload import UploadResult


UPLOAD_STATUS_PENDING = "pending"
UPLOAD_STATUS_PROCESSING = "processing"
UPLOAD_STATUS_COMPLETED = "completed"
UPLOAD_STATUS_FAILED = "failed"


def import_box_score_csv(
    db: Session,
    team_id: int,
    file_path: str | Path,
    owner_id: int | None = None,
) -> UploadResult:
    query = select(Team).where(Team.id == team_id)
    if owner_id is not None:
        query = query.where(Team.owner_id == owner_id)

    team = db.scalar(query)
    if team is None:
        raise ValueError(f"Team {team_id} does not exist")

    rows = parse_box_score_csv(file_path)

    players = {
        player.name.casefold(): player
        for player in db.scalars(select(Player).where(Player.team_id == team_id)).all()
    }
    games = {
        (game.game_date, game.opponent.casefold()): game
        for game in db.scalars(select(Game).where(Game.team_id == team_id)).all()
    }

    games_created = 0
    players_created = 0
    stats_created = 0
    stats_updated = 0

    for row in rows:
        player = players.get(row.player.casefold())
        if player is None:
            player = Player(team_id=team_id, name=row.player)
            db.add(player)
            db.flush()
            players[row.player.casefold()] = player
            players_created += 1

        game_key = (row.game_date, row.opponent.casefold())
        game = games.get(game_key)
        if game is None:
            game = Game(team_id=team_id, game_date=row.game_date, opponent=row.opponent)
            db.add(game)
            db.flush()
            games[game_key] = game
            games_created += 1

        existing_stats = db.scalar(
            select(PlayerGameStats).where(
                PlayerGameStats.player_id == player.id,
                PlayerGameStats.game_id == game.id,
            )
        )

        values = _stats_values(row)
        if existing_stats is None:
            db.add(PlayerGameStats(player_id=player.id, game_id=game.id, **values))
            stats_created += 1
        else:
            for field, value in values.items():
                setattr(existing_stats, field, value)
            stats_updated += 1

    db.commit()

    return UploadResult(
        team_id=team_id,
        rows_processed=len(rows),
        games_created=games_created,
        players_created=players_created,
        stats_created=stats_created,
        stats_updated=stats_updated,
    )


def create_upload_job(
    db: Session,
    team_id: int,
    filename: str,
    stored_path: str | Path,
    owner_id: int,
) -> UploadJob:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        raise ValueError(f"Team {team_id} does not exist")

    job = UploadJob(
        team_id=team_id,
        owner_id=owner_id,
        filename=filename,
        stored_path=str(stored_path),
        status=UPLOAD_STATUS_PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_upload_job(db: Session, job_id: int, owner_id: int) -> UploadJob | None:
    return db.scalar(select(UploadJob).where(UploadJob.id == job_id, UploadJob.owner_id == owner_id))


def list_team_upload_jobs(db: Session, team_id: int, owner_id: int) -> list[UploadJob]:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        raise ValueError(f"Team {team_id} does not exist")

    return list(
        db.scalars(
            select(UploadJob)
            .where(UploadJob.team_id == team_id, UploadJob.owner_id == owner_id)
            .order_by(UploadJob.created_at.desc(), UploadJob.id.desc())
        ).all()
    )


def process_upload_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        process_upload_job_in_session(db, job_id)
    finally:
        db.close()


def process_upload_job_in_session(db: Session, job_id: int) -> UploadJob | None:
    job = db.get(UploadJob, job_id)
    if job is None:
        return None

    job.status = UPLOAD_STATUS_PROCESSING
    job.error_message = None
    job.started_at = _utc_now()
    db.commit()

    try:
        result = import_box_score_csv(db, job.team_id, job.stored_path, owner_id=job.owner_id)
    except Exception as exc:
        db.rollback()
        failed_job = db.get(UploadJob, job_id)
        if failed_job is None:
            return None

        failed_job.status = UPLOAD_STATUS_FAILED
        failed_job.error_message = str(exc)
        failed_job.completed_at = _utc_now()
        db.commit()
        db.refresh(failed_job)
        return failed_job

    completed_job = db.get(UploadJob, job_id)
    if completed_job is None:
        return None

    completed_job.status = UPLOAD_STATUS_COMPLETED
    completed_job.rows_processed = result.rows_processed
    completed_job.games_created = result.games_created
    completed_job.players_created = result.players_created
    completed_job.stats_created = result.stats_created
    completed_job.stats_updated = result.stats_updated
    completed_job.error_message = None
    completed_job.completed_at = _utc_now()
    db.commit()
    db.refresh(completed_job)
    return completed_job


def _stats_values(row: BoxScoreRow) -> dict[str, float | int]:
    return {
        "minutes": row.minutes,
        "points": row.points,
        "rebounds": row.rebounds,
        "assists": row.assists,
        "steals": row.steals,
        "blocks": row.blocks,
        "turnovers": row.turnovers,
        "fgm": row.fgm,
        "fga": row.fga,
        "three_pm": row.three_pm,
        "three_pa": row.three_pa,
        "ftm": row.ftm,
        "fta": row.fta,
    }


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
