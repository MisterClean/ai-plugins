SELECT (ts//300000)*300000 bucket_start_ms,count(*) observations,count(DISTINCT vehicle_id) observed_ids,
 avg((ts-vehicle_ts)/1000.0) mean_source_age_s
FROM {source} WHERE kind=$kind AND route=$route
 AND archive_date BETWEEN $start_date::DATE AND $end_date::DATE
 AND ts>=epoch_ms($window_start::TIMESTAMPTZ) AND ts<epoch_ms($window_end::TIMESTAMPTZ)
GROUP BY bucket_start_ms ORDER BY bucket_start_ms
