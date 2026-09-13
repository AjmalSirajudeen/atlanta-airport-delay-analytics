"""Run ATL delay analysis and write tables plus figures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis import delay_causes, delay_rate, group_means, passenger_cost_estimate
from src.cleaning import clean_flights
from src.data_loader import load_flights
from src.statistics import run_anova_suite
from src.visualization import (
    plot_arrival_delay_hist,
    plot_delay_by_airline,
    plot_delay_by_month,
    plot_delay_causes,
    plot_delay_rate_by_airline,
)


def _json_safe(obj):
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="ATL airport delay analytics")
    parser.add_argument("--path", type=str, default=None, help="BTS-style flights CSV")
    parser.add_argument("--out-dir", type=str, default=str(ROOT / "outputs"))
    args = parser.parse_args()

    raw = load_flights(args.path)
    flights = clean_flights(raw)
    source = args.path or ("data/raw/atl_flights.csv" if (ROOT / "data/raw/atl_flights.csv").exists() else "data/sample/atl_flights_sample.csv")
    print(f"Loaded {len(raw)} rows from {source}")
    print(f"Operated ATL flights after cleaning: {len(flights)}")

    out_dir = Path(args.out_dir)
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    airline_arr = group_means(flights, "Reporting_Airline", "ArrDelay")
    month_arr = group_means(flights, "Month", "ArrDelay")
    airline_rate = delay_rate(flights, "Reporting_Airline", "arr_delayed")
    causes = delay_causes(flights)
    anova = run_anova_suite(flights)
    cost = passenger_cost_estimate(flights)

    airline_arr.to_csv(out_dir / "arrival_delay_by_airline.csv", index=False)
    month_arr.to_csv(out_dir / "arrival_delay_by_month.csv", index=False)
    airline_rate.to_csv(out_dir / "arrival_delay_rate_by_airline.csv", index=False)
    causes.to_csv(out_dir / "delay_causes.csv", index=False)

    summary = {
        "source": source,
        "n_operated_flights": int(len(flights)),
        "n_airlines": int(flights["Reporting_Airline"].nunique()),
        "mean_dep_delay": float(flights["DepDelay"].mean()),
        "mean_arr_delay": float(flights["ArrDelay"].mean()),
        "pct_dep_delayed_15": float(flights["dep_delayed"].mean() * 100),
        "pct_arr_delayed_15": float(flights["arr_delayed"].mean() * 100),
        "anova": anova,
        "cost_illustration": cost,
        "note": (
            "If the source is the bundled sample, this is a 3,000-flight January 2015 "
            "ATL subset, not the original ~350,000-flight year-long file."
        ),
    }
    (out_dir / "run_summary.json").write_text(json.dumps(_json_safe(summary), indent=2))

    paths = [
        plot_arrival_delay_hist(flights, fig_dir / "arrival_delay_hist.png"),
        plot_delay_by_month(flights, fig_dir / "arrival_delay_by_month.png"),
        plot_delay_by_airline(flights, fig_dir / "arrival_delay_by_airline.png"),
        plot_delay_rate_by_airline(flights, fig_dir / "arrival_delay_rate_by_airline.png"),
        plot_delay_causes(causes, fig_dir / "delay_causes.png"),
    ]

    print(
        f"Mean dep delay {summary['mean_dep_delay']:.2f} min; "
        f"mean arr delay {summary['mean_arr_delay']:.2f} min"
    )
    print(f"Arrival delay rate (15+ min): {summary['pct_arr_delayed_15']:.1f}%")
    print(f"Wrote {out_dir / 'run_summary.json'}")
    for p in paths:
        print(f"Wrote {p}")


if __name__ == "__main__":
    main()
