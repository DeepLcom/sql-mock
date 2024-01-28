<img src="./SQLMock_logo.png" alt="SQLMock Logo" width="250"/>

# SQL Mock: Python Library for Mocking SQL Queries with Dictionary Inputs

[![PyPI version](https://img.shields.io/pypi/v/sql-mock.svg)](https://pypi.org/project/sql-mock/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/sql-mock.svg)](https://pypi.org/project/sql-mock/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blueviolet.svg)](https://github.com/DeepLcom/sql-mock/blob/main/LICENSE)

The primary purpose of this library is to simplify the testing of SQL data models and queries by allowing users to mock input data and create tests for various scenarios. It provides a consistent and convenient way to test the execution of your query without the need to process a massive amount of data.

## Documentation

* [Installation](#installation)
* [Quickstart](#quickstart)
* Basic usage
  * [Create table mocks](/docs/defining_table_mocks.md)
  * [Specifying default values](/docs/default_values.md)
  * [Specifying the query to test](/docs/your_sql_query_to_test.md)
  * [Result assertions](/docs/result_assertion.md)
* System specific usage
  * [Use with BigQuery](/docs/bigquery.md)
  * [Use with Clickhouse](/docs/clickhouse.md)
  * [Use with Redshift](/docs/redshift.md)
  * [Use with Snowflake](/docs/snowflake.md)
  * [Use with dbt](/docs/dbt.md)

You can find some examples in the [examples folder](https://github.com/DeepLcom/sql-mock/tree/main/examples).

### Installation

The library can be installed from [PyPI](https://pypi.org/project/sql-mock/) using pip:

```shell
# BigQuery
pip install --upgrade "sql-mock[bigquery]"

# Clickhouse
pip install --upgrade "sql-mock[clickhouse]"

# Redshift
pip install --upgrade "sql-mock[redshift]"

# Snowflake
pip install --upgrade "sql-mock[snowflake]"
```

If you need to modify this source code, install the dependencies using poetry:

```shell
poetry install --all-extras
```

#### Recommended Setup for Pytest

If you are using pytest, make sure to add a `conftest.py` file to the root of your project.
In the file add the following lines:

```python
import pytest
pytest.register_assert_rewrite('sql_mock')
```

This allows you to get a rich comparison when using the `.assert_equal` method on the table mock instances.

We also recommend using [pytest-icdiff](https://github.com/hjwp/pytest-icdiff) for better visibility on diffs of failed tests.

### Quickstart

Before diving into specific database scenarios, let's start with a simplified example of how SQL Mock works behind the scenes.

1. You have an original SQL query, for instance:

   ```sql
   -- path/to/query_for_result_table.sql
   SELECT id FROM data.table1
   ```

2. Using SQL Mock, you define table mocks. You can use the built-in column types provided by SQL Mock. Available column types include `Int`, `String`, `Date`, and more. Each database type has their own column types. Define your tables by subclassing a mock table class that fits your database (e.g. `BigQueryTableMock`) and specifying the column types along with default values. In our example we use the `ClickHouseTableMock` class

    ```python
    from sql_mock.clickhouse import column_mocks as col
    from sql_mock.clickhouse.table_mocks import ClickHouseTableMock
    from sql_mock.table_mocks import table_meta

    @table_meta(table_ref='data.table1')
    class Table(ClickHouseTableMock):
        id = col.Int(default=1)
        name = col.String(default='Peter')

    @table_meta(table_ref='data.result_table', query_path='path/to/query_for_result_table.sql')
    class ResultTable(ClickHouseTableMock):
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

4. **Getting results for a table mock:** Use the `from_mocks` method of the table mock object to generate mock query results based on your mock data.

    ```python
    res = ResultTable.from_mocks(input_data=[input_table_mock])
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

## Pydantic V1 vs. V2

SQL Mock's published version supports Pydantic V2. You might run into issues when your code depends on Pydantic V1.
We have an alternative branch you can install from that supports Pydantic V1 in the meanwhile: <https://github.com/DeepLcom/sql-mock/tree/pydantic-v1>

## Contributing

We welcome contributions to improve and enhance this open-source project. Whether you want to report issues, suggest new features, or directly contribute to the codebase, your input is valuable. To ensure a smooth and collaborative experience for both contributors and maintainers, please follow these guidelines:

### Reporting Issues

If you encounter a bug, have a feature request, or face any issues with the project, we encourage you to report them using the project's issue tracker. When creating an issue, please include the following information:

* A clear and descriptive title.
* A detailed description of the problem or suggestion.
* Steps to reproduce the issue (if applicable).
* Any error messages or screenshots that help clarify the problem.

### Feature Requests

If you have ideas for new features or improvements, please use the project's issue tracker to submit a feature request. We appreciate well-documented feature requests that explain the motivation and potential use cases.

### Contributing Code

Find more about contributing code in the [Contribution Guidelines](./CONTRIBUTION.md)

## Experimental

### SQL Mock Buddy - A custom (Chat) GPT to support you

We ran a small experiment to create a custom GPT for SQL Mock.
The SQL Mock Buddy can be accessed here: [https://chat.openai.com/g/g-FIXNcqu1l-sql-mock-buddy](https://chat.openai.com/g/g-FIXNcqu1l-sql-mock-buddy)

SQL Mock Buddy should help you to get started quickly with SQL Mock.

It is still in beta mode and you should definitely double-check its output!

## FAQ

### My database system is not supported yet but I want to use SQL Mock. What should I do?

We are planning to add more and more supported database systems. However, if your system is not supported yet, you can still use SQL Mock. There are only 2 things you need to do:

#### Create your `TableMock` class

First, you need to create a `TableMock` class for your database system that inherits from `sql_mock.table_mocks.BaseTableMock`.

That class needs to implement the `_get_results` method which should make sure to fetch the results of a query (e.g. produced by `self._generate_query()`) and return it as list of dictionaries.

Look at one of the existing client libraries to see how this could work (e.g. [BigQueryTableMock](https://github.com/DeepLcom/sql-mock/blob/main/src/sql_mock/bigquery/table_mocks.py)).

You might want to create a settings class as well in case you need some specific connection settings to be available within the `_get_results` method.

#### Create your `ColumnMocks`

Your database system might support specific database types. In order to make them available as column types, you can use the `sql_mock.column_mocks.BaseColumnMock` class as a base and inherit your specific column types from it.
For most of your column mocks you might only need to specify the `dtype` that should be used to parse the inputs.

A good practise is to create a `BaseColumnMock` class that is specific to your database and inherit all your column types from it, e.g.:

```python
from sql_mock.column_mocks import BaseColumnMock

class MyFancyDatabaseColumnMock(BaseColumnMock):
    # In case you need some specific logic that overwrites the default behavior, you can do so here
    pass

class Int(MyFancyDatabaseColumnMock):
    dtype = "Integer"

class String(MyFancyDatabaseColumnMock):
    dtype = "String"
```

#### Contribute your database setup

There will definitely be folks in the community that are in the need of support for the database you just created all the setup for.
Feel free to create a PR on this repository that we can start supporting your database system!

### I am missing a specific BaseColumnMock type for my model fields

We implemented some basic column types but it could happen that you don't find the one you need.
Luckily, you can easily create those with the tools provided.
The only thing you need to do is to inherit from the `BaseColumnMock` that is specific to your database system (e.g. `BigQueryColumnMock`) and write classes for the column mocks you are missing. Usually you only need to set the correct `dtype`. This would later be used in the `cast(col to <dtype>)` expression.

```python
# Replace the import with the database system you are using
from sql_mock.bigquery.column_mock import BigQueryColumnMock

class MyFancyMissingColType(BigQueryColumnMock):
    dtype = "FancyMissingColType"

    # In case you need to implement additional logic for casting, you can do so here
    ...
```

**Don't forget to create a PR in case you feel that your column mock type could be useful for the community**!
