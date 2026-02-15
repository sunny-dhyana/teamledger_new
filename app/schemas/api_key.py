from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class APIKeyCreate(BaseModel):
    name: str
    scopes: Optional[str] = ""
    expires_at: Optional[datetime] = None

class APIKeyResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    key_prefix: str  # Only show prefix or partial key? 
    # Actually requirement says: key_hash. We probably shouldn't return key_hash.
    # But usually we return the raw key ONCE upon creation.
    scopes: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class APIKeyCreatedResponse(APIKeyResponse):
    key: str # The actual key, shown only once
