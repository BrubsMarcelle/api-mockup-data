import copy
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.domain.models.api_mock import Template, MockGerado
from app.core.domain.ports.repository import ApiRepositoryInterface
from app.core.utils.generators import generate_cpf, generate_cod_associado

class MockService:
    def __init__(self, repository: ApiRepositoryInterface):
        self.repository = repository

    async def register_template(self, template_data: Dict[str, Any]) -> str:
        endpoint = template_data.get("endpoint")
        method = template_data.get("method")
        
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
            template_data["endpoint"] = endpoint

        existing = await self.repository.get_template_by_endpoint(endpoint, method)
        if existing:
            raise ValueError(f"Já existe um template cadastrado para o endpoint {endpoint} com o método {method}.")

        template = Template(**template_data)
        return await self.repository.create_template(template)

    async def generate_mock(self, endpoint: str, method: str, modified_fields: Dict[str, Any], identity_value: str = None, payload_customizado: Dict[str, Any] = None, descricao: str = None) -> MockGerado:
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

        payload_final = copy.deepcopy(payload_customizado) if payload_customizado is not None else copy.deepcopy(template.payload_padrao)
        
        self._update_nested_dict(payload_final, updates)

        mock = MockGerado(
            template_id=str(template.id),
            url_acesso=endpoint,
            method=method,
            modified_fields=updates,
            payload_final=payload_final,
            identity_value=identity_value,
            descricao=descricao
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
        """Busca os metadados dos templates agrupados por url_base e conta mocks por endpoint."""
        all_data = await self.repository.search_all()
        
        templates = [i for i in all_data if i.get("source_type") == "template"]
        mocks = [i for i in all_data if i.get("source_type") == "mock_gerado"]

        mock_counts = {}
        for m in mocks:
            key = (m.get("url_acesso"), m.get("method"))
            mock_counts[key] = mock_counts.get(key, 0) + 1
            
        grouped_data = {}
        
        for item in templates:
            url_base = item.get("url_base")
            if not url_base:
                continue
                
            if url_base not in grouped_data:
                grouped_data[url_base] = {
                    "name_api": item.get("name_api"),
                    "url_base": url_base,
                    "tag_squad": item.get("tag_squad"),
                    "origem_sistema": item.get("origem_sistema"),
                    "base_de_dados": item.get("base_de_dados"),
                    "count_endpoints": 0,
                    "endpoints": []
                }
            t_endpoint = item.get("endpoint")
            if t_endpoint and not t_endpoint.startswith("/"):
                t_endpoint = "/" + t_endpoint
                
            count_mocks = mock_counts.get((t_endpoint, item.get("method")), 0) + 1
            
            grouped_data[url_base]["count_endpoints"] += 1
            grouped_data[url_base]["endpoints"].append({
                "id": item.get("id") or str(item.get("_id")),
                "endpoint": item.get("endpoint"),
                "method": item.get("method"),
                "identity_field": item.get("identity_field"),
                "campos_editaveis": item.get("campos_editaveis", []),
                "payload_padrao": item.get("payload_padrao"),
                "count_mocks": count_mocks
            })
            
        return list(grouped_data.values())

    async def get_all_mocks_by_endpoint(self, endpoint: str) -> List[Dict[str, Any]]:
        """Retorna todos os mocks (template e gerados) para um endpoint específico, formatados."""
        results = await self.repository.search_all({"endpoint": endpoint})
        
        formatted_results = []
        for item in results:
            source_type = item.get("source_type")
            data_criacao = item.get("data_criacao")
            
            formatted_date = ""
            if isinstance(data_criacao, datetime):
                formatted_date = data_criacao.strftime("%d/%m/%Y")
            elif isinstance(data_criacao, str):
                try:
                    dt = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%d/%m/%Y")
                except:
                    formatted_date = data_criacao

            payload = item.get("payload_padrao") if source_type == "template" else item.get("payload_final")
            descricao = item.get("name_api") if source_type == "template" else item.get("descricao")
            
            formatted_results.append({
                "payload": payload,
                "descricao": descricao,
                "data_criacao": formatted_date,
                "identity_value": item.get("identity_value"),
                "type_generate": source_type
            })
        return formatted_results

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
