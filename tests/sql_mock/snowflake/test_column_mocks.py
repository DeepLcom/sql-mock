from sql_mock.snowflake.column_mocks import DECIMAL, SnowflakeColumnMock


def test_init_not_nullable():
    """
    ...then nullable should be False and dtype be the same as passed.
    """

    class ColMock(SnowflakeColumnMock):
        dtype = "INTEGER"

    column = ColMock(default=42)

    assert column.default == 42
    assert column.dtype == "INTEGER"
    assert not column.nullable


def test_init_nullable():
    """
    ...then nullable should be True"
    """

    class ColMock(SnowflakeColumnMock):
        dtype = "INTEGER"

    column = ColMock(default=42, nullable=True)

    assert column.default == 42
    assert column.dtype == "INTEGER"
    assert column.nullable


class TestDecimalColumn:
    def test_decimal_initialization_not_nullable(self):
        """Ensure that the Decimal object is initialized correctly."""
        decimal_col = DECIMAL(default=0.0, precision=10, scale=2, nullable=False)
        assert decimal_col.dtype == "DECIMAL(10, 2)"
        assert decimal_col.default == 0.0
        assert not decimal_col.nullable

    def test_decimal_initialization_nullable(self):
        """Ensure that the Decimal object is initialized correctly."""
        decimal_col = DECIMAL(default=None, precision=10, scale=2, nullable=True)
        assert decimal_col.dtype == "DECIMAL(10, 2)"
        assert decimal_col.default is None
        assert decimal_col.nullable
