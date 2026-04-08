import apiClient from './client';
import type {
  PreferencesCreate,
  PreferencesUpdate,
  PreferencesResponse,
} from '../types';

export async function getPreferences(): Promise<PreferencesResponse> {
  const { data } = await apiClient.get<PreferencesResponse>('/preferences');
  return data;
}

export async function updatePreferences(payload: PreferencesUpdate): Promise<PreferencesResponse> {
  const { data } = await apiClient.put<PreferencesResponse>('/preferences', payload);
  return data;
}

export async function createPreferences(payload: PreferencesCreate): Promise<PreferencesResponse> {
  const { data } = await apiClient.post<PreferencesResponse>('/preferences', payload);
  return data;
}
