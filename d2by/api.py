import asyncio
import datetime
import json
import aiohttp

from config import D2BY_TIME_DELTA, DEFAULT_D2BY_HEADERS
from main_app.utils import teams_right_order
from telegram import send_telegram_message
from main_app.utils import update_team_name


async def collect_d2by_v2_matches():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.d2by.com/api/v2/web/matchs?pageSize=1000&sort=scheduledAt&status=pre_match,live",
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

    data = response["data"]["datas"]

    matches = []
    for match in data:
        if not match.get("endAt"):
            team_1 = match["opponents"][0]["name"]
            team_2 = match["opponents"][1]["name"]
            team_1 = update_team_name(team_1)
            team_2 = update_team_name(team_2)
            team_1, team_2, is_reverse = teams_right_order(team_1, team_2)

            if is_reverse:
                if match["opponents"][1]["acronym"]:
                    team_1_short = match["opponents"][1]["acronym"]
                else:
                    team_1_short = match["opponents"][1]["name"]

                if match["opponents"][0]["acronym"]:
                    team_2_short = match["opponents"][0]["acronym"]
                else:
                    team_2_short = match["opponents"][0]["name"]
            else:
                if match["opponents"][1]["acronym"]:
                    team_2_short = match["opponents"][1]["acronym"]
                else:
                    team_2_short = match["opponents"][1]["name"]

                if match["opponents"][0]["acronym"]:
                    team_1_short = match["opponents"][0]["acronym"]
                else:
                    team_1_short = match["opponents"][0]["name"]

            matches.append(dict(
                team_1=team_1,
                team_2=team_2,
                start_at=datetime.datetime.strptime(
                    match["beginAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ) + datetime.timedelta(hours=D2BY_TIME_DELTA),
                additional_data=dict(
                    d2by_id=match["id"],
                    team_1_short=team_1_short,
                    team_2_short=team_2_short,
                    url=f"https://d2by.com/esports/{match['slug']}",
                    game=match["videogame"]["name"],
                    site="d2by",
                ),
            ))

    return matches


async def get_bets_of_d2by_match(match, bet_types):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.d2by.com/api/v2/web/matchs/{match.d2by_id}/markets",
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

    data = response["data"]

    tasks = [create_bet_v2(bet, match, bet_types) for bet in data]
    return await asyncio.gather(*tasks)


async def create_bet_v2(bet_data: dict, match, bet_types: list):
    bet_type = None
    for bt in bet_types:
        if bet_data["template"] in bt.d2by_type:
            bet_type = bt.id
            break

    selections = bet_data["selections"]

    if bet_type and selections:
        bet = dict(
            map=bet_data["gamePosition"],
            is_active=True if bet_data.get("status") == "active" and bet_data.get("reviewed") else False,
            type_id=bet_type,
            match_id=match.match_id,
            d2by_id=bet_data["id"],
            cfs={},
            probs={},
            is_shown=False,
            value=None,
            side=None,
        )

        for selection in selections:
            prob = (
                1
                if selection["probability_with_margin"] == 0
                else selection["probability_with_margin"]
            )
            prob = (
                1
                if prob is None
                else prob
            )
            cf = round(1 / prob, 3)

            is_reverse = False
            if selection["name"] == match.team_1_short:
                if selection["participant_side"] == "home":
                    is_reverse = False
                else:
                    is_reverse = True

                team = "1"
            elif selection["name"] == match.team_2_short:
                if selection["participant_side"] == "away":
                    is_reverse = False
                else:
                    is_reverse = True

                team = "2"
            else:
                team = selection["name"]
            bet["cfs"].update({team: cf})
            bet["probs"].update(
                {team: {"prob": prob, "position": selection["position"]}}
            )

        if "handicap" in bet_data["template"]:
            bet["side"] = 1 if (selections[0]["handicap"] < 0 and not is_reverse) or (selections[0]["handicap"] > 0 and is_reverse) else 2
            bet["value"] = abs(selections[0]["handicap"])

        if "over-under" in bet_data["template"]:
            bet["value"] = float(bet_data["line"])

        return bet


async def make_bet(auth_token, data, bet_id):
    headers = DEFAULT_D2BY_HEADERS
    headers["authorization"] = f"Bearer {auth_token['value']}"

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.post(
            "https://api.d2by.com/api/v2/web/matchs/predicts", json=data,
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

            if response["meta"]["status"] == 200:
                return bet_id
            else:
                return 0


async def get_balance(auth_token):
    headers = DEFAULT_D2BY_HEADERS
    headers["Authorization"] = f"Bearer {auth_token['value']}"

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.get(
            "https://api.d2by.com/api/v1/web/user/profile",
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

            if response["meta"]["status"] == 200:
                gold = round(response["data"]["coin"]["gold"], 2)
                gem = round(response["data"]["coin"]["gem"], 2)
                diamond = round(response["data"]["coin"]["diamond"], 2)

                message = f"GOLD: {gold}\nDIAMOND: {diamond}\nGEM: {gem}"

                await send_telegram_message(message)
