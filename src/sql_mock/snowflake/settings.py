from pydantic_settings import BaseSettings, SettingsConfigDict


class SnowflakeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SQL_MOCK_SNOWFLAKE_")
    account: str
    user: str
    password: str
