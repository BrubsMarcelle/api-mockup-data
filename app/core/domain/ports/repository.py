from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.core.domain.models.api_mock import Template, MockGerado

class ApiRepositoryInterface(ABC):
    @abstractmethod
    async def create_template(self, template: Template) -> str:
        """Register a new API template."""
        pass

    @abstractmethod
    async def get_template_by_endpoint(self, endpoint: str, method: str) -> Optional[Template]:
        """Fetch an API template by endpoint and method."""
        pass

    @abstractmethod
    async def create_mock_gerado(self, mock: MockGerado) -> str:
        """Save a new generated mock."""
        pass

    @abstractmethod
    async def find_mock_by_identity(self, endpoint: str, method: str, identity_value: str) -> Optional[MockGerado]:
        """Find a mock based on an identifying value (e.g., CPF)."""
        pass

    @abstractmethod
    async def search_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search all API templates based on filters."""
        pass
