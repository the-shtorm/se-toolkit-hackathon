"""User notification preferences database model."""
import uuid
import enum
from sqlalchemy import Column, String, Boolean, Integer, Time, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database import Base


class DigestFrequencyEnum(enum.Enum):
    """Digest frequency options."""
    daily = "daily"
    weekly = "weekly"


class UserPreferences(Base):
    """User notification preferences."""

    __tablename__ = "notification_preferences"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    web_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(Time, nullable=True)
    quiet_hours_end = Column(Time, nullable=True)
    max_daily_notifications = Column(Integer, default=50)
    timezone = Column(String(100), default="UTC")
    digest_enabled = Column(Boolean, default=False)
    digest_frequency = Column(SAEnum(DigestFrequencyEnum), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<UserPreferences user_id={self.user_id}>"
