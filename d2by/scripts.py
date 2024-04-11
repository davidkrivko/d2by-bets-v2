import asyncio
import itertools

from d2by.api import collect_d2by_v2_matches, get_bets_of_d2by_match
from d2by.matches import get_d2by_matches
from d2by.tables import D2BYMatches, D2BYBets
from database.bets import get_bet_types, save_bets
from database.matches import save_match_data


async def update_matches():
    matches = await collect_d2by_v2_matches()

    uni_matches = []
    uni_teams = set([(data["team_1"], data["team_2"]) for data in matches])
    for match in matches:
        if (match["team_1"], match["team_2"]) in uni_teams:
            uni_matches.append(match)
            uni_teams.remove((match["team_1"], match["team_2"]))

    await save_match_data(list(uni_matches))


async def update_bets():
    matches = await get_d2by_matches()
    bet_types = await get_bet_types()

    bets_tasks = [get_bets_of_d2by_match(match, bet_types) for match in matches]

    bets = await asyncio.gather(*bets_tasks)
    bets_data = list(itertools.chain(*bets))
    bets_data = [bet_data for bet_data in bets_data if bet_data is not None]

    await save_bets(bets_data, D2BYBets)


if __name__ == "__main__":
    asyncio.run(update_bets())
