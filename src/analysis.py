"""Descriptive summaries used in the original DMAIC analysis."""

from __future__ import annotations

import pandas as pd

from .cleaning import DELAY_THRESHOLD_MIN

# Assumptions taken from the original cost section. Applied to whatever
# dataset is loaded; do not treat the dollar result as the 2015 paper figure
# unless the full-year file is used.
AVG_WAGE_PER_HOUR = 22.0
AVG_PASSENGERS = 123


def delay_distribution(df: pd.DataFrame, column: str) -> pd.Series:
    """Positive delays only, matching the original JMP fits (zeros excluded)."""
    return df.loc[df[column] > 0, column].dropna()


def group_means(df: pd.DataFrame, by: str, value: str) -> pd.DataFrame:
    g = df.dropna(subset=[value]).groupby(by, observed=False)[value]
    out = g.agg(mean="mean", median="median", count="size").reset_index()
    return out.sort_values("mean", ascending=False)


def delay_rate(df: pd.DataFrame, by: str, flag: str) -> pd.DataFrame:
    g = df.groupby(by, observed=False)[flag]
    out = g.agg(delay_rate="mean", n="size").reset_index()
    out["delay_rate"] = out["delay_rate"] * 100
    return out.sort_values("delay_rate", ascending=False)


def delay_causes(df: pd.DataFrame) -> pd.DataFrame:
    """BTS cause minutes. Carrier + late aircraft were the original focus."""
    cols = [
        "CarrierDelay",
        "LateAircraftDelay",
        "WeatherDelay",
        "NASDelay",
        "SecurityDelay",
    ]
    present = [c for c in cols if c in df.columns]
    totals = {c: float(pd.to_numeric(df[c], errors="coerce").fillna(0).sum()) for c in present}
    frame = pd.DataFrame({"cause": list(totals), "minutes": list(totals.values())})
    controllable = {"CarrierDelay", "LateAircraftDelay"}
    frame["class"] = frame["cause"].map(
        lambda c: "airline-controllable" if c in controllable else "largely-uncontrollable"
    )
    return frame.sort_values("minutes", ascending=False)


def passenger_cost_estimate(df: pd.DataFrame) -> dict:
    """Wage-loss illustration using the original study's $22/hr and 123 pax.

    The paper applied this to origin cities whose average delay exceeded 15
    minutes. Here it is computed on the loaded ATL arrival set.
    """
    arrivals = df[df["direction"] == "arrival"].dropna(subset=["ArrDelay"])
    if arrivals.empty:
        return {"cities_over_threshold": 0, "passenger_minutes": 0, "wage_loss_usd": 0.0}

    by_city = arrivals.groupby("partner_city")["ArrDelay"].agg(mean="mean", n="size")
    over = by_city[by_city["mean"] > DELAY_THRESHOLD_MIN].copy()
    over["minutes_over"] = over["mean"] - DELAY_THRESHOLD_MIN
    passenger_minutes = float((over["minutes_over"] * over["n"] * AVG_PASSENGERS).sum())
    wage_loss = passenger_minutes / 60.0 * AVG_WAGE_PER_HOUR
    return {
        "cities_over_threshold": int(len(over)),
        "flights_in_those_cities": int(over["n"].sum()) if len(over) else 0,
        "passenger_minutes": passenger_minutes,
        "wage_loss_usd": wage_loss,
        "wage_per_hour": AVG_WAGE_PER_HOUR,
        "passengers_per_flight": AVG_PASSENGERS,
    }
