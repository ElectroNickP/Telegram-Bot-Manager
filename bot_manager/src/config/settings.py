from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Telegram Bot Manager"
    DEBUG: bool = False
    SECRET_KEY: str = "changeme_in_production"
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "bot_manager"
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Encryption
    ENCRYPTION_KEY: str  # Fernet key (must be 32 url-safe base64-encoded bytes)

    class Config:
        env_file = ".env"

settings = Settings()
