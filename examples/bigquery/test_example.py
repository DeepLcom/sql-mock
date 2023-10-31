import datetime

from sql_mock.bigquery import column_mocks as col
from sql_mock.bigquery.table_mocks import BigQueryMockTable
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="data.users")
class UserTable(BigQueryMockTable):
    user_id = col.Int(default=1)
    user_name = col.String(default="Mr. T")


@table_meta(table_ref="data.subscriptions")
class SubscriptionTable(BigQueryMockTable):
    subscription_id = col.Int(default=1)
    period_start_date = col.Date(default=datetime.date(2023, 9, 5))
    period_end_date = col.Date(default=datetime.date(2023, 9, 5))
    user_id = col.Int(default=1)


@table_meta(query_path="./examples/test_query.sql")
class MultipleSubscriptionUsersTable(BigQueryMockTable):
    user_id = col.Int(default=1)


def test_something():
    users = UserTable.from_dicts([{"user_id": 1}, {"user_id": 2}])
    subscriptions = SubscriptionTable.from_dicts(
        [
            {"subscription_id": 1, "user_id": 1},
            {"subscription_id": 2, "user_id": 1},
            {"subscription_id": 2, "user_id": 2},
        ]
    )

    subscriptions_per_user__expected = [
        {"user_id": 1, "subscription_count": 2},
        {"user_id": 2, "subscription_count": 1},
    ]
    users_with_multiple_subs__expected = [{"user_id": 1, "subscription_count": 2}]
    end_result__expected = [{"user_id": 1}]

    res = MultipleSubscriptionUsersTable.from_mocks(input_data=[users, subscriptions])

    # Check the results of the subscriptions_per_user CTE
    res.assert_cte_equal("subscriptions_per_user", subscriptions_per_user__expected)
    # Check the results of the users_with_multiple_subs CTE
    res.assert_cte_equal("users_with_multiple_subs", users_with_multiple_subs__expected)
    # Check the end result
    res.assert_equal(end_result__expected)
