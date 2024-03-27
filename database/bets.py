import asyncio

from sqlalchemy import select, update, insert
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.connection import async_session
from database.tables import BetsType


async def get_bet_types():
    async with async_session() as session:
        try:
            # Select all rows from the BetsType table
            stmt = select(BetsType)
            result = await session.execute(stmt)
            bet_types = result.scalars().all()
            return bet_types
        except Exception as e:
            # Handle exceptions
            print(f"An error occurred: {e}")


async def get_bets_ids(table):
    async with async_session() as session:
        select_stmt = (
            select(table)
            .with_only_columns(
                *[
                    table.id,
                    table.match_id,
                    table.type_id
                ])
        )
        try:
            result_set = await session.execute(select_stmt)
            return result_set.scalars().all()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass


async def save_bets(bets_data: list, table):
    bets_ids = await get_bets_ids(table)

    update_bets = []
    create_bets = bets_data.copy()
    for bet_id in bets_ids:
        for bet_data in bets_data:
            if (
                    bet_data["match_id"] == bet_id[1]
                    and bet_data["type_id"] == bet_id[2]
            ):
                create_bets.remove(bet_data)

                bet_data["id"] = bet_id[0]
                update_bets.append(bet_data)

    async with async_session() as session:
        update_stmts = []
        for bet in update_bets:
            update_stmt = (
                update(table)
                .where(
                    table.id == bet["id"]
                )
                .values(bet)
            )
            update_stmts.append(session.execute(update_stmt))

        try:
            await asyncio.gather(*update_stmts)
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass

        try:
            insert_stmt = insert(table).values(create_bets)
            await session.execute(insert_stmt)
            await session.commit()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass
