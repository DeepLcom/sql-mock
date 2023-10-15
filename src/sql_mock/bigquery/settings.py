from pydantic_settings import BaseSettings


class BigQuerySettings(BaseSettings):
    google_application_credentials: str
