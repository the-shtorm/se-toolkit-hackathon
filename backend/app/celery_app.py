"""Celery application for scheduled tasks."""
import os
from celery import Celery

# Get Redis URL from env or default
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

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
    This task is called by Celery at the scheduled time.
    It marks the notification as 'sent' and broadcasts via WebSocket.
    
    Uses synchronous psycopg2 queries (not asyncpg) because Celery workers
    are synchronous and don't play well with asyncio.run().
    """
    import uuid
    import json
    from datetime import datetime, timezone
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Build synchronous database URL
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/notifications")
    # Convert asyncpg URL to psycopg2 format
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get notification
        cur.execute(
            "SELECT id, title, message, priority, status, created_by, group_id, created_at, sent_at, read_at "
            "FROM notifications WHERE id = %s",
            (str(uuid.UUID(notification_id)),)
        )
        notification = cur.fetchone()
        
        if not notification:
            conn.close()
            return {"status": "error", "message": "Notification not found"}
        
        # Update status to sent
        now = datetime.now(timezone.utc)
        cur.execute(
            "UPDATE notifications SET status = 'sent', sent_at = %s WHERE id = %s",
            (now, str(uuid.UUID(notification_id)))
        )
        conn.commit()
        
        # Get recipients
        cur.execute(
            "SELECT user_id FROM notification_recipients WHERE notification_id = %s",
            (str(uuid.UUID(notification_id)),)
        )
        recipients = cur.fetchall()
        conn.close()
        
        # Broadcast via HTTP endpoint (synchronous)
        import requests
        notif_data = {
            "id": str(notification["id"]),
            "title": notification["title"],
            "message": notification["message"],
            "priority": notification["priority"],
            "status": "sent",
            "created_by": str(notification["created_by"]),
            "group_id": str(notification["group_id"]) if notification["group_id"] else None,
            "created_at": notification["created_at"].isoformat() if notification["created_at"] else None,
            "sent_at": now.isoformat(),
            "read_at": None,
            "group_name": None,
        }
        
        payload = {
            "type": "notification:new",
            "data": {**notif_data, "scheduled": True},
        }
        
        # Send to each recipient via backend's broadcast endpoint
        for recipient in recipients:
            user_id = str(recipient["user_id"])
            try:
                requests.post(
                    "http://backend:8000/api/v1/notifications/broadcast",
                    json={"user_id": user_id, "payload": payload},
                    timeout=5
                )
            except Exception as e:
                print(f"Failed to broadcast to user {user_id}: {e}")
        
        return {"status": "sent", "notification_id": notification_id}
        
    except Exception as exc:
        raise self.retry(exc=exc)
