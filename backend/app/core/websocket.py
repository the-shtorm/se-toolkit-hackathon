"""WebSocket connection manager for real-time notifications."""
import asyncio
import logging
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for authenticated users."""

    def __init__(self) -> None:
        # user_id -> set of active WebSocket connections
        self._connections: Dict[UUID, Set[WebSocket]] = {}
        self._ping_interval = 30  # seconds

    async def connect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Accept a new WebSocket connection for a user."""
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)
        logger.info(f"WebSocket connected for user {user_id} (total: {len(self._connections[user_id])})")

    async def disconnect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Remove a WebSocket connection for a user."""
        user_connections = self._connections.get(user_id)
        if user_connections:
            user_connections.discard(websocket)
            if not user_connections:
                del self._connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id} (remaining: {len(self._connections.get(user_id, set()))})")

    async def send_personal(self, message: dict, user_id: UUID) -> None:
        """Send a message to all WebSocket connections for a specific user."""
        connections = self._connections.get(user_id, set()).copy()
        if not connections:
            return

        failed: Set[WebSocket] = set()
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                failed.add(ws)

        # Remove failed connections
        for ws in failed:
            connections.discard(ws)
            if not connections:
                self._connections.pop(user_id, None)

    async def send_personal_text(self, message: str, user_id: UUID) -> None:
        """Send a text message to all WebSocket connections for a specific user."""
        connections = self._connections.get(user_id, set()).copy()
        if not connections:
            return

        failed: Set[WebSocket] = set()
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                failed.add(ws)

        for ws in failed:
            connections.discard(ws)
            if not connections:
                self._connections.pop(user_id, None)

    async def handle_ping_pong(self, websocket: WebSocket) -> None:
        """Handle ping/pong heartbeat for a WebSocket connection."""
        while True:
            await asyncio.sleep(self._ping_interval)
            try:
                await websocket.send_json({"type": "ping"})
                # Wait for pong response with timeout
                await asyncio.wait_for(websocket.receive_json(), timeout=10)
            except (asyncio.TimeoutError, Exception):
                break

    def get_active_connections(self, user_id: UUID) -> int:
        """Get the number of active connections for a user."""
        return len(self._connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """Get the total number of active WebSocket connections."""
        return sum(len(conns) for conns in self._connections.values())


# Global instance
manager = ConnectionManager()
