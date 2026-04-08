"""Notification snooze API endpoints."""
from uuid import UUID
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser
from app.models.snooze import NotificationSnooze
from app.models.notification import Notification, NotificationStatusEnum
from app.schemas.snooze import SnoozeCreate, SnoozeResponse, QuickSnoozeOptions

router = APIRouter(prefix="/snoozes", tags=["Snoozes"])


# Quick snooze duration mappings
QUICK_SNOOZE_MAP = {
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
    "1w": timedelta(weeks=1),
}


@router.post(
    "",
    response_model=SnoozeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Snooze a notification",
)
async def snooze_notification(
    snooze_data: SnoozeCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Snooze a notification until a specific time."""
    # Verify notification belongs to user
    notif_result = await db.execute(
        select(Notification).where(Notification.id == snooze_data.notification_id)
    )
    notification = notif_result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Create snooze
    snooze = NotificationSnooze(
        notification_id=snooze_data.notification_id,
        user_id=current_user.id,
        snoozed_until=snooze_data.snoozed_until,
    )
    db.add(snooze)
    await db.commit()
    await db.refresh(snooze)
    return SnoozeResponse.model_validate(snooze)


@router.post(
    "/quick",
    response_model=SnoozeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Quick snooze with preset durations",
)
async def quick_snooze(
    notification_id: str,
    duration: str = Query(..., pattern="^(15m|1h|4h|1d|1w)$"),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Snooze notification with a preset duration."""
    # Verify notification exists
    notif_result = await db.execute(
        select(Notification).where(Notification.id == UUID(notification_id))
    )
    notification = notif_result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Calculate snooze time
    delta = QUICK_SNOOZE_MAP[duration]
    snoozed_until = datetime.now(timezone.utc) + delta

    snooze = NotificationSnooze(
        notification_id=UUID(notification_id),
        user_id=current_user.id,
        snoozed_until=snoozed_until,
    )
    db.add(snooze)
    await db.commit()
    await db.refresh(snooze)
    return SnoozeResponse.model_validate(snooze)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Un-snooze a notification",
)
async def unsnooze_notification(
    notification_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Remove snooze from a notification (wake it up now)."""
    result = await db.execute(
        select(NotificationSnooze).where(
            NotificationSnooze.notification_id == UUID(notification_id),
            NotificationSnooze.user_id == current_user.id,
        )
    )
    snooze = result.scalar_one_or_none()
    if snooze:
        await db.delete(snooze)
        await db.commit()


@router.get(
    "",
    response_model=list[SnoozeResponse],
    summary="List active snoozes",
)
async def list_snoozes(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all active snoozes for the current user."""
    result = await db.execute(
        select(NotificationSnooze)
        .where(NotificationSnooze.user_id == current_user.id)
        .order_by(NotificationSnooze.snoozed_until)
    )
    snoozes = result.scalars().all()
    return [SnoozeResponse.model_validate(s) for s in snoozes]


@router.get(
    "/options",
    response_model=QuickSnoozeOptions,
    summary="Get quick snooze options",
)
async def get_snooze_options():
    """Get available quick snooze options."""
    return QuickSnoozeOptions()
