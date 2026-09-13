"""A small set of matplotlib charts used in the original trend analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .analysis import delay_distribution, delay_rate, group_means
from .cleaning import DELAY_THRESHOLD_MIN


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def plot_arrival_delay_hist(df: pd.DataFrame, out: Path) -> Path:
    values = delay_distribution(df, "ArrDelay")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(values.clip(upper=180), bins=40, color="#2c5f8a", edgecolor="white")
    ax.axvline(DELAY_THRESHOLD_MIN, color="#c0392b", linestyle="--", label="FAA 15-minute threshold")
    ax.set_title("Arrival delay minutes (positive delays only)")
    ax.set_xlabel("Arrival delay (minutes)")
    ax.set_ylabel("Flights")
    ax.legend()
    return _save(fig, out)


def plot_delay_by_month(df: pd.DataFrame, out: Path) -> Path:
    means = group_means(df, "Month", "ArrDelay").sort_values("Month")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(means["Month"].astype(int), means["mean"], color="#2c5f8a")
    ax.axhline(DELAY_THRESHOLD_MIN, color="#c0392b", linestyle="--", label="15-minute threshold")
    ax.set_title("Average arrival delay by month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average arrival delay (minutes)")
    ax.legend()
    return _save(fig, out)


def plot_delay_by_airline(df: pd.DataFrame, out: Path) -> Path:
    means = group_means(df, "Reporting_Airline", "ArrDelay")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(means["Reporting_Airline"][::-1], means["mean"][::-1], color="#2c5f8a")
    ax.axvline(DELAY_THRESHOLD_MIN, color="#c0392b", linestyle="--", label="15-minute threshold")
    ax.set_title("Average arrival delay by airline")
    ax.set_xlabel("Average arrival delay (minutes)")
    ax.legend()
    return _save(fig, out)


def plot_delay_rate_by_airline(df: pd.DataFrame, out: Path) -> Path:
    rates = delay_rate(df, "Reporting_Airline", "arr_delayed")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(rates["Reporting_Airline"][::-1], rates["delay_rate"][::-1], color="#2c5f8a")
    ax.set_title("Arrival delay rate by airline (share delayed 15+ minutes)")
    ax.set_xlabel("Percent of flights delayed")
    return _save(fig, out)


def plot_delay_causes(causes: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [
        "#2c5f8a" if c == "airline-controllable" else "#7f8c8d" for c in causes["class"]
    ]
    ax.barh(causes["cause"][::-1], causes["minutes"][::-1], color=colors[::-1])
    ax.set_title("Total BTS delay minutes by cause")
    ax.set_xlabel("Minutes")
    return _save(fig, out)
