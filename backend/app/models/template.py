"""Notification template database model."""
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database import Base


class NotificationTemplate(Base):
    """Reusable notification template."""

    __tablename__ = "notification_templates"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    category = Column(String(100), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<NotificationTemplate {self.name}>"
