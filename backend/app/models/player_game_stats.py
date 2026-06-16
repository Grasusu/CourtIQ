from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PlayerGameStats(Base):
    __tablename__ = "player_game_stats"
    __table_args__ = (UniqueConstraint("player_id", "game_id", name="uq_player_game_stats"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    minutes: Mapped[float] = mapped_column(nullable=False)
    points: Mapped[int] = mapped_column(nullable=False)
    rebounds: Mapped[int] = mapped_column(nullable=False)
    assists: Mapped[int] = mapped_column(nullable=False)
    steals: Mapped[int] = mapped_column(nullable=False)
    blocks: Mapped[int] = mapped_column(nullable=False)
    turnovers: Mapped[int] = mapped_column(nullable=False)
    fgm: Mapped[int] = mapped_column(nullable=False)
    fga: Mapped[int] = mapped_column(nullable=False)
    three_pm: Mapped[int] = mapped_column(nullable=False)
    three_pa: Mapped[int] = mapped_column(nullable=False)
    ftm: Mapped[int] = mapped_column(nullable=False)
    fta: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    player = relationship("Player", back_populates="game_stats")
    game = relationship("Game", back_populates="player_stats")
