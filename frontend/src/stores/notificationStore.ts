import { create } from 'zustand';
import type { Notification } from '../types';
import * as api from '../api/notifications';

interface NotificationState {
  notifications: Notification[];
  total: number;
  page: number;
  pageSize: number;
  statusFilter: string | null;
  unreadCount: number;
  isLoading: boolean;

  // Actions
  fetchNotifications: (page?: number) => Promise<void>;
  fetchStats: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  addNotification: (notification: Notification) => void;
  updateNotification: (notification: Notification) => void;
  setStatusFilter: (filter: string | null) => void;
  setPage: (page: number) => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  total: 0,
  page: 1,
  pageSize: 20,
  statusFilter: null,
  unreadCount: 0,
  isLoading: false,

  fetchNotifications: async (page) => {
    const state = get();
    const targetPage = page ?? state.page;
    set({ isLoading: true });
    try {
      const result = await api.getNotifications(
        targetPage,
        state.pageSize,
        state.statusFilter ?? undefined
      );
      set({
        notifications: result.items,
        total: result.total,
        page: result.page,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false });
    }
  },

  fetchStats: async () => {
    try {
      const stats = await api.getStats();
      set({ unreadCount: stats.unread_count });
    } catch {
      // Ignore
    }
  },

  markAsRead: async (id) => {
    try {
      const updated = await api.markAsRead(id);
      get().updateNotification(updated);
      await get().fetchStats();
    } catch {
      // Ignore
    }
  },

  markAllAsRead: async () => {
    try {
      await api.markAllAsRead();
      await get().fetchNotifications();
      await get().fetchStats();
    } catch {
      // Ignore
    }
  },

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      total: state.total + 1,
    }));
  },

  updateNotification: (updated) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === updated.id ? updated : n
      ),
    }));
  },

  setStatusFilter: (filter) => {
    set({ statusFilter: filter, page: 1 });
    get().fetchNotifications(1);
  },

  setPage: (page) => {
    set({ page });
    get().fetchNotifications(page);
  },
}));
