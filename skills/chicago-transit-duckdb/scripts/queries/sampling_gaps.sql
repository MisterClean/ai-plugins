WITH u AS (
 SELECT DISTINCT kind,route,vehicle_id,ts FROM {source}
 WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE
), w AS (
 SELECT *,lag(ts) OVER(PARTITION BY kind,route,vehicle_id ORDER BY ts) previous_ts FROM u
)
SELECT kind,route,count(*) intervals,quantile_cont((ts-previous_ts)/1000.0,0.5) median_gap_s,
 quantile_cont((ts-previous_ts)/1000.0,0.95) p95_gap_s,
 count(*) FILTER(WHERE ts-previous_ts>90000) gaps_over_90s
FROM w WHERE previous_ts IS NOT NULL GROUP BY kind,route ORDER BY kind,route
