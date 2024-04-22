import json

import aiohttp

from config import TELEGRAM_BOT, CHAT_ID


async def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/{TELEGRAM_BOT}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}

    async with aiohttp.ClientSession() as session:
        async with session.post(telegram_url, data=data, ssl=False) as response:
            t = await response.text()
            return t


def escape_markdown_v2(value):
    value = str(value)

    if "https" not in value:
        escape_chars = "_*[]()~`>#+-=|{}.!"
        for char in escape_chars:
            value = value.replace(char, f"\\{char}")
    return value


async def send_match_to_telegram(bets_data):
    d2by_bets = json.loads(bets_data["d2by_cfs"]) if isinstance(bets_data["d2by_cfs"], str) else {}
    bets_data['d2by_cfs'] = " , ".join([f"{key}: {value}" for key, value in d2by_bets.items()])

    bets4pro_bets = json.loads(bets_data["bets4pro_cfs"]) if isinstance(bets_data["bets4pro_cfs"], str) else {}
    bets_data['bets4pro_cfs'] = " , ".join([f"{key}: {value}" for key, value in bets4pro_bets.items()])

    bet_data = bets_data.apply(escape_markdown_v2)

    side = f', on side {bet_data["side"]}' if bet_data['side'] != 'None' else ''
    value = f', with value {bet_data["value"]}' if bet_data['value'] != 'None' else ''
    map = f', on map {bet_data["value"]}' if bet_data['map'] != 'nan' else ''

    message = (
        f"**{bet_data['team_1']} \\- {bet_data['team_2']}**\n"
        f"Make bet on **{bet_data['site']}** with parameters:\n"
        f"name \\- {bet_data['bets4pro_bet_name']}{side}{value}{map}\n"
        f"[D2BY]({bet_data['d2by_url']}): **{bet_data['d2by_cfs']}**\n"
        f"[Bets4PRO]({bet_data['bets4pro_url']}): **{bet_data['bets4pro_cfs']}**\n"
    )
    await send_telegram_message(message)

    return bets_data["bet_id"]
