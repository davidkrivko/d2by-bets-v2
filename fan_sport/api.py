import copy
import datetime
import json

import aiohttp

from config import DEFAULT_FAN_HEADERS, FAN_SPORT_DELTA

from database.bets import save_bets
from database.matches import save_match_data
from fan_sport.betsModel import betsModel

from fan_sport.tables import FanSportMatches
from fan_sport.tables import FanSportBets
from main_app.utils import teams_right_order

from utils import (
    update_team_name,
    are_teams_similar,
    remove_id_key,
    is_reversed,
    create_fan_sport_url,
    get_team_name,
    add_bet_to_cfs,
)


async def get_fan_sport_leagues(sport: int, is_live):
    if is_live:
        match_type = "LiveFeed"
    else:
        match_type = "LineFeed"

    async with aiohttp.ClientSession(headers=DEFAULT_FAN_HEADERS) as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetChampsZip?sport={sport}&lng=en",
            ssl=False
        ) as resp:
            response = await resp.text()
            leagues = json.loads(response)
    return leagues


async def get_fan_sport_league_matches(league_id, is_live):
    if is_live:
        match_type = "LiveFeed"
    else:
        match_type = "LineFeed"

    async with aiohttp.ClientSession(headers=DEFAULT_FAN_HEADERS) as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetChampZip?lng=en&champ={league_id}",
            ssl=False
        ) as resp:
            response = await resp.text()
            matches = json.loads(response)
    return matches


async def get_fan_sport_match_data(sub_match_id, is_live):
    if is_live:
        match_type = "LiveFeed"
    else:
        match_type = "LineFeed"

    async with aiohttp.ClientSession(headers=DEFAULT_FAN_HEADERS) as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetGameZip?id={sub_match_id}&lng=en",
            ssl=False
        ) as resp:
            response = await resp.text()
            data = json.loads(response)

    return data


async def collect_fan_sport_leagues(sport_id, match_type, lgs: set = None):
    leagues = await get_fan_sport_leagues(sport_id, match_type)

    if leagues["Success"]:
        leagues = leagues["Value"]

        if leagues:
            if lgs:
                res = {
                    league["LI"]
                    for league in leagues
                    for lg in lgs
                    if lg in league["L"].lower()
                }
            else:
                res = {league["LI"] for league in leagues}

            return res
        else:
            return set()
    else:
        return set()


async def collect_fan_sport_league_matches_v2(
    league_id: int, sport_id: int, is_live: str
):
    match_key = "I" if is_live else "CI"
    matches = await get_fan_sport_league_matches(league_id, is_live)

    if matches["Success"]:
        matches = matches["Value"]
        if not matches:
            return []
        matches = matches["G"]

        res = []
        for match in matches:
            team_1 = update_team_name(match["O1"])
            team_2 = update_team_name(match["O2"])
            team_1, team_2, _ = teams_right_order(team_1, team_2)

            res.append({
                "team_1": team_1,
                "team_2": team_2,
                "start_at": (
                        datetime.datetime.fromtimestamp(match["S"])
                        + datetime.timedelta(hours=FAN_SPORT_DELTA)
                ),
                "url": create_fan_sport_url(
                    is_live,
                    sport_id,
                    match.get("LI"),
                    match.get("L"),
                    match.get("I"),
                    match.get("O1"),
                    match.get("O2"),
                ),
                "sub_matches": ",".join([sub[match_key] for sub in match.get("SG", [])]),
                "is_live": is_live,
            })

        await save_match_data(matches, FanSportMatches)

        return res
    else:
        return []


async def get_fan_sport_bets(
    sub_match: int,
    is_live: bool,
    bet_types: dict,
):
    bets = await get_fan_sport_match_data(sub_match, is_live)

    if bets["Success"]:
        values = bets["Value"]

        n_map = values.get("P", None)
        if bets:
            bets = values["E"]

            cfs = {}
            for bet in bets:

                bet_model = betsModel.get(str(bet["T"]), {})

                bet_type = None
                for b_type in bet_types:
                    if bet_model["GN"] == b_type[3]:
                        bet_type = b_type[0]

                if bet_type:
                    value = bet.get("P", None)
                    bet_name = get_team_name(bet_model["N"], is_reverse)



                    if is_reverse:
                        if not d2by_bet[3] and not value:
                            add_bet_to_cfs(
                                cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                            )

                            # if d2by_bet[4] == 18:
                            #     if str(d2by_bet[10]) not in bet_model["GN"]:
                            #         add_bet_to_cfs(
                            #             cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                            #         )
                        else:
                            if value:
                                if abs(value) == d2by_bet[3]:
                                    if "handicap" in bet_model["GN"].lower():
                                        if (
                                            str(d2by_bet[10]) in bet_model["N"]
                                            and value == d2by_bet[3]
                                        ) or (
                                            str(d2by_bet[10]) not in bet_model["N"]
                                            and value == d2by_bet[3] * -1
                                        ):
                                            add_bet_to_cfs(
                                                cfs,
                                                d2by_bet[0],
                                                bet_name,
                                                bet["C"],
                                                fan_url,
                                            )
                                    elif "total" not in bet_model["GN"].lower():
                                        add_bet_to_cfs(
                                            cfs,
                                            d2by_bet[0],
                                            bet_name,
                                            bet["C"],
                                            fan_url,
                                        )
                    else:
                        if not d2by_bet[3] and not value:
                            add_bet_to_cfs(
                                cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                            )

                            # if d2by_bet[4] == 18:
                            #     if str(d2by_bet[10]) in bet_model["GN"]:
                            #         add_bet_to_cfs(
                            #             cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                            #         )
                        else:
                            if value:
                                if abs(value) == d2by_bet[3]:
                                    if "handicap" in bet_model["GN"].lower():
                                        if (
                                            str(d2by_bet[10]) in bet_model["N"]
                                            and value == d2by_bet[3] * -1
                                        ) or (
                                            str(d2by_bet[10]) not in bet_model["N"]
                                            and value == d2by_bet[3]
                                        ):
                                            add_bet_to_cfs(
                                                cfs,
                                                d2by_bet[0],
                                                bet_name,
                                                bet["C"],
                                                fan_url,
                                            )
                                    elif "total" not in bet_model["GN"].lower():
                                        add_bet_to_cfs(
                                            cfs,
                                            d2by_bet[0],
                                            bet_name,
                                            bet["C"],
                                            fan_url,
                                        )
                    if (
                        "total" in bet_model["GN"].lower()
                        and "handicap" not in bet_model["GN"].lower()
                    ):
                        if value == d2by_bet[3]:
                            bet_name = "Over" if "Over" in bet_name else "Under"
                            add_bet_to_cfs(
                                cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                            )

            bets_data = [cf for cf in cfs.values()]
            await save_bets(bets_data, FanSportBets)
