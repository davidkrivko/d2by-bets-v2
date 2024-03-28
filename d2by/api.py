import asyncio
import datetime
import json
import aiohttp

from config import D2BY_TIME_DELTA, DEFAULT_D2BY_HEADERS
from main_app.utils import teams_right_order
from telegram import send_telegram_message_v2
from utils import update_team_name


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
            team_1, team_2, _ = teams_right_order(team_1, team_2)

            matches.append(dict(
                d2by_id=match["id"],
                team_1=team_1,
                team_2=team_2,
                team_1_short=match["opponents"][0]["acronym"]
                if match["opponents"][0]["acronym"]
                else match["opponents"][0]["name"],
                team_2_short=match["opponents"][1]["acronym"]
                if match["opponents"][1]["acronym"]
                else match["opponents"][1]["name"],
                d2by_url=f"https://d2by.com/esports/{match['slug']}",
                start_at=datetime.datetime.strptime(
                    match["beginAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ) + datetime.timedelta(hours=D2BY_TIME_DELTA),
                game=match["videogame"]["name"],
            ))

    return matches


async def get_bets_of_d2by_match(match: dict, bet_types):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.d2by.com/api/v2/web/matchs/{match['d2by_id']}/markets",
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

    data = response["data"]

    tasks = [create_bet_v2(bet, match, bet_types) for bet in data]
    await asyncio.gather(*tasks)


async def create_bet_v2(bet_data: dict, match: dict, bet_types: list):
    bet_type = None
    for bt in bet_types:
        if bet_data["name"] in bt[2]:
            bet_type = bt["id"]

    selections = bet_data["selections"]

    if bet_type and selections:
        bet = dict(
            map=bet_data["gamePosition"],
            is_active=True if bet_data["status"] == "active" else False,
            type_id=bet_type,
            match_id=match["id"],
            d2by_id=bet_data["id"],
            cfs={},
            probs={},
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
            if selection["name"] == match["team_1_short"]:
                team = "1"
            elif selection["name"] == match["team_2_short"]:
                team = "2"
            else:
                team = selection["name"]
            bet["cfs"].update({team: cf})
            bet["probs"].update(
                {team: {"prob": prob, "position": selection["position"]}}
            )

        if "handicap" in bet_data["template"]:
            bet["side"] = 1 if selections[0]["handicap"] < 0 else 2
            bet["value"] = abs(selections[0]["handicap"])

        if "over-under" in bet_data["template"]:
            bet["value"] = float(bet_data["line"])

        return bet


async def make_bet(auth_token, data):
    headers = DEFAULT_D2BY_HEADERS
    headers["authorization"] = f"Bearer {auth_token['value']}"

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.post(
            "https://api.d2by.com/api/v2/web/matchs/predicts", json=[data],
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

            if response["meta"]["status"] == 200:
                return {"status": "Success", "market": data["market"]}
            else:
                return {"status": response["meta"]["internalMessage"], "market": data["market"]}


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

                await send_telegram_message_v2(message)
