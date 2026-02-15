from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_user, get_request_context
from app.core.permissions import RequestContext
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
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if x_api_key:
        from app.core.security import create_access_token
        from app.core.deps import get_api_key_dependency
        import hashlib
        from sqlalchemy import select
        from app.models.api_key import APIKey

        hashed = hashlib.sha256(x_api_key.encode()).hexdigest()
        result = await db.execute(select(APIKey).where(APIKey.key_hash == hashed))
        api_key_obj = result.scalars().first()

        if not api_key_obj or not api_key_obj.is_active:
            raise HTTPException(status_code=401, detail="Invalid API Key")

        role = api_key_obj.scopes if api_key_obj.scopes else "member"

        token = create_access_token(
            subject=current_user.id,
            claims={
                "org_id": org_id,
                "role": role,
                "membership_id": "api-key-membership"
            }
        )

        return StandardResponse.success({
            "access_token": token,
            "token_type": "bearer"
        })

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

@router.post("/{org_id}/members/{user_id}/remove")
async def remove_member(
    org_id: str,
    user_id: str,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if context.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not your active organization")

    context.permissions.require_admin()

    org_service = OrganizationService(db)
    success = await org_service.remove_member(org_id, user_id, context.role)

    if not success:
        raise HTTPException(status_code=400, detail="Cannot remove member")

    return StandardResponse.success({"message": "Member removed successfully"})

@router.put("/{org_id}/members/{user_id}/role")
async def change_member_role(
    org_id: str,
    user_id: str,
    new_role: str,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if context.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not your active organization")

    context.permissions.require_admin()

    org_service = OrganizationService(db)
    membership = await org_service.change_role(org_id, user_id, new_role, context.role)

    if not membership:
        raise HTTPException(status_code=400, detail="Cannot change role")

    return StandardResponse.success({
        "user_id": user_id,
        "role": membership.role,
        "message": "Role updated successfully"
    })

@router.post("/{org_id}/leave")
async def leave_organization(
    org_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    org_service = OrganizationService(db)
    success = await org_service.leave_organization(org_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail="Cannot leave organization")

    return StandardResponse.success({"message": "Left organization successfully"})
