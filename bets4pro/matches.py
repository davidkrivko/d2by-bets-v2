from sqlalchemy import select

from database.connection import async_session
from bets4pro.tables import Bets4ProMatches


async def get_matches_ids():
    async with async_session() as session:
        try:
            select_stmt = select(Bets4ProMatches)
            result_set = await session.execute(select_stmt)
            return result_set.scalars().fetchall()
        except TimeoutError as te:
            print(f"Timeout error: {te}")
        except Exception as e:
            print(f"Error occurred: {e}")
