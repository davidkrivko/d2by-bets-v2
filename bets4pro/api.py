import datetime
import json
import jwt
import aiohttp

from bs4 import BeautifulSoup

from bets4pro.login import create_new_token
from config import SECRET_KEY, DEFAULT_BETS4PRO_HEADERS, BETS4PRO_DELTA
from main_app.utils import teams_right_order
from main_app.utils import update_team_name


async def get_match_bets(match, bet_types):
    async with aiohttp.ClientSession(headers=DEFAULT_BETS4PRO_HEADERS) as session:
        async with session.get(
            f"https://bets4.org/widget/cofs_api.php?tournament_id={match.bets4pro_id}",
            ssl=False
        ) as resp:
            response = await resp.text()
            bets = json.loads(response)

            all_bets = []
            if len(bets["response"]) > 0:
                bets = bets["response"]["cofs"]
                for bet in bets:
                    b_type = bet["type"]

                    type_id = None
                    for t in bet_types:
                        if b_type in str(t.bets4pro_type):
                            type_id = t.id
                            break

                    map = None
                    side = None
                    value = None
                    if "game" in b_type:
                        map = int(b_type.split("game")[1])
                    elif "hc" in b_type:
                        side = int(b_type.split("hc")[-1])
                        value = float(bet["show_type"].split()[-1])

                        if value > 0:
                            side = 1 if side == 2 else 2

                    if type_id is None:
                        continue

                    if not match.is_reverse:
                        cfs_data = {
                            "1": round(1 + bet["team_1_cof"], 3),
                            "2": round(1 + bet["team_2_cof"], 3),
                        }
                    else:
                        cfs_data = {
                            "1": round(1 + bet["team_2_cof"], 3),
                            "2": round(1 + bet["team_1_cof"], 3),
                        }
                        if 'hc' in b_type:
                            side = 1 if side == 2 else 2

                    is_live = True if str(bet["live"]) == "1" else False

                    is_active = False
                    if str(bet["status"]) == "0" and str(bet["live"]) == "0":
                        is_active = True
                    elif bet["status"] is True and str(bet["live"]) == "1" and bet["time_from_update"] < 60:
                        is_active = True

                    bet_data = {
                        "is_live": is_live,
                        "type_id": type_id,
                        "match_id": match.match_id,
                        "map": map,
                        "side": side,
                        "value": value,
                        "bets4pro_name": b_type,
                        "is_shown": False,
                    }
                    bet_data["hash"] = jwt.encode(bet_data, SECRET_KEY, algorithm='HS256')
                    bet_data["is_active"] = is_active
                    bet_data["cfs"] = cfs_data

                    all_bets.append(bet_data)

        return all_bets


def get_match_data(block, is_live=False):
    link = block.find_parent()
    match = link.find_parent()

    match_id = link["href"].split("/")[2].split("-")[1]

    match_time = match.find(class_="main-content__item_top-time").get_text(separator="_^_", strip=True).split()

    if match_time[0] == 'coming':
        start_at = datetime.datetime.now()
    else:
        match_time_l = match_time[0].split(":")
        match_time_dt = datetime.timedelta(hours=int(match_time_l[0]), minutes=int(match_time_l[1]))

        start_at = (
            datetime.datetime.now() - match_time_dt
            if match_time[1] == "ago"
            else datetime.datetime.now() + match_time_dt
        )

    team_1 = block.find(class_="team_1").get_text(separator="_^_", strip=True).split("_^_")[0]
    team_2 = block.find(class_="team_2").get_text(separator="_^_", strip=True).split("_^_")[0]

    url = f"https://bets4.org{link['href']}"

    team_1 = update_team_name(team_1)
    team_2 = update_team_name(team_2)
    team_1, team_2, is_reverse = teams_right_order(team_1, team_2)

    match_data = {
        "team_1": update_team_name(team_1),
        "team_2": update_team_name(team_2),
        "start_at": start_at + datetime.timedelta(hours=BETS4PRO_DELTA),
        "additional_data": {
            "bets4pro_id": match_id,
            "is_live": is_live,
            "url": url,
            "site": "bets4pro",
            "is_reverse": is_reverse,
        },
    }

    return match_data


async def get_html_matches():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://bets4.org/en/", headers=DEFAULT_BETS4PRO_HEADERS, ssl=False) as response:
            html_str = await response.text()

    html_str = html_str.replace('style="display: none;"', "")
    soup = BeautifulSoup(html_str, 'html.parser')

    live_block = soup.find(class_='is_live')
    if live_block is not None:
        live_blocks = live_block.find_all(class_='main-content__item_bottom')
    else:
        live_blocks = []

    upcoming_block = soup.find(class_='main-content__left_block-two')
    if upcoming_block is not None:
        upcoming_blocks = upcoming_block.find_all(class_='main-content__item_bottom')
    else:
        upcoming_blocks = []

    return live_blocks, upcoming_blocks


async def make_bet(bet_data, headers):
    bet_name = bet_data["bets4pro_bet_name"]
    side_name = "team_" + bet_data["bet"]
    tournament = bet_data["bets4pro_match_id"]
    bet_cof = json.loads(bet_data["bets4pro_cfs"])[bet_data["bet"]] - 1
    user_id = "76561199008104347"
    user_betcoin = 0.01

    data = (f"team_{bet_name}={side_name}"
            f"&{side_name}_cof_{bet_name}={bet_cof}"
            f"&type={bet_name}"
            f"&tournament={tournament}"
            f"&user_betcoin={user_betcoin}"
            f"&user_id={user_id}"
            f"&button_name=place-bet")

    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://bets4.org/engine/function/bet.php",
                headers=headers, data=data, ssl=False) as response:
            text = await response.text()

            if response.status == 500:  # token is not valid
                create_new_token()
                return "Error"
            else:
                if "Error" in text:
                    return "Error"
                else:
                    response = json.loads(text)

                    response = response["response"]
                    if response.get("return_url"):
                        return "Done"
