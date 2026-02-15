from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import Token, UserCreate, UserResponse
from app.core.response import StandardResponse

router = APIRouter()

@router.post("/register")
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    print(f"DEBUG: Router received register request for {user_in.email}")
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_in)
    print(f"DEBUG: Router sending success response for {user.email}")
    return StandardResponse.success({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    })

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = await auth_service.create_user_token(user)
    return StandardResponse.success({
        "access_token": token.access_token,
        "token_type": token.token_type
    })
