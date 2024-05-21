import asyncio
import datetime
import json
import re

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz

from d2by.api import make_bet as d2by_make_bet
from bets4pro.api import make_bet as bets4pro_make_bet
from config import THRESHOLD
from main_app.bets import get_bets


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
    bet_data["cfs"] = {}
    for id, bet in bet_data.iterrows():
        if not row[f'{bet["site"]}_is_shown'] and bet["value"] < 2.8:
            bet_data.loc[id, "bet_id"] = row[f'{bet["site"]}_id']
            bet_data.at[id, "cfs"] = row[f'{bet["site"]}_cfs']

    bet_data = bet_data[bet_data["bet_id"] != 0]

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
        "map", "type_id", "d2by_probs", "d2by_true_id", "d2by_is_shown",
        "d2by_url", "bets4pro_bet_name", "bets4pro_is_shown", "bets4pro_match_start_at",
        "bets4pro_url", "bets4pro_match_id", "bets4pro_is_reverse"
    ]
    bets_df = pd.DataFrame(
        columns=columns,
        data=bets
    )

    start_at = (pd.to_datetime(datetime.datetime.now() - datetime.timedelta(seconds=30)))
    end_at = (pd.to_datetime(datetime.datetime.now() + datetime.timedelta(minutes=1)))

    live_f = bets_df["bets4pro_bet_name"].isin(["live_match", "live_game1", "live_game2", "live_game3"])
    live_df = bets_df[live_f]

    bets_df["start_at"] = pd.to_datetime(bets_df["start_at"])

    start_at_f = bets_df["bets4pro_match_start_at"] > start_at
    end_at_f = bets_df["bets4pro_match_start_at"] < end_at
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
        pass
        for _, bet in group.iterrows():
            prob_data = json.loads(bet["d2by_probs"])
            prob_data = prob_data[bet["bet"]]
            data = {
                "amount": bet["amount"],
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


def remove_id_key(d):
    ids = []

    ids.append(d.pop("id"))
    ids.extend(d.pop("sub_matches", []))

    ids = [str(i) for i in ids]

    d["fan_ids"] = ",".join(ids)
    return d


def are_teams_similar(team1, team2):
    similarity_score = fuzz.ratio(team1, team2)
    return similarity_score >= THRESHOLD


def is_reversed(d2by_team_1, d2by_team_2, fan_team_1, fan_team_2):
    same = fuzz.ratio(d2by_team_1, fan_team_1) + fuzz.ratio(d2by_team_2, fan_team_2)
    not_same = fuzz.ratio(d2by_team_1, fan_team_2) + fuzz.ratio(d2by_team_2, fan_team_1)

    if same > not_same:
        return False
    else:
        return True


def create_fan_sport_url(is_live, sport_id, league_id, league_name, match_id, team_1, team_2):
    if sport_id == 40:
        sport = "esports"
    elif sport_id == 3:
        sport = "basketball"
    elif sport_id == 1:
        sport = "football"
    else:
        return

    league_input = str(league_id) + " " + league_name
    league = re.sub(r'[^a-zA-Z0-9]+', '-', league_input).lower()

    match_input = str(match_id) + " " + team_1 + " " + team_2
    match = re.sub(r'[^a-zA-Z0-9]+', '-', match_input).lower()

    match_type = "live" if is_live else "line"

    return f"https://fan-sport.com/{match_type}/{sport}/{league}/{match}"


def calculate_odds_from_bets(team_am_1, team_am_2):
    team_1_am = team_am_1 + 1
    team_2_am = team_am_2 + 1

    team_1_cf = 1 + (team_2_am / team_1_am * 0.93)
    team_2_cf = 1 + (team_1_am / team_2_am * 0.93)

    return round(team_1_cf, 2), round(team_2_cf, 2)


def calculate_bets(fan_cf_1, fan_cf_2, d2by_cf_1, d2by_cf_2, d2by_am_1, d2by_am_2):
    if d2by_cf_1 > fan_cf_1:
        amount_bet = (115 * fan_cf_1 * d2by_am_1 + 115 * fan_cf_1 - 100 * d2by_am_1 - 193 - 93 * d2by_am_2) / (100 - 115 * fan_cf_1)
        side = 1
    elif d2by_cf_2 > fan_cf_2:
        amount_bet = (115 * fan_cf_2 * d2by_am_2 + 115 * fan_cf_2 - 100 * d2by_am_2 - 193 - 93 * d2by_am_1) / (100 - 115 * fan_cf_2)
        side = 2
    else:
        return None, None

    return amount_bet, side


def get_team_name(bet_name, reverse):
    if not reverse:
        if "1" in bet_name:
            return "1"
        elif "2" in bet_name:
            return "2"
        else:
            return bet_name
    else:
        if "1" in bet_name:
            return "2"
        elif "2" in bet_name:
            return "1"
        else:
            return bet_name


def add_bet_to_cfs(data, bet_id, bet_name, coef, url):
    b_data = data.get(bet_id, None)
    if not b_data:
        data[bet_id] = {
            "id": bet_id,
            "fan_bets": {f"{bet_name}": coef},
            "fan_url": url,
        }
    else:
        data[bet_id]["fan_bets"].update({f"{bet_name}": coef})
