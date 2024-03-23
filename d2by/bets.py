from sqlalchemy import and_, select

from database.v2.connection import async_session_2 as async_session
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.v2.tables import bets_table, bets_type, d2by_matches


def compare_bet_cfs_v2(data, bet):
    return (
        data.get("d2by_bets") != bet[4]
        or bet[1] != data["isActive"]
    )


async def get_bets_of_match(match_id: int, map_number):
    async with async_session() as session:
        type_join_stmt = bets_table.join(
            bets_type, bets_table.c.type_id == bets_type.c.id
        )
        match_join_stmt = type_join_stmt.join(
            d2by_matches, bets_table.c.match_id == d2by_matches.c.id
        )

        # Create the select query
        select_query = (
            select(
                *[
                    bets_table.c.id,
                    bets_table.c.d2by_bets,
                    bets_table.c.map_v2,
                    bets_table.c["value"].label("bet_values"),
                    bets_type.c.id.label("type_id"),
                    bets_type.c.fan_sport_bet_type,
                    bets_type.c.fan_sport_bet_type_football,
                    d2by_matches.c.id.label("match_id"),
                    d2by_matches.c.team_1,
                    d2by_matches.c.team_2,
                    bets_table.c.above_bets,
                    bets_type.c.description,
                ]
            )
            .select_from(match_join_stmt)
            .where(
                (bets_table.c.match_id == match_id)
                & (bets_table.c.map_v2 == map_number)
                & (bets_table.c.isActive == True)
            )
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        return res


async def add_bet(data: dict):
    async with async_session() as session:
        try:
            select_query = bets_table.select().where(
                and_(
                    bets_table.c.type_id == data["type_id"],
                    bets_table.c.match_id == data["match_id"],
                    bets_table.c.value == data.get("value"),
                    bets_table.c.map_v2 == data.get("map_v2"),
                    bets_table.c.above_bets == data.get("above_bets"),
                    bets_table.c.extra == data.get("extra"),
                ),
            )

            result_set = await session.execute(select_query)
            bet = result_set.fetchone()
        except Exception as e:
            return

        try:
            # If bet does not exist, insert it
            if not bet:
                insert_stmt = bets_table.insert().values(data)
                await session.execute(insert_stmt)
            elif bet:
                if compare_bet_cfs_v2(data, bet):
                    data["is_shown"] = False

                    update_stmt = (
                        bets_table.update().where(bets_table.c.id == bet[0]).values(data)
                    )
                    await session.execute(update_stmt)

            await session.commit()
        except SQLTimeoutError:
            return await add_bet(data)
