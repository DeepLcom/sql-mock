# SQL Mock: Python Library for Mocking SQL Queries with Dictionary Inputs

## Usage

The primary purpose of this library is to simplify the testing of SQL data models and queries by allowing users to mock input data and create tests for various scenarios. It library provides a consistent and convenient way to test the execution of your query without the need to process a massive amount of data.

The library currently supports the following databases. Database specific documentations are provided in the links:
* [BigQuery](src/sql_mock/bigquery/README.md)
* [Clickhouse](src/sql_mock/clickhouse/README.md)

### How it works

Before diving into specific database scenarios, let's start with a simplified example of how SQL Mock works behind the scenes.


1. You have an original SQL query, for instance:
   ```sql
   SELECT id FROM data.table1
   ```


2. Using SQL Mock, you define mock tables. You can use the built-in column types provided by SQL Mock. Available column types include `Int`, `String`, `Date`, and more. Each database type has their own column types. Define your tables by subclassing a mock table class that fits your database (e.g. `BigQueryMockTable`) and specifying the column types along with default values. In our example we use the `ClickhouseTableMock` class
    ```python
    from sql_mock.clickhouse import column_mocks as col
    from sql_mock.clickhouse.table_mocks import ClickHouseTableMock

    class Table(ClickHouseTableMock):
        id = col.Int(default=1)
        name = col.String(default='Peter')

    class ResultTable(ClickhouseTableMock):
        id = col.Int(default=1)
    ```

3. **Creating mock data:** Define mock data for your tables using dictionaries. Each dictionary represents a row in the table, with keys corresponding to column names. Table column keys that don't get a value will use the default.
    ```python
    user_data = [
        {}, # This will use the defaults for both id and name
        {'id': 2, 'name': 'Martin'},
        {'id': 3}, # This will use defaults for the name
    ]

    table_input_data = Table(data=user_data)
    ```


4. **Getting results for a table mock:** Use the `from_inputs` method of the table mock object to generate mock query results based on your mock data.
    ```python
    res = ResultTable.from_inputs(query='SELECT id FROM data.table1', input_data={'data.table1': table_input_data})
    ```

5. Behind the scene SQL Mock replaces table references (e.g. `data.table1`) in your query with Common Table Expressions (CTEs) filled with dummy data. It can roughly be compared to something like this:
    ```sql
    WITH data__table1 AS (
        -- Mocked inputs
        SELECT 
            cast('1' AS 'String') AS id, 
            cast('Peter' AS 'String') AS name
        UNION ALL 
        SELECT 
            cast('2' AS 'String') AS id, 
            cast('Martin' AS 'String') AS name
        UNION ALL 
        SELECT 
            cast('3' AS 'String') AS id, 
            cast('Peter' AS 'String') AS name
    )

    result AS (
        -- Original query with replaced references
        SELECT id FROM data__table1 
    )

    SELECT 
        cast(id AS 'String') AS id
    FROM result
    ```

6. Finally, you can compare your results to some expected results using the `assert_equal` method.
    ```python
    expected = [{'id': '1'},{'id': '2'},{'id': '3'}]
    res.assert_equal(expected)
    ```

### Setup for Pytest
If you are using pytest, make sure to add a `conftest.py` file to the root of your project.
In the file add the following lines:
```python
import pytest
pytest.register_assert_rewrite('sql_mock')
```
This allows you to get a rich comparison when using the `.assert_equal` method on the table mock instances.

We also recommend using [pytest-icdiff](https://github.com/hjwp/pytest-icdiff) for better visibility on diffs of failed tests.

### Examples
You can find some examples in the [examples folder](examples/).
