"""Notification Pydantic schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class NotificationStatusEnum(str, Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    priority: PriorityEnum = PriorityEnum.medium
    group_id: Optional[UUID] = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: UUID
    title: str
    message: str
    priority: PriorityEnum
    status: NotificationStatusEnum
    created_by: UUID
    group_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated notification list response."""
    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
