from app.core.config import settings
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.outbound.database.firestore_db import FirestoreDB
from app.adapters.outbound.repositories.mongo_api_repository import MongoApiRepository
from app.adapters.outbound.repositories.firestore_api_repository import FirestoreApiRepository

def get_repository():
    if settings.DATABASE_TYPE == "mongodb":
        return MongoApiRepository(MongoDB.db)
    else:
        return FirestoreApiRepository(FirestoreDB.client)
