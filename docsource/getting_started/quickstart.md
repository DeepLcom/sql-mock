```{toctree}
:maxdepth: 2
```

# Quickstart

Before diving into specific database scenarios, let's start with a simplified example of how SQL Mock works behind the scenes.


1. You have an original SQL query, for instance:
   ```sql
   -- path/to/query_for_result_table.sql
   SELECT id FROM data.table1
   ```


2. Using SQL Mock, you define mock tables. You can use the built-in column types provided by SQL Mock. Available column types include `Int`, `String`, `Date`, and more. Each database type has their own column types. Define your tables by subclassing a mock table class that fits your database (e.g. `BigQueryMockTable`) and specifying the column types along with default values. In our example we use the `ClickHouseTableMock` class
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
