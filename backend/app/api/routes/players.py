"""Player routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.player import PlayerCreate, PlayerRead
from app.services.player_service import create_player, get_player, list_team_players


router = APIRouter(tags=["players"])


@router.post("/teams/{team_id}/players", response_model=PlayerRead, status_code=201)
def create_player_route(team_id: int, payload: PlayerCreate, db: Session = Depends(get_db)):
    try:
        player = create_player(db, team_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if player is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return player


@router.get("/teams/{team_id}/players", response_model=list[PlayerRead])
def list_team_players_route(team_id: int, db: Session = Depends(get_db)):
    players = list_team_players(db, team_id)
    if players is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return players


@router.get("/players/{player_id}", response_model=PlayerRead)
def get_player_route(player_id: int, db: Session = Depends(get_db)):
    player = get_player(db, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return player
