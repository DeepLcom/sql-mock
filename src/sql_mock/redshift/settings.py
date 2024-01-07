from pydantic_settings import BaseSettings, SettingsConfigDict


class RedshiftSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SQL_MOCK_REDSHIFT_")
    host: str
    database: str
    user: str
    password: str = None
    port: int = 5439
