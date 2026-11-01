---
name: chicago-transit-duckdb
description: Analyze and efficiently query CTA bus, CTA L train, and Metra vehicle-position archives from chicagotransitalerts.app using DuckDB 2. Use for this position feed, recent Chicago transit data, route or line fleet deployment, sampling cadence, freshness, estimated coordinates, bus headways, movement diagnostics, JSON-to-Parquet conversion, incremental ingestion, or query-performance profiling. Apply even when the user gives only the subscription page or asks for the last several complete days. Do not use as a source of live arrivals, passenger ridership, schedules, or validated on-time performance.
metadata:
  version: "1.0.0"
---

# Chicago Transit with DuckDB

Turn the public daily position archive into a validated, repeatable analytical dataset. Prefer persistent native DuckDB tables for repeated local queries, minute summaries for fleet readouts, and sorted Parquet for portable storage. Treat historical benchmark results as measured evidence, not a guarantee for future workloads.

## Establish scope and evidence

1. Identify Chicago dates, modes, routes/lines, grain and requested output. Infer sensible defaults rather than requiring an implementation questionnaire.
2. Read [source-and-schema.md](references/source-and-schema.md) before ingestion or timestamp interpretation. Fetch the current index once; the subscription page is a discovery page, not the position dataset.
3. Select complete calendar days in `America/Chicago`. For “last seven complete days”, end yesterday in that timezone. Use a trusted client/session date as `--as-of` when supplied. Verify every requested file is published. State missing dates instead of silently substituting an older window.
4. Reuse compatible databases or validated local files. Inspect schema, dates and source manifest before querying. Use the bundled pipeline for a fresh dataset or incremental append.
5. Verify `SELECT version()` reports DuckDB 2.x. Pin `duckdb==2.0.0` for historical reproduction; verify official releases when asked for the current newest version. Record the actual version.

## Ingest and query

Resolve paths relative to this skill directory. Write datasets and outputs to the task workspace, outside the skill folder.

```bash
python -m venv /path/to/venv
/path/to/venv/bin/python -m pip install -r scripts/requirements.txt
# Activate that environment, then use the helpers below.
python scripts/transit_archive.py ingest --db /path/to/transit.duckdb --raw-dir /path/to/raw --days 7
python scripts/transit_archive.py export --db /path/to/transit.duckdb --out /path/to/parquet
python scripts/profile_queries.py --db /path/to/transit.duckdb --start 2026-10-24 --end 2026-10-30 --out /path/to/results --compare-files
```

Use `ingest --end YYYY-MM-DD` for a historical window, `--as-of YYYY-MM-DD` to reproduce completeness on a Chicago date, and `--index /path/to/index.json` to pin metadata. Dependencies: Python 3.10+, DuckDB 2.x, `pytz` for Python timestamp results, `curl` for downloads, and IANA timezone data. The requirements file installs the Python packages; add `duckdb==2.0.0` to the install command for historical reproduction.

The helper verifies hashes, sizes, row counts, required values, coordinate ranges and Chicago dates. It parses explicit schemas and commits each file with its minute summary atomically. Identical ingested hashes are skipped; changed hashes stop rather than duplicating data. Preserve original compressed files and source timestamp values.

Expose `positions_raw` as the common typed source projection, `positions` as normalized timestamps, mode-specific views, and `train_exact_positions` as exact-coordinate deduplicated train records. Preserve stationary observations. Treat null train `approx` flags as unknown. Keep archive calendar date separate from scheduled service date.

Read [metrics-and-queries.md](references/metrics-and-queries.md) before choosing denominators or transit interpretations. Filter dates, kind and route before windows. Use `fleet_minutes` for recurring fleet analysis and inspect `coverage_gaps` before interpreting absences or headways.

Start recurring readouts with all-mode `coverage_daily`, source `freshness`, and `train_quality`; then use `fleet_hourly` for deployment, the pattern-specific screenline pilot for regularity, and `movement_diagnostics` for suspect jumps/held coordinates. Read the catalog for scope and denominators. These helpers analyze published daily archives; they do not subscribe to or operate a live polling feed.

## Apply the source-specific safeguards

- Normalize timestamps by mode and observed magnitude. Bus `vehicle_ts` was milliseconds; Metra was seconds despite schema hints saying milliseconds. Inspect each new batch, retain `vehicle_ts_raw` and reject unrecognized or mixed units. CTA train source timestamps were absent, so equivalent train source-age claims are unavailable.
- Exclude estimated and unknown train coordinates for precise movement; inspect duplicates separately. Run numbers are not physical trainsets.
- Flag missing collection coverage rather than interpreting it as zero vehicles, cancelled trips or an outage. Route absence may also mean no service.
- Count distinct IDs on a fixed time grid instead of weighting by observation rows. Extra train polls otherwise overweight some periods. State recorded-minute and expected-minute denominators.
- Treat displacement/time as diagnostic. Held coordinates, source age, GPS jumps, run reuse and pattern switches can invalidate apparent speeds, especially without train source timestamps.
- Keep pattern-specific screenline headways separate from route-wide or stop-specific headways. Obtain geometry and a common geographic stop before pooling variants. Obtain schedules before judging adherence or missed trips; obtain demand data before claiming ridership or passenger waiting times.

## Profile performance fairly

Read [performance-and-benchmark.md](references/performance-and-benchmark.md) for layout choices and measured historical evidence. Compare logically equivalent queries, fully fetch results and verify equality with explicit floating tolerances. Separate downloading, validation, ingestion, sorting, export and summary construction from query timing.

Report first execution separately from at least three warmed repetitions. A fresh connection does not flush OS caches. Record engine version, CPU availability, threads, memory limit, file/row counts, compression, row groups and query parameters. Profile in separate untimed runs. DuckDB 2.0 nests measurements under `query` and `system`; set JSON format before assigning a `.json` profiling path.

Start with default asynchronous I/O. It benefits Parquet and native storage; JSON still uses synchronous I/O and parsing. Benchmark remote storage separately. Use one database-owning writer process and persistent connections locally. Do not add indexes or duplicate complete layouts without measured benefit.

## Deliver an inspectable answer

Lead with the finding and implication. Include period/timezone, sample sizes, coverage, approximation flags and limits that affect interpretation. Provide SQL, parameters, source/checksum manifest, metric definitions and profiles. Label historical numbers with their environment and dates. Report what was measured rather than inventing latency percentiles, speedups, causes or confidence ratings.

Use [evaluation cases](evals/evals.json) for realistic requests and [recorded validation](evals/validation.json) for the tested environment and outcomes. Run `python scripts/test_transit_archive.py` for offline checks of timestamps, daylight saving, idempotency and complete JSON/Parquet/native query comparisons. These test helpers, not LLM triggering accuracy or comparative agent performance.
