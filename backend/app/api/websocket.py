"""WebSocket API endpoint for real-time notifications."""
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Cookie, Query

from app.core.websocket import manager
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/notifications")
async def websocket_endpoint(
    websocket: WebSocket,
    access_token: str | None = Cookie(None, alias="access_token"),
    token: str | None = Query(None, alias="token"),
):
    """
    WebSocket endpoint for real-time notification streaming.

    Authenticate via HTTPOnly cookie (access_token) or query param (token).
    Once connected, the client will receive:
    - "ping" messages for heartbeat (client should respond with "pong")
    - "notification:new" messages when new notifications arrive
    - "notification:read" messages when a notification is marked as read
    """
    # Authenticate: try cookie first, then query param
    auth_token = access_token or token
    if not auth_token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    payload = decode_access_token(auth_token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    user_id_str = payload.get("sub")
    if user_id_str is None:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        await websocket.close(code=4001, reason="Invalid user ID in token")
        return

    # Connect
    await manager.connect(websocket, user_id)

    try:
        # Handle incoming messages (pong responses, etc.)
        while True:
            data = await websocket.receive_json()

            # Handle pong response from client
            if data.get("type") == "pong":
                logger.debug(f"Received pong from user {user_id}")
                continue

            # Handle client-side messages
            msg_type = data.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        await manager.disconnect(websocket, user_id)
