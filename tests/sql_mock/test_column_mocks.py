import pytest
from sql_mock.column_mocks import ColumnMock

def test_init_no_default_not_nullable():
    """
    ...then it should raise an error.
    """
    with pytest.raises(ValueError, match="Default cannot be None if column is not nullable"):
        ColumnMock(default=None, nullable=False)

def test_init_default_not_nullable():
    """
    ...then it should set the default value and nullable should be False.
    """
    column = ColumnMock(default=42)
    assert column.default == 42
    assert not column.nullable

def test_init_default_nullable():
    """
    ...then it should set the default value and nullable should be True.
    """
    column = ColumnMock(default="Hello", nullable=True)
    assert column.default == "Hello"
    assert column.nullable

def test_to_sql_with_value():
    """
    ...then it should return the SQL cast expression using the provided value.
    """
    column = ColumnMock(default=3.14)
    sql = column.to_sql("price", value=42)
    assert sql == "cast('42' AS None) AS price"

def test_to_sql_without_value():
    """
    ...then it should return the SQL cast expression using the default value.
    """
    class ColumnTestMock(ColumnMock):
        dtype = 'String'

    column = ColumnTestMock(default="OpenAI")
    sql = column.to_sql("company")
    assert sql == "cast('OpenAI' AS String) AS company"

def test_to_sql_without_value_and_no_default():
    """
    ...then it should return the SQL cast expression using the default value.
    """
    class ColumnTestMock(ColumnMock):
        dtype = 'String'

    column = ColumnTestMock(default=None, nullable=True)
    sql = column.to_sql("company")
    assert sql == "cast(NULL AS String) AS company"
