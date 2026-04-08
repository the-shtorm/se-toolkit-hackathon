import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import * as groupsApi from '../api/groups';
import { listUsers } from '../api/auth';
import type { GroupResponse, GroupDetailResponse, GroupMember, UserResponse } from '../types';

export default function GroupsPage() {
  const { user, logout } = useAuth();
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<GroupDetailResponse | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMembersModal, setShowMembersModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');

  const fetchGroups = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await groupsApi.getGroups();
      setGroups(result.items);
    } catch {
      setError('Failed to load groups');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchGroupDetail = useCallback(async (id: string) => {
    try {
      const detail = await groupsApi.getGroup(id);
      setSelectedGroup(detail);
      setShowMembersModal(true);
    } catch {
      setError('Failed to load group details');
    }
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await groupsApi.createGroup({ name: newName, description: newDesc || undefined });
      setNewName('');
      setNewDesc('');
      setShowCreateModal(false);
      await fetchGroups();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create group');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this group?')) return;
    try {
      await groupsApi.deleteGroup(id);
      setGroups((g) => g.filter((x) => x.id !== id));
      if (selectedGroup?.id === id) setSelectedGroup(null);
    } catch {
      setError('Failed to delete group');
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!selectedGroup) return;
    if (!confirm('Remove this member?')) return;
    try {
      await groupsApi.removeMember(selectedGroup.id, userId);
      await fetchGroupDetail(selectedGroup.id);
    } catch {
      setError('Failed to remove member');
    }
  };

  useEffect(() => {
    fetchGroups();
  }, [fetchGroups]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-gray-800">Smart Notification Manager</h1>
              <Link to="/notifications" className="text-sm text-gray-600 hover:text-blue-600">
                Notifications
              </Link>
              <span className="text-sm font-semibold text-blue-600">Groups</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
              <span
                className="text-xs text-gray-400 font-mono cursor-pointer hover:text-gray-600"
                title="Your User ID (click to copy)"
                onClick={() => {
                  if (user?.id) {
                    navigator.clipboard.writeText(user.id);
                  }
                }}
              >
                {user?.id?.slice(0, 8)}...
              </span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Groups</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            + Create Group
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
            <button onClick={() => setError('')} className="ml-2 text-sm underline">Dismiss</button>
          </div>
        )}

        {isLoading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">Loading groups...</div>
        ) : groups.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            No groups yet. Create one to start sending notifications to teams!
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {groups.map((g) => (
              <div key={g.id} className="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1 cursor-pointer" onClick={() => fetchGroupDetail(g.id)}>
                    <h3 className="text-lg font-semibold text-gray-900">{g.name}</h3>
                    {g.description && (
                      <p className="text-sm text-gray-500 mt-1">{g.description}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-2">{g.member_count} member{g.member_count !== 1 ? 's' : ''}</p>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(g.id); }}
                    className="text-red-400 hover:text-red-600 text-sm ml-2"
                    title="Delete group"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Group Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Create Group</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Dev Team"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Optional description"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Members Modal */}
      {showMembersModal && selectedGroup && (
        <MembersModal
          group={selectedGroup}
          onClose={() => { setShowMembersModal(false); setSelectedGroup(null); }}
          onRemove={handleRemoveMember}
          onRefresh={() => fetchGroupDetail(selectedGroup.id)}
        />
      )}
    </div>
  );
}

function MembersModal({
  group,
  onClose,
  onRemove,
  onRefresh,
}: {
  group: GroupDetailResponse;
  onClose: () => void;
  onRemove: (userId: string) => void;
  onRefresh: () => void;
}) {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [role, setRole] = useState<'member' | 'admin'>('member');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    listUsers().then(setUsers).catch(() => setUsers([]));
  }, []);

  const availableUsers = users.filter(
    (u) => !group.members.some((m) => m.user_id === u.id)
  );

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserId) return;
    setError('');
    setAdding(true);
    try {
      await groupsApi.addMember(group.id, { user_id: selectedUserId, role });
      setSelectedUserId('');
      onRefresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add member');
    } finally {
      setAdding(false);
    }
  };

  const copyId = (id: string) => {
    navigator.clipboard.writeText(id);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-gray-800">
            {group.name} — Members ({group.member_count})
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        {/* Add member form */}
        <form onSubmit={handleAdd} className="mb-4 p-3 bg-gray-50 rounded space-y-2">
          <h4 className="text-sm font-semibold text-gray-700">Add Member</h4>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2">
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              required
              className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select user...</option>
              {availableUsers.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.username} ({u.email})
                </option>
              ))}
            </select>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as 'member' | 'admin')}
              className="px-2 py-1 text-sm border border-gray-300 rounded"
            >
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
            <button
              type="submit"
              disabled={adding || !selectedUserId}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Add
            </button>
          </div>
        </form>

        {/* Members list */}
        <ul className="divide-y divide-gray-200">
          {group.members.map((m: GroupMember) => (
            <li key={m.id} className="py-2 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{m.username}</p>
                <p className="text-xs text-gray-500">{m.email}</p>
                <p
                  className="text-xs text-gray-400 font-mono cursor-pointer hover:text-gray-600"
                  title="Click to copy"
                  onClick={() => copyId(m.user_id)}
                >
                  {m.user_id.slice(0, 12)}...
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded ${
                    m.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {m.role}
                </span>
                <button
                  onClick={() => onRemove(m.user_id)}
                  className="text-red-400 hover:text-red-600 text-xs"
                  title="Remove"
                >
                  Remove
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
