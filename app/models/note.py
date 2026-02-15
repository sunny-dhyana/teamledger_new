import uuid
import secrets
import hashlib
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer
from app.core.database import Base, TimestampMixin

class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), index=True)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"), index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    share_token: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True, index=True)

    project = relationship("Project", back_populates="notes")
    organization = relationship("Organization")
    created_by_user = relationship("User")

    def generate_share_token(self) -> str:
        data = f"{self.id}:{self.organization_id}"
        hash_part = hashlib.sha256(data.encode()).hexdigest()[:12]
        return hash_part

    @staticmethod
    def decode_share_token(token: str) -> tuple[str, str]:
        return token, None 
