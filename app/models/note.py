import uuid
import secrets
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer
from app.core.database import Base, TimestampMixin

class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"))
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    share_token: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True, index=True)

    project = relationship("Project", back_populates="notes")
    organization = relationship("Organization")
    created_by_user = relationship("User") 
