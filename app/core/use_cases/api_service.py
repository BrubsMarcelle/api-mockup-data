import copy
from typing import Any, Dict, List, Optional
from app.core.domain.models.api_mock import Template, MockGerado
from app.core.domain.ports.repository import ApiRepositoryInterface
from app.core.utils.generators import generate_cpf, generate_cod_associado

class MockService:
    def __init__(self, repository: ApiRepositoryInterface):
        self.repository = repository

    async def register_template(self, template_data: Dict[str, Any]) -> str:
        template = Template(**template_data)
        return await self.repository.create_template(template)

    async def generate_mock(self, endpoint: str, method: str, modified_fields: Dict[str, Any], identity_value: str = None) -> MockGerado:
        template = await self.repository.get_template_by_endpoint(endpoint, method)
        if not template:
            raise ValueError(f"Template not found for endpoint {endpoint} and method {method}")

        # Ensure modified fields are in campos_editaveis
        for field in modified_fields.keys():
            if field not in template.campos_editaveis:
                raise ValueError(f"Field '{field}' is not editable for this template.")

        # RF03: Auto-generation of fields if missing but marked as editable
        updates = copy.deepcopy(modified_fields)
        if "cpf" in template.campos_editaveis and "cpf" not in updates:
            updates["cpf"] = generate_cpf()
        if "cod_associado" in template.campos_editaveis and "cod_associado" not in updates:
            updates["cod_associado"] = generate_cod_associado()

        # Try to automatically determine identity_value if not provided
        if not identity_value and template.identity_field in updates:
            identity_value = str(updates[template.identity_field])

        # Construct payload_final using deep update
        payload_final = copy.deepcopy(template.payload_padrao)
        self._update_nested_dict(payload_final, updates)

        mock = MockGerado(
            template_id=str(template.id),
            url_acesso=endpoint,
            modified_fields=updates,
            payload_final=payload_final,
            identity_value=identity_value
        )
        _id = await self.repository.create_mock_gerado(mock)
        mock.id = _id
        return mock

    async def simulate_endpoint(self, endpoint: str, method: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Matches a request to a mock or returns standard response."""
        template = await self.repository.get_template_by_endpoint(endpoint, method)
        if not template:
            return {"error": "Endpoint mockup not found"}

        # Try to find a mock by identity value using the mapped field
        target_identity = None
        if template.identity_field:
            # Deep search for the key in input_data (important for nested POST bodies)
            target_identity = self._find_value_recursively(input_data, template.identity_field)
        
        if target_identity:
            mock = await self.repository.find_mock_by_identity(endpoint, method, str(target_identity))
            if mock:
                return mock.payload_final
        
        # Fallback: try all values found in input_data structure
        all_values = []
        self._extract_all_values(input_data, all_values)
        for val in [str(v) for v in all_values]:
            mock = await self.repository.find_mock_by_identity(endpoint, method, val)
            if mock:
                return mock.payload_final

        # Default to standard response if no mock hit (Template remains immutable)
        return template.payload_padrao

    async def search(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return await self.repository.search_all(filters)

    def _update_nested_dict(self, data: Dict[str, Any], updates: Dict[str, Any]):
        """Helper to update dictionary fields. Supports dot notation (key.subkey)."""
        for k, v in updates.items():
            if "." in k:
                # Dot notation for specific nested path
                keys = k.split(".")
                self._set_nested_value(data, keys, v)
            else:
                # Flat key, but could be anywhere in the structure
                self._set_deep_value(data, k, v)

    def _set_nested_value(self, data: Any, keys: List[str], value: Any):
        """Recursively follows a path of keys to set a value."""
        if not keys:
            return
        
        current_key = keys[0]
        
        if isinstance(data, dict) and current_key in data:
            if len(keys) == 1:
                data[current_key] = value
            else:
                self._set_nested_value(data[current_key], keys[1:], value)
        
        elif isinstance(data, list):
            # If we're at a list, try to apply to all items in the list
            for item in data:
                self._set_nested_value(item, keys, value)
        
        elif isinstance(data, dict):
            # Search deeper for the start of the path
            for v in data.values():
                self._set_nested_value(v, keys, value)

    def _set_deep_value(self, data: Any, target_key: str, value: Any):
        """Recursively sets value for target_key wherever it is found."""
        if isinstance(data, dict):
            if target_key in data:
                data[target_key] = value
                return True
            for v in data.values():
                if self._set_deep_value(v, target_key, value):
                    pass # Continue to find all occurrences? Usually yes for mocks.
        elif isinstance(data, list):
            for item in data:
                self._set_deep_value(item, target_key, value)
        return False

    def _find_value_recursively(self, data: Any, target_key: str) -> Any:
        """Deep search for a key in a dictionary or list."""
        if isinstance(data, dict):
            if target_key in data:
                return data[target_key]
            for v in data.values():
                res = self._find_value_recursively(v, target_key)
                if res is not None:
                    return res
        elif isinstance(data, list):
            for item in data:
                res = self._find_value_recursively(item, target_key)
                if res is not None:
                    return res
        return None

    def _extract_all_values(self, data: Any, values: List[Any]):
        """Extracts all literal values from a nested structure for fallback search."""
        if isinstance(data, dict):
            for v in data.values():
                self._extract_all_values(v, values)
        elif isinstance(data, list):
            for item in data:
                self._extract_all_values(item, values)
        else:
            if data is not None:
                values.append(data)
