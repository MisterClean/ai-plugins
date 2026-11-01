-- Empirical bus headways at one fixed distance along each observed route pattern.
-- No schedule or stop adherence is implied. Missing crossings can lengthen headways.
WITH points AS (
 SELECT DISTINCT route,pid,vehicle_id,archive_date,ts,vehicle_ts,pdist
 FROM {source}
 WHERE kind='bus' AND route=$route AND archive_date BETWEEN $start_date::DATE AND $end_date::DATE
 AND vehicle_ts IS NOT NULL AND pdist IS NOT NULL
), gates AS (
 SELECT route,pid,coalesce(CAST($gate_ft AS DOUBLE),quantile_cont(pdist,0.5)) gate_ft
 FROM points GROUP BY route,pid
), previous AS (
 SELECT *,lag(pdist) OVER w previous_ft,lag(vehicle_ts) OVER w previous_time
 FROM points WINDOW w AS(PARTITION BY route,pid,vehicle_id ORDER BY ts)
), crossings AS (
 SELECT p.route,p.pid,p.archive_date,p.vehicle_id,g.gate_ft,
 previous_time+(gate_ft-previous_ft)/(pdist-previous_ft)*(vehicle_ts-previous_time) cross_ms
 FROM previous p JOIN gates g USING(route,pid)
 WHERE previous_ft<gate_ft AND pdist>=gate_ft
 AND pdist-previous_ft BETWEEN 1 AND 4000
 AND vehicle_ts-previous_time BETWEEN 1000 AND 120000
), passage_gaps AS (
 SELECT *,lag(cross_ms) OVER (PARTITION BY route,pid,vehicle_id,archive_date ORDER BY cross_ms) previous_vehicle_cross
 FROM crossings
), passage_episodes AS (
 SELECT *,sum(CASE WHEN previous_vehicle_cross IS NULL OR cross_ms-previous_vehicle_cross>300000 THEN 1 ELSE 0 END)
 OVER(PARTITION BY route,pid,vehicle_id,archive_date ORDER BY cross_ms ROWS UNBOUNDED PRECEDING) episode
 FROM passage_gaps
), passages AS (
 -- Collapse repeated gate crossings by the same bus within five minutes (GPS jitter).
 SELECT route,pid,archive_date,vehicle_id,gate_ft,episode,min(cross_ms) cross_ms
 FROM passage_episodes GROUP BY ALL
), ordered AS (
 SELECT *,lag(cross_ms) OVER w previous_cross_ms
 FROM passages WINDOW w AS(PARTITION BY route,pid,archive_date ORDER BY cross_ms)
), classified AS (
 SELECT *,extract(hour FROM epoch_ms(cross_ms::BIGINT) AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago') hour_local,
 extract(hour FROM epoch_ms(previous_cross_ms::BIGINT) AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago') previous_hour_local,
 (cross_ms-previous_cross_ms)/60000.0 headway_minutes
 FROM ordered WHERE isodow(archive_date)<=5
)
SELECT route,pid,CASE WHEN hour_local=8 THEN '08:00-09:00' ELSE '17:00-18:00' END peak_period,
 count(*) headway_intervals,count(DISTINCT archive_date) days_observed,min(gate_ft) gate_ft,
 avg(headway_minutes) mean_headway_min,
 quantile_cont(headway_minutes,0.5) median_headway_min,
 quantile_cont(headway_minutes,0.9) p90_headway_min,
 stddev_pop(headway_minutes)/avg(headway_minutes) headway_cv,
 count(*) FILTER(WHERE headway_minutes<2) headways_under_2_min
FROM classified WHERE hour_local IN (8,17) AND previous_hour_local=hour_local
AND NOT EXISTS (
 SELECT 1 FROM coverage_gaps g
 WHERE previous_cross_ms<g.end_ts AND cross_ms>=g.start_ts
)
GROUP BY route,pid,peak_period ORDER BY route,pid,peak_period
