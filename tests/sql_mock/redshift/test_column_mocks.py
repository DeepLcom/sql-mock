from sql_mock.redshift.column_mocks import DECIMAL, RedshiftColumnMock


def test_init_nullable():
    """
    ...then nullable should be True and dtype be the same as passed.
    """

    class ColMock(RedshiftColumnMock):
        dtype = "BIGINT"

    column = ColMock(default=42)

    assert column.default == 42
    assert column.dtype == "BIGINT"
    assert column.nullable


def test_init_not_nullable():
    """
    ...then nullable should be False"
    """

    class ColMock(RedshiftColumnMock):
        dtype = "BIGINT"

    column = ColMock(default=42, nullable=False)

    assert column.default == 42
    assert column.dtype == "BIGINT"
    assert not column.nullable


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
