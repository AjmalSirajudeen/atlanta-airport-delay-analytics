# Data

## Bundled sample

`sample/atl_flights_sample.csv` is a **real** 3,000-flight subset of Bureau of
Transportation Statistics on-time records for January 2015, keeping only flights
with origin or destination ATL.

It is not the full ~350,000-flight year used in the original Cornell study.

## Full rebuild (recommended for results you want to discuss)

Download official monthly BTS on-time zips and keep ATL flights:

```bash
python scripts/download_bts.py --year 2015 --months 1-12
```

That writes `raw/atl_flights.csv` (gitignored). Then:

```bash
python scripts/run_pipeline.py
```

Source: https://www.transtats.bts.gov (On-Time Performance).

## Bring your own CSV

Pass any BTS-style file that includes:

`Year, Month, FlightDate, Reporting_Airline, Origin, OriginCityName, Dest,
DestCityName, DepDelay, ArrDelay, Cancelled, Diverted, Distance`

Optional cause fields: `CarrierDelay, WeatherDelay, NASDelay, SecurityDelay,
LateAircraftDelay`.

```bash
python scripts/run_pipeline.py --path /path/to/your_flights.csv
```
