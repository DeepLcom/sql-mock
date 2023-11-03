# Your SQL query to test

There are multiple ways on how you can provide the SQL query that you want to test. Let's walk through them and also cover some specifics.

## Ways to provide your SQL query to be tested

### Option 1 (recommended): Use the `table_meta` decorator

When defining your [Table Mock classes](./defining_table_mocks.md), you can pass a path to your query (`query_path` argument) or the query as string (`query` argument) to the `table_meta` decorator of the table mock you want to test.

```python
# Pass the query path
@table_meta(table_ref='data.result_table', query_path='path/to/query_for_result_table.sql')
class ResultTable(BigQueryTableMock):
    id = col.Int(default=1)

# Pass the query itself
query = 'SELECT user_id AS id FROM data.users'
@table_meta(table_ref='data.result_table', query=query)
class ResultTable(BigQueryTableMock):
    id = col.Int(default=1)
```

The advantage of that option is that you only need to define your Table Mock class once (e.g. in a `models.py` file). After that you can reuse it for many tests.

### Option 2: Pass the query in the `.from_mocks` call

You can also pass your query in your test case when you call the `from_mocks` method.

```python 
res = ResultTable.from_mocks(query='SELECT 1', input_data=[<your-input-mocks-table-instances>])
```

Note that this will overwride whatever was specified by using the `table_meta` decorator.

## Queries with Jinja templates

Sometimes we need to test queries that use jinja templates (e.g. for dbt).
In those cases, you can provide the necessary context for rendering your query using the `from_mocks` call.

**Example**:

Let's assume the following jinja template query:

```jinja
SELECT * FROM data.users 
WHERE created_at > {{ creation_date }}
```

We can provide the `creation_date` variable in a dictionary using the `query_template_kwargs` argument:

```python
res = ResultTable.from_mocks(input_data=[your_input_mock_instances], query_template_kwargs={'creation_date': '2023-09-05'})
```

This will automatically render your query using the given input.
