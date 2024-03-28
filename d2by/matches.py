import pandas as pd
from sqlalchemy import text, select, func, and_
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from config import D2BY_TIME_DELTA
from database.connection import async_session


# async def get_d2by_live_matches():
#     query_cols = [
#         d2by_matches.c.id,
#         d2by_matches.c.team_1,
#         d2by_matches.c.team_2,
#         d2by_matches.c.team_1_short,
#         d2by_matches.c.team_2_short,
#         d2by_matches.c.start_time,
#         d2by_matches.c.d2by_id,
#     ]
#     cols = [
#         "id",
#         "team_1",
#         "team_2",
#         "team_1_short",
#         "team_2_short",
#         "start_time",
#         "d2by_id",
#     ]
#
#     fifteen_minutes_ago = func.now() + text("INTERVAL '5 minutes'") + text(f"INTERVAL '{D2BY_TIME_DELTA} hours'")
#
#     async with async_session() as session:
#         select_query = (
#             select(*query_cols)
#             .select_from(d2by_matches)
#             .where(d2by_matches.c.start_time <= fifteen_minutes_ago)
#         )
#
#         try:
#             result_set = await session.execute(select_query)
#             res = result_set.fetchall()
#         except SQLTimeoutError:
#             return []
#
#         df = pd.DataFrame(columns=cols, data=res)
#
#         return df.to_dict(orient="records")
#
#
# async def get_d2by_line_matches(is_all: bool = False):
#     query_cols = [
#         d2by_matches.c.id,
#         d2by_matches.c.team_1,
#         d2by_matches.c.team_2,
#         d2by_matches.c.team_1_short,
#         d2by_matches.c.team_2_short,
#         d2by_matches.c.start_time,
#         d2by_matches.c.d2by_id,
#     ]
#     cols = [
#         "id",
#         "team_1",
#         "team_2",
#         "team_1_short",
#         "team_2_short",
#         "start_time",
#         "d2by_id",
#     ]
#
#     fifteen_minutes_ago = func.now() + text(f"INTERVAL '{D2BY_TIME_DELTA} hours'")
#     three_hours_more = func.now() + text("INTERVAL '3 hours'") + text(f"INTERVAL '{D2BY_TIME_DELTA} hours'")
#
#     async with async_session() as session:
#         if is_all:
#             select_query = (
#                 select(*query_cols)
#                 .select_from(d2by_matches)
#                 .where(
#                     d2by_matches.c.start_time > fifteen_minutes_ago,
#                 )
#             )
#         else:
#             select_query = (
#                 select(*query_cols)
#                 .select_from(d2by_matches)
#                 .where(
#                     and_(
#                         d2by_matches.c.start_time > fifteen_minutes_ago,
#                         d2by_matches.c.start_time < three_hours_more
#                     )
#                 )
#             )
#
#         try:
#             result_set = await session.execute(select_query)
#             res = result_set.fetchall()
#         except SQLTimeoutError:
#             return []
#         except Exception as e:
#             pass
#
#         df = pd.DataFrame(columns=cols, data=res)
#
#         return df.to_dict(orient="records")
