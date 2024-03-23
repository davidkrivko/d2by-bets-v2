from d2by.api import collect_d2by_v2_matches


async def update_matches():
    matches = await collect_d2by_v2_matches()

    matches = await asyncio.gather(*tasks)
    await save_match_data(list(matches))
