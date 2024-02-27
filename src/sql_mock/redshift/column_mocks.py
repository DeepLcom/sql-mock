from sql_mock.column_mocks import BaseColumnMock


class RedshiftColumnMock(BaseColumnMock):
    pass


class SMALLINT(RedshiftColumnMock):
    dtype = "SMALLINT"


class INTEGER(RedshiftColumnMock):
    dtype = "INTEGER"


class BIGINT(RedshiftColumnMock):
    dtype = "BIGINT"


class DECIMAL(RedshiftColumnMock):
    def __init__(self, default, precision, scale, nullable=False) -> None:
        self.dtype = f"DECIMAL({precision}, {scale})"
        super().__init__(default, nullable)


class REAL(RedshiftColumnMock):
    dtype = "REAL"


class DOUBLE_PRECISION(RedshiftColumnMock):
    dtype = "DOUBLE PRECISION"


class BOOLEAN(RedshiftColumnMock):
    dtype = "BOOLEAN"


class CHAR(RedshiftColumnMock):
    dtype = "CHAR"


class VARCHAR(RedshiftColumnMock):
    dtype = "VARCHAR"


class DATE(RedshiftColumnMock):
    dtype = "DATE"


class TIMESTAMP(RedshiftColumnMock):
    dtype = "TIMESTAMP"


class TIMESTAMPTZ(RedshiftColumnMock):
    dtype = "TIMESTAMPTZ"


class GEOMETRY(RedshiftColumnMock):
    dtype = "GEOMETRY"


class GEOGRAPHY(RedshiftColumnMock):
    dtype = "GEOGRAPHY"


class HLLSKETCH(RedshiftColumnMock):
    dtype = "HLLSKETCH"


class SUPER(RedshiftColumnMock):
    dtype = "SUPER"


class TIME(RedshiftColumnMock):
    dtype = "TIME"


class TIMETZ(RedshiftColumnMock):
    dtype = "TIMETZ"


class VARBYTE(RedshiftColumnMock):
    dtype = "VARBYTE"
