from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, Numeric
from sqlalchemy.dialects.postgresql import JSONB
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
    additional_data = Column(JSON)

    bets4pro_bets = relationship("bets4pro.tables.Bets4ProBets")
    d2by_bets = relationship("d2by.tables.D2BYBets")
    fansport_bets = relationship("fan_sport.tables.FanSportBets")

    bets4pro_matches = relationship("bets4pro.tables.Bets4ProMatches")
    d2by_matches = relationship("d2by.tables.D2BYMatches")
    fansport_matches = relationship("fan_sport.tables.FanSportMatches")


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


class BetsHistory(Base):
    __tablename__ = 'bets_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)

    team_1 = Column(String)
    team_2 = Column(String)
    start_at = Column(TIMESTAMP)

    map = Column(Integer, nullable=True)
    side = Column(Integer, nullable=True)
    value = Column(Numeric, nullable=True)
    type_id = Column(Integer)

    bets4pro_cfs = Column(JSONB, default={})
    d2by_cfs = Column(JSONB, default={})
    fan_cfs = Column(JSONB, default={})
    bet = Column(String)
    site = Column(String)

    d2by_url = Column(String)
    bets4pro_url = Column(String)
    d2by_type = Column(String, nullable=True)

    bet_cf = Column(Numeric)
    amount = Column(Numeric)
