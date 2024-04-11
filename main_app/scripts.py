import asyncio
import datetime
import json

import numpy as np
import pandas as pd

from main_app.bets import get_bets
from bets4pro.script import update_bets as update_bets_bets4pro, update_matches as update_matches_bets4pro
from d2by.scripts import update_bets as update_bets_d2by, update_matches as update_matches_d2by


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
        "match_id", "bets4pro_cfs", "d2by_cfs",
        "fan_cfs", "bets4pro_id", "d2by_id",
        "fan_id", "value", "side",
        "map", "type_id"
    ]
    bets_df = pd.DataFrame(
        columns=columns,
        data=bets
    )

    # Apply the function row-wise
    result_df = bets_df.apply(compare_bets, axis=1)

    # Concatenate the resulting DataFrames
    result_df = pd.concat(result_df.tolist(), ignore_index=True)

    return result_df


async def add_rows():
    start_at = datetime.datetime.now()
    await asyncio.gather(*[update_matches_d2by(), update_matches_bets4pro()])
    await asyncio.gather(*[update_bets_bets4pro(), update_bets_d2by()])
    end_at = datetime.datetime.now()

    print(end_at - start_at)


if __name__ == "__main__":
    start_at = datetime.datetime.now()

    bets = asyncio.run(get_good_bets())



    end_at = datetime.datetime.now()
    print(end_at - start_at)
