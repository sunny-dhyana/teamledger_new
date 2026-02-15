import secrets
import hashlib
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate

class APIKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_api_key(self, org_id: str, key_in: APIKeyCreate) -> tuple[APIKey, str]:
        # Generate random key
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        db_key = APIKey(
            organization_id=org_id,
            name=key_in.name,
            key_hash=key_hash,
            key_prefix=raw_key[:8],
            scopes=key_in.scopes,
            expires_at=key_in.expires_at,
            is_active=True
        )
        self.db.add(db_key)
        await self.db.commit()
        await self.db.refresh(db_key)
        return db_key, raw_key

    async def list_api_keys(self, org_id: str) -> List[APIKey]:
        result = await self.db.execute(select(APIKey).where(APIKey.organization_id == org_id))
        return result.scalars().all()

    async def revoke_api_key(self, key_id: str, org_id: str) -> Optional[APIKey]:
        result = await self.db.execute(select(APIKey).where(
            APIKey.id == key_id,
            APIKey.organization_id == org_id
        ))
        key = result.scalars().first()
        if key:
            key.is_active = False
            self.db.add(key)
            await self.db.commit()
            await self.db.refresh(key)
        return key
