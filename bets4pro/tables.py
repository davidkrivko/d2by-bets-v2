from sqlalchemy import (
    Table,
    Column,
    String,
    Integer,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import JSONB

from database.connection import meta
from database.tables import bets_types_table


bets4pro_table = Table(
    "bets4pro",
    meta,
    Column("id", Integer, primary_key=True),
    Column("team_1", String),
    Column("team_2", String),
    Column("match_id", String),
    Column("start_time", TIMESTAMP),
    Column("is_live", Boolean),
    Column("url", String),
    extend_existing=True
)


bets4pro_bets_table = Table(
    "bets4pro_bets",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("cfs", JSONB, nullable=True),
    Column("map", Integer, nullable=True),
    Column("side", Integer, nullable=True),
    Column("value", Numeric, nullable=True),
    Column("type_id", ForeignKey(bets_types_table.c.id, ondelete="CASCADE")),
    Column("match_id", ForeignKey(bets4pro_table.c.id, ondelete="CASCADE")),
    Column("is_live", Boolean),
    Column("is_active", Boolean),
    extend_existing=True
)
