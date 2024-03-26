import asyncio
import itertools

from bets4pro.api import get_html_matches, get_match_data, get_match_bets
from bets4pro.bets import get_bet_types
from bets4pro.matches import get_matches_ids
from bets4pro.tables import Bets4ProBets, Bets4ProMatches
from database.bets import save_bets
from database.matches import save_match_data


async def update_matches():
    live_blocks, upcoming_blocks = await get_html_matches()

    tasks = []
    for i, blocks in enumerate([live_blocks, upcoming_blocks]):
        for block in blocks:
            if i == 0:
                tasks.append(get_match_data(block, True))
            else:
                tasks.append(get_match_data(block))

    matches = await asyncio.gather(*tasks)
    await save_match_data(list(matches), Bets4ProMatches)


async def update_bets():
    matches = await get_matches_ids()
    bet_types = await get_bet_types()

    tasks = [get_match_bets(match, bet_types) for match in matches]
    bets = await asyncio.gather(*tasks)
    bets = list(itertools.chain(*bets))

    await save_bets(list(bets), Bets4ProBets)


if __name__ == "__main__":
    asyncio.run(update_matches())
