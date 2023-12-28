from pydantic import BaseSettings


class ClickHouseSettings(BaseSettings):
    host: str
    user: str
    password: str
    port: str

    class Config:
        env_prefix = "SQL_MOCK_CLICKHOUSE_"
