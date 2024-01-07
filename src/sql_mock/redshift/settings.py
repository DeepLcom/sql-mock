from pydantic import BaseSettings


class RedshiftSettings(BaseSettings):
    host: str
    database: str
    user: str
    password: str = None
    port: int = 5439

    class Config:
        env_prefix = "SQL_MOCK_REDSHIFT_"
