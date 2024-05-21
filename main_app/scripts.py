import asyncio
import datetime
import os

import numpy as np
import pandas as pd
from simplegmail import Gmail

from bets4pro.login import login
from bets4pro.tables import Bets4ProBets

from d2by.login import get_token
from d2by.tables import D2BYBets
from main_app.bets import is_shown_true, save_history
from bets4pro.script import update_bets as update_bets_bets4pro, update_matches as update_matches_bets4pro
from d2by.scripts import update_bets as update_bets_d2by, update_matches as update_matches_d2by
from main_app.matches import delete_old_matches
from main_app.utils import make_bets_on_web_sites, get_good_bets
from telegram import send_match_to_telegram


async def update_rows():
    i = 0
    while True:
        if i == 0:
            start_at = datetime.datetime.now()

        tasks = [update_bets_bets4pro(), update_bets_d2by()]

        i += 1
        if i == 100:
            end_at = datetime.datetime.now()
            i = 0
            print("Compare circle: ", end_at - start_at)

            tasks.extend([update_matches_d2by(), update_matches_bets4pro(), delete_old_matches()])

        await asyncio.gather(*tasks)


def make_amounts(group):
    if all(group["bet_cf"] > 2):
        group["amount"] = 1

        return group
    else:
        probs = 1 / group["bet_cf"]

        if probs.sum() < 1:
            total_bet = 2
            group["amount"] = np.round(total_bet * probs / probs.sum(), 2)

            return group


async def compare_circle(d2by_token, bets4pro_token):
    all_bets = await get_good_bets()

    if all_bets is None:
        return

    all_bets["bet_cf"] = all_bets.apply(lambda x: x["cfs"][x["bet"]], axis=1)

    all_bets['side'].fillna(-1, inplace=True)
    all_bets['map'].fillna(-1, inplace=True)
    all_bets['value'].fillna(-1, inplace=True)
    all_bets['amount'] = 1

    fork_bets = (
        all_bets.groupby([
            "value",
            "side",
            "match_id",
            "map",
            "type_id",
        ])
        .filter(lambda x: len(x) == 2)
        .reset_index(drop=True)
    )

    fork_bets = (
        fork_bets.groupby([
        "value",
        "side",
        "match_id",
        "map",
        "type_id",
        ])
        .apply(lambda x: make_amounts(x))
        .reset_index(drop=True)
    )

    fork_bets_f = list(fork_bets[["value", "side", "match_id", "map", "type_id"]].apply(tuple, axis=1).values)

    mask = all_bets.apply(
        lambda row: tuple(row[["value", "side", "match_id", "map", "type_id"]].values) in fork_bets_f,
        axis=1
    )

    all_bets_filtered = all_bets[~mask]
    all_bets = pd.concat(
        [all_bets_filtered, fork_bets]
    )

    all_bets.loc[all_bets["map"] == -1, "map"] = None
    all_bets.loc[all_bets["side"] == -1, "side"] = None
    all_bets.loc[all_bets["value"] == -1, "value"] = None

    tasks = []

    if all_bets is not None:
        for name, bets in all_bets.groupby(["site"]):
            tasks.append(make_bets_on_web_sites(bets, name[0], d2by_token, bets4pro_token))

        bets_data = await asyncio.gather(*tasks)

        for bet in bets_data:
            if bet["site"] == "bets4pro":
                table = Bets4ProBets
            elif bet["site"] == "d2by":
                table = D2BYBets
            else:
                table = None

            bets_indexs = ['site', 'value', 'bet', 'team_1', 'team_2', 'start_at', 'bets4pro_cfs', 'd2by_cfs',
                           'fan_cfs',
                           'side', 'map', 'type_id', 'd2by_url', 'bets4pro_url']

            save_bets = all_bets[(all_bets["site"] == bet["site"]) & (all_bets["bet_id"].isin(bet["ids"]))]

            sb = save_bets.loc[:, bets_indexs]
            sb.loc[sb["side"].isna(), "side"] = -1
            sb.loc[sb["map"].isna(), "map"] = -1
            sb = sb.to_dict(orient="records")

            await is_shown_true(bet["ids"], table)
            tasks = [save_history(sb)]
            tasks.extend([send_match_to_telegram(bet) for _, bet in save_bets.iterrows()])

            await asyncio.gather(*tasks)


async def main_script():
    d2by_username = os.environ.get("D2BY_USERNAME")
    d2by_password = os.environ.get("D2BY_PASSWORD")
    gmail = Gmail()

    BETS4PRO_SESSION = login()
    D2BY_TOKEN = get_token(d2by_username, d2by_password, gmail)

    # BETS4PRO_SESSION = None
    # D2BY_TOKEN = None

    i = 0
    while True:
        if i == 0:
            start_at = datetime.datetime.now()

        await compare_circle(D2BY_TOKEN, BETS4PRO_SESSION)
        i += 1

        if i == 1000:
            end_at = datetime.datetime.now()
            i = 0
            print("Compare circle 1000: ", end_at - start_at)
