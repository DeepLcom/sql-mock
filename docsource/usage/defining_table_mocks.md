```{toctree}
:maxdepth: 2
```

# Defining table mocks

When you want to provide mocked data to test your SQL model, you need to create MockTable classes for all upstream data that your model uses, as well as for the model you want to test. Those mock tables can be created by inheriting from a `BaseMockTable` class for the database provider you are using (e.g. `BigQueryMockTable`).

**We recommend to have a central `model.py` file where you create those models that you can easily reuse them across your tests**

```python
# models.py

from sql_mock.bigquery import column_mocks as col
from sql_mock.bigquery.table_mocks import BigQueryMockTable, table_meta

# The models you are goign to use as inputs need to have a `table_ref` specified
@table_meta(table_ref='data.table1')
class Table(BigQueryMockTable):
    id = col.Int(default=1)
    name = col.String(default='Peter')

@table_meta(
    table_ref='data.result_table', 
    query_path='path/to/query_for_result_table.sql', 
    default_inputs=[Table()] # You can provide default inputs on a class level
)
class ResultTable(BigQueryMockTable):
    id = col.Int(default=1)
```

Some important things to mention:

**The models you are goign to use as inputs need to have a `table_ref` specified.**
The `table_ref` is how the table will be referenced in your production database (usually some pattern like `<schema>.<table>`)

**The result model needs to have a query.** 
There are currently 2 ways to provide a query to the model: 

1. Pass a path to your query file in the class definition using the `table_meta` decorator. This allows us to only specify it once.   
    ```python
    @table_meta(table_ref='data.result_table', query_path='path/to/query_for_result_table.sql')
    class ResultTable(BigQueryMockTable):
        ...
    ```
2. Pass it as `query` argument to the `from_mocks` method when you are using the model in your test. This will also overwrite whatever query was read from the `query_path` in the `table_meta` decorator.
    ```python
    res = ResultTable.from_mocks(query='SELECT 1', input_data=[<your-input-mocks-table-instances>])
    ```

More details on how to handle queries can be found [in the "Your SQL query to test" section](./your_sql_query_to_test.md)
