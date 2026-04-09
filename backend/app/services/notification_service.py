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
from app.models.group import GroupMember
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

    # Fetch group name if applicable
    group_name = None
    if notification.group_id:
        from app.models.group import NotificationGroup
        grp_result = await db.execute(
            select(NotificationGroup.name).where(NotificationGroup.id == notification.group_id)
        )
        grp = grp_result.scalar_one_or_none()
        if grp:
            group_name = grp

    payload = {
        "type": f"notification:{event}",
        "data": {
            **NotificationResponse.model_validate(notification).model_dump(mode="json"),
            "group_name": group_name,
        },
    }

    for user_id in recipient_ids:
        if manager.get_active_connections(user_id) > 0:
            await manager.send_personal(payload, user_id)


async def create_notification(
    db: AsyncSession,
    notification_data: NotificationCreate,
    created_by: UUID,
) -> Notification:
    """Create a notification. If group_id is set, adds all group members as recipients."""
    notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        priority=notification_data.priority,
        status=NotificationStatusEnum.sent,
        created_by=created_by,
        group_id=notification_data.group_id,
    )

    db.add(notification)
    await db.flush()

    if notification_data.group_id:
        # Add all group members as recipients
        members_result = await db.execute(
            select(GroupMember.user_id).where(GroupMember.group_id == notification_data.group_id)
        )
        member_ids = [row[0] for row in members_result.all()]

        for member_id in member_ids:
            recipient = NotificationRecipient(
                notification_id=notification.id,
                user_id=member_id,
                delivery_status=DeliveryStatusEnum.delivered,
                delivered_at=datetime.now(timezone.utc),
            )
            db.add(recipient)
    else:
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
    group_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Notification], int]:
    """Get paginated list of notifications for a user. Excludes 'pending' by default."""
    import uuid
    base_query = (
        select(Notification)
        .join(NotificationRecipient)
        .where(NotificationRecipient.user_id == user_id)
    )

    # Exclude pending notifications unless explicitly requested
    if status_filter:
        base_query = base_query.where(Notification.status == status_filter)
    else:
        base_query = base_query.where(Notification.status != NotificationStatusEnum.pending)

    if group_id:
        base_query = base_query.where(Notification.group_id == uuid.UUID(group_id))

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    # Enrich with group names
    enriched = []
    for n in notifications:
        gname = None
        if n.group_id:
            from app.models.group import NotificationGroup
            grp = await db.execute(
                select(NotificationGroup.name).where(NotificationGroup.id == n.group_id)
            )
            g = grp.scalar_one_or_none()
            if g:
                gname = g
        enriched.append((n, gname))

    return enriched, total


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
