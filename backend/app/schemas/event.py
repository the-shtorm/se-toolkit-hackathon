"""Event Pydantic schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class EventCreate(BaseModel):
    """Schema for creating a scheduled event."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    group_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None


class EventUpdate(BaseModel):
    """Schema for updating a scheduled event."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1, max_length=5000)
    priority: Optional[str] = None
    group_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None


class EventResponse(BaseModel):
    """Schema for event response."""
    id: UUID
    name: str
    description: Optional[str] = None
    title: str
    message: str
    priority: str
    created_by: UUID
    group_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    notification_id: Optional[UUID] = None
    celery_task_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    """Paginated event list response."""
    items: list[EventResponse]
    total: int
    page: int
    page_size: int
