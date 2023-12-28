from sql_mock.column_mocks import ColumnMock


class RedshiftColumnMock(ColumnMock):
    pass


class ACLITEM(RedshiftColumnMock):
    dtype = "ACLITEM"


class BOOLEAN(RedshiftColumnMock):
    dtype = "BOOLEAN"


class INT8(RedshiftColumnMock):
    dtype = "INT8"


class INT4(RedshiftColumnMock):
    dtype = "INT4"


class INT2(RedshiftColumnMock):
    dtype = "INT2"


class VARCHAR(RedshiftColumnMock):
    dtype = "VARCHAR"


class OID(RedshiftColumnMock):
    dtype = "OID"


class REGPROC(RedshiftColumnMock):
    dtype = "REGPROC"


class XID(RedshiftColumnMock):
    dtype = "XID"


class FLOAT4(RedshiftColumnMock):
    dtype = "FLOAT4"


class FLOAT8(RedshiftColumnMock):
    dtype = "FLOAT8"


class TEXT(RedshiftColumnMock):
    dtype = "TEXT"


class CHAR(RedshiftColumnMock):
    dtype = "CHAR"


class DATE(RedshiftColumnMock):
    dtype = "DATE"


class TIME(RedshiftColumnMock):
    dtype = "TIME"


class TIMETZ(RedshiftColumnMock):
    dtype = "TIMETZ"


class TIMESTAMP(RedshiftColumnMock):
    dtype = "TIMESTAMP"


class TIMESTAMPTZ(RedshiftColumnMock):
    dtype = "TIMESTAMPTZ"


class NUMERIC(RedshiftColumnMock):
    def __init__(self, default, precision, scale, nullable=False):
        self.dtype = f"Decimal({precision}, {scale})"
        super().__init__(default, nullable)
