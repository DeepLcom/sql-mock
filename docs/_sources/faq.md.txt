
# FAQ

## My database system is not supported yet but I want to use SQL Mock. What should I do?

We are planning to add more and more supported database systems. However, if your system is not supported yet, you can still use SQL Mock. There are only 2 things you need to do:

### Create your `MockTable` class

First, you need to create a `MockTable` class for your database system that inherits from `sql_mock.table_mocks.BaseMockTable`.

That class needs to implement the `_get_results` method which should make sure to fetch the results of a query (e.g. produced by `self._generate_query()`) and return it as list of dictionaries.

Look at one of the existing client libraries to see how this could work (e.g. [BigQueryMockTable](https://github.com/DeepLcom/sql-mock/blob/main/src/sql_mock/bigquery/table_mocks.py)).

You might want to create a settings class as well in case you need some specific connection settings to be available within the `_get_results` method.

### Create your `ColumnMocks`

Your database system might support specific database types. In order to make them available as column types, you can use the `sql_mock.column_mocks.ColumnMock` class as a base and inherit your specific column types from it.
For most of your column mocks you might only need to specify the `dtype` that should be used to parse the inputs.

A good practise is to create a `ColumnMock` class that is specific to your database and inherit all your column types from it, e.g.:

```python
from sql_mock.column_mocks import ColumnMock

class MyFanceDatabaseColumnMock(ColumnMock):
    # In case you need some specific logic that overwrites the default behavior, you can do so here
    pass

class Int(MyFanceDatabaseColumnMock):
    dtype = "Integer"

class String(MyFanceDatabaseColumnMock):
    dtype = "String"
```

### Contribute your database setup

There will definitely be folks in the community that are in the need of support for the database you just created all the setup for.
Feel free to create a PR on this repository that we can start supporting your database system!


## I am missing a specific ColumnMock type for my model fields

We implemented some basic column types but it could happen that you don't find the one you need.
Luckily, you can easily create those with the tools provided.
The only thing you need to do is to inherit from the `ColumnMock` that is specific to your database system (e.g. `BigQueryColumnMock`) and write classes for the column mocks you are missing. Usually you only need to set the correct `dtype`. This would later be used in the `cast(col to <dtype>)` expression.

```python
# Replace the import with the database system you are using
from sql_mock.bigquery.column_mock import BigQueryColumnMock

class MyFancyMissingColType(BigQueryColumnMock):
    dtype = "FancyMissingColType"

    # In case you need to implement additional logic for casting, you can do so here
    ...
```

**Don't forget to create a PR in case you feel that your column mock type could be useful for the community**!
