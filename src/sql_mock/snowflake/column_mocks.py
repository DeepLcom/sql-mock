from sql_mock.column_mocks import BaseColumnMock


class SnowflakeColumnMock(BaseColumnMock):
    pass


class INTEGER(SnowflakeColumnMock):
    dtype = "INTEGER"


class FLOAT(SnowflakeColumnMock):
    dtype = "FLOAT"


class BOOLEAN(SnowflakeColumnMock):
    dtype = "BOOLEAN"


class STRING(SnowflakeColumnMock):
    dtype = "STRING"


class TEXT(SnowflakeColumnMock):
    dtype = "TEXT"


class BINARY(SnowflakeColumnMock):
    dtype = "BINARY"


class DATE(SnowflakeColumnMock):
    dtype = "DATE"


class TIME(SnowflakeColumnMock):
    dtype = "TIME"


class TIMESTAMP(SnowflakeColumnMock):
    dtype = "TIMESTAMP"


class TIMESTAMP_LTZ(SnowflakeColumnMock):
    dtype = "TIMESTAMP_LTZ"


class TIMESTAMP_NTZ(SnowflakeColumnMock):
    dtype = "TIMESTAMP_NTZ"


class TIMESTAMP_TZ(SnowflakeColumnMock):
    dtype = "TIMESTAMP_TZ"


class VARIANT(SnowflakeColumnMock):
    dtype = "VARIANT"


class OBJECT(SnowflakeColumnMock):
    dtype = "OBJECT"


class ARRAY(SnowflakeColumnMock):
    dtype = "ARRAY"
    use_quotes_for_casting = False


class GEOGRAPHY(SnowflakeColumnMock):
    dtype = "GEOGRAPHY"


class DECIMAL(SnowflakeColumnMock):
    def __init__(self, default, precision, scale, nullable=False) -> None:
        self.dtype = f"DECIMAL({precision}, {scale})"
        super().__init__(default, nullable)
