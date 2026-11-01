-- Displacement/source-time diagnostics for ONE chosen route/line; not service speed.
-- CTA trains fall back to collection time because source timestamps are absent.
WITH u AS (
 SELECT DISTINCT kind,route,vehicle_id,ts,vehicle_ts,lat,lon,pid,direction,destination,trip_id,approx
 FROM {source}
 WHERE kind=$kind AND route=$route
 AND archive_date BETWEEN $start_date::DATE AND $end_date::DATE
), variants AS (
 SELECT *,count(*) OVER(PARTITION BY kind,route,vehicle_id,ts) same_poll_variants FROM u
), w AS (
 SELECT *,lag(ts) OVER v previous_ts,
 lag(coalesce(vehicle_ts,ts)) OVER v previous_time,
 lag(lat) OVER v previous_lat,lag(lon) OVER v previous_lon,
 lag(pid) OVER v previous_pid,lag(direction) OVER v previous_direction,
 lag(destination) OVER v previous_destination,lag(trip_id) OVER v previous_trip,
 lag(approx) OVER v previous_approx,lag(same_poll_variants) OVER v previous_variants
 FROM variants WINDOW v AS(PARTITION BY kind,route,vehicle_id ORDER BY ts)
), pairs AS (
 SELECT *, (ts-previous_ts)/1000.0 poll_gap_s,
 (coalesce(vehicle_ts,ts)-previous_time)/1000.0 time_gap_s,
 2*6371008.8*asin(sqrt(least(1.0,
 pow(sin(radians(lat-previous_lat)/2),2)
 +cos(radians(lat))*cos(radians(previous_lat))*pow(sin(radians(lon-previous_lon)/2),2)))) displacement_m,
 (kind!='train' OR (approx=false AND previous_approx=false)) IS TRUE exact_endpoints,
 pid IS NOT DISTINCT FROM previous_pid AND direction IS NOT DISTINCT FROM previous_direction
 AND destination IS NOT DISTINCT FROM previous_destination AND trip_id IS NOT DISTINCT FROM previous_trip continuous
 FROM w WHERE previous_ts IS NOT NULL
), checked AS (
 SELECT *,displacement_m/nullif(time_gap_s,0)*2.2369362921 diagnostic_mph,
 exact_endpoints AND continuous AND same_poll_variants=1 AND previous_variants=1
 AND poll_gap_s BETWEEN 15 AND 120 AND time_gap_s BETWEEN 15 AND 120 usable
 FROM pairs
)
SELECT kind,route,count(*) candidate_pairs,
 count(*) FILTER(WHERE NOT exact_endpoints) estimated_or_unknown_endpoint_pairs,
 count(*) FILTER(WHERE NOT continuous) continuity_change_pairs,
 count(*) FILTER(WHERE same_poll_variants>1 OR previous_variants>1) ambiguous_poll_pairs,
 count(*) FILTER(WHERE time_gap_s<=0) nonpositive_time_pairs,
 count(*) FILTER(WHERE poll_gap_s>120 OR time_gap_s>120) long_gap_pairs,
 count(*) FILTER(WHERE usable) usable_pairs,
 count(*) FILTER(WHERE usable AND displacement_m<1) held_coordinate_pairs,
 count(*) FILTER(WHERE usable AND diagnostic_mph>90) over_90mph_pairs,
 count(*) FILTER(WHERE usable AND displacement_m>=10 AND diagnostic_mph<=90) moving_pairs,
 quantile_cont(diagnostic_mph,0.5) FILTER(WHERE usable AND displacement_m>=10 AND diagnostic_mph<=90) moving_pair_median_mph,
 quantile_cont(diagnostic_mph,0.95) FILTER(WHERE usable AND displacement_m>=10 AND diagnostic_mph<=90) moving_pair_p95_mph
FROM checked GROUP BY kind,route ORDER BY kind,route
