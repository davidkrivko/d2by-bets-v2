from sqlalchemy import select

from database.connection import async_session
from tables import Bets4ProMatches
from sqlalchemy.exc import TimeoutError as SQLTimeoutError


async def get_matches_ids():
    async with async_session() as session:
        select_stmt = (
            select(Bets4ProMatches.id)
        )
        try:
            result_set = await session.execute(select_stmt)
            return result_set.fetchall()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass
