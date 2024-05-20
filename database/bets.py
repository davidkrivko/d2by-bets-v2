import asyncio

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.connection import async_session
from database.tables import BetsType


async def save_bets(bets_data: list, table):
    async with async_session() as session:
        try:
            cols = table.__table__.columns.keys()

            stmt = insert(table).values(bets_data)
            set_ = {field: getattr(stmt.excluded, field) for field in cols if field not in ("id", "is_shown")}

            stmt = stmt.on_conflict_do_update(
                constraint=f'{table.__table__.name}_unique_constrain',
                set_=set_
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            print(e)


async def get_bet_types():
    async with async_session() as session:
        try:
            # Select all rows from the BetsType table
            stmt = select(BetsType)
            result = await session.execute(stmt)
            bet_types = result.scalars().all()
            return bet_types
        except Exception as e:
            # Handle exceptions
            print(f"An error occurred: {e}")


async def get_bets_ids(table):
    async with async_session() as session:
        select_stmt = (
            select(table)
            .with_only_columns(
                *[
                    table.id,
                    table.match_id,
                    table.type_id
                ])
        )
        try:
            result_set = await session.execute(select_stmt)
            return result_set.scalars().all()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass
