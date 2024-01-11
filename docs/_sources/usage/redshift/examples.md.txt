```{toctree}
:maxdepth: 2
```

# Example: Testing Subscription Counts in Redshift

```python
import datetime
from sql_mock.redshift import column_mocks as col
from sql_mock.redshift.table_mocks import RedshiftMockTable
from sql_mock.table_mocks import table_meta

# Define mock tables for your data model that inherit from RedshiftMockTable
@table_meta(table_ref="data.users")
class UserTable(RedshiftMockTable):
    user_id = col.INTEGER(default=1)
    user_name = col.VARCHAR(default="Mr. T")


@table_meta(table_ref="data.subscriptions")
class SubscriptionTable(RedshiftMockTable):
    subscription_id = col.INTEGER(default=1)
    period_start_date = col.DATE(default=datetime.date(2023, 9, 5))
    period_end_date = col.DATE(default=datetime.date(2023, 9, 5))
    user_id = col.INTEGER(default=1)

# Define a mock table for your expected results
class SubscriptionCountTable(RedshiftMockTable):
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
