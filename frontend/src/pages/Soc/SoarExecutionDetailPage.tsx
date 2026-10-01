import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Check, X, RefreshCw } from 'lucide-react';
import { soarApi } from '../../services/soarApi';
import type { PlaybookExecution } from '../../types/soar';
import '../../components/soar/soar.css';

export const SoarExecutionDetailPage: React.FC = () => {
  const { executionId } = useParams<{ executionId: string }>();

  const [execution, setExecution] = useState<PlaybookExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Approval modal / action state
  const [approvalReason, setApprovalReason] = useState('Analyst confirmed malicious behavior; authorization granted.');
  const [actionLoading, setActionLoading] = useState(false);

  const fetchExecution = async () => {
    if (!executionId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await soarApi.getExecutionDetail(executionId);
      setExecution(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load execution detail');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecution();
  }, [executionId]);

  const handleApprove = async () => {
    if (!execution) return;
    setActionLoading(true);
    try {
      const updated = await soarApi.approveExecution(execution.execution_id, {
        approver: 'lead_soc_analyst',
        reason: approvalReason,
      });
      setExecution(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to approve execution');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!execution) return;
    setActionLoading(true);
    try {
      const updated = await soarApi.rejectExecution(execution.execution_id, {
        approver: 'lead_soc_analyst',
        reason: approvalReason || 'Analyst rejected high-risk automated containment step.',
      });
      setExecution(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to reject execution');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="soar-container" style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>
        Loading execution audit log and step traces...
      </div>
    );
  }

  if (error || !execution) {
    return (
      <div className="soar-container">
        <div style={{ padding: 20, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5' }}>
          {error || 'Execution not found.'}
        </div>
        <div style={{ marginTop: 16 }}>
          <Link to="/soc/automation/executions" className="soar-btn">
            &larr; Back to Execution Logs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="soar-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <span>
          <strong>Simulated Execution Audit Trace:</strong> Safe sandbox environment. All state machine mutations and synthetic artifacts are logged strictly for educational verification.
        </span>
        <span className="soar-safety-badge">Simulation Mode Only</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <Link to="/soc/automation/executions" style={{ color: '#06b6d4', textDecoration: 'none', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
          <ArrowLeft size={16} /> Back to Execution Logs
        </Link>
        <div className="soar-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 700, fontSize: '0.95rem' }}>
                {execution.execution_id}
              </span>
              <span className={`soar-badge ${execution.status}`}>{execution.status}</span>
            </div>
            <h1 className="soar-title">{execution.playbook_name}</h1>
            <p className="soar-subtitle">
              Triggered by {execution.trigger_source} for entity <code>{execution.source_id}</code>
            </p>
          </div>
          <div>
            <button className="soar-btn" onClick={fetchExecution}>
              <RefreshCw size={14} /> Refresh Trace
            </button>
          </div>
        </div>
      </div>

      {/* Human Approval Gate Action Banner if Waiting */}
      {execution.status === 'WAITING_APPROVAL' && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid #f59e0b',
          borderRadius: 10,
          padding: 24,
          marginBottom: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
            <AlertTriangle size={28} color="#fbbf24" style={{ flexShrink: 0, marginTop: 2 }} />
            <div style={{ flexGrow: 1 }}>
              <h3 style={{ margin: '0 0 6px 0', color: '#fbbf24', fontSize: '1.2rem' }}>
                Human-in-the-Loop Analyst Approval Required
              </h3>
              <p style={{ margin: '0 0 16px 0', color: '#fde68a', fontSize: '0.9rem' }}>
                This playbook paused before executing a high-risk automated containment/eradication action. Review the execution traces below before approving the state machine to resume.
              </p>

              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: '0.82rem', color: '#fde68a', marginBottom: 6 }}>
                  Approval Reason / Analyst Notes:
                </label>
                <input
                  type="text"
                  value={approvalReason}
                  onChange={(e) => setApprovalReason(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 10,
                    borderRadius: 6,
                    background: '#1e293b',
                    border: '1px solid #d97706',
                    color: '#fff',
                    fontSize: '0.9rem',
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: 12 }}>
                <button
                  className="soar-btn soar-btn-success"
                  onClick={handleApprove}
                  disabled={actionLoading}
                >
                  <Check size={16} /> Approve &amp; Resume Playbook
                </button>
                <button
                  className="soar-btn soar-btn-danger"
                  onClick={handleReject}
                  disabled={actionLoading}
                >
                  <X size={16} /> Reject Action
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Overview Metadata Bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 16,
        background: '#111827',
        border: '1px solid #334155',
        borderRadius: 8,
        padding: '16px 20px',
        marginBottom: 24,
      }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Playbook ID</span>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: 2, fontFamily: 'monospace' }}>
            {execution.playbook_identifier}
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Progress</span>
          <div style={{ fontWeight: 600, color: '#38bdf8', marginTop: 2 }}>
            {execution.current_step_order} / {execution.total_steps} Steps
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Requested By</span>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: 2 }}>
            {execution.requested_by}
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Approval Decision</span>
          <div style={{ fontWeight: 600, color: execution.approved_by ? '#34d399' : '#94a3b8', marginTop: 2 }}>
            {execution.approval_status || 'None Required'} {execution.approved_by ? `by ${execution.approved_by}` : ''}
          </div>
        </div>
      </div>

      {/* Execution Step Logs Timeline */}
      <div className="soar-card">
        <div className="soar-card-title">
          <span>Execution Step-by-Step Traces ({execution.step_logs?.length || 0})</span>
        </div>

        {!execution.step_logs || execution.step_logs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 32, color: '#64748b' }}>
            No steps recorded yet.
          </div>
        ) : (
          <div className="soar-step-sequence">
            {execution.step_logs.map((log) => {
              let parsedInput = {};
              let parsedOutput = {};
              try {
                if (log.input_summary) parsedInput = JSON.parse(log.input_summary);
                if (log.output_summary) parsedOutput = JSON.parse(log.output_summary);
              } catch {}

              return (
                <div key={log.id} className="soar-step-item">
                  <div className="soar-step-order" style={{
                    background: log.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.2)' : log.status === 'WAITING_APPROVAL' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: log.status === 'COMPLETED' ? '#34d399' : log.status === 'WAITING_APPROVAL' ? '#fbbf24' : '#f87171',
                  }}>
                    {log.step_order}
                  </div>
                  <div className="soar-step-content">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <div className="soar-step-name">{log.step_name}</div>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#38bdf8' }}>
                          {log.action_type}
                        </span>
                        <span className={`soar-badge ${log.status}`}>{log.status}</span>
                      </div>
                    </div>

                    <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: 10 }}>
                      Started: {new Date(log.started_at).toLocaleTimeString()}
                      {log.completed_at ? ` &bull; Completed: ${new Date(log.completed_at).toLocaleTimeString()}` : ''}
                      {log.retry_attempt > 0 ? ` &bull; Retries: ${log.retry_attempt}` : ''}
                    </div>

                    {log.error_message && (
                      <div style={{
                        padding: '8px 12px',
                        background: 'rgba(239, 68, 68, 0.15)',
                        border: '1px solid #ef4444',
                        borderRadius: 6,
                        color: '#fca5a5',
                        fontSize: '0.82rem',
                        marginBottom: 10
                      }}>
                        <strong>Error ({log.error_code}):</strong> {log.error_message}
                      </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                      <div style={{ background: '#0f172a', padding: 10, borderRadius: 6, fontSize: '0.78rem' }}>
                        <div style={{ color: '#64748b', marginBottom: 4, fontWeight: 600 }}>Input Telemetry:</div>
                        <pre style={{ margin: 0, color: '#cbd5e1', overflowX: 'auto', fontFamily: 'monospace' }}>
                          {JSON.stringify(parsedInput, null, 2)}
                        </pre>
                      </div>

                      <div style={{ background: '#0f172a', padding: 10, borderRadius: 6, fontSize: '0.78rem' }}>
                        <div style={{ color: '#34d399', marginBottom: 4, fontWeight: 600 }}>Action Output:</div>
                        <pre style={{ margin: 0, color: '#a7f3d0', overflowX: 'auto', fontFamily: 'monospace' }}>
                          {JSON.stringify(parsedOutput, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Artifacts & Summary */}
      {execution.artifacts_json && (
        <div className="soar-card">
          <div className="soar-card-title">Generated Execution Artifacts</div>
          <pre style={{
            background: '#0f172a',
            padding: 14,
            borderRadius: 8,
            color: '#38bdf8',
            fontFamily: 'monospace',
            fontSize: '0.82rem',
            overflowX: 'auto',
            margin: 0,
          }}>
            {JSON.stringify(JSON.parse(execution.artifacts_json), null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
