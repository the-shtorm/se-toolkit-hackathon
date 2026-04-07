import { useEffect, useRef, useState, useCallback } from 'react';
import type { Notification, WSMessage } from '../types';
import { getWsToken } from '../api/ws';

type WebSocketStatus = 'connecting' | 'open' | 'closed' | 'error';

interface UseWebSocketOptions {
  onNotification?: (notification: Notification) => void;
  onStatusChange?: (status: WebSocketStatus) => void;
  enabled?: boolean;
}

const HEARTBEAT_INTERVAL = 30_000; // 30 seconds
const RECONNECT_BASE_DELAY = 1_000;
const RECONNECT_MAX_DELAY = 30_000;

export function useWebSocket({
  onNotification,
  onStatusChange,
  enabled = true,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<WebSocketStatus>('closed');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempt = useRef(0);
  const heartbeatTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const cleanup = useCallback(() => {
    if (heartbeatTimer.current) {
      clearInterval(heartbeatTimer.current);
      heartbeatTimer.current = null;
    }
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onclose = null; // Prevent reconnect on manual close
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(async () => {
    if (!enabled) return;

    cleanup();

    setStatus('connecting');
    onStatusChange?.('connecting');

    // Get auth token for WebSocket
    const token = await getWsToken();
    if (!token) {
      setStatus('error');
      onStatusChange?.('error');
      return;
    }

    // Use Vite dev server proxy (same origin, cookie works correctly)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/notifications?token=${token}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('open');
      onStatusChange?.('open');
      reconnectAttempt.current = 0;

      // Start heartbeat
      heartbeatTimer.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, HEARTBEAT_INTERVAL);
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const message: WSMessage = JSON.parse(event.data);

        if (message.type === 'ping') {
          ws.send(JSON.stringify({ type: 'pong' }));
          return;
        }

        if (message.type === 'notification:new' && message.data && 'id' in message.data) {
          onNotification?.(message.data as Notification);
        }

        if (message.type === 'notification:read' && message.data && 'id' in message.data) {
          onNotification?.(message.data as Notification);
        }
      } catch {
        // Ignore parse errors
      }
    };

    ws.onclose = () => {
      setStatus('closed');
      onStatusChange?.('closed');

      if (heartbeatTimer.current) {
        clearInterval(heartbeatTimer.current);
        heartbeatTimer.current = null;
      }

      // Reconnect with exponential backoff
      if (enabled) {
        const delay = Math.min(
          RECONNECT_BASE_DELAY * Math.pow(2, reconnectAttempt.current),
          RECONNECT_MAX_DELAY
        );
        reconnectAttempt.current += 1;

        reconnectTimer.current = setTimeout(() => {
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      setStatus('error');
      onStatusChange?.('error');
    };
  }, [enabled, onNotification, onStatusChange, cleanup]);

  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      cleanup();
    };
  }, [enabled, connect, cleanup]);

  return { status, reconnect: connect, disconnect: cleanup };
}
