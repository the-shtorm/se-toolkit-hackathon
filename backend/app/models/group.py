"""Notification group database models."""
import uuid
import enum
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database import Base


class MemberRoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"


class NotificationGroup(Base):
    """Group for organizing notification recipients."""

    __tablename__ = "notification_groups"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<NotificationGroup {self.name}>"


class GroupMember(Base):
    """Many-to-many relationship between groups and users."""

    __tablename__ = "group_members"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(PG_UUID(as_uuid=True), ForeignKey("notification_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(MemberRoleEnum), default=MemberRoleEnum.member, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<GroupMember group={self.group_id} user={self.user_id} role={self.role}>"
