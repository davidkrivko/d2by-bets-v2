from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship

from database.connection import Base


class Match(Base):
    __tablename__ = 'matches'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_1 = Column(String)
    team_2 = Column(String)
    start_at = Column(TIMESTAMP)

    bets4pro_matches = relationship("Bets4ProMatches", back_populates="match")
    d2by_matches = relationship("D2BYMatches", back_populates="match")
    fansport_matches = relationship("FanSportBetsMatches", back_populates="match")


class BetsType(Base):
    __tablename__ = 'bets_type'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    d2by_type = Column(String, nullable=True)
    fansport_type = Column(String, nullable=True)
    bets4pro_type = Column(String, nullable=True)

    bets4pro_bets = relationship("Bets4ProBets", back_populates="bet_type")
    d2by_bets = relationship("D2BYBets", back_populates="bet_type")
    fansport_bets = relationship("FanSportBets", back_populates="bet_type")
