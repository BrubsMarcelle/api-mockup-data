from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.core.domain.models.api_mock import APIConfig, APIMock
from app.core.domain.ports.repository import ApiRepositoryInterface

class MongoApiRepository(ApiRepositoryInterface):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.configs_collection = self.db["api_configs"]
        self.mocks_collection = self.db["api_mocks"]

    async def create_api_config(self, config: APIConfig) -> str:
        data = config.model_dump(by_alias=True, exclude={"id"})
        result = await self.configs_collection.insert_one(data)
        return str(result.inserted_id)

    async def get_api_config_by_endpoint(self, endpoint: str, method: str) -> Optional[APIConfig]:
        # Normalizing endpoint for matching
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
            
        data = await self.configs_collection.find_one({
            "endpoint": endpoint,
            "method": method.upper()
        })
        if data:
            data["_id"] = str(data["_id"])
            return APIConfig(**data)
        return None

    async def create_mock(self, mock: APIMock) -> str:
        data = mock.model_dump(by_alias=True, exclude={"id"})
        result = await self.mocks_collection.insert_one(data)
        return str(result.inserted_id)

    async def find_mock_by_identity(self, endpoint: str, method: str, identity_value: str) -> Optional[APIMock]:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        data = await self.mocks_collection.find_one({
            "endpoint": endpoint,
            "identity_value": identity_value
        })
        if data:
            data["_id"] = str(data["_id"])
            return APIMock(**data)
        return None

    async def search_all(self) -> List[Dict[str, Any]]:
        results = []
        # Get configs
        async for config in self.configs_collection.find():
            config["_id"] = str(config["_id"])
            config["source_type"] = "standard"
            results.append(config)
        
        # Get mocks
        async for mock in self.mocks_collection.find():
            mock["_id"] = str(mock["_id"])
            mock["source_type"] = "mock"
            results.append(mock)
            
        return results
