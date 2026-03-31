import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mock_db")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    def connect_db(cls):
        cls.client = AsyncIOMotorClient(MONGO_URI)
        cls.db = cls.client[DATABASE_NAME]

    @classmethod
    def close_db(cls):
        cls.client.close()

def get_database():
    return MongoDB.db
