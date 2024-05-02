import asyncio
import datetime
import json
import os

import numpy as np
import pandas as pd
from simplegmail import Gmail

from bets4pro.login import login
from bets4pro.tables import Bets4ProBets
from d2by.api import make_bet as d2by_make_bet
from bets4pro.api import make_bet as bets4pro_make_bet
from d2by.login import get_token
from d2by.tables import D2BYBets
from main_app.bets import get_bets, is_shown_true, save_history
from bets4pro.script import update_bets as update_bets_bets4pro, update_matches as update_matches_bets4pro
from d2by.scripts import update_bets as update_bets_d2by, update_matches as update_matches_d2by
from main_app.matches import delete_old_matches
from telegram import send_match_to_telegram


def compare_bets(row):
    bets4pro_cfs = row['bets4pro_cfs'] if row['bets4pro_cfs'] else {}
    d2by_cfs = row['d2by_cfs'] if row['d2by_cfs'] else {}
    fan_cfs = row['fan_cfs'] if row['fan_cfs'] else {}

    df_columns = ["bets4pro", "d2by", "fan"]

    cfs = [bets4pro_cfs, d2by_cfs, fan_cfs]
    df_index = list(set().union(*cfs))

    cfs_data = pd.DataFrame(cfs, index=df_columns).reindex(columns=df_index).values.tolist()
    cfs_df = pd.DataFrame(cfs_data, index=df_columns, columns=df_index)

    max_cfs = pd.concat([cfs_df.idxmax(), cfs_df.max()], axis=1)
    max_cfs.rename(columns={0: "site", 1: "value"}, inplace=True)
    cfs_df.replace(max_cfs["value"], np.nan, inplace=True)
    average_values = cfs_df.mean(skipna=True)

    compare = max_cfs["value"] / average_values
    compare = compare > 1.15

    bet_data = max_cfs[compare]
    bet_data["bet"] = bet_data.index

    bet_data["bet_id"] = 0
    for id, bet in bet_data.iterrows():
        bet_data.loc[id, "bet_id"] = row[f'{bet["site"]}_id']

    for index, value in row.items():
        bet_data[index] = value if not isinstance(value, dict) else json.dumps(value)

    return bet_data


async def get_good_bets():
    bets = await get_bets()

    columns = [
        "match_id", "team_1", "team_2", "start_at",
        "bets4pro_cfs", "d2by_cfs",
        "fan_cfs", "bets4pro_id", "d2by_id",
        "fan_id", "value", "side",
        "map", "type_id", "d2by_probs", "d2by_true_id",
        "d2by_url", "bets4pro_bet_name", "bets4pro_url",
        "bets4pro_match_id"
    ]
    bets_df = pd.DataFrame(
        columns=columns,
        data=bets
    )

    start_at = pd.to_datetime(datetime.datetime.now() - datetime.timedelta(seconds=30)) - datetime.timedelta(hours=2)
    end_at = pd.to_datetime(datetime.datetime.now() + datetime.timedelta(minutes=1)) - datetime.timedelta(hours=2)

    live_f = bets_df["bets4pro_bet_name"].isin(["live_match", "live_game1", "live_game2", "live_game3"])
    live_df = bets_df[live_f]

    bets_df["start_at"] = pd.to_datetime(bets_df["start_at"])

    start_at_f = bets_df["start_at"] > start_at
    end_at_f = bets_df["start_at"] < end_at
    before_df = bets_df[~live_f & start_at_f & end_at_f]

    bets_df = pd.concat(
        [live_df, before_df],
        axis=0
    ).reset_index(drop=True)

    # Apply the function row-wise
    result_df = bets_df.apply(compare_bets, axis=1)

    # Concatenate the resulting DataFrames
    if result_df.shape[0] > 0:
        result_df = pd.concat(result_df.tolist(), ignore_index=True)

        return result_df


async def make_bets_on_web_sites(group, site, d2by_token, bets4pro_token):
    ids = []
    tasks = []

    if site == "bets4pro":
        for _, bet in group.iterrows():
            tasks.append(bets4pro_make_bet(bet, bets4pro_token, bet["bet_id"]))

            ids.append(bet["bet_id"])
        ids = await asyncio.gather(*tasks)
    elif site == "d2by":
        for _, bet in group.iterrows():
            prob_data = json.loads(bet["d2by_probs"])
            prob_data = prob_data[bet["bet"]]
            data = {
                "amount": 1,
                "coinType": "GOLD",
                "market": bet["d2by_true_id"],
                "type": "SINGLE",
                "currentRate": prob_data["prob"],
                "selectPosition": prob_data["position"],
            }
            tasks.append(d2by_make_bet(d2by_token, [data], bet["bet_id"]))

            ids.append(bet["bet_id"])
        ids = await asyncio.gather(*tasks)

    return {"site": site, "ids": ids}


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


async def compare_circle(d2by_token, bets4pro_token):
    all_bets = await get_good_bets()

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
