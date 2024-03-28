from sqlalchemy import Column, Integer, String, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import relationship

from database.connection import Base


class Match(Base):
    __tablename__ = 'matches'
    __table_args__ = {
        'extend_existing': True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_1 = Column(String)
    team_2 = Column(String)
    start_at = Column(TIMESTAMP)

    bets4pro_bets = relationship("bets4pro.tables.Bets4ProBets")
    d2by_bets = relationship("d2by.tables.D2BYBets")
    fansport_bets = relationship("fan_sport.tables.FanSportBets")


class BetsType(Base):
    __tablename__ = 'bets_type'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    d2by_type = Column(String, nullable=True)
    fansport_type = Column(String, nullable=True)
    bets4pro_type = Column(String, nullable=True)

    bets4pro_bets = relationship("bets4pro.tables.Bets4ProBets")
    d2by_bets = relationship("d2by.tables.D2BYBets")
    fansport_bets = relationship("fan_sport.tables.FanSportBets")
