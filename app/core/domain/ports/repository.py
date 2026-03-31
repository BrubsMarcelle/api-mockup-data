from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.core.domain.models.api_mock import APIConfig, APIMock

class ApiRepositoryInterface(ABC):
    @abstractmethod
    async def create_api_config(self, config: APIConfig) -> str:
        """Register a new API configuration."""
        pass

    @abstractmethod
    async def get_api_config_by_endpoint(self, endpoint: str, method: str) -> Optional[APIConfig]:
        """Fetch an API configuration by endpoint and method."""
        pass

    @abstractmethod
    async def create_mock(self, mock: APIMock) -> str:
        """Save a new generated mock."""
        pass

    @abstractmethod
    async def find_mock_by_identity(self, endpoint: str, method: str, identity_value: str) -> Optional[APIMock]:
        """Find a mock based on an identifying value (e.g., CPF)."""
        pass

    @abstractmethod
    async def search_all(self) -> List[Dict[str, Any]]:
        """Search all API configs and mocks."""
        pass
