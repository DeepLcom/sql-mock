WITH subscriptions_per_user AS (
    SELECT
        count(sub.user_id) AS subscription_count,
        users.user_id
    FROM data.users AS users
    LEFT JOIN data.subscriptions AS sub ON sub.user_id = users.user_id
    GROUP BY users.user_id
),

users_with_multiple_subs AS (
    SELECT
        *
    FROM subscriptions_per_user
    WHERE subscription_count >= 2
)

SELECT user_id FROM users_with_multiple_subs
