```{toctree}
:maxdepth: 2
```

# Installation

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


## Recommended Setup for Pytest
If you are using pytest, make sure to add a `conftest.py` file to the root of your project.
In the file add the following lines:
```python
import pytest
pytest.register_assert_rewrite('sql_mock')
```
This allows you to get a rich comparison when using the `.assert_equal` method on the table mock instances.

We also recommend using [pytest-icdiff](https://github.com/hjwp/pytest-icdiff) for better visibility on diffs of failed tests.
