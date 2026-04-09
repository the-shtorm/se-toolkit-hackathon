"""Internal broadcast endpoint for Celery task notifications."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.websocket import manager

router = APIRouter(prefix="/notifications", tags=["Internal"])


class BroadcastRequest(BaseModel):
    user_id: str
    payload: dict


@router.post(
    "/broadcast",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,  # Hide from public docs
)
async def broadcast_notification(request: BroadcastRequest):
    """
    Internal endpoint for broadcasting notifications.
    Called by Celery workers when a scheduled notification fires.
    """
    try:
        user_id = UUID(request.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Broadcast via WebSocket
    if manager.get_active_connections(user_id) > 0:
        await manager.send_personal(request.payload, user_id)
    # Always return 204 even if no active connections
    # (notification is still marked as 'sent' in the database)
