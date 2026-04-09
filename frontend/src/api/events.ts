import apiClient from './client';
import type {
  EventCreate,
  EventUpdate,
  EventResponse,
  EventListResponse,
} from '../types';

export async function getEvents(page = 1, pageSize = 20): Promise<EventListResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  const { data } = await apiClient.get<EventListResponse>(`/events?${params}`);
  return data;
}

export async function createEvent(payload: EventCreate): Promise<EventResponse> {
  const { data } = await apiClient.post<EventResponse>('/events', payload);
  return data;
}

export async function updateEvent(id: string, payload: EventUpdate): Promise<EventResponse> {
  const { data } = await apiClient.put<EventResponse>(`/events/${id}`, payload);
  return data;
}

export async function deleteEvent(id: string): Promise<void> {
  await apiClient.delete(`/events/${id}`);
}
