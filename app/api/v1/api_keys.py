from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_org
from app.models.organization import Organization
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreatedResponse
from app.services.api_key_service import APIKeyService
from app.services.usage_service import UsageService
from app.core.response import StandardResponse

router = APIRouter()

@router.post("/")
async def create_api_key(
    key_in: APIKeyCreate,
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = APIKeyService(db)
    api_key, raw_key = await service.create_api_key(current_org.id, key_in)

    return StandardResponse.success({
        "id": api_key.id,
        "organization_id": api_key.organization_id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes,
        "is_active": api_key.is_active,
        "created_at": api_key.created_at.isoformat(),
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
        "key": raw_key
    })

@router.get("/")
async def list_api_keys(
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = APIKeyService(db)
    keys = await service.list_api_keys(current_org.id)
    return StandardResponse.success([{
        "id": k.id,
        "organization_id": k.organization_id,
        "name": k.name,
        "key_prefix": k.key_prefix,
        "scopes": k.scopes,
        "is_active": k.is_active,
        "created_at": k.created_at.isoformat(),
        "expires_at": k.expires_at.isoformat() if k.expires_at else None
    } for k in keys])

@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = APIKeyService(db)
    key = await service.revoke_api_key(key_id, current_org.id)
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    return StandardResponse.success({
        "id": key.id,
        "organization_id": key.organization_id,
        "name": key.name,
        "key_prefix": key.key_prefix,
        "scopes": key.scopes,
        "is_active": key.is_active,
        "created_at": key.created_at.isoformat(),
        "expires_at": key.expires_at.isoformat() if key.expires_at else None
    })
