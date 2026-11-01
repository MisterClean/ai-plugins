# Performance and measured evidence

## Starting architecture

Retain immutable gzip JSON. Parse and validate once, append native rows in daily batches sorted by kind/route/time/vehicle, and maintain minute-level distinct-ID summaries. Export Parquet by kind/archive date with Zstandard and initially 122,880-row groups. Benchmark other orderings and smaller train groups only for relevant workloads.

Small daily train files limit per-file parallelism. Weekly/monthly compaction may help remote scans but trades against date pruning. Avoid vehicle or route/hour fragmentation. Choose remote files through a manifest, verify range requests, and measure transferred bytes and requests. Native storage and Parquet support column/filter pruning; native tables add statistics useful for repeated or join-heavy workloads.

Start with one SSD-backed database and persistent connections. Filter dates, mode and route; select needed columns. Sorting improves automatic min/max pruning. Add ART indexes only after measuring highly selective equality queries; they do not generally accelerate aggregate/window work. Monitor spill space; engine buffers are not process RSS.

DuckDB 2.0 uses asynchronous I/O for supported Parquet, seekable CSV and native storage, while JSON remains synchronous. Start with defaults, then tune asynchronous threads/read-ahead if measured I/O requires it. Do not blindly increase CPU workers to create more remote requests. Use one database-owning writer; evaluate Quack/DuckLake only if a shared deployment actually needs them.

## Historical test: October 24–30, 2026

Measured in the original benchmark using DuckDB Python 2.0.0, Linux x86_64, nine available CPUs, eight workers, 5GB engine memory limit, local files. All 21 files passed SHA-256, size and row-count verification. Total: 9,369,989 observations; bus 6,766,005, CTA train 1,937,913, Metra 666,071. Three warm runs followed a first execution; complete fetch/Python dictionary construction included. OS caches were not flushed. Equivalent results matched with floating-point rounding to seven decimals.

| Query | Gzip JSON ms | Zstd Parquet ms | Native daily route/time ms |
|---|---:|---:|---:|
| Route 66, one hour | 566.6 | 8.9 | 3.3 |
| Red Line, one hour | 92.6 | 8.7 | 6.7 |
| Daily fleet by route/line | 3777.0 | 61.2 | 54.1 |
| Bus source freshness | 3159.4 | 119.8 | 65.9 |
| Sampling gaps, 66 and Red | 3720.0 | 124.0 | 90.6 |
| Train position quality | 478.3 | 111.1 | 96.5 |
| Hourly fleet, all modes | 4042.7 | 347.6 | 229.7 |
| Movement, five routes/lines | 3768.7 | 290.9 | 224.2 |
| Pilot bus screenline headways | 3555.2 | 149.8 | 85.4 |

The same hourly result took 32.6ms from 1,006,676 minute-summary rows built in 0.325s. Summed per-file parse/validation/sorted inserts: 10.21s, excluding downloads/final checkpoint. Parquet export: 1.76s. Gzip files: 275,981,524 bytes; Parquet: 119,148,564 bytes; delivered one-layout native database plus summary: approximately 213MB. A globally vehicle-sorted native alternative traded small wins; this did not justify two copies by default. Maximum profiled query buffers were approximately 1.28GB; no temp spill.

No controlled cold-disk, remote-object, concurrent-client, daily append-only or multi-year benchmark was performed. Three warm repetitions do not establish production p95 latency. The reusable bundled helper changes some query definitions (including normalized Metra freshness); do not claim it exactly reproduces every historical number.

Period-specific quality findings: 167 exact duplicate train rows; Yellow 51.92% and Green 1.53% estimated coordinates; 39 globally missing bus minute bins including October 30 17:41–18:06 Chicago; Metra source times in seconds contrary to manifest hints. Recheck rather than treating these as permanent feed properties.

## Repository integration validation

See [evals/validation.json](../evals/validation.json) for the October 31, 2026 integration exercise on macOS: a fresh download, seven-day native conversion, incremental append, Parquet export, equal-result profiling, and an independent read-only planning exercise. It records a separate environment and query set; do not substitute those timings for the historical Linux table above. The integration fixed an undeclared Python timezone dependency and archive-date extraction from dated parent directories, and added executable coverage/denominator and guarded movement queries.

## Profiling protocol

Capture first execution and warm median/min/max/runs; randomize task order where possible. Match complete results, with explicit numerical tolerances. Save SQL/parameters. Profile separately from timed runs. EXPLAIN ANALYZE executes the query and can establish pruning, scans and row-group behavior.

Set `enable_profiling='json'` before assigning a `.json` `profiling_output`. DuckDB 2.0 stores CPU/scanned-row/group data in `query`, engine buffer/temp peaks in `system`, and byte counters in `io`. Inspect actual keys when versions change; leave unavailable metrics unknown. Label first execution as such unless OS caches were controlled. Measure preprocessing and incremental refresh costs separately when requested.

Official documentation:

- https://duckdb.org/docs/2.0/guides/performance/file_formats
- https://duckdb.org/docs/2.0/data/parquet/tips
- https://duckdb.org/docs/2.0/guides/performance/indexing
- https://duckdb.org/docs/2.0/data/io
- https://duckdb.org/docs/2.0/guides/performance/how_to_tune_workloads
- https://duckdb.org/docs/2.0/connect/concurrency
- https://duckdb.org/release_calendar

Skill-design reference: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md . Use concise core instructions, progressive disclosure, deterministic helpers and realistic evaluation prompts. Creator-repository code is not included in this package.
