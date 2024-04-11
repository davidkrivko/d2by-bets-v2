from database.connection import async_session
from sqlalchemy.dialects.postgresql import insert

from database.tables import Match


async def save_match_data(matches_data: list):
    async with async_session() as session:
        try:
            stmt = insert(Match).values(matches_data)
            on_conflict_stmt = stmt.on_conflict_do_update(
                constraint='matches_unique_constrain',
                set_={k.name: getattr(stmt.excluded, k.name) for k in Match.__table__.columns if k.name != 'id'}
            )
            await session.execute(on_conflict_stmt)
            await session.commit()
        except Exception as e:
            print(e)
