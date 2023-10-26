SELECT 
    dg.data_geek_id,
    dg.name,
    COUNT(*) AS visit_count
FROM data.meetup_visits AS mv 
LEFT JOIN data.data_geeks AS dg ON mv.data_geek_id = dg.data_geek_id
