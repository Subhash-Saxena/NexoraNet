import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle,
  Database,
  RefreshCw,
  Search,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { AdminContentItem } from '../../types/analytics';
import '../../components/analytics/analytics.css';

const TYPES = ['ALL', 'course', 'module', 'topic', 'lesson', 'lab', 'question', 'soc_scenario', 'challenge'];
const STATUSES = ['ALL', 'PUBLISHED', 'DRAFT', 'REVIEW', 'ARCHIVED'];

export const AdminContentPage: React.FC = () => {
  const [items, setItems] = useState<AdminContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [actionMessage, setActionMessage] = useState<{ text: string; error: boolean } | null>(null);

  const fetchContent = async () => {
    try {
      setLoading(true);
      const data = await analyticsApi.getAdminContent({
        type: typeFilter === 'ALL' ? undefined : typeFilter,
        status: statusFilter === 'ALL' ? undefined : statusFilter,
      });
      setItems(data);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load content:', err);
      setActionMessage({ text: err.message || 'Failed to load content', error: true });
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
  }, [typeFilter, statusFilter]);

  const handleUpdateStatus = async (item: AdminContentItem, newStatus: string) => {
    setActionMessage(null);
    try {
      const itemType = item.content_type || item.type || '';
      const res = await analyticsApi.updateContentStatus(itemType, item.id, newStatus);
      setActionMessage({ text: res.message, error: false });
      // Update local item
      setItems((prev) =>
        prev.map((i) =>
          (i.content_type || i.type) === itemType && i.id === item.id ? { ...i, status: newStatus } : i
        )
      );
    } catch (err: any) {
      setActionMessage({ text: err.message || 'Status update failed', error: true });
    }
  };

  const filteredItems = items.filter((item) => {
    const q = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      (item.slug && item.slug.toLowerCase().includes(q)) ||
      (item.category && item.category.toLowerCase().includes(q))
    );
  });

  return (
    <div className="analytics-container">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <Link to="/admin" style={{ color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none', fontSize: '0.85rem' }}>
              <ArrowLeft size={14} />
              <span>Admin Dashboard</span>
            </Link>
          </div>
          <h1>
            <Database className="text-cyan-400" size={28} />
            <span>Curriculum & Simulation Content Management</span>
          </h1>
          <p className="analytics-tagline">
            Lifecycle state machine for educational materials, practical labs, questions, and SOC scenarios.
          </p>
        </div>

        <button
          className="btn-secondary"
          onClick={fetchContent}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Action Feedback Banner */}
      {actionMessage && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: actionMessage.error ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
            border: `1px solid ${actionMessage.error ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
            color: actionMessage.error ? '#f87171' : '#34d399',
          }}
        >
          {actionMessage.error ? <AlertCircle size={18} /> : <CheckCircle size={18} />}
          <span>{actionMessage.text}</span>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="admin-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Type filters */}
          <div className="filter-tabs">
            {TYPES.map((t) => (
              <button
                key={t}
                className={`tab-btn ${typeFilter === t ? 'active' : ''}`}
                onClick={() => setTypeFilter(t)}
                style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
              >
                {t.toUpperCase().replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Search */}
          <div style={{ position: 'relative', minWidth: '240px' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
            <input
              type="text"
              placeholder="Filter by title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '0.45rem 0.75rem 0.45rem 2rem',
                background: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '0.375rem',
                color: '#f9fafb',
                fontSize: '0.85rem',
              }}
            />
          </div>
        </div>

        {/* Status Pills */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#9ca3af', fontWeight: 600 }}>Status:</span>
          {STATUSES.map((st) => (
            <button
              key={st}
              className={`tab-btn ${statusFilter === st ? 'active' : ''}`}
              onClick={() => setStatusFilter(st)}
              style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Content Table */}
      <div className="admin-card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
            Loading content records...
          </div>
        ) : filteredItems.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
            No content matches the selected filters.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>ID</th>
                  <th>Title / Asset Name</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => {
                  const rawType = item.content_type || item.type || 'Asset';
                  const displayType = rawType.replace(/_/g, ' ');
                  const assetSlug = item.code_or_slug || item.slug;
                  return (
                    <tr key={`${rawType}-${item.id}`}>
                      <td style={{ textTransform: 'capitalize', color: '#93c5fd', fontWeight: 600 }}>
                        {displayType}
                      </td>
                      <td style={{ fontFamily: 'monospace', color: '#6b7280' }}>#{item.id}</td>
                      <td>
                        <div style={{ fontWeight: 600, color: '#f3f4f6' }}>{item.title}</div>
                        {assetSlug && (
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', fontFamily: 'monospace' }}>
                            {assetSlug}
                          </div>
                        )}
                      </td>
                    <td style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{item.category || '-'}</td>
                    <td>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          padding: '0.2rem 0.5rem',
                          borderRadius: '9999px',
                          background:
                            item.status === 'PUBLISHED'
                              ? 'rgba(16, 185, 129, 0.15)'
                              : item.status === 'ARCHIVED'
                              ? 'rgba(107, 114, 128, 0.2)'
                              : 'rgba(245, 158, 11, 0.15)',
                          color:
                            item.status === 'PUBLISHED'
                              ? '#34d399'
                              : item.status === 'ARCHIVED'
                              ? '#9ca3af'
                              : '#fbbf24',
                          border: `1px solid ${
                            item.status === 'PUBLISHED'
                              ? 'rgba(16, 185, 129, 0.3)'
                              : item.status === 'ARCHIVED'
                              ? 'rgba(107, 114, 128, 0.3)'
                              : 'rgba(245, 158, 11, 0.3)'
                          }`,
                        }}
                      >
                        {item.status}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        {item.status !== 'PUBLISHED' && (
                          <button
                            className="btn-primary"
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                            onClick={() => handleUpdateStatus(item, 'PUBLISHED')}
                            title="Validate and publish live"
                          >
                            Publish
                          </button>
                        )}
                        {item.status === 'PUBLISHED' && (
                          <button
                            className="btn-secondary"
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                            onClick={() => handleUpdateStatus(item, 'DRAFT')}
                            title="Unpublish to Draft"
                          >
                            Unpublish
                          </button>
                        )}
                        {item.status !== 'ARCHIVED' && (
                          <button
                            className="btn-secondary"
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: '#f87171' }}
                            onClick={() => handleUpdateStatus(item, 'ARCHIVED')}
                            title="Archive item"
                          >
                            Archive
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
