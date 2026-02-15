from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(NoteBase):
    id: str
    project_id: str
    organization_id: str
    version: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_shared: bool = False

    class Config:
        from_attributes = True

class ShareLinkResponse(BaseModel):
    share_url: str
    share_token: str
