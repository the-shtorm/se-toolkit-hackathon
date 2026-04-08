"""Notification snooze Pydantic schemas."""
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class SnoozeCreate(BaseModel):
    """Schema for snoozing a notification."""
    notification_id: UUID
    snoozed_until: datetime


class SnoozeResponse(BaseModel):
    """Schema for snooze response."""
    id: UUID
    notification_id: UUID
    user_id: UUID
    snoozed_until: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuickSnoozeOptions(BaseModel):
    """Quick snooze options."""
    options: list[dict[str, str]] = [
        {"label": "15 minutes", "value": "15m"},
        {"label": "1 hour", "value": "1h"},
        {"label": "4 hours", "value": "4h"},
        {"label": "1 day", "value": "1d"},
        {"label": "1 week", "value": "1w"},
    ]
