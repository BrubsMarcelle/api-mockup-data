from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.core.domain.models.api_mock import Template, MockGerado

class ApiRepositoryInterface(ABC):
    @abstractmethod
    async def create_template(self, template: Template) -> str:
        """Registrar um novo template de API."""
        pass

    @abstractmethod
    async def get_template_by_endpoint(self, endpoint: str, method: str) -> Optional[Template]:
        """Buscar um template de API por endpoint e método."""
        pass

    @abstractmethod
    async def create_mock_gerado(self, mock: MockGerado) -> str:
        """Salvar um novo mock gerado."""
        pass

    @abstractmethod
    async def find_mock_by_identity(self, endpoint: str, method: str, identity_value: str) -> Optional[MockGerado]:
        """Buscar um mock baseado em um valor de identidade (ex: CPF)."""
        pass

    @abstractmethod
    async def search_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pesquisar todos os templates de API baseados em filtros."""
        pass
