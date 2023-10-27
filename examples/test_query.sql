SELECT
    count(*) AS subscription_count,
    user_id
FROM data.users
LEFT JOIN data.subscriptions USING(user_id)
GROUP BY user_id
