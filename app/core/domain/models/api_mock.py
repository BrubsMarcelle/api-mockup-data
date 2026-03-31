from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class APIConfig(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    url_base: str
    endpoint: str
    method: str
    input_type: str  # body or query
    tag_squad: str
    standard_response: Dict[str, Any]
    floating_fields: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class APIMock(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    api_config_id: str
    endpoint: str  # Path to match
    modified_fields: Dict[str, Any]
    final_response: Dict[str, Any]
    response_tag: str  # e.g., "standard", "mock"
    # To identify which mock to return based on input data
    identity_value: Optional[str] = None  # e.g., "cpf_123"
    created_at: datetime = Field(default_factory=datetime.utcnow)
