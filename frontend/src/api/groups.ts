import apiClient from './client';
import type {
  GroupCreate,
  GroupUpdate,
  GroupResponse,
  GroupDetailResponse,
  GroupListResponse,
  AddMemberRequest,
  GroupMemberResponse,
} from '../types';

export async function getGroups(page = 1, pageSize = 20): Promise<GroupListResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  const { data } = await apiClient.get<GroupListResponse>(`/groups?${params}`);
  return data;
}

export async function getGroup(id: string): Promise<GroupDetailResponse> {
  const { data } = await apiClient.get<GroupDetailResponse>(`/groups/${id}`);
  return data;
}

export async function createGroup(payload: GroupCreate): Promise<GroupResponse> {
  const { data } = await apiClient.post<GroupResponse>('/groups', payload);
  return data;
}

export async function updateGroup(id: string, payload: GroupUpdate): Promise<GroupResponse> {
  const { data } = await apiClient.put<GroupResponse>(`/groups/${id}`, payload);
  return data;
}

export async function deleteGroup(id: string): Promise<void> {
  await apiClient.delete(`/groups/${id}`);
}

export async function addMember(groupId: string, payload: AddMemberRequest): Promise<GroupMemberResponse> {
  const { data } = await apiClient.post<GroupMemberResponse>(`/groups/${groupId}/members`, payload);
  return data;
}

export async function removeMember(groupId: string, userId: string): Promise<void> {
  await apiClient.delete(`/groups/${groupId}/members/${userId}`);
}
