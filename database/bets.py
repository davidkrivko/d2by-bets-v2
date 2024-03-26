import asyncio

from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.connection import async_session


async def get_bets_ids(table):
    async with async_session() as session:
        select_stmt = (
            table
            .select()
            .with_only_columns(
                *[
                    table.c.id,
                    table.c.match_id,
                    table.c.type_id
                ])
        )
        try:
            result_set = await session.execute(select_stmt)
            return result_set.fetchall()
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
                table
                .update()
                .where(
                    table.c.id == bet["id"]
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
            insert_stmt = table.insert().values(create_bets)
            await session.execute(insert_stmt)
            await session.commit()
        except SQLTimeoutError:
            pass
        except Exception as e:
            pass
