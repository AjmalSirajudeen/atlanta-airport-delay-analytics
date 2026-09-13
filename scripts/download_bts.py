"""Download BTS on-time files and keep ATL origin/destination flights.

Official public source (monthly zips):
https://transtats.bts.gov/PREZIP/

Example:
  python scripts/download_bts.py --year 2015 --months 1-12
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import REQUIRED, OPTIONAL_CAUSES

BASE = "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
COLS = REQUIRED + OPTIONAL_CAUSES


def _parse_months(text: str) -> list[int]:
    if "-" in text:
        a, b = text.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in text.split(",") if x.strip()]


def download_month(year: int, month: int) -> pd.DataFrame:
    url = BASE.format(year=year, month=month)
    print(f"Downloading {url}")
    req = Request(url, headers={"User-Agent": "atlanta-airport-delay-analytics/0.1"})
    with urlopen(req, timeout=180) as resp:
        blob = resp.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        name = [n for n in zf.namelist() if n.endswith(".csv")][0]
        with zf.open(name) as fh:
            df = pd.read_csv(fh, usecols=lambda c: c in COLS, low_memory=False)
    atl = df[(df["Origin"] == "ATL") | (df["Dest"] == "ATL")].copy()
    print(f"  {year}-{month:02d}: {len(atl)} ATL flights")
    return atl


def main() -> None:
    parser = argparse.ArgumentParser(description="Download BTS ATL on-time flights")
    parser.add_argument("--year", type=int, default=2015)
    parser.add_argument("--months", type=str, default="1", help="e.g. 1 or 1-12 or 1,2,3")
    parser.add_argument(
        "--out",
        type=str,
        default=str(ROOT / "data" / "raw" / "atl_flights.csv"),
    )
    args = parser.parse_args()

    frames = [download_month(args.year, m) for m in _parse_months(args.months)]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(out, index=False)
    print(f"Wrote {len(combined)} rows to {out}")


if __name__ == "__main__":
    main()
