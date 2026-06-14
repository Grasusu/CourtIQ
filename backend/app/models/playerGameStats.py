from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Player_Game_Stats(Base):
    __tablename__ = "player_game_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    minutes: Mapped[float] = mapped_column(nullable=False)
    points: Mapped[float] = mapped_column(nullable=False)
    rebounds: Mapped[float] = mapped_column(nullable=False)
    assists: Mapped[float] = mapped_column(nullable=False)
    steals: Mapped[float] = mapped_column(nullable=False)
    blocks: Mapped[float] = mapped_column(nullable=False)
    turnovers: Mapped[float] = mapped_column(nullable=False)
    fgm: Mapped[float] = mapped_column(nullable=False)
    fga: Mapped[float] = mapped_column(nullable=False)
    three_pm: Mapped[float] = mapped_column(nullable=False)
    three_pa: Mapped[float] = mapped_column(nullable=False)
    ftm: Mapped[float] = mapped_column(nullable=False)
    fta: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    player = relationship("Player", back_populates="game_stats")
    game = relationship("Game", back_populates="player_stats")