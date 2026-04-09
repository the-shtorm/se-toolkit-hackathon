"""Group Pydantic schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class MemberRoleEnum(str, Enum):
    admin = "admin"
    member = "member"


class GroupCreate(BaseModel):
    """Schema for creating a notification group."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    """Schema for updating a notification group."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class GroupMemberResponse(BaseModel):
    """Schema for a group member."""
    id: UUID
    user_id: UUID
    username: str
    email: str
    role: MemberRoleEnum
    joined_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GroupResponse(BaseModel):
    """Schema for group response."""
    id: UUID
    name: str
    description: Optional[str] = None
    created_by: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class GroupDetailResponse(GroupResponse):
    """Schema for group with members list."""
    members: list[GroupMemberResponse] = []


class AddMemberRequest(BaseModel):
    """Schema for adding a member to a group."""
    user_id: UUID
    role: MemberRoleEnum = MemberRoleEnum.member


class GroupListResponse(BaseModel):
    """Paginated group list response."""
    items: list[GroupResponse]
    total: int
    page: int
    page_size: int
