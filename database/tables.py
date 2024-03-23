from sqlalchemy import Table, Column, Integer, String
from database.connection import meta


bets_types_table = Table(
    "bets_type",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String),
    Column("d2by_type", String, nullable=True),
    Column("fansport_type", String, nullable=True),
    Column("bets4pro_type", String, nullable=True),
    extend_existing=True
)
