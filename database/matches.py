from database.connection import async_session
from sqlalchemy.dialects.postgresql import insert


async def save_match_data(matches_data: list, table):
    async with async_session() as session:
        try:
            cols = table.__table__.columns.keys()

            stmt = insert(table).values(matches_data)
            set_ = {field: getattr(stmt.excluded, field) for field in cols}

            stmt = stmt.on_conflict_do_update(
                constraint=f'{table.__table__.name}_unique_constrain',
                set_=set_
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            print(e)
