# Metrics and queries

Treat these as feed observations and observed deployment, not validated schedule adherence. Obtain authoritative schedules, geometry, stop passages, capacities and passenger counts before making claims requiring them.

## Bundled query catalog

SQL lives in `scripts/queries/`. Read a query before adapting its parameters. `{source}` is a trusted relation identifier substituted by the profiler; other inputs use DuckDB named parameters.

| Query | Output grain | Limitation |
|---|---|---|
| daily_fleet | Mode/route/calendar day: records, distinct IDs, collection bounds | IDs are not trips or physical trainsets |
| fleet_hourly | Recorded route-minute distinct IDs summarized into UTC hours, with recorded/expected calendar minutes | Missing route-minutes remain unknown |
| coverage_daily | Mode/calendar day: observed minutes, DST-aware expected minutes, collection instants and bounds | Empty mode-days require manifest inspection; inactive service is not proven collector failure |
| freshness | Mode/route: source age median/p95, missing/negative times, share >60s | Train source age unavailable; normalize Metra first |
| train_quality | Line: estimated/unknown coordinates, duplicate analytical observations | Duplicates and estimation vary with time |
| sampling_gaps | Consecutive deduplicated vehicle observations | Service breaks are not proven collection faults |
| route_window | Chosen mode/route/time window, five-minute observed IDs | Vehicle turnover can inflate long-window ID counts |
| movement_diagnostics | Chosen mode/route: usable, held, suspect-jump and excluded consecutive pairs | Diagnostic displacement/time, not validated operating speed |

For deployment, use distinct IDs per fixed minute. Record `minutes_observed` and expected calendar coverage. A record-based average overweights densely polled trains. IDs observed at any point within a minute still differ from instantaneous fleet size. Layovers and non-revenue movements may be included. Do not call more vehicles on a longer route better service.

`fleet_hourly` and `summary_hourly.sql` use UTC hour instants, each containing 60 expected calendar minutes even on Chicago daylight saving days. They return hours with observations only; an absent route-hour is unknown rather than zero. `coverage_daily` derives 1,380/1,440/1,500-minute day bounds from Chicago midnights. Check `archive_ingest` for wholly empty or absent mode-days, which a position-based query cannot emit. All-mode missing minutes include inactive service periods, especially overnight Metra, so coverage is not an uptime percentage without an operating calendar.

Inspect system-wide `coverage_gaps` before route-specific absence. It describes missing global bus record bins, not confirmed collector downtime or a suspension. Missing route records may also mean no scheduled service. Do not fill unknown route-minutes with zero without evidence.

Compute source age from normalized milliseconds. Report missing source times and negative ages alongside quantiles and a named threshold. Sixty seconds is descriptive, not a CTA SLA. Use `positions.vehicle_ts` for Metra; do not subtract raw epoch seconds from milliseconds.

## Pilot screenline headways

Use `scripts/screenline_headways.sql` as a starting point. Keep each `pid` separate: pattern IDs distinguish variants as well as directions, and their distance coordinates do not define one common geographic point.

1. Fix a gate along each pattern. The example uses median observed `pdist`; freeze its location before comparing periods, because a sample-dependent median can move.
2. Identify same-bus/pattern consecutive observations bracketing the gate. Require positive distance change, reasonable source-time separation and no long unobserved jump.
3. Interpolate source-time crossing; collapse repeated crossings by the same bus within five minutes to reduce jitter. That heuristic suits the long sample routes, not arbitrary short loops.
4. Sort passages and calculate headways by pattern/day. Exclude intervals overlapping missing global bus bins. Retain boundary context where feasible: the example requires both endpoints within the same hour, which truncates long intervals and must be disclosed.
5. Report sample count, days, gate rule/location, mean/median/p90, coefficient of variation and share under a descriptive short-headway threshold. Missing individual passages may still inflate headways.

Show interval counts and represented days beside each result; small pattern/peak samples can make p90 and variability unstable. Keep such results exploratory rather than ranking patterns on a handful of passages.

Do not label these route-wide stop headways or passenger waiting times. Obtain geometry and validated common stop passages before pooling branches; obtain schedules before judging expected headway.

Run the pilot explicitly against a compatible database containing `positions` and `coverage_gaps`:

```python
import duckdb
from pathlib import Path
con = duckdb.connect('/path/to/transit.duckdb', read_only=True)
sql = Path('/path/to/skill/scripts/screenline_headways.sql').read_text()
result = con.execute(sql.format(source='positions'), {
    'start_date': '2026-10-24', 'end_date': '2026-10-30',
    'route': '66', 'gate_ft': None,
}).fetchall()
```

Pass a fixed `gate_ft` to hold the screenline constant across periods. Update the query's peak-hour classification when the user's question requires a different window; do not silently reuse its 08:00 and 17:00 weekday defaults.

## Movement diagnostics

Run `scripts/queries/movement_diagnostics.sql` with `source='positions'`, `start_date`, `end_date`, `kind`, and `route`, or select the route with the profiler's `--kind`/`--route` options. The profiler also runs the broader fleet/quality queries; its route options scope the route-window and movement tasks. The template preserves consecutive-observation adjacency before exclusions, rejects conflicting same-poll endpoints, checks pattern/direction/destination/trip continuity, and requires both poll and normalized source-time gaps of 15–120 seconds. Missing source timestamps fall back to poll time, including all CTA train records; inspect `freshness` before interpreting the time basis. Its exclusion counts overlap; do not sum them as a partition. Adapt descriptive thresholds explicitly for other use cases.

Deduplicate analytical observations; partition by mode, route and vehicle; preserve pattern/direction/trip continuity and avoid bridging run reuse or long breaks. Use source-time differences where available. Exclude estimated and unknown train endpoints. Flag zero/negative time differences, long gaps, reversals and coordinate jumps.

Great-circle displacement is a chord, not actual path distance. Held coordinates followed by a jump can inflate poll-to-poll speed; train collection time is especially unreliable as source time. The historical test used 15–120-second intervals, counted >90mph jumps separately, and reported moving percentiles for displacements at least 10m and speeds at most 90mph. These were diagnostic filters, not validated physical limits. Preserve exclusions and do not publish these as commercial or validated train speeds.

## Useful recurring reports

- Feed QA: all-mode calendar coverage and cadence, source-age distributions, negative/missing timestamps, estimated train coordinates and duplicates.
- Observed deployment: route/line UTC-hour or peak-period fixed-minute IDs, split by weekday/weekend, with recorded and expected minutes. Compare like time windows and route patterns; daily distinct IDs are not a fleet snapshot.
- Bus regularity pilot: fixed-pattern screenline passages, headway spread and short intervals, with sample sizes, global-gap exclusions and boundary truncation. Freeze per-pattern gates across comparisons.
- Movement QA: held coordinates, jumps and excluded pairs by route/line. Use these to select records for investigation, not to rank commercial speeds.

For a continuous 30/60-second operations dashboard, separately obtain an authorized live feed and track collection health, source age and update cadence. This daily archive cannot supply current dispatch decisions or real-time arrivals.

## Evidence required for stronger claims

| Claim | Additional evidence |
|---|---|
| Missed trips, cancellations, on-time performance | Applicable service calendar, schedule version, trip/run mapping and feed health |
| Stop headways, passenger waiting | Geographic stop passages, direction/branch handling, coverage and arrival assumptions |
| Ridership, crowding, passenger delay | Passenger counts, capacity or an authoritative demand model |
| Corridor commercial speed | Validated path distance and stop-to-stop times, dwell and source continuity |
| Cause of disruption | Independent incident or operating evidence; positions alone establish association |
