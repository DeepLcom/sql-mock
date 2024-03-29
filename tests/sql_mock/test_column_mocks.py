import pytest

from sql_mock.column_mocks import BaseColumnMock


def test_init_no_default_not_nullable():
    """
    ...then it should raise an error.
    """
    with pytest.raises(ValueError, match="Default cannot be None if column is not nullable"):
        BaseColumnMock(default=None, nullable=False)


def test_init_default_nullable():
    """
    ...then it should set the default value and nullable should be True.
    """
    column = BaseColumnMock(default=42)
    assert column.default == 42
    assert column.nullable


def test_init_default_not_nullable():
    """
    ...then it should set the default value and nullable should be False.
    """
    column = BaseColumnMock(default="Hello", nullable=False)
    assert column.default == "Hello"
    assert not column.nullable


def test_to_sql_with_value():
    """
    ...then it should return the SQL cast expression using the provided value.
    """
    column = BaseColumnMock(default=3.14)
    sql = column.to_sql("price", value=42)
    assert sql == "cast('42' AS None) AS price"


def test_to_sql_without_value():
    """
    ...then it should return the SQL cast expression using the default value.
    """

    class ColumnTestMock(BaseColumnMock):
        dtype = "String"

    column = ColumnTestMock(default="OpenAI")
    sql = column.to_sql("company")
    assert sql == "cast('OpenAI' AS String) AS company"


def test_to_sql_with_none_for_nullable_column():
    """
    ...then it should return the SQL cast expression using the default value.
    """

    class ColumnTestMock(BaseColumnMock):
        dtype = "String"

    column = ColumnTestMock(default="OpenAI", nullable=True)
    sql = column.to_sql("company", value=None)
    assert sql == "cast(NULL AS String) AS company"


def test_to_sql_without_value_and_no_default():
    """
    ...then it should return the SQL cast expression using the default value.
    """

    class ColumnTestMock(BaseColumnMock):
        dtype = "String"

    column = ColumnTestMock(default=None, nullable=True)
    sql = column.to_sql("company")
    assert sql == "cast(NULL AS String) AS company"


def test_to_sql_not_use_quotes_for_casting():
    """
    ...then it should not quote the value in the cast expression.
    """

    class ColumnTestMock(BaseColumnMock):
        dtype = "Integer"
        use_quotes_for_casting = False

    column = ColumnTestMock(default=3.14)
    sql = column.to_sql("price", value=42)
    assert sql == "cast(42 AS Integer) AS price"
