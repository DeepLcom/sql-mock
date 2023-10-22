

# Using SQL Mock with ClickHouse

## Settings:

You need to provide the following environment variables: 
* `SQL_MOCK_CLICKHOUSE_HOST`: Host of your Clickhouse instance
* `SQL_MOCK_CLICKHOUSE_USER`: User you want to use for the connection
* `SQL_MOCK_CLICKHOUSE_PASSWORD`: Password of your user
* `SQL_MOCK_CLICKHOUSE_PORT`: Port of your Clickhouse instance

## Example: Testing Subscription Counts in ClickHouse

```python
from sql_mock.clickhouse import column_mocks as col
from sql_mock.clickhouse.table_mocks import ClickHouseTableMock
from sql_mock.table_mocks import table_meta

# Define mock tables for your data model that inherit from ClickHouseTableMock
@table_meta(table_ref='data.users')
class UserTable(ClickHouseTableMock):
    user_id = col.Int(default=1)
    user_name = col.String(default="Mr. T")

@table_meta(table_ref='data.subscriptions')
class SubscriptionTable(ClickHouseTableMock):
    subscription_id = col.Int(default=1)
    period_start_date = col.Date(default=datetime.date(2023, 9, 5))
    period_end_date = col.Date(default=datetime.date(2023, 9, 5))
    user_id = col.Int(default=1)

# Define a mock table for your expected results
class SubscriptionCountTable(ClickHouseTableMock):
    subscription_count = col.Int(default=1)
    user_id = col.Int(default=1)

# Your original SQL query
query = """
SELECT
    count(*) AS subscription_count,
    user_id
FROM data.users
LEFT JOIN data.subscriptions USING(user_id)
GROUP BY user_id
"""

# Create mock data for the 'data.users' and 'data.subscriptions' tables
users = UserTable.from_dicts([{'user_id': 1}, {'user_id': 2}])
subscriptions = SubscriptionTable.from_dicts([
    {'subscription_id': 1, 'user_id': 1},
    {'subscription_id': 2, 'user_id': 1},
    {'subscription_id': 2, 'user_id': 2},
])

# Define your expected results
expected = [
    {'user_id': 1, 'subscription_count': 2}, 
    {'user_id': 2, 'subscription_count': 1}
]

# Simulate the SQL query using SQL Mock
res = SubscriptionCountTable.from_mocks(query=query, input_data=[users, subscriptions])

# Assert the results
res.assert_equal(expected)
```
