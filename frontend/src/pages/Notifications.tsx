import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useWebSocket } from '../hooks/useWebSocket';
import { useNotificationStore } from '../stores/notificationStore';
import * as snoozesApi from '../api/snoozes';
import type { Notification, SnoozeOption } from '../types';
import NavBar from '../components/NavBar';

const priorityColors: Record<string, string> = {
  low: 'bg-blue-100 text-blue-800 border-blue-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  critical: 'bg-red-100 text-red-800 border-red-200',
};

const filters = [
  { label: 'All', value: null },
  { label: 'Unread', value: 'sent' },
  { label: 'Read', value: 'read' },
];

export default function Dashboard() {
  const { user, logout } = useAuth();
  const {
    notifications,
    total,
    page,
    statusFilter,
    unreadCount,
    isLoading,
    fetchNotifications,
    fetchStats,
    markAsRead,
    markAllAsRead,
    addNotification,
    updateNotification,
    setStatusFilter,
    setPage,
  } = useNotificationStore();

  const [toast, setToast] = useState<Notification | null>(null);
  const [snoozeMenu, setSnoozeMenu] = useState<{ notifId: string; x: number; y: number } | null>(null);
  const [snoozeOptions, setSnoozeOptions] = useState<SnoozeOption[]>([]);

  // Handle new notification from WebSocket
  const handleNewNotification = useCallback(
    (notification: Notification) => {
      if (notification.status === 'read') {
        updateNotification(notification);
      } else {
        addNotification(notification);
        // Show toast
        setToast(notification);
        setTimeout(() => setToast(null), 5000);
      }
    },
    [addNotification, updateNotification]
  );

  // WebSocket hook
  const { status: wsStatus, reconnect } = useWebSocket({
    onNotification: handleNewNotification,
    enabled: true,
  });

  // Load snooze options
  useEffect(() => {
    snoozesApi.getSnoozeOptions().then((res) => setSnoozeOptions(res.options)).catch(() => {});
  }, []);

  // Handle quick snooze
  const handleQuickSnooze = async (notifId: string, duration: string) => {
    try {
      await snoozesApi.quickSnooze(notifId, duration);
      // Optimistically hide notification from list
      const opt = snoozeOptions.find((o) => o.value === duration);
      setToast({
        id: notifId,
        title: '⏰ Snoozed',
        message: `Notification snoozed until ${opt?.label || duration}`,
        priority: 'low',
        status: 'read',
        created_by: '',
        group_id: null,
        group_name: null,
        created_at: new Date().toISOString(),
        sent_at: null,
        read_at: null,
      } as Notification);
      setTimeout(() => setToast(null), 3000);
    } catch {
      setToast({
        id: notifId,
        title: '⚠️ Snooze Failed',
        message: 'Could not snooze notification',
        priority: 'high',
        status: 'sent',
        created_by: '',
        group_id: null,
        group_name: null,
        created_at: new Date().toISOString(),
        sent_at: null,
        read_at: null,
      } as Notification);
      setTimeout(() => setToast(null), 3000);
    }
    setSnoozeMenu(null);
  };

  // Close snooze menu on click outside
  useEffect(() => {
    const closeMenu = () => setSnoozeMenu(null);
    if (snoozeMenu) {
      document.addEventListener('click', closeMenu);
      return () => document.removeEventListener('click', closeMenu);
    }
  }, [snoozeMenu]);

  // Initial load
  useEffect(() => {
    fetchNotifications(1);
    fetchStats();
  }, []);

  const wsStatusIndicator = () => {
    const colors = {
      connecting: 'bg-yellow-400',
      open: 'bg-green-400',
      closed: 'bg-gray-400',
      error: 'bg-red-400',
    };
    return (
      <span className="flex items-center gap-1 text-xs text-gray-500" title={`WebSocket: ${wsStatus}`}>
        <span className={`w-2 h-2 rounded-full ${colors[wsStatus]}`}></span>
        {wsStatus === 'open' ? 'Live' : wsStatus}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 max-w-sm animate-slide-in">
          <div className="bg-white rounded-lg shadow-xl border-l-4 border-blue-500 p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-900">{toast.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{toast.message}</p>
                <span
                  className={`inline-block mt-2 px-2 py-0.5 text-xs font-medium rounded border ${
                    priorityColors[toast.priority]
                  }`}
                >
                  {toast.priority}
                </span>
              </div>
              <button
                onClick={() => setToast(null)}
                className="ml-4 text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <NavBar extra={
        <span className="flex items-center gap-1 text-xs text-gray-500" title={`WebSocket: ${wsStatus}`}>
          <span className={`w-2 h-2 rounded-full ${wsStatus === 'open' ? 'bg-green-400' : wsStatus === 'connecting' ? 'bg-yellow-400' : 'bg-gray-400'}`}></span>
          {wsStatus === 'open' ? 'Live' : wsStatus}
        </span>
      } />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats & Controls */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Notifications</h2>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  Mark all as read
                </button>
              )}
              <button
                onClick={reconnect}
                className="text-sm text-gray-500 hover:text-gray-700"
                title="Reconnect WebSocket"
              >
                ↻ Refresh connection
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-2">
            {filters.map((f) => (
              <button
                key={f.label}
                onClick={() => setStatusFilter(f.value)}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  (statusFilter === f.value) || (statusFilter === null && f.value === null)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Notification List */}
        <div className="bg-white rounded-lg shadow">
          {isLoading ? (
            <div className="p-8 text-center text-gray-500">Loading notifications...</div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No notifications found. Create one via the API!
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {notifications.map((notif) => (
                <li
                  key={notif.id}
                  className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${
                    notif.status === 'read' ? 'opacity-60' : ''
                  }`}
                  onClick={() => {
                    if (notif.status !== 'read') {
                      markAsRead(notif.id);
                    }
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-sm font-semibold text-gray-900">{notif.title}</h3>
                        {notif.group_name && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-indigo-100 text-indigo-800 border border-indigo-200">
                            👥 {notif.group_name}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span>
                          {new Date(notif.created_at!).toLocaleString()}
                        </span>
                        {notif.read_at && (
                          <span>• Read at {new Date(notif.read_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                    <span
                      className={`ml-4 px-2 py-1 text-xs font-medium rounded border whitespace-nowrap ${
                        priorityColors[notif.priority]
                      }`}
                    >
                      {notif.priority}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSnoozeMenu({ notifId: notif.id, x: e.clientX, y: e.clientY });
                      }}
                      className="ml-2 text-gray-400 hover:text-yellow-600 text-lg"
                      title="Snooze"
                    >
                      ⏰
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {/* Pagination */}
          {total > 20 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, total)} of {total}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page <= 1}
                  className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page * 20 >= total}
                  className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Snooze Menu Popup */}
      {snoozeMenu && (
        <div
          className="fixed z-50 bg-white rounded-lg shadow-xl border border-gray-200 p-3"
          style={{ top: snoozeMenu.y + 10, left: Math.min(snoozeMenu.x, window.innerWidth - 220) }}
          onClick={(e) => e.stopPropagation()}
        >
          <p className="text-sm font-semibold text-gray-800 mb-2">Snooze for...</p>
          <div className="grid grid-cols-2 gap-2">
            {snoozeOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => handleQuickSnooze(snoozeMenu.notifId, opt.value)}
                className="px-3 py-2 text-sm bg-gray-50 hover:bg-blue-50 hover:text-blue-600 rounded border border-gray-200 transition-colors"
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
