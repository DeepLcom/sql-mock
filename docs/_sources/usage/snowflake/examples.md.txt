```{toctree}
:maxdepth: 2
```

# Example: Testing Subscription Counts in Snowflake

```python
import datetime
from sql_mock.snowflake import column_mocks as col
from sql_mock.snowflake.table_mocks import SnowflakeMockTable
from sql_mock.table_mocks import table_meta

# Define mock tables for your data model that inherit from SnowflakeMockTable
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


# Define a mock table for your expected results
class SubscriptionCountTable(SnowflakeMockTable):
    subscription_count = col.INTEGER(default=1)
    user_id = col.INTEGER(default=1)

# Your original SQL query
query = """
SELECT
    count(*) AS subscription_count,
    user_id
FROM data.users
LEFT JOIN data.subscriptions USING(user_id)
GROUP BY user_id
"""

def test_something():
  # Create mock data for the 'data.users' and 'data.subscriptions' tables
  users = UserTable.from_dicts([{'user_id': 1}, {'user_id': 2}])
  subscriptions = SubscriptionTable.from_dicts([
      {'subscription_id': 1, 'user_id': 1},
      {'subscription_id': 2, 'user_id': 1},
      {'subscription_id': 2, 'user_id': 2},
  ])

  # Define your expected results
  expected = [
      {"USER_ID": 1, "SUBSCRIPTION_COUNT": 2},
      {"USER_ID": 2, "SUBSCRIPTION_COUNT": 1},
  ]

  # Simulate the SQL query using SQL Mock
  res = SubscriptionCountTable.from_mocks(query=query, input_data=[users, subscriptions])

  # Assert the results
  res.assert_equal(expected)
```
