"""Notification API endpoints."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser, CurrentDB
from app.models.user import User
from app.models.notification import NotificationStatusEnum
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and send notification",
)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Create a new notification. The creator is automatically added as recipient."""
    return await notification_service.create_notification(
        db=db,
        notification_data=notification_data,
        created_by=current_user.id,
    )


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List user's notifications",
)
async def list_notifications(
    current_user: CurrentUser,
    db: CurrentDB,
    status_filter: Optional[NotificationStatusEnum] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Get paginated list of notifications for the current user."""
    notifications, total = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )

    return NotificationListResponse(
        items=[
            NotificationResponse.model_validate(n) for n in notifications
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/stats",
    summary="Get notification statistics",
)
async def get_stats(
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Get unread notification count for current user."""
    unread_count = await notification_service.get_unread_count(
        db=db,
        user_id=current_user.id,
    )
    return {"unread_count": unread_count}


@router.put(
    "/read-all",
    summary="Mark all notifications as read",
)
async def mark_all_as_read(
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Mark all unread notifications as read."""
    count = await notification_service.mark_all_as_read(
        db=db,
        user_id=current_user.id,
    )
    return {"message": f"Marked {count} notifications as read", "count": count}


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
async def mark_as_read(
    notification_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Mark a specific notification as read."""
    import uuid
    try:
        notif_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID format",
        )

    notification = await notification_service.mark_notification_as_read(
        db=db,
        notification_id=notif_uuid,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification by ID",
)
async def get_notification(
    notification_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Get a specific notification if user is a recipient."""
    import uuid
    try:
        notif_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID format",
        )

    notification = await notification_service.get_notification_by_id(
        db=db,
        notification_id=notif_uuid,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification
