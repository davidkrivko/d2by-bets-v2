from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    TIMESTAMP,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from database.connection import Base


class D2BYMatches(Base):
    __tablename__ = 'd2by_matches'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_1 = Column(String)
    team_2 = Column(String)
    start_at = Column(TIMESTAMP)
    game = Column(String)
    team_1_short = Column(String, nullable=True)
    team_2_short = Column(String, nullable=True)
    match_id = Column(Integer, ForeignKey('matches.id', ondelete="CASCADE"))
    d2by_id = Column(String, nullable=True)
    url = Column(String, nullable=True)

    match = relationship("database.tables.Match", overlaps="d2by_matches")


class D2BYBets(Base):
    __tablename__ = 'd2by_bets'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cfs = Column(JSONB, default={})
    probs = Column(JSONB, default={})
    value = Column(Float, nullable=True)
    side = Column(Integer, nullable=True)
    map = Column(Integer, nullable=True)
    is_shown = Column(Boolean)
    type_id = Column(Integer, ForeignKey('bets_type.id', ondelete="CASCADE"))
    match_id = Column(Integer, ForeignKey('matches.id', ondelete="CASCADE"))
    d2by_id = Column(String)
    is_active = Column(Boolean)

    bet_type = relationship("database.tables.BetsType", overlaps="d2by_bets")
    match = relationship("database.tables.Match", overlaps="d2by_bets")
