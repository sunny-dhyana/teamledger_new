from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(BaseModel):
    name: str
    slug: Optional[str] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MemberResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: str

    class Config:
        from_attributes = True

class InviteTokenResponse(BaseModel):
    invite_token: str

class JoinOrganizationRequest(BaseModel):
    invite_token: str
