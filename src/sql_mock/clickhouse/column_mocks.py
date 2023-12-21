from sql_mock.column_mocks import ColumnMock


class ClickhouseColumnMock(ColumnMock):
    def __init__(self, default, nullable=False) -> None:
        super().__init__(default, nullable)
        if nullable:
            self.dtype = f"Nullable({self.dtype})"


class Int(ClickhouseColumnMock):
    dtype = "Integer"


class Date(ClickhouseColumnMock):
    dtype = "Date"


class Datetime(ClickhouseColumnMock):
    dtype = "Datetime"


class Datetime64(ClickhouseColumnMock):
    dtype = "Datetime64"


class String(ClickhouseColumnMock):
    dtype = "String"


class Float(ClickhouseColumnMock):
    dtype = "Float"


class Boolean(ClickhouseColumnMock):
    dtype = "Boolean"


class Decimal(ClickhouseColumnMock):
    def __init__(self, default, precision, scale, nullable=False) -> None:
        self.dtype = f"Decimal({precision}, {scale})"
        super().__init__(default, nullable)


class Array(ClickhouseColumnMock):
    use_quotes_for_casting = False

    def __init__(
        self,
        inner_dtype,
        default,
        nullable=False,
    ) -> None:
        self.dtype = f"Array({inner_dtype})"
        super().__init__(default, nullable)
