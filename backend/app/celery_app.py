"""Celery application for scheduled tasks."""
import os
from celery import Celery

# Get Redis URL from env or default
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/notifications")

celery_app = Celery(
    "notification_tasks",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_notification(self, notification_id: str) -> dict:
    """
    Send a scheduled notification.
    This task is called by Celery Beat at the scheduled time.
    It marks the notification as 'sent' and broadcasts via WebSocket.
    """
    import asyncio
    import uuid
    from datetime import datetime, timezone
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.database import async_session_factory
    from app.models.notification import Notification, NotificationRecipient, NotificationStatusEnum, DeliveryStatusEnum
    from app.core.websocket import manager

    async def _send():
        async with async_session_factory() as db:
            notif_result = await db.execute(
                select(Notification).where(Notification.id == uuid.UUID(notification_id))
            )
            notification = notif_result.scalar_one_or_none()
            if not notification:
                return {"status": "error", "message": "Notification not found"}

            notification.status = NotificationStatusEnum.sent
            notification.sent_at = datetime.now(timezone.utc)
            await db.commit()

            # Broadcast via WebSocket
            recipient_ids_result = await db.execute(
                select(NotificationRecipient.user_id).where(
                    NotificationRecipient.notification_id == notification.id
                )
            )
            recipient_ids = [row[0] for row in recipient_ids_result.all()]

            from app.schemas.notification import NotificationResponse
            payload = {
                "type": "notification:new",
                "data": {
                    **NotificationResponse.model_validate(notification).model_dump(mode="json"),
                    "scheduled": True,
                },
            }
            for user_id in recipient_ids:
                if manager.get_active_connections(user_id) > 0:
                    await manager.send_personal(payload, user_id)

            return {"status": "sent", "notification_id": notification_id}

    try:
        return asyncio.run(_send())
    except Exception as exc:
        raise self.retry(exc=exc)
