"""Notification template Pydantic schemas."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TemplateCreate(BaseModel):
    """Schema for creating a notification template."""
    name: str = Field(..., min_length=1, max_length=255)
    title_template: str = Field(..., min_length=1, max_length=255)
    message_template: str = Field(..., min_length=1, max_length=5000)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    category: Optional[str] = Field(None, max_length=100)
    is_public: bool = False


class TemplateUpdate(BaseModel):
    """Schema for updating a notification template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title_template: Optional[str] = Field(None, min_length=1, max_length=255)
    message_template: Optional[str] = Field(None, min_length=1, max_length=5000)
    priority: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: UUID
    name: str
    title_template: str
    message_template: str
    priority: str
    category: Optional[str] = None
    created_by: UUID
    is_public: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Paginated template list response."""
    items: list[TemplateResponse]
    total: int
    page: int
    page_size: int
