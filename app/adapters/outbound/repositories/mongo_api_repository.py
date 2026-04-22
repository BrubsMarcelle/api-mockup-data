from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.core.domain.models.api_mock import Template, MockGerado, User
from app.core.domain.ports.repository import ApiRepositoryInterface

class MongoApiRepository(ApiRepositoryInterface):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.templates_collection = self.db["mock_templates"]
        self.mocks_collection = self.db["mock_instances"]
        self.users_collection = self.db["users"]

    async def create_user(self, user: User) -> str:
        data = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.users_collection.insert_one(data)
        return str(result.inserted_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        data = await self.users_collection.find_one({"username": username})
        if data:
            data["_id"] = str(data["_id"])
            return User(**data)
        return None

    async def update_user_password(self, username: str, new_hashed_password: str) -> bool:
        result = await self.users_collection.update_one(
            {"username": username},
            {"$set": {"hashed_password": new_hashed_password}}
        )
        return result.modified_count > 0

    async def create_template(self, template: Template) -> str:
        data = template.model_dump(by_alias=True, exclude={"id"})
        result = await self.templates_collection.insert_one(data)
        return str(result.inserted_id)

    async def get_template_by_endpoint(self, endpoint: str, method: str) -> Optional[Template]:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
            
        data = await self.templates_collection.find_one({
            "endpoint": endpoint,
            "method": method.upper()
        })
        if data:
            data["_id"] = str(data["_id"])
            return Template(**data)
        return None

    async def create_mock_gerado(self, mock: MockGerado) -> str:
        data = mock.model_dump(by_alias=True, exclude={"id"})
        result = await self.mocks_collection.insert_one(data)
        return str(result.inserted_id)

    async def find_mock_by_identity(self, endpoint: str, method: str, identity_value: str) -> Optional[MockGerado]:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
            
        method = method.upper()

        data = await self.mocks_collection.find_one({
            "url_acesso": endpoint,
            "method": method,
            "identity_value": identity_value
        })
        if data:
            data["_id"] = str(data["_id"])
            return MockGerado(**data)
        return None

    async def search_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query_templates = {}
        query_mocks = {}
        
        if filters:
            if filters.get("url_base"):
                query_templates["url_base"] = {"$regex": filters["url_base"], "$options": "i"}
            if filters.get("endpoint"):
                query_templates["endpoint"] = {"$regex": filters["endpoint"], "$options": "i"}
                query_mocks["url_acesso"] = {"$regex": filters["endpoint"], "$options": "i"}
            if filters.get("identity_field"):
                query_templates["identity_field"] = filters["identity_field"]
            if filters.get("tag_squad"):
                query_templates["tag_squad"] = filters["tag_squad"]
            
            if filters.get("identity_value"):
                query_mocks["identity_value"] = filters["identity_value"]

        results = []
        async for template in self.templates_collection.find(query_templates):
            template["_id"] = str(template["_id"])
            template["source_type"] = "template"
            results.append(template)
        
        if not filters or query_mocks:
            async for mock in self.mocks_collection.find(query_mocks):
                mock["_id"] = str(mock["_id"])
                mock["source_type"] = "mock_gerado"
                results.append(mock)
            
        return results
