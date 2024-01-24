from pydantic_settings import BaseSettings, SettingsConfigDict


class ClickHouseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SQL_MOCK_CLICKHOUSE_")
    host: str
    user: str
    password: str
    port: str
    use_secure_connection: bool = False
