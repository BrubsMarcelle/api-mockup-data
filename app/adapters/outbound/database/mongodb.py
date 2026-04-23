from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    def connect_db(cls):
        if settings.ENVIRONMENT == "prod":
            cls.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=20000
            )
        else:
            cls.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
        
        cls.db = cls.client[settings.DATABASE_NAME]

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.close()

def get_database():
    return MongoDB.db
