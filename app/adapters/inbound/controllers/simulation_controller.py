from typing import Any, Dict
from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.use_cases.api_service import MockService
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.outbound.repositories.mongo_api_repository import MongoApiRepository

router = APIRouter()

def get_service():
    db = MongoDB.db
    repository = MongoApiRepository(db)
    return MockService(repository)

@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def simulate_endpoint(full_path: str, request: Request, service: MockService = Depends(get_service)):
    # Normalize full_path to include the leading slash
    endpoint = "/" + full_path if not full_path.startswith("/") else full_path
    method = request.method.upper()
    
    # Extract data from request (Body or Query params)
    input_data = {}
    
    # Query parameters
    input_data.update(dict(request.query_params))
    
    # Body data (only if JSON)
    try:
        body = await request.json()
        if isinstance(body, dict):
            input_data.update(body)
    except Exception:
        # Ignore body cases if not parseable or not present
        pass
    
    # Service logic to find the best match
    response_json = await service.simulate_endpoint(endpoint, method, input_data)
    
    if "error" in response_json and len(response_json.keys()) == 1:
        raise HTTPException(status_code=404, detail=f"No mockup found for {endpoint} with input data.")
        
    return response_json
