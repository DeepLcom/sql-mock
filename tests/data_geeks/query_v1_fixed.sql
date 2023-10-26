SELECT 
    dg.data_geek_id,
    dg.name,
    COUNT(mv.data_geek_id) AS visit_count
FROM data.data_geeks AS dg  
LEFT JOIN data.meetup_visits AS mv ON mv.data_geek_id = dg.data_geek_id
GROUP BY 1, 2
