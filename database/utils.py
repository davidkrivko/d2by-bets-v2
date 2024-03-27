from database.connection import engine, Base


async def create_all_tables():
    import database.tables
    import bets4pro.tables
    import d2by.tables

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
