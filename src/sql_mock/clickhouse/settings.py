from pydantic import BaseSettings


class ClickHouseSettings(BaseSettings):
    host: str
    user: str
    password: str
    port: str
    use_secure_connection: bool = False

    class Config:
        env_prefix = "SQL_MOCK_CLICKHOUSE_"
