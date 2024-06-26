from d2by.tables import D2BYMatches
from database.connection import async_session
from sqlalchemy import select


async def get_d2by_matches():
    async with async_session() as session:
        try:
            select_stmt = select(D2BYMatches)
            result_set = await session.execute(select_stmt)
            return result_set.scalars().fetchall()
        except TimeoutError as te:
            print(f"Timeout error: {te}")
        except Exception as e:
            print(f"Error occurred: {e}")
