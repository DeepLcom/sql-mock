# SQL Mock: Python Library for Mocking SQL Queries with Dictionary Inputs

SQL Mock is a Python library that simplifies the process of mocking SQL queries with dictionary inputs for testing purposes. This library allows you to create mock tables, define mock data, and simulate SQL query results, making it easier to test your SQL-related code without the need for a real database connection.


SQL Mock: Effortless SQL Query Testing with Dummy Data

SQL Mock is a Python library that simplifies the testing of SQL queries by seamlessly replacing table references with Common Table Expressions (CTEs) filled with dummy data. Here's how it works:

### Setup for Pytest
If you are using pytest, make sure to add a `conftest.py` file to the root of your project.
In the file add the following lines:
```python
import pytest
pytest.register_assert_rewrite('sql_mock')
```
This allows you to get a rich comparison when using the `.assert_equal` method on the table mock instances.

We also recommend using [pytest-icdiff](https://github.com/hjwp/pytest-icdiff) for better visibility on diffs of failed tests.

### What It Does:

Table Reference Replacement: SQL Mock takes your SQL query and cleverly replaces table references (e.g., `<schema>.<table>`) with CTEs containing dummy data. For example:

Original SQL Query:

```sql
SELECT id FROM data.table1
```

SQL Mock test:
```python
from sql_mock.clickhouse import column_mocks as col
from sql_mock.clickhouse.table_mocks import ClickHouseTableMock

class Table(ClickHouseTableMock):
    id = col.String(default=1)

class ResultTable(ClickhouseTableMock):
    id = col.String(default=1)

query = 'SELECT id FROM data.table1'
sql_mock = ClickHouseSQLMock(query=query)

table_data = Table(data=[{}, {'id': 2}])
res = ResultTable.from_inputs(query=query, input_data={"data.table1": table_data})
```

What roughly happens behind the scence:
```sql
WITH data__table1 AS (
  SELECT cast('1' AS 'String') AS id
  UNINON ALL 
  SELECT cast('2' AS 'String') AS id
)
SELECT id FROM data__table1
```

* **Effortless Testing**: You can now test your SQL queries without needing a real test data. SQL Mock provides a playground for your queries.

* **Streamlined Mocking**: Creating CTEs with mock data is effortless, so you can focus on testing your SQL logic.

### When It's Useful:

* **Query Testing:** If you're working with SQL queries and want to test them thoroughly, SQL Mock allows you to do so without the need for test data in the database.

* **Database-Independent Testing**: When you want your tests to be independent of specific database setups, SQL Mock steps in to provide a consistent testing environment.

* **Quick and Isolated Testing:** SQL Mock speeds up testing by isolating it from real data sources, allowing for faster development cycles.

In a nutshell, SQL Mock simplifies query testing by seamlessly replacing table references with CTEs filled with dummy data. It's the perfect tool for developers who need efficient and reliable SQL query testing, regardless of their database environment.


## Usage

### Defining Mock Tables

To create mock tables, you can use the built-in column types provided by SQL Mock. Available column types include `Int`, `String`, `Date`, and more. Define your tables by subclassing `BaseMockTable` or other table mock instances and specifying the column types along with default values. In our example we use the `ClickhouseTableMock` class

```python
from sql_mock.clickhouse import column_mocks as col
from sql_mock.clickhouse.table_mocks import ClickhouseTableMock

class UserTable(ClickhouseTableMock):
    user_id = col.Int(default=1)
    user_name = col.String(default="John Doe")
```

### Creating Mock Data

Define mock data for your tables using dictionaries. Each dictionary represents a row in the table, with keys corresponding to column names. Table column keys that don't get a value will use the default

```python
user_data = [
    {"user_id": 1, "user_name": "Alice"},
    {"user_id": 2}, # This will use the default 'John Doe' as user_name
    {} # This will use the defaults for both user_id and user_name
]
```

### Getting results for a table mock

Create an table mock object for your final model. 
Use the `ClickHouseTableMock` class for ClickHouse setups or an appropriate class for your database system.

```python
from sql_mock.clickhouse.table_mocks import ClickHouseSQLMock

query = """
SELECT user_id, user_name
FROM data.users
WHERE user_id = 1
"""
class ResultTable(ClickhouseTableMock):
    user_id = col.Int(default=1)
    user_name = col.String(default="John Doe")
```

### Generating Mock Query Results

Use the `from_inputs` method of the table mock object to generate mock query results based on your mock data.

```python
results = ResultTable.from_inputs(query=query, input_data={"data.users": user_data})

# Now, you can test and assert the results as needed usin the assert_equal method.
results.assert_equal(<some expected data>)
```

## Example

Here's a complete example of how to use SQL Mock for testing for Clickhouse:

```python
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
```
