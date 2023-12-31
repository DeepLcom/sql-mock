from sql_mock.column_mocks import ColumnMock


class BigQueryColumnMock(ColumnMock):
    pass


class Int(BigQueryColumnMock):
    dtype = "Integer"


class Date(BigQueryColumnMock):
    dtype = "Date"


class String(BigQueryColumnMock):
    dtype = "String"


class Float(BigQueryColumnMock):
    dtype = "Float"


class Decimal(BigQueryColumnMock):
    def __init__(self, default, precision, scale, nullable=False) -> None:
        self.dtype = f"Decimal({precision}, {scale})"
        super().__init__(default, nullable)


class Array(BigQueryColumnMock):
    use_quotes_for_casting = False

    def __init__(
        self,
        inner_dtype,
        default,
        nullable=False,
    ) -> None:
        self.dtype = f"Array<{inner_dtype}>"
        super().__init__(default, nullable)
