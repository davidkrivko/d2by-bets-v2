from sqlalchemy import (
    Table,
    Column,
    String,
    Numeric,
    Integer,
    TIMESTAMP,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB

from database.connection import meta
from database.tables import bets_types_table


d2by_matches = Table(
    "d2by_matches",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("team_1", String),
    Column("team_2", String),
    Column("start_time", TIMESTAMP),
    Column("game", String),
    Column("team_1_short", String, nullable=True),
    Column("team_2_short", String, nullable=True),
    Column("d2by_id", String, nullable=True),
    Column("d2by_url", String, nullable=True),
    extend_existing=True,
)


d2by_bets_table = Table(
    "d2by_bets",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("cfs", JSONB, default={}),
    Column("probs", JSONB, default={}),
    Column("value", Numeric(precision=5, scale=1)),
    Column("side", Integer, nullable=True),
    Column("map", Integer, nullable=True),
    Column("type_id", ForeignKey(bets_types_table.c.id, ondelete="CASCADE")),
    Column("match_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE")),
    Column("d2by_id", String),
    Column("is_active", Boolean),
    extend_existing=True,
)
