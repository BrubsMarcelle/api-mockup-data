from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.use_cases.api_service import MockService
from app.adapters.outbound.repositories.repository_factory import get_repository
from app.core.use_cases.auth_service import AuthService
from app.core.domain.models.api_mock import MockGeradoCreate, TemplateBody, SquadTag, DatabaseOrigin, Method

router = APIRouter()

def get_service():
    repository = get_repository()
    return MockService(repository)

@router.post(
    "/register-template", 
    summary="1. Cadastrar um novo Template (A Regra)",
    responses={
        200: {"description": "Template criado com sucesso e ID retornado."},
        401: {"description": "Não autorizado. Token JWT ausente ou inválido."},
        400: {"description": "Dados inválidos enviados no corpo da requisição."}
    }
)
async def register_template(
    body: TemplateBody,
    name_api: str = Query(..., description="Nome da API"),
    url_base: str = Query(..., description="A URL do servidor original", example="https://api.dmcard.com.br"),
    endpoint: str = Query(..., description="O path da API (Ex: v1/usuarios)"),
    method: Method = Query(Method.POST, description="O método HTTP (GET, POST, etc.)"),
    identity_field: Optional[str] = Query(None, description="Qual campo identifica o dado (Ex: cpf)"),
    tag_squad: Optional[SquadTag] = Query(None, description="Squad responsável"),
    base_de_dados: Optional[DatabaseOrigin] = Query(None, description="Base de dados de origem"),
    origem_sistema: Optional[str] = Query(None, description="Informe se o sistema é 'Legado' ou 'Argo'"),
    service: MockService = Depends(get_service),
    current_user: str = Depends(AuthService.get_current_user)
):
    """
    Este endpoint salva a **regra principal** do seu mock. 
    A configuração administrativa fica no topo (Parameters) e o JSON no Body embaixo.
    """
    try:
        template_dict = {
            "name_api": name_api,
            "endpoint": endpoint,
            "method": method.upper(),
            "identity_field": identity_field,
            "url_base": url_base,
            "tag_squad": tag_squad,
            "base_de_dados": base_de_dados,
            "origem_sistema": origem_sistema,
            "payload_padrao": body.payload_padrao,
            "campos_editaveis": body.campos_editaveis
        }

        if not template_dict["endpoint"].startswith("/"):
            template_dict["endpoint"] = "/" + template_dict["endpoint"]
        
        template_id = await service.register_template(template_dict)
        return {"id": template_id, "message": "API template registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/generate-mock", 
    summary="2. Gerar uma instância customizada",
    responses={
        200: {"description": "Mock gerado com sucesso para este cenário."},
        401: {"description": "Não autorizado. Token JWT ausente ou inválido."},
        404: {"description": "O template para este endpoint não foi encontrado."},
        400: {"description": "Erro ao tentar mesclar o JSON customizado."}
    }
)
async def generate_mock(
    request_data: MockGeradoCreate, 
    service: MockService = Depends(get_service),
    current_user: str = Depends(AuthService.get_current_user)
):
    """
    Este endpoint cria uma **instância fidedigna** de um mock. 
    A partir de um template já cadastrado, você diz o que quer que mude.
    
    ### 📝 Campos do Formulário:
    *   **endpoint**: O caminho cadastrado anteriormente.
    *   **method**: O método (deve ser o mesmo do template).
    *   **modified_fields**: O JSON apenas dos campos que você quer sobrecrever.
    *   **identity_value**: O dado único que identifica esta variação (Ex: o valor cadastrado no campo identity_field do template).
    *   **payload_customizado**: O JSON completo que você quer usar como base para o mock, se não informado, será usado o payload_padrao do template.
    *   **descricao**: Descrição do mock / Descrever o cenario daquele mock, de uma forma curta
    
    ### ↩️ Retornos:
    *   **200**: Sucesso! O dado customizado foi salvo e está pronto para ser simulado.
    *   **404**: Erro! Você não pode gerar um mock para um endpoint que ainda não foi cadastrado como template.
    """
    try:
        endpoint = request_data.endpoint
        method = request_data.method.upper()
        modified_fields = request_data.modified_fields
        identity_value = request_data.identity_value
        descricao = request_data.descricao

        if not endpoint:
            raise HTTPException(status_code=400, detail="Missing endpoint.")
        
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        mock = await service.generate_mock(
            endpoint, 
            method, 
            modified_fields, 
            identity_value,
            request_data.payload_customizado,
            descricao
        )
        return {
            "message": "Mock generated successfully.",
            "mock": mock.model_dump(by_alias=True)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", summary="3. Pesquisar Templates e Mocks", responses={401: {"description": "Não autorizado."}})
async def search_all(
    url_base: Optional[str] = Query(None, description="Filtrar por pedaço da URL Base"),
    endpoint: Optional[str] = Query(None, description="Filtrar por pedaço do Endpoint"),
    identity_value: Optional[str] = Query(None, description="Filtrar pelo VALOR informado (Ex: '57462')"),
    tag_squad: Optional[SquadTag] = Query(None, description="Filtrar pela Squad"),
    base_de_dados: Optional[DatabaseOrigin] = Query(None, description="Filtrar pela Base de Dados"),
    service: MockService = Depends(get_service),
    current_user: str = Depends(AuthService.get_current_user)
):
    """
    Lista os templates e instâncias de mock com filtros opcionais.
    Se não encontrar nada que corresponda aos filtros informados, retorna **404**.
    """
    filters = {
        "url_base": url_base,
        "endpoint": endpoint,
        "identity_value": identity_value,
        "tag_squad": tag_squad,
        "base_de_dados": base_de_dados
    }
    active_filters = {k: v for k, v in filters.items() if v is not None}
    
    results = await service.search(active_filters)
    
    if not results:
        raise HTTPException(
            status_code=404, 
            detail="Não foi encontrado nenhum template ou mock com esses filtros. Verifique os valores informados."
        )
    
    return results

@router.get(
    "/templates-metadata", 
    summary="4. Listar Metadados dos Templates"
)
async def get_templates_metadata(service: MockService = Depends(get_service)):
    """
    Retorna apenas os metadados dos templates cadastrados.
    """
    return await service.get_all_templates_metadata()

@router.get(
    "/list-mocks-by-endpoint", 
    summary="5. Listar todos os mocks por endpoint"
)
async def list_mocks_by_endpoint(
    endpoint: str = Query(..., description="O endpoint para listar os mocks (Ex: /v1/usuarios)"),
    service: MockService = Depends(get_service)
):
    """
    Retorna uma lista de todos os mocks cadastrados (template e variações) para um endpoint específico.
    Inclui o payload, descrição, data de criação formatada e o tipo de geração.
    """
    return await service.get_all_mocks_by_endpoint(endpoint)
