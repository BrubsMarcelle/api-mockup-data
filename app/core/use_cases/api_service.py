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
            raise ValueError(f"Template não encontrado para o endpoint {endpoint} e método {method}.")

        for field in modified_fields.keys():
            if field not in template.campos_editaveis:
                raise ValueError(f"O campo '{field}' não é editável para este template.")

        updates = copy.deepcopy(modified_fields)
        if "cpf" in template.campos_editaveis and "cpf" not in updates:
            updates["cpf"] = generate_cpf()
        if "cod_associado" in template.campos_editaveis and "cod_associado" not in updates:
            updates["cod_associado"] = generate_cod_associado()

        if not identity_value and template.identity_field in updates:
            identity_value = str(updates[template.identity_field])

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
        """Tenta encontrar um mock específico ou retorna a resposta padrão do template."""
        template = await self.repository.get_template_by_endpoint(endpoint, method)
        if not template:
            return {"error": "Mockup de endpoint não encontrado"}

        target_identity = None
        if template.identity_field:
            target_identity = self._find_value_recursively(input_data, template.identity_field)
        
        if target_identity:
            mock = await self.repository.find_mock_by_identity(endpoint, method, str(target_identity))
            if mock:
                return mock.payload_final
        
        all_values = []
        self._extract_all_values(input_data, all_values)
        for val in [str(v) for v in all_values]:
            mock = await self.repository.find_mock_by_identity(endpoint, method, val)
            if mock:
                return mock.payload_final

        return template.payload_padrao

    async def search(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return await self.repository.search_all(filters)

    async def get_all_templates_metadata(self) -> List[Dict[str, Any]]:
        """Busca apenas os metadados dos templates para popular formulários no Front-end."""
        all_results = await self.repository.search_all({"source_type": "template"})
        
        metadata_list = []
        for item in all_results:
            metadata_list.append({
                "id": item.get("id") or str(item.get("_id")),
                "endpoint": item.get("endpoint"),
                "method": item.get("method"),
                "url_base": item.get("url_base"),
                "identity_field": item.get("identity_field"),
                "campos_editaveis": item.get("campos_editaveis", [])
            })
        return metadata_list

    def _update_nested_dict(self, data: Dict[str, Any], updates: Dict[str, Any]):
        """Auxiliar para atualizar campos de dicionário. Suporta notação de ponto (chave.subchave)."""
        for k, v in updates.items():
            if "." in k:
                keys = k.split(".")
                self._set_nested_value(data, keys, v)
            else:
                self._set_deep_value(data, k, v)

    def _set_nested_value(self, data: Any, keys: List[str], value: Any):
        """Segue recursivamente um caminho de chaves para definir um valor."""
        if not keys:
            return
        
        current_key = keys[0]
        
        if isinstance(data, dict) and current_key in data:
            if len(keys) == 1:
                data[current_key] = value
            else:
                self._set_nested_value(data[current_key], keys[1:], value)
        
        elif isinstance(data, list):
            for item in data:
                self._set_nested_value(item, keys, value)
        
        elif isinstance(data, dict):
            for v in data.values():
                self._set_nested_value(v, keys, value)

    def _set_deep_value(self, data: Any, target_key: str, value: Any):
        """Define o valor para target_key recursivamente onde quer que ele seja encontrado."""
        if isinstance(data, dict):
            if target_key in data:
                data[target_key] = value
                return True
            for v in data.values():
                if self._set_deep_value(v, target_key, value):
                    pass
        elif isinstance(data, list):
            for item in data:
                self._set_deep_value(item, target_key, value)
        return False

    def _find_value_recursively(self, data: Any, target_key: str) -> Any:
        """Busca profunda por uma chave em um dicionário ou lista."""
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
        """Extrai todos os valores literais de uma estrutura aninhada para busca de fallback."""
        if isinstance(data, dict):
            for v in data.values():
                self._extract_all_values(v, values)
        elif isinstance(data, list):
            for item in data:
                self._extract_all_values(item, values)
        else:
            if data is not None:
                values.append(data)
