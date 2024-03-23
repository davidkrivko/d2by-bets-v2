from database.v2.connection import async_session_2 as async_session
from tables import bets4pro_table
from sqlalchemy.exc import TimeoutError as SQLTimeoutError


async def save_match_data(match_data: list):
    async with async_session() as session:
        delete_stmt = bets4pro_table.delete()
        try:
            await session.execute(delete_stmt)
            await session.commit()
        except SQLTimeoutError:
            pass

        insert_stmt = bets4pro_table.insert().values(match_data)
        try:
            await session.execute(insert_stmt)
            await session.commit()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass


async def get_matches_ids():
    async with async_session() as session:
        select_stmt = (
            bets4pro_table
            .select()
            .with_only_columns(*[bets4pro_table.c.id])
        )
        try:
            result_set = await session.execute(select_stmt)
            return result_set.fetchall()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass
