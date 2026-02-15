from typing import Optional, Union
from fastapi import HTTPException
from app.models.api_key import APIKey

class PermissionChecker:
    def __init__(self, org_id: str, role: Optional[str] = None, api_key: Optional[APIKey] = None):
        self.org_id = org_id
        self.role = role
        self.api_key = api_key
        self.scopes = api_key.scopes if api_key else []

    def can_read(self) -> bool:
        if self.api_key:
            return "read" in self.scopes or "write" in self.scopes or "admin" in self.scopes
        return True

    def can_write(self) -> bool:
        if self.api_key:
            return "write" in self.scopes or "admin" in self.scopes
        return True

    def can_admin(self) -> bool:
        if self.api_key:
            return "admin" in self.scopes
        return self.role in ["owner", "admin"]

    def require_read(self):
        if not self.can_read():
            raise HTTPException(status_code=403, detail="Read permission required")

    def require_write(self):
        if not self.can_write():
            raise HTTPException(status_code=403, detail="Write permission required")

    def require_admin(self):
        if not self.can_admin():
            raise HTTPException(status_code=403, detail="Admin permission required")

class RequestContext:
    def __init__(
        self,
        org_id: str,
        user_id: Optional[str] = None,
        membership_id: Optional[str] = None,
        role: Optional[str] = None,
        api_key: Optional[APIKey] = None
    ):
        self.org_id = org_id
        self.user_id = user_id
        self.membership_id = membership_id
        self.role = role
        self.api_key = api_key
        self.permissions = PermissionChecker(org_id, role, api_key)

    @property
    def is_api_key_auth(self) -> bool:
        return self.api_key is not None
