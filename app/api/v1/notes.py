from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_org, get_current_user, get_api_key_dependency, oauth2_scheme
from app.models.organization import Organization
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate, SharedNoteUpdate
from app.services.note_service import NoteService
from app.services.usage_service import UsageService
from app.core.config import settings
from app.core.response import StandardResponse
from jose import jwt


router = APIRouter()

# Helper to resolve context (JWT or API Key)
async def get_read_context(
    token: Optional[str] = Depends(oauth2_scheme), # auto_error=True by default on scheme... wait
    # We can't use oauth2_scheme directly if we want optional.
    # But here we can use Header for Authorization manually or define a new scheme.
    # For simplicity, we'll try to use get_current_org but catch error? No, Depends(get_current_org) raises.
    # We need a custom dependency here.
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> tuple[str, Optional[str]]: # Returns (org_id, user_id)
    
    # Try API Key first if present
    if x_api_key:
        api_key_dep = await get_api_key_dependency(x_api_key, db)
        if api_key_dep:
            return api_key_dep.organization_id, None
    
    # Try JWT
    # We verify logic similar to get_current_org manually here
    # Or strict: if X-API-Key is NOT present, we require JWT.
    # If X-API-Key present, we use it.
    
    # Let's rely on standard dependencies but use a trick:
    # We can't easily conditionally use Dependencies.
    
    # Redefine the endpoint logic to handle auth manually?
    raise HTTPException(status_code=401, detail="Authentication required")

# Actually, clean way:
# Split endpoints? No, same URL.
# Use `Depends(get_current_org)` implies JWT.
# Use `Depends(get_api_key)` implies APIKey.
# We can make `token` optional in a custom dependency.

from fastapi.security import OAuth2PasswordBearer
oauth2_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_org_context_mixed(
    token: Optional[str] = Depends(oauth2_optional),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> str: # Returns org_id
    if x_api_key:
        # Check API Key
        # Reuse get_api_key_dependency logic
        from app.models.api_key import APIKey
        from sqlalchemy import select
        import hashlib
        hashed = hashlib.sha256(x_api_key.encode()).hexdigest()
        result = await db.execute(select(APIKey).where(APIKey.key_hash == hashed))
        api_key_obj = result.scalars().first()
        if api_key_obj and api_key_obj.is_active:
             return api_key_obj.organization_id
        # if invalid api key, maybe fall through or fail? 
        # Usually fail if key provided but invalid.
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if token:
        # Check JWT
        # Decode and extract org_id
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            org_id = payload.get("org_id")
            if org_id:
                return org_id
        except:
            pass
            
    raise HTTPException(status_code=401, detail="Not authenticated")


@router.post("/")
async def create_note(
    note_in: NoteCreate,
    project_id: str,
    current_org: Organization = Depends(get_current_org),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    note_service = NoteService(db)
    note = await note_service.create_note(project_id, current_org.id, current_user.id, note_in)

    # Track usage
    usage_service = UsageService(db)
    await usage_service.increment_usage(current_org.id, "notes_created")

    return StandardResponse.success({
        "id": note.id,
        "project_id": note.project_id,
        "organization_id": note.organization_id,
        "title": note.title,
        "content": note.content,
        "version": note.version,
        "created_by": note.created_by,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat()
    })

@router.get("/")
async def list_notes(
    project_id: str,
    org_id: str = Depends(get_org_context_mixed), # Supports API Key or JWT
    db: AsyncSession = Depends(get_db)
) -> Any:
    note_service = NoteService(db)
    notes = await note_service.get_notes(project_id, org_id)
    return StandardResponse.success([{
        "id": n.id,
        "project_id": n.project_id,
        "organization_id": n.organization_id,
        "title": n.title,
        "content": n.content,
        "version": n.version,
        "created_by": n.created_by,
        "created_at": n.created_at.isoformat(),
        "updated_at": n.updated_at.isoformat(),
        "is_shared": n.share_token is not None
    } for n in notes])

@router.get("/{note_id}")
async def get_note(
    note_id: str,
    project_id: str,
    org_id: str = Depends(get_org_context_mixed),
    db: AsyncSession = Depends(get_db)
) -> Any:
    note_service = NoteService(db)
    note = await note_service.get_note(note_id, project_id, org_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return StandardResponse.success({
        "id": note.id,
        "project_id": note.project_id,
        "organization_id": note.organization_id,
        "title": note.title,
        "content": note.content,
        "version": note.version,
        "created_by": note.created_by,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
        "is_shared": note.share_token is not None
    })

@router.put("/{note_id}")
async def update_note(
    note_id: str,
    project_id: str,
    note_in: NoteUpdate,
    current_org: Organization = Depends(get_current_org), # Write requires JWT
    db: AsyncSession = Depends(get_db)
) -> Any:
    note_service = NoteService(db)
    note = await note_service.update_note(note_id, project_id, current_org.id, note_in)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return StandardResponse.success({
        "id": note.id,
        "project_id": note.project_id,
        "organization_id": note.organization_id,
        "title": note.title,
        "content": note.content,
        "version": note.version,
        "created_by": note.created_by,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat()
    })

@router.post("/{note_id}/share")

async def generate_share_link(
    note_id: str,
    project_id: str,
    access_level: str = "view",
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate a shareable link for a note"""
    if access_level not in ["view", "edit"]:
        raise HTTPException(status_code=400, detail="Invalid access level")
        
    note_service = NoteService(db)
    share_token = await note_service.generate_share_token(note_id, project_id, current_org.id, access_level)
    
    if not share_token:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Construct the share URL
    share_url = f"{settings.FRONTEND_URL}/shared/{share_token}"
    
    return StandardResponse.success({
        "share_url": share_url,
        "share_token": share_token,
        "access_level": access_level
    })

@router.delete("/{note_id}/share")
async def revoke_share_link(
    note_id: str,
    project_id: str,
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Revoke the shareable link for a note"""
    note_service = NoteService(db)
    success = await note_service.revoke_share_token(note_id, project_id, current_org.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return StandardResponse.success({"message": "Share link revoked successfully"})

@router.get("/shared/{share_token}")
async def get_shared_note(
    share_token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Public endpoint to access a shared note (no authentication required)"""
    note_service = NoteService(db)
    note = await note_service.get_note_by_share_token(share_token)
    
    if not note:
        raise HTTPException(status_code=404, detail="Shared note not found")
    
    return StandardResponse.success({
        "id": note.id,
        "project_id": note.project_id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
        "access_level": note.share_access_level
    })

@router.put("/shared/{share_token}")
async def update_shared_note(
    share_token: str,
    note_in: SharedNoteUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a shared note (if access level permits)"""
    note_service = NoteService(db)
    note = await note_service.update_shared_note(share_token, note_in)
    
    if not note:
        raise HTTPException(status_code=403, detail="Note not found or edit permission denied")
    
    return StandardResponse.success({
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "updated_at": note.updated_at.isoformat()
    })
