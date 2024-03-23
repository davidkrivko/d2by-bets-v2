from database.connection import db, meta


async def create_all_tables():
    from database import tables
    from d2by import tables
    from bets4pro import tables

    async with db.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)
