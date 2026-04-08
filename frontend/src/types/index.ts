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
  group_id: string | null;
  group_name: string | null;
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

export type MemberRole = 'admin' | 'member';

export interface GroupMember {
  id: string;
  user_id: string;
  username: string;
  email: string;
  role: MemberRole;
  joined_at: string | null;
}

export interface GroupCreate {
  name: string;
  description?: string;
}

export interface GroupUpdate {
  name?: string;
  description?: string;
}

export interface GroupResponse {
  id: string;
  name: string;
  description: string | null;
  created_by: string;
  created_at: string | null;
  updated_at: string | null;
  member_count: number;
}

export interface GroupDetailResponse extends GroupResponse {
  members: GroupMember[];
}

export interface AddMemberRequest {
  user_id: string;
  role: MemberRole;
}

export interface GroupListResponse {
  items: GroupResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface GroupMemberResponse extends GroupMember {}

export interface EventCreate {
  name: string;
  description?: string;
  title: string;
  message: string;
  priority?: string;
  group_id?: string;
  scheduled_at?: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
}

export interface EventUpdate {
  name?: string;
  description?: string;
  title?: string;
  message?: string;
  priority?: string;
  group_id?: string;
  scheduled_at?: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
}

export interface EventResponse {
  id: string;
  name: string;
  description: string | null;
  title: string;
  message: string;
  priority: string;
  created_by: string;
  group_id: string | null;
  scheduled_at: string | null;
  is_recurring: boolean;
  recurrence_rule: string | null;
  notification_id: string | null;
  created_at: string | null;
}

export interface EventListResponse {
  items: EventResponse[];
  total: number;
  page: number;
  page_size: number;
}

// Templates
export interface TemplateCreate {
  name: string;
  title_template: string;
  message_template: string;
  priority?: string;
  category?: string;
  is_public?: boolean;
}

export interface TemplateUpdate {
  name?: string;
  title_template?: string;
  message_template?: string;
  priority?: string;
  category?: string;
  is_public?: boolean;
}

export interface TemplateResponse {
  id: string;
  name: string;
  title_template: string;
  message_template: string;
  priority: string;
  category: string | null;
  created_by: string;
  is_public: boolean;
  created_at: string | null;
}

export interface TemplateListResponse {
  items: TemplateResponse[];
  total: number;
  page: number;
  page_size: number;
}

// User Preferences
export interface PreferencesCreate {
  web_enabled?: boolean;
  email_enabled?: boolean;
  sms_enabled?: boolean;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
  max_daily_notifications?: number;
  timezone?: string;
  digest_enabled?: boolean;
  digest_frequency?: string | null;
}

export interface PreferencesUpdate {
  web_enabled?: boolean;
  email_enabled?: boolean;
  sms_enabled?: boolean;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
  max_daily_notifications?: number;
  timezone?: string;
  digest_enabled?: boolean;
  digest_frequency?: string | null;
}

export interface PreferencesResponse {
  id: string;
  user_id: string;
  web_enabled: boolean;
  email_enabled: boolean;
  sms_enabled: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  max_daily_notifications: number;
  timezone: string;
  digest_enabled: boolean;
  digest_frequency: string | null;
  created_at: string | null;
  updated_at: string | null;
}
