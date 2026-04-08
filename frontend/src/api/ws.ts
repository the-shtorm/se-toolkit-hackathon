import apiClient from './client';

/**
 * Get a fresh authentication token for WebSocket connections.
 * The backend can't read HTTP-only cookies from the frontend JS,
 * so we use a dedicated endpoint that returns the token for WS auth.
 */
export async function getWsToken(): Promise<string | null> {
  try {
    const { data } = await apiClient.get<{ token: string }>('/auth/ws-token');
    return data.token;
  } catch {
    return null;
  }
}
