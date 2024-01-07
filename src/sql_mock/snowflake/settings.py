from pydantic import BaseSettings


class SnowflakeSettings(BaseSettings):
    account: str
    user: str
    password: str

    class Config:
        env_prefix = "SQL_MOCK_SNOWFLAKE_"
