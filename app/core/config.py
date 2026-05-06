from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "local"  
    SECRET_KEY: str
    MONGO_URI: Optional[str] = None  # Opcional: só necessário quando DATABASE_TYPE=mongodb
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_NAME: str = "api_mock_db"
    DATABASE_TYPE: str = "mongodb"  # mongodb ou firestore
    FIREBASE_PROJECT_ID: Optional[str] = None
    PORT: int = 8080
    RELOAD: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
