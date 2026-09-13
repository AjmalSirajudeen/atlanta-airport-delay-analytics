"""One-way ANOVA on the factors studied in the original report."""

from __future__ import annotations

import pandas as pd
from scipy import stats


def anova_one_way(df: pd.DataFrame, factor: str, value: str) -> dict:
    """One-way ANOVA: does mean delay differ across factor levels?"""
    clean = df.dropna(subset=[factor, value])
    groups = [g[value].to_numpy() for _, g in clean.groupby(factor, observed=False) if len(g) > 1]
    labels = [str(name) for name, g in clean.groupby(factor, observed=False) if len(g) > 1]
    if len(groups) < 2:
        return {"factor": factor, "value": value, "n_groups": len(groups), "pvalue": None, "F": None}
    result = stats.f_oneway(*groups)
    return {
        "factor": factor,
        "value": value,
        "n_groups": len(groups),
        "n": int(len(clean)),
        "F": float(result.statistic),
        "pvalue": float(result.pvalue),
        "group_means": {lab: float(g.mean()) for lab, g in zip(labels, groups)},
    }


def run_anova_suite(df: pd.DataFrame) -> list[dict]:
    """Factors from the original ANOVA section: airline type, month, distance."""
    tests = [
        ("airline_type", "DepDelay"),
        ("Month", "DepDelay"),
        ("airline_type", "ArrDelay"),
        ("Month", "ArrDelay"),
        ("distance_group", "ArrDelay"),
    ]
    return [anova_one_way(df, factor, value) for factor, value in tests]
