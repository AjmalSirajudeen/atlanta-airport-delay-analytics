"""Clean ATL flights and add analysis fields used in the original study."""

from __future__ import annotations

import pandas as pd

# FAA / ACRP threshold used in the Cornell report.
DELAY_THRESHOLD_MIN = 15

# Airline groups from Table 1 of the original report.
AIRLINE_TYPE = {
    "AA": "Major",
    "DL": "Major",
    "UA": "Major",
    "AS": "Medium",
    "F9": "Medium",
    "NK": "Medium",
    "US": "Medium",
    "WN": "Medium",
    "EV": "Regional",
    "MQ": "Regional",
    "OO": "Regional",
}


def clean_flights(df: pd.DataFrame, airport: str = "ATL") -> pd.DataFrame:
    """Keep ATL origin/destination flights and derive delay flags."""
    out = df.copy()
    out = out[(out["Origin"] == airport) | (out["Dest"] == airport)]
    out["Cancelled"] = out["Cancelled"].fillna(0).astype(int)
    out["Diverted"] = out["Diverted"].fillna(0).astype(int)
    operated = out[(out["Cancelled"] == 0) & (out["Diverted"] == 0)].copy()

    operated["airline_type"] = (
        operated["Reporting_Airline"].map(AIRLINE_TYPE).fillna("Other")
    )
    operated["dep_delayed"] = operated["DepDelay"] >= DELAY_THRESHOLD_MIN
    operated["arr_delayed"] = operated["ArrDelay"] >= DELAY_THRESHOLD_MIN
    operated["direction"] = operated.apply(
        lambda r: "departure" if r["Origin"] == airport else "arrival", axis=1
    )
    # Partner city: the non-ATL airport/city on the itinerary.
    operated["partner_city"] = operated.apply(
        lambda r: r["DestCityName"] if r["Origin"] == airport else r["OriginCityName"],
        axis=1,
    )
    operated["distance_group"] = pd.cut(
        operated["Distance"],
        bins=[0, 1000, 2000, 3000, 4000, 10_000],
        labels=["0-999", "1000-1999", "2000-2999", "3000-3999", "4000+"],
        right=False,
    )
    return operated.reset_index(drop=True)
