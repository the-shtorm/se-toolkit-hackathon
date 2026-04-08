import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import * as eventsApi from '../api/events';
import type { EventResponse } from '../types';

const priorities = ['low', 'medium', 'high', 'critical'] as const;
const priorityColors: Record<string, string> = {
  low: 'bg-blue-100 text-blue-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

export default function EventsPage() {
  const { user, logout } = useAuth();
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Form
  const [name, setName] = useState('');
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [scheduledAt, setScheduledAt] = useState('');

  const fetchEvents = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await eventsApi.getEvents();
      setEvents(result.items);
    } catch {
      setError('Failed to load events');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await eventsApi.createEvent({
        name,
        title,
        message,
        description: description || undefined,
        priority,
        scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : undefined,
      });
      setName(''); setTitle(''); setMessage(''); setDescription('');
      setScheduledAt(''); setPriority('medium');
      setShowCreate(false);
      await fetchEvents();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create event');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this event?')) return;
    try {
      await eventsApi.deleteEvent(id);
      setEvents((ev) => ev.filter((x) => x.id !== id));
    } catch {
      setError('Failed to delete event');
    }
  };

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  const formatDate = (d: string | null) => {
    if (!d) return 'Immediate';
    return new Date(d).toLocaleString();
  };

  const isPast = (d: string | null) => {
    if (!d) return false;
    return new Date(d) < new Date();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Nav */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-gray-800">Smart Notification Manager</h1>
              <Link to="/notifications" className="text-sm text-gray-600 hover:text-blue-600">Notifications</Link>
              <Link to="/groups" className="text-sm text-gray-600 hover:text-blue-600">Groups</Link>
              <span className="text-sm font-semibold text-blue-600">Events</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.username}</span>
              <button onClick={logout} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Logout</button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Scheduled Events</h2>
          <button onClick={() => setShowCreate(true)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            + Schedule Notification
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error} <button onClick={() => setError('')} className="ml-2 text-sm underline">Dismiss</button>
          </div>
        )}

        {isLoading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">Loading events...</div>
        ) : events.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            No scheduled events. Create one to send a notification at a future time!
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {events.map((ev) => (
              <div key={ev.id} className={`bg-white rounded-lg shadow p-5 ${isPast(ev.scheduled_at) ? 'opacity-60' : ''}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-gray-900">{ev.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">{ev.title}</p>
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-gray-400">⏰ {formatDate(ev.scheduled_at)}</p>
                      {ev.scheduled_at && !isPast(ev.scheduled_at) && (
                        <p className="text-xs text-green-600 font-medium">Scheduled</p>
                      )}
                      {ev.scheduled_at && isPast(ev.scheduled_at) && (
                        <p className="text-xs text-gray-500">Sent</p>
                      )}
                      {!ev.scheduled_at && (
                        <p className="text-xs text-blue-600">Immediate</p>
                      )}
                      {ev.is_recurring && (
                        <p className="text-xs text-purple-600">🔄 {ev.recurrence_rule}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-2">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${priorityColors[ev.priority]}`}>
                      {ev.priority}
                    </span>
                    <button onClick={() => handleDelete(ev.id)} className="text-red-400 hover:text-red-600 text-xs ml-1">✕</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Schedule Notification</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Weekly Report" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notification Title</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Title of the notification" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                <textarea value={message} onChange={(e) => setMessage(e.target.value)} required rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Notification content" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select value={priority} onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded">
                    {priorities.map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Schedule Time</label>
                  <input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description (optional)</label>
                <input type="text" value={description} onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded" placeholder="Optional note" />
              </div>
              <div className="flex gap-2 justify-end pt-2">
                <button type="button" onClick={() => setShowCreate(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50">Cancel</button>
                <button type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  {scheduledAt ? 'Schedule' : 'Send Now'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
