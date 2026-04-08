import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import * as preferencesApi from '../api/preferences';
import type { PreferencesResponse } from '../types';

const timezones = [
  'UTC', 'US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific',
  'Europe/London', 'Europe/Paris', 'Europe/Berlin',
  'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Kolkata',
  'Australia/Sydney',
];

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [prefs, setPrefs] = useState<PreferencesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [webEnabled, setWebEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [smsEnabled, setSmsEnabled] = useState(false);
  const [quietHoursStart, setQuietHoursStart] = useState('');
  const [quietHoursEnd, setQuietHoursEnd] = useState('');
  const [maxDaily, setMaxDaily] = useState(50);
  const [timezone, setTimezone] = useState('UTC');
  const [digestEnabled, setDigestEnabled] = useState(false);
  const [digestFrequency, setDigestFrequency] = useState('daily');

  const fetchPreferences = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await preferencesApi.getPreferences();
      setPrefs(data);
      setWebEnabled(data.web_enabled);
      setEmailEnabled(data.email_enabled);
      setSmsEnabled(data.sms_enabled);
      setQuietHoursStart(data.quiet_hours_start?.slice(0, 5) || '');
      setQuietHoursEnd(data.quiet_hours_end?.slice(0, 5) || '');
      setMaxDaily(data.max_daily_notifications);
      setTimezone(data.timezone);
      setDigestEnabled(data.digest_enabled);
      setDigestFrequency(data.digest_frequency || 'daily');
    } catch {
      // No preferences yet, will create on save
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        web_enabled: webEnabled,
        email_enabled: emailEnabled,
        sms_enabled: smsEnabled,
        quiet_hours_start: quietHoursStart || null,
        quiet_hours_end: quietHoursEnd || null,
        max_daily_notifications: maxDaily,
        timezone,
        digest_enabled: digestEnabled,
        digest_frequency: digestEnabled ? digestFrequency : null,
      };

      let result;
      if (prefs) {
        result = await preferencesApi.updatePreferences(payload);
      } else {
        result = await preferencesApi.createPreferences(payload);
      }
      setPrefs(result);
      setSuccess('Preferences saved successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save preferences');
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => { fetchPreferences(); }, [fetchPreferences]);

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
              <Link to="/events" className="text-sm text-gray-600 hover:text-blue-600">Events</Link>
              <Link to="/templates" className="text-sm text-gray-600 hover:text-blue-600">Templates</Link>
              <span className="text-sm font-semibold text-blue-600">Settings</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.username}</span>
              <button onClick={logout} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Logout</button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Notification Preferences</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error} <button onClick={() => setError('')} className="ml-2 text-sm underline">Dismiss</button>
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            {success} <button onClick={() => setSuccess('')} className="ml-2 text-sm underline">Dismiss</button>
          </div>
        )}

        {isLoading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">Loading preferences...</div>
        ) : (
          <form onSubmit={handleSave} className="bg-white rounded-lg shadow p-6 space-y-6">
            {/* Notification Channels */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Notification Channels</h3>
              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={webEnabled}
                    onChange={(e) => setWebEnabled(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700">Web notifications</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={emailEnabled}
                    onChange={(e) => setEmailEnabled(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700">Email notifications</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={smsEnabled}
                    onChange={(e) => setSmsEnabled(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700">SMS notifications (coming soon)</span>
                </label>
              </div>
            </div>

            {/* Quiet Hours */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Quiet Hours</h3>
              <p className="text-sm text-gray-500 mb-3">Notifications will be suppressed during these hours</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                  <input
                    type="time"
                    value={quietHoursStart}
                    onChange={(e) => setQuietHoursStart(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                  <input
                    type="time"
                    value={quietHoursEnd}
                    onChange={(e) => setQuietHoursEnd(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  />
                </div>
              </div>
            </div>

            {/* Daily Limit */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Daily Limit</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max notifications per day: {maxDaily}
                </label>
                <input
                  type="range"
                  min="0"
                  max="200"
                  value={maxDaily}
                  onChange={(e) => setMaxDaily(Number(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-400">
                  <span>0</span>
                  <span>200</span>
                </div>
              </div>
            </div>

            {/* Timezone */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Timezone</h3>
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded"
              >
                {timezones.map((tz) => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            </div>

            {/* Digest */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Digest Settings</h3>
              <label className="flex items-center gap-3 mb-3">
                <input
                  type="checkbox"
                  checked={digestEnabled}
                  onChange={(e) => setDigestEnabled(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-700">Enable daily/weekly digest</span>
              </label>
              {digestEnabled && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                  <select
                    value={digestFrequency}
                    onChange={(e) => setDigestFrequency(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>
              )}
            </div>

            {/* Save Button */}
            <div className="flex justify-end pt-4">
              <button
                type="submit"
                disabled={isSaving}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Preferences'}
              </button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
