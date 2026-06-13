from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    season = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    players = relationship("Player", back_populates="team")
    games = relationship("Game", back_populates="team")