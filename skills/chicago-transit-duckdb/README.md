# Chicago transit archives with DuckDB

Analyze the public CTA bus, CTA L train, and Metra vehicle-position archive from [Chicago Transit Alerts](https://chicagotransitalerts.app/subscribe/). The [skill entrypoint](SKILL.md) explains source semantics and routes to detailed guidance.

## Install

```bash
npx skills add MisterClean/ai-plugins --skill chicago-transit-duckdb
```

For manual installation, copy this entire directory into your agent's documented skills directory. Optional `agents/openai.yaml` supplies UI metadata for compatible hosts; it is not required to use the skill. See the repository's [installation guidance](../../README.md#installation).

## Run the full workflow

Requirements: Python 3.10+, DuckDB 2.x, `pytz`, `curl`, and IANA timezone data. From the installed skill directory, create an environment and keep all datasets/results outside the skill:

```bash
python3 -m venv /path/to/transit-venv
source /path/to/transit-venv/bin/activate
python -m pip install -r scripts/requirements.txt

# Last seven complete America/Chicago calendar days; publication is verified.
python scripts/transit_archive.py ingest \
  --db /path/to/data/transit.duckdb --raw-dir /path/to/data/raw --days 7

# An empty destination is required for each export or benchmark run.
python scripts/transit_archive.py export \
  --db /path/to/data/transit.duckdb --out /path/to/data/parquet

# Example historical window: choose dates present in your database.
python scripts/profile_queries.py \
  --db /path/to/data/transit.duckdb --start 2026-10-24 --end 2026-10-30 \
  --out /path/to/results/week --compare-files --kind bus --route 66 \
  --window-start 2026-10-30T08:00:00-05:00 --window-end 2026-10-30T09:00:00-05:00
```

For that historical ingestion window, add `--as-of 2026-10-31 --end 2026-10-30` to `ingest`. Add `duckdb==2.0.0` to the dependency installation command to reproduce the tested engine. Re-running ingestion skips identical files and stops if published hashes change. To append a newly published day, run ingestion for the expanded window against the same database and raw directory. Downloads, validation, and per-file conversion durations are separate from query timing.

The profiler checks eight query results across native DuckDB, retained gzip JSON, and sorted Zstandard Parquet. It writes SQL, parameters, environment, first/warm timings, JSON profiles, plans, and result files; it also verifies the minute-summary hourly fleet result against raw observations. Route options scope the route-window and movement queries; coverage/fleet/quality tasks retain their documented broader scope. No controlled cold-cache or remote-object performance is claimed.

## Planning questions this supports

- How does observed route/line deployment vary by hour and day type, with recorded/expected minute denominators?
- Where do missing observations, stale timestamps, duplicates, or estimated coordinates limit interpretation?
- How variable are bus passages at a fixed pattern-specific screenline, with samples and coverage exclusions?
- Which records have held coordinates, jumps, or continuity breaks that warrant investigation?

The [metric guide](references/metrics-and-queries.md) defines these measures and provides the headway invocation. Daily archives are retrospective data, even though the collector samples roughly every 30–60 seconds. Positions alone do not establish live arrivals, ridership, passenger waiting, cancellations, validated speeds, or on-time performance.

## Validation

```bash
python scripts/test_transit_archive.py
```

Offline tests exercise timestamp units, bad-input rollback, idempotency, cross-process persistence, daylight saving denominators/repeated hours, movement exclusions, and full JSON/Parquet/native profiling under a dated parent directory. [Recorded validation](evals/validation.json) describes the separate seven-day real-data exercise; [evaluation prompts](evals/evals.json) support future behavioral testing. Raw archives and generated databases are not distributed in this repository.
