import datetime
from sql_mock.clickhouse import column_mocks as col
from sql_mock.clickhouse.table_mocks import ClickHouseTableMock

query = """
SELECT
    count(*) AS subscription_count,
    user_id
FROM data.users
LEFT JOIN data.subscriptions USING(user_id)
GROUP BY user_id
"""


class UserTable(ClickHouseTableMock):
    user_id = col.Int(default=1)
    user_name = col.String(default="Mr. T")


class SubscriptionTable(ClickHouseTableMock):
    subscription_id = col.Int(default=1)
    period_start_date = col.Date(default=datetime.date(2023, 9, 5))
    period_end_date = col.Date(default=datetime.date(2023, 9, 5))
    user_id = col.Int(default=1)

class SubscriptionCountTable(ClickHouseTableMock):
    subscription_count = col.Int(default=1)
    user_id = col.Int(default=1)

def test_something():
    users = UserTable(data=[{"user_id": 1}, {"user_id": 2}])
    subscriptions = SubscriptionTable(
        data=[
            {"subscription_id": 1, "user_id": 1},
            {"subscription_id": 2, "user_id": 1},
            {"subscription_id": 2, "user_id": 2},
        ]
    )

    expected = [{"user_id": 2, "subscription_count": 1}, {"user_id": 1, "subscription_count": 2}]
    
    res = SubscriptionCountTable.from_inputs(query=query, input_data={"data.users": users, "data.subscriptions": subscriptions})
    
    res.assert_equal(expected)
