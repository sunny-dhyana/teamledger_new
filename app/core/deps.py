from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.membership import Membership
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, org_id=payload.get("org_id"), role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == token_data.user_id))
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

async def get_current_org(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Organization:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        org_id: str = payload.get("org_id")
        if not org_id:
             # If no org in token, maybe user has no active org context. 
             # Requirement says "Each request must operate within an 'active organization context'".
             # So we should enforce it.
             raise HTTPException(status_code=400, detail="No active organization context")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Verify user is actually a member of this org
    result = await db.execute(select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.organization_id == org_id
    ))
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    result_org = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result_org.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # We could attach the membership role to the org object or return a wrapper, 
    # but for now returning the Org model is fine. 
    # The requirement says "Store the active organization in JWT claims."
    return org

async def get_api_key_dependency(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if x_api_key:
        from app.models.api_key import APIKey
        from datetime import datetime
        import hashlib

        hashed = hashlib.sha256(x_api_key.encode()).hexdigest()

        result = await db.execute(select(APIKey).where(APIKey.key_hash == hashed))
        api_key_obj = result.scalars().first()

        if api_key_obj and api_key_obj.is_active:
             if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                 raise HTTPException(status_code=401, detail="API Key expired")

             # Track API call usage
             from app.services.usage_service import UsageService
             usage_service = UsageService(db)
             await usage_service.increment_usage(api_key_obj.organization_id, "api_calls")

             return api_key_obj
        else:
            raise HTTPException(status_code=401, detail="Invalid API Key")
    return None
