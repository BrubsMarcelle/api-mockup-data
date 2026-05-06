from typing import List, Optional, Dict, Any
from google.cloud.firestore import AsyncClient
from app.core.domain.models.api_mock import Template, MockGerado, User
from app.core.domain.ports.repository import ApiRepositoryInterface
import datetime

class FirestoreApiRepository(ApiRepositoryInterface):
    def __init__(self, db: AsyncClient):
        self.db = db
        self.templates_collection = "mock_templates"
        self.mocks_collection = "mock_instances"
        self.users_collection = "users"

    async def create_user(self, user: User) -> str:
        data = user.model_dump(by_alias=True, exclude={"id"})
        doc_ref = self.db.collection(self.users_collection).document()
        await doc_ref.set(data)
        return doc_ref.id

    async def get_user_by_username(self, username: str) -> Optional[User]:
        docs = self.db.collection(self.users_collection).where("username", "==", username).limit(1).stream()
        async for doc in docs:
            data = doc.to_dict()
            data["_id"] = doc.id
            return User(**data)
        return None

    async def update_user_password(self, username: str, new_hashed_password: str) -> bool:
        docs = self.db.collection(self.users_collection).where("username", "==", username).limit(1).stream()
        async for doc in docs:
            await doc.reference.update({"hashed_password": new_hashed_password})
            return True
        return False

    async def create_template(self, template: Template) -> str:
        data = template.model_dump(by_alias=True, exclude={"id"})
        doc_ref = self.db.collection(self.templates_collection).document()
        await doc_ref.set(data)
        return doc_ref.id

    async def get_template_by_endpoint(self, endpoint: str, method: str) -> Optional[Template]:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
            
        docs = self.db.collection(self.templates_collection)\
            .where("endpoint", "==", endpoint)\
            .where("method", "==", method.upper())\
            .limit(1).stream()
            
        async for doc in docs:
            data = doc.to_dict()
            data["_id"] = doc.id
            return Template(**data)
        return None

    async def create_mock_gerado(self, mock: MockGerado) -> str:
        data = mock.model_dump(by_alias=True, exclude={"id"})
        doc_ref = self.db.collection(self.mocks_collection).document()
        await doc_ref.set(data)
        return doc_ref.id

    async def find_mock_by_identity(self, endpoint: str, method: str, identity_value: str) -> Optional[MockGerado]:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
            
        method = method.upper()

        docs = self.db.collection(self.mocks_collection)\
            .where("url_acesso", "==", endpoint)\
            .where("method", "==", method)\
            .where("identity_value", "==", identity_value)\
            .limit(1).stream()
            
        async for doc in docs:
            data = doc.to_dict()
            data["_id"] = doc.id
            return MockGerado(**data)
        return None

    async def search_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Firestore has limitations with multiple range filters and regex
        # For simplicity, we'll implement basic filtering and potentially refine
        
        templates_query = self.db.collection(self.templates_collection)
        mocks_query = self.db.collection(self.mocks_collection)
        
        if filters:
            if filters.get("url_base"):
                # Firestore doesn't support regex natively in the same way Mongo does
                # We'll do simple equality or handle it in memory if needed
                pass 
            if filters.get("endpoint"):
                templates_query = templates_query.where("endpoint", "==", filters["endpoint"])
                mocks_query = mocks_query.where("url_acesso", "==", filters["endpoint"])
            if filters.get("identity_field"):
                templates_query = templates_query.where("identity_field", "==", filters["identity_field"])
            if filters.get("tag_squad"):
                templates_query = templates_query.where("tag_squad", "==", filters["tag_squad"])
            if filters.get("identity_value"):
                mocks_query = mocks_query.where("identity_value", "==", filters["identity_value"])

        results = []
        
        # Get templates
        docs = templates_query.stream()
        async for doc in docs:
            data = doc.to_dict()
            data["_id"] = doc.id
            data["source_type"] = "template"
            results.append(data)
            
        # Get mocks
        docs = mocks_query.stream()
        async for doc in docs:
            data = doc.to_dict()
            data["_id"] = doc.id
            data["source_type"] = "mock_gerado"
            results.append(data)
            
        return results
