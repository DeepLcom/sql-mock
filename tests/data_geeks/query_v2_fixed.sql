SELECT 
    dg.data_geek_id,
    COUNT(mv.data_geek_id) AS visit_count
FROM data.data_geeks AS dg 
LEFT JOIN data.meetup_visits AS mv ON 
    mv.data_geek_id = dg.data_geek_id
    AND mv.date >= '2023-01-01' -- Only look at visits from this year
GROUP BY data_geek_id
