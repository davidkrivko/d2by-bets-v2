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


class Bets4ProMatches(Base):
    __tablename__ = 'bets4pro_matches'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_1 = Column(String)
    team_2 = Column(String)
    match_id = Column(Integer, ForeignKey('matches.id', ondelete="CASCADE"))
    start_at = Column(TIMESTAMP)
    is_live = Column(Boolean)
    url = Column(String, nullable=True)

    match = relationship("Match", back_populates="bets4pro_matches")


class Bets4ProBets(Base):
    __tablename__ = 'bets4pro_bets'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cfs = Column(JSONB, nullable=True)
    map = Column(Integer, nullable=True)
    side = Column(Integer, nullable=True)
    value = Column(Numeric, nullable=True)
    type_id = Column(Integer, ForeignKey('bets_type.id', ondelete="CASCADE"))
    match_id = Column(Integer, ForeignKey('matches.id', ondelete="CASCADE"))
    is_live = Column(Boolean)
    is_active = Column(Boolean)

    bet_type = relationship("BetsType", back_populates="bets4pro_bets")
    match = relationship("Match", back_populates="bets4pro_bets")
