import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowLeft,
  RefreshCw,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { AdminAuditLog } from '../../types/analytics';
import '../../components/analytics/analytics.css';

export const AdminAuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AdminAuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await analyticsApi.getAdminAuditLogs(100);
      setLogs(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filtered = logs.filter((l) => {
    const q = search.toLowerCase();
    return (
      l.action.toLowerCase().includes(q) ||
      l.target_type.toLowerCase().includes(q) ||
      l.target_id.toLowerCase().includes(q) ||
      (l.details && l.details.toLowerCase().includes(q))
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
            <Activity className="text-cyan-400" size={28} />
            <span>Administrative Governance & Audit Ledger</span>
          </h1>
          <p className="analytics-tagline">
            Immutable, timestamped record of administrative content changes, validations, and security events.
          </p>
        </div>

        <button
          className="btn-secondary"
          onClick={fetchLogs}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <RefreshCw size={16} />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Filter / Search Bar */}
      <div className="admin-card" style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ fontSize: '0.85rem', color: '#9ca3af' }}>
          Showing <strong>{filtered.length}</strong> immutable audit records
        </div>

        <input
          type="text"
          placeholder="Filter audit actions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            minWidth: '240px',
            padding: '0.45rem 0.75rem',
            background: '#1f2937',
            border: '1px solid #374151',
            borderRadius: '0.375rem',
            color: '#f9fafb',
            fontSize: '0.85rem',
          }}
        />
      </div>

      {/* Logs Table */}
      <div className="admin-card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
            Loading audit events...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
            No audit records found.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Timestamp (UTC)</th>
                  <th>Actor Role</th>
                  <th>Action</th>
                  <th>Target Type</th>
                  <th>Target ID</th>
                  <th>Audit Details</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((log) => (
                  <tr key={log.id}>
                    <td style={{ color: '#9ca3af', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          padding: '0.2rem 0.45rem',
                          borderRadius: '0.25rem',
                          background:
                            log.actor_role === 'ADMIN'
                              ? 'rgba(239, 68, 68, 0.15)'
                              : log.actor_role === 'INSTRUCTOR'
                              ? 'rgba(245, 158, 11, 0.15)'
                              : '#1f2937',
                          color:
                            log.actor_role === 'ADMIN'
                              ? '#f87171'
                              : log.actor_role === 'INSTRUCTOR'
                              ? '#fbbf24'
                              : '#9ca3af',
                        }}
                      >
                        {log.actor_role}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#38bdf8' }}>
                      {log.action}
                    </td>
                    <td style={{ textTransform: 'capitalize', color: '#e5e7eb' }}>
                      {log.target_type}
                    </td>
                    <td style={{ fontFamily: 'monospace', color: '#9ca3af' }}>
                      {log.target_id}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                      {log.details || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
