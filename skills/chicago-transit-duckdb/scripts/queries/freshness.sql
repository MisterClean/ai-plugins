SELECT kind,route,count(*) observations,count(*) FILTER(WHERE vehicle_ts IS NULL) missing_source_time,
 quantile_cont((ts-vehicle_ts)/1000.0,0.5) median_source_age_s,
 quantile_cont((ts-vehicle_ts)/1000.0,0.95) p95_source_age_s,
 count(*) FILTER(WHERE vehicle_ts IS NOT NULL AND ts<vehicle_ts) negative_age,
 count(*) FILTER(WHERE vehicle_ts IS NOT NULL AND ts-vehicle_ts>60000) over_60s,
 count(*) FILTER(WHERE vehicle_ts IS NOT NULL) source_timed_observations
FROM {source} WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE
GROUP BY kind,route ORDER BY kind,route
