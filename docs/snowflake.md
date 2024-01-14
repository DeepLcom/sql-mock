# Bigquery Docs

## Settings

In order to use SQL Mock with Snowflake, you need to provide the following environment variables when you run tests:

* `SQL_MOCK_SNOWFLAKE_ACCOUNT`: The name of your Snowflake account
* `SQL_MOCK_SNOWFLAKE_USER`: The name of your Snowflake user
* `SQL_MOCK_SNOWFLAKE_PASSWORD`: The password for your Snowflake user

Having those environment variables enables SQL Mock to connect to your Snowflake instance.

## Example: Testing Subscription Counts in Snowflake

```python
import datetime
from sql_mock.snowflake import column_mocks as col
from sql_mock.snowflake.table_mocks import SnowflakeTableMock
from sql_mock.table_mocks import table_meta

# Define table mocks for your data model that inherit from SnowflakeTableMock
@table_meta(table_ref="data.users")
class UserTable(SnowflakeTableMock):
    user_id = col.INTEGER(default=1)
    user_name = col.STRING(default="Mr. T")


@table_meta(table_ref="data.subscriptions")
class SubscriptionTable(SnowflakeTableMock):
    subscription_id = col.INTEGER(default=1)
    period_start_date = col.DATE(default=datetime.date(2023, 9, 5))
    period_end_date = col.DATE(default=datetime.date(2023, 9, 5))
    user_id = col.INTEGER(default=1)


# Define a mock table for your expected results
class SubscriptionCountTable(SnowflakeTableMock):
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
