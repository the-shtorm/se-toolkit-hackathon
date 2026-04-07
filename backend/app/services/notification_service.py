"""Notification business logic."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import (
    Notification,
    NotificationRecipient,
    PriorityEnum,
    NotificationStatusEnum,
    DeliveryStatusEnum,
)
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.core.websocket import manager


async def _broadcast_notification(db: AsyncSession, notification: Notification, event: str) -> None:
    """Broadcast notification event to all recipients via WebSocket."""
    result = await db.execute(
        select(NotificationRecipient.user_id).where(
            NotificationRecipient.notification_id == notification.id
        )
    )
    recipient_ids = [row[0] for row in result.all()]

    payload = {
        "type": f"notification:{event}",
        "data": NotificationResponse.model_validate(notification).model_dump(mode="json"),
    }

    for user_id in recipient_ids:
        if manager.get_active_connections(user_id) > 0:
            await manager.send_personal(payload, user_id)


async def create_notification(
    db: AsyncSession,
    notification_data: NotificationCreate,
    created_by: UUID,
) -> Notification:
    """Create a notification and add the creator as recipient."""
    notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        priority=notification_data.priority,
        status=NotificationStatusEnum.sent,
        created_by=created_by,
    )

    db.add(notification)
    await db.flush()

    # Add creator as recipient
    recipient = NotificationRecipient(
        notification_id=notification.id,
        user_id=created_by,
        delivery_status=DeliveryStatusEnum.delivered,
        delivered_at=datetime.now(timezone.utc),
    )
    db.add(recipient)

    await db.commit()
    await db.refresh(notification)

    # Broadcast to WebSocket
    await _broadcast_notification(db, notification, "new")

    return notification


async def get_notification_by_id(
    db: AsyncSession,
    notification_id: UUID,
    user_id: UUID,
) -> Notification | None:
    """Get a specific notification if user is a recipient."""
    query = (
        select(Notification)
        .join(NotificationRecipient)
        .where(
            Notification.id == notification_id,
            NotificationRecipient.user_id == user_id,
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_notifications(
    db: AsyncSession,
    user_id: UUID,
    status_filter: NotificationStatusEnum | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Notification], int]:
    """Get paginated list of notifications for a user."""
    base_query = (
        select(Notification)
        .join(NotificationRecipient)
        .where(NotificationRecipient.user_id == user_id)
    )

    if status_filter:
        base_query = base_query.where(Notification.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return list(notifications), total


async def mark_notification_as_read(
    db: AsyncSession,
    notification_id: UUID,
    user_id: UUID,
) -> Notification | None:
    """Mark a notification as read for a specific user."""
    notification = await get_notification_by_id(db, notification_id, user_id)
    if notification is None:
        return None

    notification.status = NotificationStatusEnum.read
    notification.read_at = datetime.now(timezone.utc)

    # Also update recipient status
    recipient_query = select(NotificationRecipient).where(
        NotificationRecipient.notification_id == notification_id,
        NotificationRecipient.user_id == user_id,
    )
    result = await db.execute(recipient_query)
    recipient = result.scalar_one_or_none()

    if recipient:
        recipient.delivery_status = DeliveryStatusEnum.read

    await db.commit()
    await db.refresh(notification)

    # Broadcast to WebSocket
    await _broadcast_notification(db, notification, "read")

    return notification


async def mark_all_as_read(
    db: AsyncSession,
    user_id: UUID,
) -> int:
    """Mark all unread notifications as read for a user."""
    recipient_query = select(NotificationRecipient).where(
        NotificationRecipient.user_id == user_id,
        NotificationRecipient.delivery_status != DeliveryStatusEnum.read,
    )
    result = await db.execute(recipient_query)
    recipients = result.scalars().all()

    notification_ids = []
    for recipient in recipients:
        notification_ids.append(recipient.notification_id)
        recipient.delivery_status = DeliveryStatusEnum.read

    if notification_ids:
        await db.execute(
            select(Notification)
            .where(Notification.id.in_(notification_ids))
        )
        update_stmt = (
            Notification.__table__
            .update()
            .where(Notification.id.in_(notification_ids))
            .values(
                status=NotificationStatusEnum.read,
                read_at=datetime.now(timezone.utc),
            )
        )
        await db.execute(update_stmt)

    await db.commit()
    return len(recipients)


async def get_unread_count(
    db: AsyncSession,
    user_id: UUID,
) -> int:
    """Get count of unread notifications for a user."""
    query = (
        select(func.count(Notification.id))
        .join(NotificationRecipient)
        .where(
            NotificationRecipient.user_id == user_id,
            Notification.status != NotificationStatusEnum.read,
        )
    )
    result = await db.execute(query)
    return result.scalar() or 0
