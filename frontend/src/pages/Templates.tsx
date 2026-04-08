import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import * as templatesApi from '../api/templates';
import type { TemplateResponse } from '../types';

const priorities = ['low', 'medium', 'high', 'critical'] as const;
const priorityColors: Record<string, string> = {
  low: 'bg-blue-100 text-blue-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

const categories = ['system', 'meeting', 'task', 'alert', 'reminder', 'custom'];

export default function TemplatesPage() {
  const { user, logout } = useAuth();
  const [templates, setTemplates] = useState<TemplateResponse[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<TemplateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);
  const [total, setTotal] = useState(0);
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  // Form
  const [name, setName] = useState('');
  const [titleTemplate, setTitleTemplate] = useState('');
  const [messageTemplate, setMessageTemplate] = useState('');
  const [priority, setPriority] = useState('medium');
  const [category, setCategory] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  const fetchTemplates = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await templatesApi.getTemplates(page, pageSize, categoryFilter || undefined);
      setTemplates(result.items);
      setTotal(result.total);
    } catch {
      setError('Failed to load templates');
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, categoryFilter]);

  const resetForm = () => {
    setName(''); setTitleTemplate(''); setMessageTemplate('');
    setPriority('medium'); setCategory(''); setIsPublic(false);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await templatesApi.createTemplate({
        name,
        title_template: titleTemplate,
        message_template: messageTemplate,
        priority,
        category: category || undefined,
        is_public: isPublic,
      });
      resetForm();
      setShowCreate(false);
      await fetchTemplates();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create template');
    }
  };

  const handleEdit = (tpl: TemplateResponse) => {
    setEditingTemplate(tpl);
    setName(tpl.name);
    setTitleTemplate(tpl.title_template);
    setMessageTemplate(tpl.message_template);
    setPriority(tpl.priority);
    setCategory(tpl.category || '');
    setIsPublic(tpl.is_public);
    setShowEdit(true);
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTemplate) return;

    setError('');
    try {
      await templatesApi.updateTemplate(editingTemplate.id, {
        name,
        title_template: titleTemplate,
        message_template: messageTemplate,
        priority,
        category: category || undefined,
        is_public: isPublic,
      });
      resetForm();
      setEditingTemplate(null);
      setShowEdit(false);
      await fetchTemplates();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update template');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this template?')) return;
    try {
      await templatesApi.deleteTemplate(id);
      setTemplates((t) => t.filter((x) => x.id !== id));
      setTotal((t) => t - 1);
    } catch {
      setError('Failed to delete template');
    }
  };

  const handleUseTemplate = async (tpl: TemplateResponse) => {
    // Navigate to notifications page with template data pre-filled (future enhancement)
    alert(`Template "${tpl.name}" selected! In a full implementation, this would pre-fill the notification creation form.`);
  };

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const totalPages = Math.ceil(total / pageSize);

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
              <span className="text-sm font-semibold text-blue-600">Templates</span>
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
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Notification Templates</h2>
            <p className="text-sm text-gray-600 mt-1">{total} templates available</p>
          </div>
          <button onClick={() => { resetForm(); setShowCreate(true); }} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            + Create Template
          </button>
        </div>

        {/* Category Filter */}
        <div className="mb-4 flex gap-2 flex-wrap">
          <button
            onClick={() => { setCategoryFilter(''); setPage(1); }}
            className={`px-3 py-1 rounded text-sm ${!categoryFilter ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => { setCategoryFilter(cat); setPage(1); }}
              className={`px-3 py-1 rounded text-sm capitalize ${categoryFilter === cat ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}`}
            >
              {cat}
            </button>
          ))}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error} <button onClick={() => setError('')} className="ml-2 text-sm underline">Dismiss</button>
          </div>
        )}

        {isLoading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">Loading templates...</div>
        ) : templates.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            No templates yet. Create one to get started!
          </div>
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {templates.map((tpl) => (
                <div key={tpl.id} className="bg-white rounded-lg shadow p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-gray-900">{tpl.name}</h3>
                      {tpl.category && (
                        <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded capitalize">
                          {tpl.category}
                        </span>
                      )}
                      <p className="text-xs text-gray-500 mt-2 line-clamp-2">{tpl.title_template}</p>
                      <p className="text-xs text-gray-400 mt-1 line-clamp-3">{tpl.message_template}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${priorityColors[tpl.priority]}`}>
                          {tpl.priority}
                        </span>
                        {tpl.is_public && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-green-100 text-green-800">
                            Public
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 ml-2">
                      <button onClick={() => handleUseTemplate(tpl)} className="text-green-400 hover:text-green-600 text-xs" title="Use">✓</button>
                      {tpl.created_by === user?.id && (
                        <>
                          <button onClick={() => handleEdit(tpl)} className="text-blue-400 hover:text-blue-600 text-xs" title="Edit">✎</button>
                          <button onClick={() => handleDelete(tpl.id)} className="text-red-400 hover:text-red-600 text-xs" title="Delete">✕</button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 bg-white border border-gray-300 rounded disabled:opacity-50 hover:bg-gray-50"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1 bg-white border border-gray-300 rounded disabled:opacity-50 hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Create Template</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Meeting Reminder" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title Template</label>
                <input type="text" value={titleTemplate} onChange={(e) => setTitleTemplate(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Reminder: {meeting_name}" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message Template</label>
                <textarea value={messageTemplate} onChange={(e) => setMessageTemplate(e.target.value)} required rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Don't forget about {meeting_name} at {time}" />
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select value={category} onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded">
                    <option value="">None</option>
                    {categories.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="isPublic" className="text-sm text-gray-700">Make public (visible to all users)</label>
              </div>
              <div className="flex gap-2 justify-end pt-2">
                <button type="button" onClick={() => { resetForm(); setShowCreate(false); }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50">Cancel</button>
                <button type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Create Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEdit && editingTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Edit Template</h3>
            <form onSubmit={handleUpdate} className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Meeting Reminder" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title Template</label>
                <input type="text" value={titleTemplate} onChange={(e) => setTitleTemplate(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Reminder: {meeting_name}" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message Template</label>
                <textarea value={messageTemplate} onChange={(e) => setMessageTemplate(e.target.value)} required rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Don't forget about {meeting_name} at {time}" />
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select value={category} onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded">
                    <option value="">None</option>
                    {categories.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="editIsPublic"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="editIsPublic" className="text-sm text-gray-700">Make public (visible to all users)</label>
              </div>
              <div className="flex gap-2 justify-end pt-2">
                <button type="button" onClick={() => { resetForm(); setEditingTemplate(null); setShowEdit(false); }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50">Cancel</button>
                <button type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Update Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
