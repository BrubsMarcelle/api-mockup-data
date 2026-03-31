import copy
from typing import Any, Dict, List, Optional
from app.core.domain.models.api_mock import APIConfig, APIMock
from app.core.domain.ports.repository import ApiRepositoryInterface

class MockService:
    def __init__(self, repository: ApiRepositoryInterface):
        self.repository = repository

    async def register_api(self, config_data: Dict[str, Any]) -> str:
        config = APIConfig(**config_data)
        return await self.repository.create_api_config(config)

    async def generate_mock(self, endpoint: str, method: str, modified_fields: Dict[str, Any], identity_value: str = None) -> APIMock:
        config = await self.repository.get_api_config_by_endpoint(endpoint, method)
        if not config:
            raise ValueError(f"API config not found for endpoint {endpoint} and method {method}")

        # Ensure modified fields are in floating_fields
        for field in modified_fields.keys():
            if field not in config.floating_fields:
                raise ValueError(f"Field '{field}' is not a floating field for this API.")

        # Construct final_response
        final_response = copy.deepcopy(config.standard_response)
        self._update_nested_dict(final_response, modified_fields)

        mock = APIMock(
            api_config_id=str(config.id),
            endpoint=endpoint,
            modified_fields=modified_fields,
            final_response=final_response,
            response_tag="mock",
            identity_value=identity_value
        )
        _id = await self.repository.create_mock(mock)
        mock.id = _id
        return mock

    async def simulate_endpoint(self, endpoint: str, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Matches a request to a mock or returns standard response."""
        # Try to find a mock by identity value.
        # Simple implementation: check if any value in input_data matches any saved mock identity_value.
        # In a real-case, we'd know which key is the identity (e.g. CPF).
        
        # Search for a mock for this endpoint.
        # If identity_value is provided, try that first.
        # Let's extract values from input_data.
        identity_values = [str(v) for v in input_data.values()]
        
        for val in identity_values:
            mock = await self.repository.find_mock_by_identity(endpoint, method, val)
            if mock:
                return mock.final_response

        # Default to standard response if no mock hit
        config = await self.repository.get_api_config_by_endpoint(endpoint, method)
        if config:
            return config.standard_response
        
        return {"error": "Endpoint mock not found"}

    async def search(self) -> List[Dict[str, Any]]:
        return await self.repository.search_all()

    def _update_nested_dict(self, data: Dict[str, Any], updates: Dict[str, Any]):
        """Helper to update dictionary fields (shallow update for now as field names are IDs)."""
        for k, v in updates.items():
            if k in data:
                data[k] = v
            # Add simple recursion support?
            # Or assume floating_fields are top-level keys for simplicity as per requirement.
            # If standard_response is deep, this might need optimization.
            # Let's do simple for now.
