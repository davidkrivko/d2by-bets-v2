from sqlalchemy import and_, select

from sqlalchemy.exc import TimeoutError as SQLTimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import async_session
from database.tables import BetsType


# async def add_bet(data: dict):
#     async with async_session() as session:
#         try:
#             select_query = bets4pro_bets_table.select().where(
#                 and_(
#                     bets4pro_bets_table.c.type_id == data["type_id"],
#                     bets4pro_bets_table.c.match_id == data["match_id"],
#                     bets4pro_bets_table.c.value == data.get("value"),
#                     bets4pro_bets_table.c.map_v2 == data.get("map_v2"),
#                     bets4pro_bets_table.c.above_bets == data.get("above_bets"),
#                     bets4pro_bets_table.c.extra == data.get("extra"),
#                 ),
#             )
#
#             result_set = await session.execute(select_query)
#             bet = result_set.fetchone()
#         except Exception as e:
#             return
#
#         try:
#             # If bet does not exist, insert it
#             if not bet:
#                 insert_stmt = bets4pro_bets_table.insert().values(data)
#                 await session.execute(insert_stmt)
#             elif bet:
#                 update_stmt = (
#                     bets4pro_bets_table.update().where(bets4pro_bets_table.c.id == bet[0]).values(data)
#                 )
#                 await session.execute(update_stmt)
#
#             await session.commit()
#         except SQLTimeoutError:
#             return await add_bet(data)
