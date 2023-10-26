# SQL Mock: Python Library for Mocking SQL Queries with Dictionary Inputs

[![PyPI version](https://img.shields.io/pypi/v/sql-mock.svg)](https://pypi.org/project/sql-mock/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/sql-mock.svg)](https://pypi.org/project/sql-mock/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blueviolet.svg)](https://github.com/DeepLcom/sql-mock/blob/main/LICENSE)

The primary purpose of this library is to simplify the testing of SQL data models and queries by allowing users to mock input data and create tests for various scenarios. It provides a consistent and convenient way to test the execution of your query without the need to process a massive amount of data.

The library currently supports the following databases. Database specific documentations are provided in the links:
* [BigQuery](src/sql_mock/bigquery/README.md)
* [Clickhouse](src/sql_mock/clickhouse/README.md)

## Installation

The library can be installed from [PyPI][pypi-project] using pip:

```shell
pip install --upgrade sql-mock
```

To install database specific versions, you can use the following:
```shell
# BigQuery
pip install --upgrade "sql-mock[bigquery]"

# Clickhouse
pip install --upgrade "sql-mock[clickhouse]"
```

If you need to modify this source code, install the dependencies using poetry:

```shell
poetry install --all-extras
```


## Usage

### How it works

Before diving into specific database scenarios, let's start with a simplified example of how SQL Mock works behind the scenes.


1. You have an original SQL query, for instance:
   ```sql
   SELECT id FROM data.table1
   ```


2. Using SQL Mock, you define mock tables. You can use the built-in column types provided by SQL Mock. Available column types include `Int`, `String`, `Date`, and more. Each database type has their own column types. Define your tables by subclassing a mock table class that fits your database (e.g. `BigQueryMockTable`) and specifying the column types along with default values. In our example we use the `ClickhouseTableMock` class
    ```python
    from sql_mock.clickhouse import column_mocks as col
    from sql_mock.clickhouse.table_mocks import ClickHouseTableMock, table_meta

    @table_meta(table_ref='data.table1)
    class Table(ClickHouseTableMock):
        id = col.Int(default=1)
        name = col.String(default='Peter')
    
    @table_meta(table_ref='data.result_table')
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

    input_table_mock = Table.from_dicts(user_data)
    ```


4. **Getting results for a table mock:** Use the `from_inputs` method of the table mock object to generate mock query results based on your mock data.
    ```python
    res = ResultTable.from_mocks(query='SELECT id FROM data.table1', input_data=[input_table_mock])
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


## Contributing

We welcome contributions to improve and enhance this open-source project. Whether you want to report issues, suggest new features, or directly contribute to the codebase, your input is valuable. To ensure a smooth and collaborative experience for both contributors and maintainers, please follow these guidelines:

### Reporting Issues

If you encounter a bug, have a feature request, or face any issues with the project, we encourage you to report them using the project's issue tracker. When creating an issue, please include the following information:

- A clear and descriptive title.
- A detailed description of the problem or suggestion.
- Steps to reproduce the issue (if applicable).
- Any error messages or screenshots that help clarify the problem.

### Feature Requests

If you have ideas for new features or improvements, please use the project's issue tracker to submit a feature request. We appreciate well-documented feature requests that explain the motivation and potential use cases.

### Contributing Code

Find more about contributing code in the [Contribution Guidelines](./CONTRIBUTION.md)
