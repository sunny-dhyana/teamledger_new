from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_user
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate, InviteTokenResponse, JoinOrganizationRequest
from app.schemas.auth import Token
from app.services.organization_service import OrganizationService
from app.services.auth_service import AuthService
from app.core.response import StandardResponse

router = APIRouter()

@router.post("/")
async def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    org_service = OrganizationService(db)
    org = await org_service.create_organization(current_user, org_in)
    return StandardResponse.success({
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "created_at": org.created_at.isoformat(),
        "updated_at": org.updated_at.isoformat()
    })

@router.get("/")
async def list_organizations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    org_service = OrganizationService(db)
    orgs = await org_service.get_user_organizations(current_user.id)
    return StandardResponse.success([{
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "created_at": org.created_at.isoformat(),
        "updated_at": org.updated_at.isoformat()
    } for org in orgs])

@router.post("/{org_id}/switch")
async def switch_organization(
    org_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    org_service = OrganizationService(db)
    user_orgs = await org_service.get_user_organizations(current_user.id)
    if not any(org.id == org_id for org in user_orgs):
         raise HTTPException(status_code=403, detail="Not a member of this organization")

    auth_service = AuthService(db)
    token = await auth_service.create_user_token(current_user, org_id)
    return StandardResponse.success({
        "access_token": token.access_token,
        "token_type": token.token_type
    })

@router.post("/{org_id}/invite")
async def generate_invite_token(
    org_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate an invite token for the organization."""
    org_service = OrganizationService(db)

    user_orgs = await org_service.get_user_organizations(current_user.id)
    if not any(org.id == org_id for org in user_orgs):
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    token = await org_service.generate_invite_token(org_id)
    return StandardResponse.success({"invite_token": token})

@router.post("/join")
async def join_organization(
    request: JoinOrganizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Join an organization using an invite token."""
    org_service = OrganizationService(db)

    membership = await org_service.join_organization_via_token(current_user.id, request.invite_token)
    if not membership:
        raise HTTPException(status_code=400, detail="Invalid or expired invite token")

    return StandardResponse.success({
        "message": "Successfully joined organization",
        "organization_id": membership.organization_id
    })
