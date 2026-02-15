from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.membership import Membership
from app.schemas.auth import UserCreate, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def register_user(self, user_in: UserCreate) -> User:
        existing_user = await self.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user_token(self, user: User, org_id: Optional[str] = None) -> Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Look up actual role if org_id is provided
        role = "member"
        if org_id:
            result = await self.db.execute(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.organization_id == org_id
                )
            )
            membership = result.scalars().first()
            if membership:
                role = membership.role

        claims = {"org_id": org_id, "role": role}

        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires, claims=claims
        )
        return Token(access_token=access_token, token_type="bearer")
