import asyncio
import itertools

from bets4pro.api import get_html_matches, get_match_data, get_match_bets
from bets4pro.bets import get_bet_types, save_bets
from bets4pro.matches import save_match_data, get_matches_ids


async def update_matches():
    live_blocks, upcoming_blocks = get_html_matches()

    tasks = []
    for i, blocks in enumerate([live_blocks, upcoming_blocks]):
        for block in blocks:
            if i == 0:
                tasks.append(get_match_data(block, True))
            else:
                tasks.append(get_match_data(block))

    matches = await asyncio.gather(*tasks)
    await save_match_data(list(matches))


async def update_bets():
    matches = await get_matches_ids()
    matches = [{"id": match_id[0]} for match_id in matches]

    bet_types = await get_bet_types()

    tasks = [get_match_bets(match, bet_types) for match in matches]
    bets = await asyncio.gather(*tasks)
    bets = list(itertools.chain(*bets))

    await save_bets(list(bets))


if __name__ == "__main__":
    asyncio.run(update_bets())
