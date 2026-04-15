import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "provisory_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "api_mock_db")
    PORT: int = int(os.getenv("PORT", 8000))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"

settings = Settings()
