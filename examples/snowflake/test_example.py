import datetime

from sql_mock.snowflake import column_mocks as col
from sql_mock.snowflake.table_mocks import SnowflakeMockTable
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="data.users")
class UserTable(SnowflakeMockTable):
    user_id = col.INTEGER(default=1)
    user_name = col.STRING(default="Mr. T")


@table_meta(table_ref="data.subscriptions")
class SubscriptionTable(SnowflakeMockTable):
    subscription_id = col.INTEGER(default=1)
    period_start_date = col.DATE(default=datetime.date(2023, 9, 5))
    period_end_date = col.DATE(default=datetime.date(2023, 9, 5))
    user_id = col.INTEGER(default=1)


@table_meta(
    query_path="./examples/test_query.sql",
    default_inputs=[
        UserTable([]),
        SubscriptionTable([]),
    ],  # We can provide defaults for the class if needed. Then we don't always need to provide data for all input tables.
)
class MultipleSubscriptionUsersTable(SnowflakeMockTable):
    user_id = col.INTEGER(default=1)


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
        {"USER_ID": 1, "SUBSCRIPTION_COUNT": 2},
        {"USER_ID": 2, "SUBSCRIPTION_COUNT": 1},
    ]
    users_with_multiple_subs__expected = [{"USER_ID": 1, "SUBSCRIPTION_COUNT": 2}]
    end_result__expected = [{"USER_ID": 1}]

    res = MultipleSubscriptionUsersTable.from_mocks(input_data=[users, subscriptions])

    # Check the results of the subscriptions_per_user CTE
    res.assert_cte_equal("subscriptions_per_user", subscriptions_per_user__expected)
    # Check the results of the users_with_multiple_subs CTE
    res.assert_cte_equal("users_with_multiple_subs", users_with_multiple_subs__expected)
    # Check the end result
    res.assert_equal(end_result__expected)


def test_with_defaults_for_subscriptions_table():
    """
    In this test case we don't provide a mock for subscriptions
    because we use the class default Subscriptions([]) which translates to an empty table.
    """
    users = UserTable.from_dicts(
        [
            {"user_id": 1},
            {"user_id": 2},
        ]
    )

    subscriptions_per_user__expected = [
        {"USER_ID": 1, "SUBSCRIPTION_COUNT": 0},
        {"USER_ID": 2, "SUBSCRIPTION_COUNT": 0},
    ]
    users_with_multiple_subs__expected = []
    end_result__expected = []

    # We don't provide a mock input for subscriptions
    res = MultipleSubscriptionUsersTable.from_mocks(input_data=[users])

    # Check the results of the subscriptions_per_user CTE
    res.assert_cte_equal("subscriptions_per_user", subscriptions_per_user__expected)
    # Check the results of the users_with_multiple_subs CTE
    res.assert_cte_equal("users_with_multiple_subs", users_with_multiple_subs__expected)
    # Check the end result
    res.assert_equal(end_result__expected)
