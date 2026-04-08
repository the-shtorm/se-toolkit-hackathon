import apiClient from './client';
import type {
  Notification,
  NotificationListResponse,
  NotificationCreate,
} from '../types';

export async function getNotifications(
  page = 1,
  pageSize = 20,
  statusFilter?: string
): Promise<NotificationListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    ...(statusFilter ? { status_filter: statusFilter } : {}),
  });
  const { data } = await apiClient.get<NotificationListResponse>(
    `/notifications?${params}`
  );
  return data;
}

export async function getNotification(id: string): Promise<Notification> {
  const { data } = await apiClient.get<Notification>(`/notifications/${id}`);
  return data;
}

export async function createNotification(
  payload: NotificationCreate
): Promise<Notification> {
  const { data } = await apiClient.post<Notification>('/notifications', payload);
  return data;
}

export async function markAsRead(id: string): Promise<Notification> {
  const { data } = await apiClient.put<Notification>(
    `/notifications/${id}/read`
  );
  return data;
}

export async function markAllAsRead(): Promise<{
  message: string;
  count: number;
}> {
  const { data } = await apiClient.put<Notification>('/notifications/read-all');
  return data;
}

export async function getStats(): Promise<{ unread_count: number }> {
  const { data } = await apiClient.get<Notification>('/notifications/stats');
  return data;
}
