import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  Database,
  Key,
  Layers,
  Lock,
  ShieldAlert,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { AdminDashboardMetrics } from '../../types/analytics';
import '../../components/analytics/analytics.css';

export const AdminDashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<AdminDashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Development role switcher
  const currentRole = localStorage.getItem('nexoranet_role') || 'STUDENT';

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsApi.getAdminDashboard();
      setMetrics(data);
      setLoading(false);
    } catch (err: any) {
      console.error('Admin API error:', err);
      setError(err.message || 'Access denied or server error');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const switchRole = (newRole: 'STUDENT' | 'INSTRUCTOR' | 'ADMIN') => {
    localStorage.setItem('nexoranet_role', newRole);
    if (newRole === 'ADMIN') {
      localStorage.setItem('nexoranet_user_id', '1'); // admin_dev
    } else if (newRole === 'INSTRUCTOR') {
      localStorage.setItem('nexoranet_user_id', '3'); // instructor_dev
    } else {
      localStorage.setItem('nexoranet_user_id', '2'); // student_dev
    }
    fetchDashboard();
  };

  return (
    <div className="analytics-container">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <h1>
            <ShieldAlert className="text-red-400" size={28} />
            <span>Platform Administration & Content Operations</span>
          </h1>
          <p className="analytics-tagline">
            Role-gated administrative governance, curriculum version control, and operational audit telemetry.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <Link to="/admin/content" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
            <Database size={16} />
            <span>Manage Content Catalog</span>
          </Link>
          <Link to="/admin/audit" className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
            <Activity size={16} />
            <span>Audit Ledger</span>
          </Link>
        </div>
      </div>

      {/* Role Switcher Toolbar for Development Verification */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.75rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: '#cbd5e1' }}>
          <Key size={16} className="text-yellow-400" />
          <span>Active Session Role Header:</span>
          <strong style={{ color: currentRole === 'ADMIN' ? '#f87171' : currentRole === 'INSTRUCTOR' ? '#fbbf24' : '#60a5fa' }}>
            {currentRole}
          </strong>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Switch Context:</span>
          <button
            className={`tab-btn ${currentRole === 'STUDENT' ? 'active' : ''}`}
            onClick={() => switchRole('STUDENT')}
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
          >
            Student (403 Test)
          </button>
          <button
            className={`tab-btn ${currentRole === 'INSTRUCTOR' ? 'active' : ''}`}
            onClick={() => switchRole('INSTRUCTOR')}
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
          >
            Instructor
          </button>
          <button
            className={`tab-btn ${currentRole === 'ADMIN' ? 'active' : ''}`}
            onClick={() => switchRole('ADMIN')}
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
          >
            Admin (Full Access)
          </button>
        </div>
      </div>

      {/* Authorization Error Banner */}
      {error && (
        <div className="admin-card" style={{ borderColor: '#ef4444', background: 'rgba(239, 68, 68, 0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
            <Lock size={28} className="text-red-400" />
            <div>
              <h3 style={{ fontSize: '1.1rem', color: '#f87171', margin: '0 0 0.5rem 0' }}>
                403 Forbidden: Administrator Authorization Required
              </h3>
              <p style={{ color: '#cbd5e1', fontSize: '0.9rem', margin: 0, lineHeight: 1.5 }}>
                {error}. Server enforces strict role verification. To test or administer the platform, switch your role to <strong>ADMIN</strong> above.
              </p>
              <button
                className="btn-primary"
                onClick={() => switchRole('ADMIN')}
                style={{ marginTop: '0.75rem', fontSize: '0.85rem' }}
              >
                Switch to Admin Context
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Metrics Dashboard */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
          Loading administrative telemetry...
        </div>
      ) : metrics && (
        <>
          <div className="analytics-metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Registered Cadets</span>
              <span className="metric-value">{metrics.total_users ?? 0}</span>
              <span className="metric-subtext">Active Users: {metrics.active_learners ?? metrics.active_students_7d ?? 0} (Recent)</span>
            </div>

            <div className="metric-card">
              <span className="metric-label">Published Assets</span>
              <span className="metric-value" style={{ color: '#34d399' }}>
                {metrics.publication_status?.published ?? metrics.publication_status?.published_questions ?? 0}
              </span>
              <span className="metric-subtext">Live in Curriculum</span>
            </div>

            <div className="metric-card">
              <span className="metric-label">Draft / Review Items</span>
              <span className="metric-value" style={{ color: '#fbbf24' }}>
                {(metrics.publication_status?.draft ?? metrics.publication_status?.draft_questions ?? 0) +
                  (metrics.publication_status?.review ?? 0)}
              </span>
              <span className="metric-subtext">Pending Validation</span>
            </div>

            <div className="metric-card">
              <span className="metric-label">Audit Ledger Records</span>
              <span className="metric-value" style={{ color: '#38bdf8' }}>
                {metrics.audit_count ?? (metrics.recent_audit_logs ? metrics.recent_audit_logs.length : 0)}
              </span>
              <span className="metric-subtext">Immutable Logged Events</span>
            </div>
          </div>

          {/* Catalog Counts Breakdown */}
          <div className="admin-card">
            <h3 style={{ fontSize: '1.15rem', color: '#f3f4f6', margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} className="text-cyan-400" />
              <span>Instructional & Hands-On Asset Inventory</span>
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {metrics.catalog_counts &&
                Object.entries(metrics.catalog_counts).map(([type, count]) => (
                  <div key={type} style={{ background: '#1f2937', padding: '1rem', borderRadius: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.85rem', color: '#9ca3af', textTransform: 'capitalize' }}>
                      {(type || '').replace(/_/g, ' ')}
                    </span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f9fafb' }}>
                      {count}
                    </span>
                  </div>
                ))}
            </div>
          </div>

          {/* Quick Links */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            <div className="admin-card">
              <h4 style={{ fontSize: '1rem', color: '#f3f4f6', margin: '0 0 0.5rem 0' }}>Content Publication Control</h4>
              <p style={{ fontSize: '0.85rem', color: '#9ca3af', lineHeight: 1.5 }}>
                Validate learning objectives, examine prerequisite graphs, and toggle publication status with strict prerequisite guards.
              </p>
              <Link to="/admin/content" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.75rem', textDecoration: 'none' }}>
                <span>Open Content Catalog</span>
              </Link>
            </div>

            <div className="admin-card">
              <h4 style={{ fontSize: '1rem', color: '#f3f4f6', margin: '0 0 0.5rem 0' }}>Security & Audit Ledger</h4>
              <p style={{ fontSize: '0.85rem', color: '#9ca3af', lineHeight: 1.5 }}>
                Track who performed each administrative operation with tamper-evident audit timestamps and actors.
              </p>
              <Link to="/admin/audit" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.75rem', textDecoration: 'none' }}>
                <span>Open Audit Ledger</span>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
