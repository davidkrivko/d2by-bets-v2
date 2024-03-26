from database.connection import async_session
from sqlalchemy.exc import TimeoutError as SQLTimeoutError


async def save_match_data(matches_data: list, table):
    async with async_session() as session:
        for data in matches_data:

            match_statement = (
                table.select()
                .where(table.c.team_1 == data["team_1"], table.c.team_2 == data["team_2"])
                .limit(1)
            )
            try:
                result_set = await session.execute(match_statement)

                match = result_set.fetchone()
            except SQLTimeoutError:
                return
            except:
                match = None

            if match is None:
                insert_stmt = table.insert().values(
                    data,
                )
                try:
                    await session.execute(insert_stmt)
                    await session.commit()
                except SQLTimeoutError:
                    return
                except Exception as e:
                    pass

                main_match_data = {
                    "team_1": data["team_1"],
                    "team_2": data["team_2"],
                    "start_at": data["start_at"],
                }

                await save_match_data([main_match_data], table)
            else:
                update_stmt = table.update().where(table.c.id == match[0]).values(data)

                try:
                    await session.execute(update_stmt)
                    await session.commit()
                except SQLTimeoutError:
                    return
                except Exception as e:
                    pass
