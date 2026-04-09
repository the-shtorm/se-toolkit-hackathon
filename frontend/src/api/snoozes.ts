import apiClient from './client';
import type {
  SnoozeCreate,
  SnoozeResponse,
  SnoozeOptions,
} from '../types';

export async function snoozeNotification(payload: SnoozeCreate): Promise<SnoozeResponse> {
  const { data } = await apiClient.post<SnoozeResponse>('/snoozes', payload);
  return data;
}

export async function quickSnooze(notificationId: string, duration: string): Promise<SnoozeResponse> {
  const { data } = await apiClient.post<SnoozeResponse>('/snoozes/quick', null, {
    params: { notification_id: notificationId, duration },
  });
  return data;
}

export async function unsnoozeNotification(notificationId: string): Promise<void> {
  await apiClient.delete(`/snoozes/${notificationId}`);
}

export async function getSnoozes(): Promise<SnoozeResponse[]> {
  const { data } = await apiClient.get<SnoozeResponse[]>('/snoozes');
  return data;
}

export async function getSnoozeOptions(): Promise<SnoozeOptions> {
  const { data } = await apiClient.get<SnoozeOptions>('/snoozes/options');
  return data;
}
