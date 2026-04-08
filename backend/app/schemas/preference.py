"""User preferences Pydantic schemas."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, time


class PreferencesCreate(BaseModel):
    """Schema for creating user preferences."""
    web_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    max_daily_notifications: int = Field(default=50, ge=0, le=500)
    timezone: str = Field(default="UTC", max_length=100)
    digest_enabled: bool = False
    digest_frequency: Optional[str] = None


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    web_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    max_daily_notifications: Optional[int] = Field(None, ge=0, le=500)
    timezone: Optional[str] = Field(None, max_length=100)
    digest_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = None


class PreferencesResponse(BaseModel):
    """Schema for preferences response."""
    id: UUID
    user_id: UUID
    web_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    max_daily_notifications: int = 50
    timezone: str = "UTC"
    digest_enabled: bool = False
    digest_frequency: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
