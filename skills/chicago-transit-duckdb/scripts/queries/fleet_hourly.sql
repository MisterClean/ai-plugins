WITH m AS (
 SELECT kind,route,archive_date,ts//60000 minute_id,count(DISTINCT vehicle_id) vehicles
 FROM {source} WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE
 GROUP BY kind,route,archive_date,minute_id
)
SELECT kind,route,archive_date,(minute_id//60)*3600000 hour_start_ms,
 count(*) minutes_observed,60::BIGINT expected_calendar_minutes,
 avg(vehicles) mean_observed_ids,min(vehicles) minimum_observed_ids,max(vehicles) maximum_observed_ids
FROM m GROUP BY kind,route,archive_date,hour_start_ms ORDER BY kind,route,archive_date,hour_start_ms
