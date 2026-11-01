# Source and schema

## Authority and discovery

- Discovery: https://chicagotransitalerts.app/subscribe/
- Manifest: https://data.chicagotransitalerts.app/positions/index.json
- Files: `https://data.chicagotransitalerts.app/positions/{bus,train,metra}/YYYY/MM/YYYY-MM-DD.ndjson.gz`
- Collector documentation: https://github.com/cailinpitt/chicago-transit-insights/blob/main/docs/POSITIONS.md
- Schedule: https://github.com/cailinpitt/chicago-transit-insights/blob/main/cron/crontab.txt
- Pollers: `scripts/observeBuses.js`, `scripts/observeTrains.js`, `scripts/observeMetra.js` in that repository.

Read `generated_at`, schema hints and `days[].files[kind]` entries containing path, rows, bytes and SHA-256. The archive began September 28, 2026. Daily publication ran at 02:40 Chicago time; original database retention was 14 days, distinct from archive availability. These operational details were observed in October 2026 and can change. Read current metadata rather than assuming freshness.

Each file is gzip NDJSON, one observation per line, sorted by collection timestamp. The file date denotes midnight-to-midnight Chicago calendar time, not necessarily a scheduled service day. This archive differs from the site's Atom/JSON service-alert feeds and does not provide live arrival predictions.

Collector baseline: buses about 60 seconds, CTA trains about 30 seconds with extra detector polls, Metra about 30 seconds. This is collection cadence, not guaranteed coordinate-update frequency. Verify observed intervals; inactive service periods can create long vehicle gaps.

## Fields

| Field | Mode | Meaning |
|---|---|---|
| `ts` | all | Collection instant, epoch milliseconds |
| `route` | all | Bus route, CTA line code, Metra line; retain as string |
| `vehicle_id` | all | Bus number, CTA run number, Metra label/fallback ID |
| `lat`, `lon` | all | Coordinates; DOUBLE; valid range does not establish accuracy |
| `vehicle_ts` | bus, Metra | Source position time; independently validate units |
| `pid`, `pdist` | bus | Route-pattern ID and distance along that pattern in feet |
| `destination` | bus, train | Headsign or destination; not a reliable schedule join key |
| `heading` | bus, Metra | Degrees |
| `sched_start_date`, `sched_start_sec` | bus | Scheduled service date YYYYMMDD and seconds after its midnight; values beyond 86400 may be valid |
| `direction` | CTA train | Tracker codes observed as 1 or 5, not universal compass labels |
| `approx` | CTA train | 1 means next-station-based estimated coordinates; null is unknown |
| `next_station` | CTA train | Next-station name |
| `trip_id` | Metra | Join to the matching static schedule version when obtained |

CTA rail codes: `red`, `blue`, `brn` (Brown), `g` (Green), `org` (Orange), `p` (Purple), `pink`, `y` (Yellow).

## Timestamp normalization and daylight saving

In October 24–30, all 666,071 Metra `vehicle_ts` values were epoch seconds while bus values were milliseconds. This contradicted the manifest's Metra unit description. Retain originals; convert only recognized values after checking mode-specific magnitude. Unknown or mixed units require investigation rather than a blanket conversion.

Use `epoch_ms(ts) AT TIME ZONE 'UTC'` for a normalized instant, then convert to `America/Chicago` for calendar labels. Do not attach Chicago timezone directly to UTC wall-clock timestamps. Use half-open time ranges.

Compute bounds from consecutive local midnights. Daylight saving days may contain 1,380 or 1,500 minutes. Keep hourly buckets as UTC instants with local display labels so the repeated autumn 01:00 hour is not merged. A bus's scheduled service date can differ from its archive date after midnight.

## Schema drift and keys

Use explicit schemas but inspect sampled keys and retain original files. The helper logs extra sampled fields, which are not retained as columns in the common projection. Required-field failures, malformed values, unknown/mixed timestamp units and archive-date mismatches stop ingestion. Update the schema deliberately before retrying.

Do not assume `(kind, route, vehicle_id, ts)` is unique. Inspect exact duplicates and conflicting same-key records. Preserve the source projection; deduplicate analytical observation fields before windows. Do not deduplicate solely on coordinates: stationary observations are valid.
