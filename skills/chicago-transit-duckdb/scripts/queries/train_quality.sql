SELECT route,count(*) observations,count(*) FILTER(WHERE approx=true) estimated_coordinates,
 count(*) FILTER(WHERE approx IS NULL) unknown_coordinate_status,
 count(*)-count(DISTINCT (ts,route,vehicle_id,lat,lon,direction,destination,approx,next_station)) duplicate_observations
FROM {source} WHERE kind='train' AND archive_date BETWEEN $start_date::DATE AND $end_date::DATE
GROUP BY route ORDER BY route
