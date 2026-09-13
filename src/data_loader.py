"""Load BTS on-time flights involving Hartsfield-Jackson Atlanta (ATL)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

REQUIRED = [
    "Year",
    "Month",
    "FlightDate",
    "Reporting_Airline",
    "Origin",
    "OriginCityName",
    "Dest",
    "DestCityName",
    "DepDelay",
    "ArrDelay",
    "Cancelled",
    "Diverted",
    "Distance",
]

OPTIONAL_CAUSES = [
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "SecurityDelay",
    "LateAircraftDelay",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_sample_path() -> Path:
    return project_root() / "data" / "sample" / "atl_flights_sample.csv"


def default_raw_path() -> Path:
    return project_root() / "data" / "raw" / "atl_flights.csv"


def load_flights(path: Optional[Path | str] = None) -> pd.DataFrame:
    """Load a BTS-style CSV. Defaults to data/raw, then the bundled ATL sample."""
    if path is None:
        raw = default_raw_path()
        path = raw if raw.exists() else default_sample_path()
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"No flights file at {path}. "
            "Pass --path, run scripts/download_bts.py, or use the bundled sample."
        )

    df = pd.read_csv(path, low_memory=False)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(
            f"{path.name} is missing columns {missing}. "
            "See data/README.md for the expected BTS fields."
        )
    for col in OPTIONAL_CAUSES:
        if col not in df.columns:
            df[col] = pd.NA
    return df[REQUIRED + OPTIONAL_CAUSES].copy()
