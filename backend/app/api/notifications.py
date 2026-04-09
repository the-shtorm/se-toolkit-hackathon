"""Notification API endpoints."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser, CurrentDB
from app.models.user import User
from app.models.notification import Notification, NotificationRecipient, NotificationStatusEnum
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
    """Create a notification. Optionally send to a group (all members receive it)."""
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
    group_id: Optional[str] = Query(None, description="Filter by group"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Get paginated list of notifications for the current user."""
    enriched_notifications, total = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
        group_id=group_id,
    )

    return NotificationListResponse(
        items=[
            {
                **NotificationResponse.model_validate(n).model_dump(),
                "group_name": gn,
            }
            for n, gn in enriched_notifications
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
    """Get notification statistics for dashboard analytics. Excludes pending (scheduled) notifications."""
    from datetime import datetime, timedelta, timezone

    # Unread count (excludes pending)
    unread_count = await notification_service.get_unread_count(
        db=db,
        user_id=current_user.id,
    )

    # Total notifications (excludes pending)
    total_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.id.in_(
            select(NotificationRecipient.notification_id).where(
                NotificationRecipient.user_id == current_user.id
            )
        )).where(Notification.status != NotificationStatusEnum.pending)
    )
    total = total_result.scalar() or 0

    # Read rate (excludes pending)
    read_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.id.in_(
            select(NotificationRecipient.notification_id).where(
                NotificationRecipient.user_id == current_user.id,
                NotificationRecipient.delivery_status == "read",
            )
        )).where(Notification.status != NotificationStatusEnum.pending)
    )
    read_count = read_result.scalar() or 0
    read_rate = round((read_count / total * 100), 1) if total > 0 else 0

    # By priority (excludes pending)
    priority_result = await db.execute(
        select(Notification.priority, func.count(Notification.id))
        .where(Notification.id.in_(
            select(NotificationRecipient.notification_id).where(
                NotificationRecipient.user_id == current_user.id
            )
        ))
        .where(Notification.status != NotificationStatusEnum.pending)
        .group_by(Notification.priority)
    )
    by_priority = {row[0]: row[1] for row in priority_result.all()}

    # Last 7 days activity (excludes pending)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    daily_result = await db.execute(
        select(
            func.date(Notification.created_at).label('date'),
            func.count(Notification.id).label('count')
        )
        .where(Notification.id.in_(
            select(NotificationRecipient.notification_id).where(
                NotificationRecipient.user_id == current_user.id
            )
        ))
        .where(Notification.created_at >= seven_days_ago)
        .where(Notification.status != NotificationStatusEnum.pending)
        .group_by(func.date(Notification.created_at))
        .order_by(func.date(Notification.created_at))
    )
    daily = {str(row[0]): row[1] for row in daily_result.all()}

    return {
        "unread_count": unread_count,
        "total": total,
        "read_count": read_count,
        "read_rate": read_rate,
        "by_priority": by_priority,
        "daily_last_7_days": daily,
    }


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
