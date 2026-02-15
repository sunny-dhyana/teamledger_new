import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer
from app.core.database import Base, TimestampMixin

class Usage(Base, TimestampMixin):
    __tablename__ = "usage_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    metric_name: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[int] = mapped_column(Integer, default=0)

    organization = relationship("Organization", back_populates="usage_metrics")
