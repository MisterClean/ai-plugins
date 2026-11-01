SELECT kind,route,archive_date,count(*) observations,count(DISTINCT vehicle_id) observed_ids,
 min(ts) first_collection_ms,max(ts) last_collection_ms
FROM {source} WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE
GROUP BY kind,route,archive_date ORDER BY kind,route,archive_date
