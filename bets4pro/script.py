import asyncio
import itertools

from bets4pro.api import get_html_matches, get_match_data, get_match_bets
from database.bets import get_bet_types
from bets4pro.matches import get_matches_ids
from bets4pro.tables import Bets4ProBets
from database.bets import save_bets
from database.matches import save_match_data


async def update_matches():
    live_blocks, upcoming_blocks = await get_html_matches()

    matches = []
    for i, blocks in enumerate([live_blocks, upcoming_blocks]):
        for block in blocks:
            if i == 0:
                matches.append(get_match_data(block, True))
            else:
                matches.append(get_match_data(block))

    teams = set()
    unique_matches = []
    for match in matches:
        team_1 = match['team_1']
        team_2 = match['team_2']
        m_teams = (team_1, team_2)
        if m_teams in teams:
            continue
        else:
            unique_matches.append(match)
            teams.add(m_teams)

    await save_match_data(unique_matches)


async def update_bets():
    matches = await get_matches_ids()
    bet_types = await get_bet_types()

    tasks = [get_match_bets(match, bet_types) for match in matches]
    bets = await asyncio.gather(*tasks)
    bets = list(itertools.chain(*bets))

    await save_bets(list(bets), Bets4ProBets)


if __name__ == "__main__":
    asyncio.run(update_bets())
