"""Events API endpoints for scheduled notifications."""
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser, CurrentDB
from app.models.event import Event
from app.models.notification import Notification, NotificationRecipient, NotificationStatusEnum, DeliveryStatusEnum
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.celery_app import send_scheduled_notification

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a scheduled event",
)
async def create_event(
    event_data: EventCreate,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Create a scheduled event. If scheduled_at is in the future, a Celery task is queued."""
    event = Event(
        name=event_data.name,
        description=event_data.description,
        title=event_data.title,
        message=event_data.message,
        priority=event_data.priority,
        created_by=current_user.id,
        group_id=event_data.group_id,
        scheduled_at=event_data.scheduled_at,
        is_recurring=event_data.is_recurring,
        recurrence_rule=event_data.recurrence_rule,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    # If scheduled for the future, queue a Celery task
    if event.scheduled_at and event.scheduled_at > datetime.now(timezone.utc):
        # Create the notification in advance as 'pending'
        notification = Notification(
            title=event.title,
            message=event.message,
            priority=event.priority,
            status=NotificationStatusEnum.pending,
            created_by=current_user.id,
            group_id=event.group_id,
        )
        db.add(notification)
        await db.flush()

        # Add recipients
        if event.group_id:
            from app.models.group import GroupMember
            members_result = await db.execute(
                select(GroupMember.user_id).where(GroupMember.group_id == event.group_id)
            )
            member_ids = [row[0] for row in members_result.all()]
            for member_id in member_ids:
                db.add(NotificationRecipient(
                    notification_id=notification.id,
                    user_id=member_id,
                    delivery_status=DeliveryStatusEnum.pending,
                ))
        else:
            db.add(NotificationRecipient(
                notification_id=notification.id,
                user_id=current_user.id,
                delivery_status=DeliveryStatusEnum.pending,
            ))

        event.notification_id = notification.id
        await db.commit()
        await db.refresh(event)

        # Schedule Celery task
        delay_seconds = (event.scheduled_at - datetime.now(timezone.utc)).total_seconds()
        send_scheduled_notification.apply_async(
            args=[str(notification.id)],
            countdown=max(int(delay_seconds), 0),
        )

    return EventResponse.model_validate(event)


@router.get(
    "",
    response_model=EventListResponse,
    summary="List events",
)
async def list_events(
    current_user: CurrentUser,
    db: CurrentDB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all events created by the current user."""
    base = select(Event).where(Event.created_by == current_user.id)

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    events_q = base.order_by(Event.scheduled_at.desc().nullslast()).offset(offset).limit(page_size)
    events = (await db.execute(events_q)).scalars().all()

    return EventListResponse(
        items=[EventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event details",
)
async def get_event(
    event_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Get event details."""
    event = await db.get(Event, UUID(event_id))
    if not event or event.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.model_validate(event)


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update event",
)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Update a scheduled event."""
    event = await db.get(Event, UUID(event_id))
    if not event or event.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return EventResponse.model_validate(event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete event",
)
async def delete_event(
    event_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Delete a scheduled event."""
    event = await db.get(Event, UUID(event_id))
    if not event or event.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Event not found")

    await db.delete(event)
    await db.commit()
