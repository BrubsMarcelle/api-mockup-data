from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Body
from app.core.use_cases.api_service import MockService
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.outbound.repositories.mongo_api_repository import MongoApiRepository

router = APIRouter()

def get_service():
    db = MongoDB.db
    repository = MongoApiRepository(db)
    return MockService(repository)

async def _handle_simulation(full_path: str, request: Request, service: MockService, body_data: Optional[Dict[str, Any]] = None):
    endpoint = "/" + full_path if not full_path.startswith("/") else full_path
    method = request.method.upper()
    
    input_data = {}
    input_data.update(dict(request.query_params))
    
    if body_data:
        input_data.update(body_data)
    else:
        try:
            raw_body = await request.json()
            if isinstance(raw_body, dict):
                input_data.update(raw_body)
        except Exception:
            pass
    
    response_json = await service.simulate_endpoint(endpoint, method, input_data)
    
    if "error" in response_json and len(response_json.keys()) == 1:
        raise HTTPException(status_code=404, detail=f"Nenhum mockup encontrado para o endpoint '{endpoint}' com o método {method}.")
        
    return response_json

@router.get("/{full_path:path}", tags=["Simulation"], summary="Simular uma requisição GET")
async def simulate_get(full_path: str, request: Request, service: MockService = Depends(get_service)):
    """
    Intercapta chamadas GET.
    Pode usar parâmetros na query (URL) para buscar dados específicos.
    """
    return await _handle_simulation(full_path, request, service)

@router.post("/{full_path:path}", tags=["Simulation"], summary="Simular uma requisição POST")
async def simulate_post(full_path: str, request: Request, body: Dict[str, Any] = Body(None), service: MockService = Depends(get_service)):
    """
    Intercepta chamadas POST. 
    Se o Body contiver um campo de busca (CPF/Código), o sistema retornará o mock correspondente.
    """
    return await _handle_simulation(full_path, request, service, body_data=body)

@router.put("/{full_path:path}", tags=["Simulation"], summary="Simular uma requisição PUT")
async def simulate_put(full_path: str, request: Request, body: Dict[str, Any] = Body(None), service: MockService = Depends(get_service)):
    """Intercepta chamadas PUT para atualização simulada."""
    return await _handle_simulation(full_path, request, service, body_data=body)

@router.patch("/{full_path:path}", tags=["Simulation"], summary="Simular uma requisição PATCH")
async def simulate_patch(full_path: str, request: Request, body: Dict[str, Any] = Body(None), service: MockService = Depends(get_service)):
    """Intercepta chamadas PATCH para atualização parcial simulada."""
    return await _handle_simulation(full_path, request, service, body_data=body)

@router.delete("/{full_path:path}", tags=["Simulation"], summary="Simular uma requisição DELETE")
async def simulate_delete(full_path: str, request: Request, body: Dict[str, Any] = Body(None), service: MockService = Depends(get_service)):
    """Intercepta chamadas DELETE para remoção simulada."""
    return await _handle_simulation(full_path, request, service, body_data=body)
