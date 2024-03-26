from database.connection import engine, metadata


async def create_all_tables():
    import database.tables
    import bets4pro.tables
    import d2by.tables

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
