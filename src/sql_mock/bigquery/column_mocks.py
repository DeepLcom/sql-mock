from typing import Any
from sql_mock.column_mocks import BaseColumnMock


class BigQueryColumnMock(BaseColumnMock):
    pass


class Boolean(BigQueryColumnMock):
    dtype = 'Boolean'


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


class Timestamp(BigQueryColumnMock):
    dtype = 'Timestamp'


class Array(BigQueryColumnMock):
    use_quotes_for_casting = False

    def __init__(
        self,
        inner_type: BigQueryColumnMock,
        default: Any,
        nullable: bool=False,
    ) -> None:
        self.dtype = f"Array<{inner_type.dtype}>"
        super().__init__(default, nullable)
