import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useNotificationStore } from '../stores/notificationStore';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  BarChart, Bar,
} from 'recharts';

const COLORS = ['#3B82F6', '#F59E0B', '#F97316', '#EF4444'];

export default function AnalyticsPage() {
  const { user, logout } = useAuth();
  const { fetchStats } = useNotificationStore();
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadStats = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchStats(true);
      setStats(data);
    } catch {
      setError('Failed to load analytics');
    } finally {
      setIsLoading(false);
    }
  }, [fetchStats]);

  useEffect(() => { loadStats(); }, [loadStats]);

  // Prepare line chart data
  const lineData = stats?.daily_last_7_days
    ? Object.entries(stats.daily_last_7_days).map(([date, count]) => ({
        date: new Date(date as string).toLocaleDateString('en', { weekday: 'short' }),
        notifications: count as number,
      }))
    : [];

  // Prepare pie chart data
  const pieData = stats?.by_priority
    ? Object.entries(stats.by_priority).map(([name, value]) => ({
        name: (name as string).charAt(0).toUpperCase() + (name as string).slice(1),
        value: value as number,
      }))
    : [];

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
              <Link to="/settings" className="text-sm text-gray-600 hover:text-blue-600">Settings</Link>
              <span className="text-sm font-semibold text-blue-600">Analytics</span>
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
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Analytics Dashboard</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error} <button onClick={() => setError('')} className="ml-2 text-sm underline">Dismiss</button>
          </div>
        )}

        {isLoading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">Loading analytics...</div>
        ) : stats ? (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-5">
                <p className="text-sm text-gray-500">Total Notifications</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{stats.total}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-5">
                <p className="text-sm text-gray-500">Unread</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{stats.unread_count}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-5">
                <p className="text-sm text-gray-500">Read Rate</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.read_rate}%</p>
              </div>
              <div className="bg-white rounded-lg shadow p-5">
                <p className="text-sm text-gray-500">Read</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{stats.read_count}</p>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Line Chart - Daily Activity */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">📈 Notifications (Last 7 Days)</h3>
                {lineData.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-8">No data available</p>
                ) : (
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={lineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Line type="monotone" dataKey="notifications" stroke="#3B82F6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>

              {/* Pie Chart - By Priority */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">🎯 By Priority</h3>
                {pieData.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-8">No data available</p>
                ) : (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>

              {/* Bar Chart - Read vs Unread */}
              <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 Read vs Unread</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: 'Read', count: stats.read_count, fill: '#10B981' },
                    { name: 'Unread', count: stats.unread_count, fill: '#3B82F6' },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            No analytics data available. Start creating notifications to see stats here!
          </div>
        )}
      </main>
    </div>
  );
}
