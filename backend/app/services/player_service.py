"""Player service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.schemas.player import PlayerCreate


def create_player(db: Session, team_id: int, payload: PlayerCreate, owner_id: int) -> Player | None:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
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


def get_player(db: Session, player_id: int, owner_id: int | None = None) -> Player | None:
    query = select(Player).where(Player.id == player_id)
    if owner_id is not None:
        query = query.join(Team).where(Team.owner_id == owner_id)

    return db.scalar(query)


def list_team_players(db: Session, team_id: int, owner_id: int) -> list[Player] | None:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        return None

    return list(
        db.scalars(
            select(Player)
            .where(Player.team_id == team_id)
            .order_by(Player.name)
        ).all()
    )
