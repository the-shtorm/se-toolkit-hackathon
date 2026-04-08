import apiClient from './client';
import type {
  TemplateCreate,
  TemplateUpdate,
  TemplateResponse,
  TemplateListResponse,
} from '../types';

export async function getTemplates(page = 1, pageSize = 20, category?: string): Promise<TemplateListResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (category) params.append('category', category);
  const { data } = await apiClient.get<TemplateListResponse>(`/templates?${params}`);
  return data;
}

export async function getTemplate(id: string): Promise<TemplateResponse> {
  const { data } = await apiClient.get<TemplateResponse>(`/templates/${id}`);
  return data;
}

export async function createTemplate(payload: TemplateCreate): Promise<TemplateResponse> {
  const { data } = await apiClient.post<TemplateResponse>('/templates', payload);
  return data;
}

export async function updateTemplate(id: string, payload: TemplateUpdate): Promise<TemplateResponse> {
  const { data } = await apiClient.put<TemplateResponse>(`/templates/${id}`, payload);
  return data;
}

export async function deleteTemplate(id: string): Promise<void> {
  await apiClient.delete(`/templates/${id}`);
}
