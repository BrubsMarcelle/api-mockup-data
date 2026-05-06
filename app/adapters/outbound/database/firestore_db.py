from google.cloud import firestore
from app.core.config import settings

class FirestoreDB:
    client: firestore.AsyncClient = None

    @classmethod
    def connect_db(cls):
        if settings.FIREBASE_PROJECT_ID:
            cls.client = firestore.AsyncClient(project=settings.FIREBASE_PROJECT_ID)
        else:
            # Tenta usar as credenciais padrão do ambiente (GCP/Firebase)
            cls.client = firestore.AsyncClient()

    @classmethod
    async def close_db(cls):
        if cls.client:
            await cls.client.close()

def get_firestore_client():
    return FirestoreDB.client
