import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.core.database import Base, TimestampMixin

class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    role: Mapped[str] = mapped_column(String, default="member")  # owner, admin, member

    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")
