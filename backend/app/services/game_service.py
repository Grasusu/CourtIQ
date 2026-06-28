"""Game service functions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.team import Team


def list_team_games(db: Session, team_id: int, owner_id: int) -> list[Game] | None:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        return None

    return list(
        db.scalars(
            select(Game)
            .where(Game.team_id == team_id)
            .order_by(Game.game_date.desc(), Game.opponent)
        ).all()
    )
