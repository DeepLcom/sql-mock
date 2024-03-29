# Defining table mocks

When you want to provide mocked data to test your SQL model, you need to create TableMock classes for all upstream data that your model uses, as well as for the model you want to test. Those table mocks can be created by inheriting from a `BaseTableMock` class for the database provider you are using (e.g. `BigQueryTableMock`).

**We recommend to have a central `model.py` file where you create those models that you can easily reuse them across your tests**

```python
# models.py

from sql_mock.bigquery import column_mocks as col
from sql_mock.bigquery.table_mocks import BigQueryTableMock, table_meta

# The models you are going to use as inputs need to have a `table_ref` specified
@table_meta(table_ref='data.table1')
class Table(BigQueryTableMock):
    id = col.Int(default=1)
    name = col.String(default='Peter')

@table_meta(
    table_ref='data.result_table',
    query_path='path/to/query_for_result_table.sql',
    default_inputs=[Table()] # You can provide default inputs on a class level
)
class ResultTable(BigQueryTableMock):
    id = col.Int(default=1)
```

Some important things to mention:

**The models you are going to use as inputs need to have a `table_ref` specified.**
The `table_ref` is how the table will be referenced in your production database (usually some pattern like `<schema>.<table>`).
In case you want to mock a CTE, you can use the `table_ref` to specify the name of the CTE.

**The result model needs to have a query.**
There are currently 3 ways to provide a query to the model:

1. Pass a path to your query file in the class definition using the `table_meta` decorator. This allows us to only specify it once.

    ```python
    @table_meta(table_ref='data.result_table', query_path='path/to/query_for_result_table.sql')
    class ResultTable(BigQueryTableMock):
        ...
    ```

2. Pass it as `query` argument to the `from_mocks` method when you are using the model in your test. This will also overwrite whatever query was read from the `query_path` in the `table_meta` decorator.

    ```python
    res = ResultTable.from_mocks(query='SELECT 1', input_data=[<your-input-mocks-table-instances>])
    ```

3. If you are using dbt there is a third option to use dbt-specific decorators. More details on that can be found [in the "Use with dbt" doc](./dbt.md)

More details on how to handle queries can be found [in the "Your SQL query to test" section](./your_sql_query_to_test.md)
