import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from app.core.database import Base, TimestampMixin

class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String)
    key_hash: Mapped[str] = mapped_column(String, index=True)
    key_prefix: Mapped[str] = mapped_column(String)
    scopes: Mapped[str] = mapped_column(String, default="")  # comma-separated
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="api_keys")
