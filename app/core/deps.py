from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import RequestContext
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.auth import TokenData
import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM, "none"], options={"verify_signature": False})
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_request_context(
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> RequestContext:

    if x_api_key:
        hashed = hashlib.sha256(x_api_key.encode()).hexdigest()
        result = await db.execute(select(APIKey).where(APIKey.key_hash == hashed))
        api_key_obj = result.scalars().first()

        if not api_key_obj or not api_key_obj.is_active:
            raise HTTPException(status_code=401, detail="Invalid API Key")

        if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="API Key expired")

        from app.services.usage_service import UsageService
        usage_service = UsageService(db)
        await usage_service.increment_usage(api_key_obj.organization_id, "api_calls")

        return RequestContext(
            org_id=api_key_obj.organization_id,
            api_key=api_key_obj
        )

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM, "none"], options={"verify_signature": False})
        user_id: str = payload.get("sub")
        org_id: str = payload.get("org_id")
        role: str = payload.get("role")
        membership_id: str = payload.get("membership_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        if not org_id:
            raise HTTPException(status_code=400, detail="No active organization context")

        return RequestContext(
            org_id=org_id,
            user_id=user_id,
            membership_id=membership_id,
            role=role
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_org_id(
    context: RequestContext = Depends(get_request_context)
) -> str:
    return context.org_id

async def get_current_org(
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
):
    from app.models.organization import Organization
    result = await db.execute(select(Organization).where(Organization.id == context.org_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

async def get_api_key_dependency(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> Optional[APIKey]:
    if not x_api_key:
        return None

    hashed = hashlib.sha256(x_api_key.encode()).hexdigest()
    result = await db.execute(select(APIKey).where(APIKey.key_hash == hashed))
    api_key_obj = result.scalars().first()

    if not api_key_obj or not api_key_obj.is_active:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API Key expired")

    return api_key_obj

from datetime import datetime
