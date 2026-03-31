from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.use_cases.api_service import MockService
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.outbound.repositories.mongo_api_repository import MongoApiRepository

router = APIRouter()

def get_service():
    db = MongoDB.db
    repository = MongoApiRepository(db)
    return MockService(repository)

@router.post("/register-api")
async def register_api(config: Dict[str, Any], service: MockService = Depends(get_service)):
    try:
        # Pre-process endpoint to ensure slash
        if "endpoint" in config and not config["endpoint"].startswith("/"):
            config["endpoint"] = "/" + config["endpoint"]
        
        config_id = await service.register_api(config)
        return {"id": config_id, "message": "API configuration registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-mock")
async def generate_mock(request_data: Dict[str, Any], service: MockService = Depends(get_service)):
    try:
        endpoint = request_data.get("endpoint")
        method = request_data.get("method", "GET").upper()
        modified_fields = request_data.get("modified_fields", {})
        identity_value = request_data.get("identity_value")  # To link to the simulation input

        if not endpoint:
            raise HTTPException(status_code=400, detail="Missing endpoint.")
        
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        mock = await service.generate_mock(endpoint, method, modified_fields, identity_value)
        return {
            "message": "Mock generated successfully.",
            "mock": mock.model_dump(by_alias=True)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search")
async def search_all(service: MockService = Depends(get_service)):
    return await service.search()
