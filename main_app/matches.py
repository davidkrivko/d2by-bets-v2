from datetime import datetime, timedelta

from database.connection import async_session
from sqlalchemy import select, delete

from database.tables import Match


async def get_matches():
    end_time = datetime.now() + timedelta(hours=3)

    async with async_session() as session:
        try:
            select_stmt = select(Match).where(Match.start_at <= end_time)
            result_set = await session.execute(select_stmt)
            return result_set.scalars().fetchall()
        except TimeoutError as te:
            print(f"Timeout error: {te}")
        except Exception as e:
            print(f"Error occurred: {e}")


async def delete_old_matches():
    delete_time = datetime.now() - timedelta(hours=7)

    async with async_session() as session:
        try:
            select_stmt = delete(Match).where(Match.start_at <= delete_time)
            result_set = await session.execute(select_stmt)
            await session.commit()
        except TimeoutError as te:
            print(f"Timeout error: {te}")
        except Exception as e:
            print(f"Error occurred: {e}")
