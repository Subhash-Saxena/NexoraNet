import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Clock, Filter } from 'lucide-react';
import { soarApi } from '../../services/soarApi';
import type { PlaybookExecution } from '../../types/soar';
import '../../components/soar/soar.css';

export const SoarExecutionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialStatus = searchParams.get('status') || 'ALL';

  const [executions, setExecutions] = useState<PlaybookExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<string>(initialStatus);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadExecutions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await soarApi.getExecutions({
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        limit: 50,
      });
      setExecutions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load executions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExecutions();
  }, [statusFilter]);

  const filteredExecutions = executions.filter((ex) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      ex.execution_id.toLowerCase().includes(q) ||
      ex.playbook_name.toLowerCase().includes(q) ||
      ex.playbook_identifier.toLowerCase().includes(q) ||
      ex.source_id.toLowerCase().includes(q)
    );
  });

  return (
    <div className="soar-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <span>
          <strong>Simulated Execution Logs:</strong> Real-time and historical traces of automated SOAR playbooks, human approvals, step outputs, and safety audit logs.
        </span>
        <span className="soar-safety-badge">Simulation Mode Only</span>
      </div>

      {/* Header */}
      <div className="soar-header">
        <div>
          <h1 className="soar-title">
            <Clock size={28} color="#06b6d4" /> Playbook Execution Traces
          </h1>
          <p className="soar-subtitle">
            Audit logs, step-by-step telemetry, and approval status for all automated runs.
          </p>
        </div>
        <div>
          <Link to="/soc/automation" className="soar-btn">
            &larr; Back to SOAR Dashboard
          </Link>
        </div>
      </div>

      {/* Nav Tabs */}
      <div className="soar-nav-tabs">
        <Link to="/soc/automation" className="soar-tab-btn">
          Overview Dashboard
        </Link>
        <Link to="/soc/automation/playbooks" className="soar-tab-btn">
          Playbooks Catalog
        </Link>
        <Link to="/soc/automation/executions" className="soar-tab-btn active">
          Execution Logs ({executions.length})
        </Link>
      </div>

      {/* Filter Bar */}
      <div style={{
        background: '#111827',
        border: '1px solid #334155',
        borderRadius: 10,
        padding: '16px 20px',
        marginBottom: 24,
        display: 'flex',
        gap: 16,
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: '1 1 280px' }}>
          <input
            type="text"
            placeholder="Search by Execution ID, Playbook, or Source Entity..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 14px',
              borderRadius: 6,
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#fff',
              fontSize: '0.9rem',
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Filter size={16} /> Status:
          </span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#fff',
              fontSize: '0.85rem',
            }}
          >
            <option value="ALL">All Statuses</option>
            <option value="WAITING_APPROVAL">Waiting Approval</option>
            <option value="RUNNING">Running</option>
            <option value="COMPLETED">Completed</option>
            <option value="FAILED">Failed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ padding: 14, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5', marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Executions Table */}
      <div className="soar-card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: 48, textAlign: 'center', color: '#94a3b8' }}>Loading execution history...</div>
        ) : filteredExecutions.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>
            No executions found matching the filter criteria.
          </div>
        ) : (
          <table className="soar-table">
            <thead>
              <tr>
                <th>Execution ID</th>
                <th>Playbook</th>
                <th>Status</th>
                <th>Steps</th>
                <th>Trigger Source</th>
                <th>Source Entity</th>
                <th>Started At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredExecutions.map((ex) => (
                <tr
                  key={ex.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/soc/automation/executions/${ex.execution_id}`)}
                >
                  <td>
                    <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 600 }}>
                      {ex.execution_id.substring(0, 16)}...
                    </span>
                  </td>
                  <td>
                    <div><strong>{ex.playbook_name}</strong></div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                      {ex.playbook_identifier}
                    </div>
                  </td>
                  <td>
                    <span className={`soar-badge ${ex.status}`}>{ex.status}</span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                      {ex.current_step_order} / {ex.total_steps}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.82rem' }}>{ex.trigger_source}</span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: '#38bdf8' }}>
                      {ex.source_id}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                      {new Date(ex.started_at).toLocaleString()}
                    </span>
                  </td>
                  <td>
                    <Link
                      to={`/soc/automation/executions/${ex.execution_id}`}
                      className="soar-btn"
                      style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      Inspect &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
