from pydantic_settings import BaseSettings, SettingsConfigDict

class BigQuerySettings(BaseSettings):    
    google_application_credentials: str 
