from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobResponse(BaseModel):
    id: str
    organization_id: str
    type: str
    status: str
    result_path: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
