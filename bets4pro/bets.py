import asyncio
from sqlalchemy import and_

from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.v2.connection import async_session_2 as async_session
from database.v2.tables import bets_types_v2_table
from tables import bets4pro_bets_table


async def get_bet_types():
    async with async_session() as session:
        select_stmt = bets_types_v2_table.select()
        try:
            result_set = await session.execute(select_stmt)
            return result_set.fetchall()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass


async def get_bets_ids():
    async with async_session() as session:
        select_stmt = (
            bets4pro_bets_table
            .select()
            .with_only_columns(
                *[
                    bets4pro_bets_table.c.id,
                    bets4pro_bets_table.c.match_id,
                    bets4pro_bets_table.c.type_id
                ])
        )
        try:
            result_set = await session.execute(select_stmt)
            return result_set.fetchall()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass


async def add_bet(data: dict):
    async with async_session() as session:
        try:
            select_query = bets4pro_bets_table.select().where(
                and_(
                    bets4pro_bets_table.c.type_id == data["type_id"],
                    bets4pro_bets_table.c.match_id == data["match_id"],
                    bets4pro_bets_table.c.value == data.get("value"),
                    bets4pro_bets_table.c.map_v2 == data.get("map_v2"),
                    bets4pro_bets_table.c.above_bets == data.get("above_bets"),
                    bets4pro_bets_table.c.extra == data.get("extra"),
                ),
            )

            result_set = await session.execute(select_query)
            bet = result_set.fetchone()
        except Exception as e:
            return

        try:
            # If bet does not exist, insert it
            if not bet:
                insert_stmt = bets4pro_bets_table.insert().values(data)
                await session.execute(insert_stmt)
            elif bet:
                update_stmt = (
                    bets4pro_bets_table.update().where(bets4pro_bets_table.c.id == bet[0]).values(data)
                )
                await session.execute(update_stmt)

            await session.commit()
        except SQLTimeoutError:
            return await add_bet(data)


async def save_bets(bets_data: list):
    bets_data_ids = await get_bets_ids()

    async with async_session() as session:
        update_stmts = []
        for bet in bets_data:
            update_stmt = (
                bets4pro_bets_table
                .update()
                .where(
                    bets4pro_bets_table.c.type_id == bet['type_id']
                    and bets4pro_bets_table.c.match_id == bet['match_id']
                )
                .values(bet)
            )
            update_stmts.append(session.execute(update_stmt))

        try:
            updated_bets = await asyncio.gather(*update_stmts)
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass

        try:
            insert_stmt = bets4pro_bets_table.insert().values(bets_data)
            await session.execute(insert_stmt)
            await session.commit()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass
