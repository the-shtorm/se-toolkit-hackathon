export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserResponse extends User {}

export type Priority = 'low' | 'medium' | 'high' | 'critical';
export type NotificationStatus = 'pending' | 'sent' | 'delivered' | 'read' | 'failed';

export interface Notification {
  id: string;
  title: string;
  message: string;
  priority: Priority;
  status: NotificationStatus;
  created_by: string;
  created_at: string | null;
  sent_at: string | null;
  read_at: string | null;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  page_size: number;
}

export interface NotificationCreate {
  title: string;
  message: string;
  priority: Priority;
}

export interface WSMessage {
  type: string;
  data: Notification | Record<string, unknown>;
}
