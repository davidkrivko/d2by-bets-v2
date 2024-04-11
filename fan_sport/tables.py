from sqlalchemy import (
    Column,
    String,
    Integer,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


class FanSportMatches(Base):
    __tablename__ = 'fansport_matches'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_1 = Column(String)
    team_2 = Column(String)
    sub_matches = Column(String)
    match_id = Column(Integer, ForeignKey('matches.id', ondelete="CASCADE"))
    start_at = Column(TIMESTAMP)
    is_live = Column(Boolean)
    url = Column(String)

    match = relationship("database.tables.Match", overlaps="fansport_matches")


class FanSportBets(Base):
    __tablename__ = 'fansport_bets'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cfs = Column(JSONB, nullable=True)
    map = Column(Integer, nullable=True)
    side = Column(Integer, nullable=True)
    value = Column(Numeric, nullable=True)
    match_id = Column(Integer, ForeignKey('matches.id', ondelete="CASCADE"))
    type_id = Column(Integer, ForeignKey('bets_type.id', ondelete="CASCADE"))
    is_active = Column(Boolean)

    bet_type = relationship("database.tables.BetsType", overlaps="fansport_bets")
    match = relationship("database.tables.Match", overlaps="fansport_bets")
