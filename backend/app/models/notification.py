"""Notification database models."""
import uuid
import enum
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database import Base


class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class NotificationStatusEnum(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class DeliveryStatusEnum(str, enum.Enum):
    pending = "pending"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class Notification(Base):
    """Notification model."""

    __tablename__ = "notifications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(
        Enum(PriorityEnum, values_callable=lambda e: [x.value for x in e], name="notification_priority"),
        default=PriorityEnum.medium,
        nullable=False,
    )
    status = Column(
        Enum(NotificationStatusEnum, values_callable=lambda e: [x.value for x in e], name="notification_status"),
        default=NotificationStatusEnum.pending,
        nullable=False,
    )
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(PG_UUID(as_uuid=True), ForeignKey("notification_groups.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Notification {self.title} [{self.priority}]>"


class NotificationRecipient(Base):
    """Notification recipient tracking model."""

    __tablename__ = "notification_recipients"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    notification_id = Column(PG_UUID(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    delivery_status = Column(
        Enum(DeliveryStatusEnum, values_callable=lambda e: [x.value for x in e], name="delivery_status"),
        default=DeliveryStatusEnum.pending,
        nullable=False,
    )
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<NotificationRecipient notification={self.notification_id} user={self.user_id}>"
