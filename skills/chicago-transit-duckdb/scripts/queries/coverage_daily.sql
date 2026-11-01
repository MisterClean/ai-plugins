-- Calendar coverage by mode, not proof of collector uptime or scheduled service.
-- Compare against archive_ingest: wholly empty mode-days do not appear here.
SELECT kind,archive_date,count(*) observations,
 count(DISTINCT ts//60000) minutes_observed,
 (epoch_ms((archive_date+INTERVAL 1 DAY)::TIMESTAMP AT TIME ZONE 'America/Chicago')
  -epoch_ms(archive_date::TIMESTAMP AT TIME ZONE 'America/Chicago'))//60000 expected_calendar_minutes,
 count(DISTINCT ts) collection_instants,
 min(ts) first_collection_ms,max(ts) last_collection_ms
FROM {source}
WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE
GROUP BY kind,archive_date ORDER BY kind,archive_date
