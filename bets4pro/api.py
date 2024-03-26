import datetime
import json
import aiohttp

from bs4 import BeautifulSoup

from main_app.utils import teams_right_order
from utils import update_team_name


HEADERS = {
    "cookie": "lang=en; _ym_uid=1698496197361582594; _ym_d=1698496197; _gcl_au=1.1.2103616613.1698496197; _ga=GA1.1.1692695333.1698496197; _fbp=fb.1.1698496197487.1957987306; overwatch=true; hs=true; soccer=true; dota2=true; PHPSESSID=co0tp0rn0o2sn41if7va91dr24; _ym_isad=2; cf_clearance=bBd_ujiRye4KITmr23U27_ki08M77MmDuz9IuNu7leE-1704307437-0-2-c1af11bd.ae1faf2b.e28cf9c4-0.2.1704307437; cs_go=true; basketball=false; hockey=true; lol=true; sc=true; valorant=true; other=true; _ga_S9E0G3W1VY=GS1.1.1704307434.5.1.1704308876.0.0.0",
    "authority": "bets4.net",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": "https://bets4.net/express-bets/",
    "sec-ch-ua": "^\^Not_A",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^\^Windows^^",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


async def get_match_bets(match_id, bet_types):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(
            f"https://bets4.org/widget/cofs_api.php?tournament_id={match_id}",
            ssl=False
        ) as resp:
            response = await resp.text()
            bets = json.loads(response)

            bets = bets["response"]["cofs"]

            all_bets = []
            for bet in bets:
                b_type = bet["type"]

                type_id = None
                for t in bet_types:
                    if b_type in str(t[4]):
                        type_id = t[0]
                        break

                map = None
                side = None
                value = None
                if "game" in b_type:
                    map = b_type.split("game")[1]
                elif "hc" in b_type:
                    side = int(b_type.split("hc")[-1])
                    value = float(bet["show_type"].split()[-1])

                if type_id is None:
                    continue

                cfs_data = {
                    "1": round(1 + bet["team_1_cof"], 3),
                    "2": round(1 + bet["team_2_cof"], 3),
                }

                is_live = True if str(bet["live"]) == "1" else False

                is_active = False
                if str(bet["status"]) == "0" and str(bet["live"]) == "0":
                    is_active = True
                elif bet["status"] is True and str(bet["live"]) == "1" and bet["time_from_update"] < 60:
                    is_active = True

                bet_data = {
                    "cfs": cfs_data,
                    "is_live": is_live,
                    "is_active": is_active,
                    "type_id": type_id,
                    "match_id": match_id,
                    "map": map,
                    "side": side,
                    "value": value,
                }
                all_bets.append(bet_data)

        return all_bets


async def get_match_data(block, is_live=False):
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
    team_1 = update_team_name(team_1)
    team_2 = update_team_name(team_2)
    team_1, team_2, _ = teams_right_order(team_1, team_2)

    match_data = {
        "team_1": update_team_name(team_1),
        "team_2": update_team_name(team_2),
        "start_time": start_at,
        "id": int(match_id),
        "is_live": is_live
    }

    return match_data


async def get_html_matches():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://bets4.org/en/", headers=HEADERS) as response:
            html_str = await response.text()

    html_str = html_str.replace('style="display: none;"', "")
    soup = BeautifulSoup(html_str, 'html.parser')

    live_block = soup.find(class_='is_live')
    live_blocks = live_block.find_all(class_='main-content__item_bottom')

    upcoming_block = soup.find(class_='main-content__left_block-two')
    upcoming_blocks = upcoming_block.find_all(class_='main-content__item_bottom')

    return live_blocks, upcoming_blocks
