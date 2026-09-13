"""Checks on cleaning rules and ANOVA output shape."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis import delay_causes, passenger_cost_estimate
from src.cleaning import DELAY_THRESHOLD_MIN, clean_flights
from src.data_loader import load_flights
from src.statistics import anova_one_way, run_anova_suite


def test_sample_loads_and_is_atl():
    raw = load_flights()
    flights = clean_flights(raw)
    assert len(flights) > 0
    assert ((flights["Origin"] == "ATL") | (flights["Dest"] == "ATL")).all()
    assert flights["Cancelled"].eq(0).all()


def test_delay_flag_uses_faa_threshold():
    raw = pd.DataFrame(
        {
            "Year": [2015, 2015],
            "Month": [1, 1],
            "FlightDate": ["2015-01-01", "2015-01-01"],
            "Reporting_Airline": ["DL", "EV"],
            "Origin": ["ATL", "ATL"],
            "OriginCityName": ["Atlanta, GA", "Atlanta, GA"],
            "Dest": ["MEM", "MEM"],
            "DestCityName": ["Memphis, TN", "Memphis, TN"],
            "DepDelay": [14, 15],
            "ArrDelay": [10, 20],
            "Cancelled": [0, 0],
            "Diverted": [0, 0],
            "Distance": [300, 300],
        }
    )
    flights = clean_flights(raw)
    assert DELAY_THRESHOLD_MIN == 15
    assert bool(flights.loc[0, "dep_delayed"]) is False
    assert bool(flights.loc[1, "dep_delayed"]) is True


def test_anova_and_cost_run_on_sample():
    flights = clean_flights(load_flights())
    suite = run_anova_suite(flights)
    assert len(suite) == 5
    assert all("pvalue" in row for row in suite)
    causes = delay_causes(flights)
    assert not causes.empty
    cost = passenger_cost_estimate(flights)
    assert "wage_loss_usd" in cost
