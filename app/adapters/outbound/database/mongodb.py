from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    def connect_db(cls):
        cls.client = AsyncIOMotorClient(settings.MONGO_URI)
        cls.db = cls.client[settings.DATABASE_NAME]

    @classmethod
    def close_db(cls):
        cls.client.close()

def get_database():
    return MongoDB.db
