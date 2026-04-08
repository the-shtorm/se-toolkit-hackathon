"""Event database model for scheduled notifications."""
import uuid
import enum
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database import Base


class Event(Base):
    """Scheduled event that triggers a notification."""

    __tablename__ = "events"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(PG_UUID(as_uuid=True), ForeignKey("notification_groups.id", ondelete="SET NULL"), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(255), nullable=True)
    notification_id = Column(PG_UUID(as_uuid=True), ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Event {self.name} at {self.scheduled_at}>"
