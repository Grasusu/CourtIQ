"""Player service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.schemas.player import PlayerCreate


def create_player(db: Session, team_id: int, payload: PlayerCreate) -> Player | None:
    team = db.get(Team, team_id)
    if team is None:
        return None

    name = payload.name.strip()
    existing_player = db.scalar(
        select(Player).where(
            Player.team_id == team_id,
            func.lower(Player.name) == name.casefold(),
        )
    )
    if existing_player is not None:
        raise ValueError("Player already exists on this team")

    player = Player(
        team_id=team_id,
        name=name,
        position=payload.position,
        jersey_number=payload.jersey_number,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def get_player(db: Session, player_id: int) -> Player | None:
    return db.get(Player, player_id)


def list_team_players(db: Session, team_id: int) -> list[Player] | None:
    team = db.get(Team, team_id)
    if team is None:
        return None

    return list(
        db.scalars(
            select(Player)
            .where(Player.team_id == team_id)
            .order_by(Player.name)
        ).all()
    )
