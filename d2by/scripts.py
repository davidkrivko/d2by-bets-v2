import asyncio

from d2by.api import collect_d2by_v2_matches
from d2by.tables import D2BYMatches
from database.matches import save_match_data


async def update_matches():
    matches = await collect_d2by_v2_matches()
    await save_match_data(list(matches), D2BYMatches)


if __name__ == "__main__":
    asyncio.run(update_matches())
