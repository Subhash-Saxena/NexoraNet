import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Play, AlertTriangle, Zap, Cpu } from 'lucide-react';
import { soarApi } from '../../services/soarApi';
import type { AutomationPlaybook, PlaybookExecution, SoarMetrics } from '../../types/soar';
import '../../components/soar/soar.css';

export const SoarDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<SoarMetrics | null>(null);
  const [playbooks, setPlaybooks] = useState<AutomationPlaybook[]>([]);
  const [executions, setExecutions] = useState<PlaybookExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Trigger modal state
  const [showTriggerModal, setShowTriggerModal] = useState(false);
  const [selectedPlaybookId, setSelectedPlaybookId] = useState('');
  const [triggerSource, setTriggerSource] = useState('ANALYST_CONSOLE');
  const [sourceId, setSourceId] = useState('ALT-MANUAL-001');
  const [triggerPayload, setTriggerPayload] = useState('{\n  "ip": "198.51.100.25",\n  "hostname": "FIN-SRV-02",\n  "severity": "HIGH"\n}');
  const [triggering, setTriggering] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [metricsRes, playbooksRes, executionsRes] = await Promise.all([
        soarApi.getSoarMetrics(),
        soarApi.getPlaybooks({ limit: 10 }),
        soarApi.getExecutions({ limit: 8 }),
      ]);
      setMetrics(metricsRes);
      setPlaybooks(playbooksRes);
      setExecutions(executionsRes);
      if (playbooksRes.length > 0 && !selectedPlaybookId) {
        setSelectedPlaybookId(playbooksRes[0].playbook_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load SOAR dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerPlaybook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlaybookId) return;

    let parsedData = {};
    try {
      if (triggerPayload.trim()) {
        parsedData = JSON.parse(triggerPayload);
      }
    } catch {
      alert('Invalid JSON in trigger payload.');
      return;
    }

    setTriggering(true);
    try {
      const res = await soarApi.triggerPlaybook({
        playbook_identifier: selectedPlaybookId,
        trigger_source: triggerSource,
        source_id: sourceId,
        trigger_data: parsedData,
        requested_by: 'soc_analyst',
      });
      setShowTriggerModal(false);
      navigate(`/soc/automation/executions/${res.execution_id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to trigger playbook');
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="soar-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Zap size={20} color="#06b6d4" />
          <span>
            <strong>NexoraNet SOAR Simulation Engine:</strong> All playbook automations run in a safe, offline, deterministic sandbox with zero live infrastructure modification.
          </span>
        </div>
        <span className="soar-safety-badge">Simulation Mode Only</span>
      </div>

      {/* Header */}
      <div className="soar-header">
        <div>
          <h1 className="soar-title">
            <Cpu size={28} color="#06b6d4" /> Security Orchestration, Automation & Response (SOAR)
          </h1>
          <p className="soar-subtitle">
            Automate triage, threat enrichment, correlation, and response playbooks with human-in-the-loop analyst approvals.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            className="soar-btn soar-btn-primary"
            onClick={() => setShowTriggerModal(true)}
          >
            <Play size={16} /> Trigger Playbook
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="soar-nav-tabs">
        <Link to="/soc/automation" className="soar-tab-btn active">
          Overview Dashboard
        </Link>
        <Link to="/soc/automation/playbooks" className="soar-tab-btn">
          Playbooks Catalog ({playbooks.length})
        </Link>
        <Link to="/soc/automation/executions" className="soar-tab-btn">
          Execution Logs
        </Link>
      </div>

      {error && (
        <div style={{ padding: 14, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5', marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Approval Alert if executions are paused */}
      {metrics && metrics.waiting_approval > 0 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid #f59e0b',
          borderRadius: 8,
          padding: '14px 20px',
          marginBottom: 24,
          color: '#fbbf24'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <AlertTriangle size={24} />
            <div>
              <strong>Action Required: {metrics.waiting_approval} Playbook Execution(s) Awaiting Analyst Approval</strong>
              <div style={{ fontSize: '0.85rem', color: '#fde68a' }}>
                High-risk actions require verification before the state machine proceeds.
              </div>
            </div>
          </div>
          <Link to="/soc/automation/executions?status=WAITING_APPROVAL" className="soar-btn" style={{ background: '#f59e0b', color: '#000', fontWeight: 700 }}>
            Review Pending Approvals
          </Link>
        </div>
      )}

      {/* KPI Metrics */}
      <div className="soar-metrics-grid">
        <div className="soar-metric-card">
          <div className="soar-metric-label">Total Playbooks</div>
          <div className="soar-metric-value">{metrics ? metrics.total_playbooks : '--'}</div>
          <div className="soar-metric-subtext">{metrics ? `${metrics.enabled_playbooks} active & armed` : 'Loading...'}</div>
        </div>
        <div className="soar-metric-card">
          <div className="soar-metric-label">Total Executions</div>
          <div className="soar-metric-value">{metrics ? metrics.total_executions : '--'}</div>
          <div className="soar-metric-subtext">{metrics ? `${metrics.completed_executions} completed` : 'Loading...'}</div>
        </div>
        <div className="soar-metric-card">
          <div className="soar-metric-label">Success Rate</div>
          <div className="soar-metric-value" style={{ color: '#34d399' }}>
            {metrics ? `${metrics.success_rate_percent}%` : '--'}
          </div>
          <div className="soar-metric-subtext">Deterministic execution rate</div>
        </div>
        <div className="soar-metric-card">
          <div className="soar-metric-label">Analyst Hours Saved</div>
          <div className="soar-metric-value" style={{ color: '#38bdf8' }}>
            {metrics ? `${metrics.analyst_hours_saved}h` : '--'}
          </div>
          <div className="soar-metric-subtext">Simulated triage acceleration</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 24 }}>
        {/* Left Column: Recent Executions */}
        <div className="soar-card">
          <div className="soar-card-title">
            <span>Recent Playbook Executions</span>
            <Link to="/soc/automation/executions" style={{ fontSize: '0.85rem', color: '#06b6d4', textDecoration: 'none' }}>
              View All Executions &rarr;
            </Link>
          </div>

          {loading ? (
            <div style={{ padding: 24, textAlign: 'center', color: '#94a3b8' }}>Loading execution history...</div>
          ) : executions.length === 0 ? (
            <div style={{ padding: 32, textAlign: 'center', color: '#64748b' }}>
              No playbook executions yet. Click &quot;Trigger Playbook&quot; above to run your first simulation!
            </div>
          ) : (
            <table className="soar-table">
              <thead>
                <tr>
                  <th>Execution ID</th>
                  <th>Playbook</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Trigger Source</th>
                  <th>Started</th>
                </tr>
              </thead>
              <tbody>
                {executions.map((ex) => (
                  <tr
                    key={ex.id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/soc/automation/executions/${ex.execution_id}`)}
                  >
                    <td>
                      <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 600 }}>
                        {ex.execution_id.substring(0, 14)}...
                      </span>
                    </td>
                    <td>
                      <strong>{ex.playbook_name}</strong>
                    </td>
                    <td>
                      <span className={`soar-badge ${ex.status}`}>{ex.status}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                        {ex.current_step_order} / {ex.total_steps} steps
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.85rem' }}>{ex.trigger_source}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        {new Date(ex.started_at).toLocaleTimeString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Right Column: Top Playbooks & Fast Launch */}
        <div>
          <div className="soar-card">
            <div className="soar-card-title">Top Active Playbooks</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {playbooks.slice(0, 5).map((pb) => (
                <div
                  key={pb.id}
                  style={{
                    padding: '12px 14px',
                    background: '#1e293b',
                    borderRadius: 8,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f8fafc' }}>
                      <Link to={`/soc/automation/playbooks/${pb.playbook_id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                        {pb.name}
                      </Link>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                      {pb.steps_count ?? pb.steps?.length ?? 4} steps &bull; {pb.trigger_type}
                    </div>
                  </div>
                  <span className={`soar-badge ${pb.risk_level}`}>{pb.risk_level}</span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 16 }}>
              <Link to="/soc/automation/playbooks" className="soar-btn" style={{ width: '100%', justifyContent: 'center' }}>
                Browse All Playbooks
              </Link>
            </div>
          </div>

          <div className="soar-card">
            <div className="soar-card-title">SOAR Architecture Guide</div>
            <ul style={{ paddingLeft: 18, fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.6, margin: 0 }}>
              <li><strong>Zero Execution:</strong> Pure declarative step transitions.</li>
              <li><strong>Safe Isolation:</strong> Endpoint containment simulates network isolation without touching host interfaces.</li>
              <li><strong>Idempotency:</strong> Re-executing identical alert triggers deduplicates safely.</li>
              <li><strong>Analyst Gate:</strong> High/Critical actions require manual human signoff.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Trigger Modal */}
      {showTriggerModal && (
        <div className="soar-modal-backdrop" onClick={() => setShowTriggerModal(false)}>
          <div className="soar-modal" onClick={(e) => e.stopPropagation()}>
            <div className="soar-modal-header">
              <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#f8fafc' }}>
                Simulate Playbook Execution
              </h2>
              <button
                onClick={() => setShowTriggerModal(false)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1.2rem', cursor: 'pointer' }}
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleTriggerPlaybook}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                  Select Playbook:
                </label>
                <select
                  value={selectedPlaybookId}
                  onChange={(e) => setSelectedPlaybookId(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 10,
                    borderRadius: 6,
                    background: '#1e293b',
                    border: '1px solid #334155',
                    color: '#fff',
                  }}
                  required
                >
                  {playbooks.map((pb) => (
                    <option key={pb.id} value={pb.playbook_id}>
                      [{pb.playbook_id}] {pb.name} ({pb.risk_level} risk)
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                    Trigger Source:
                  </label>
                  <input
                    type="text"
                    value={triggerSource}
                    onChange={(e) => setTriggerSource(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 10,
                      borderRadius: 6,
                      background: '#1e293b',
                      border: '1px solid #334155',
                      color: '#fff',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                    Source Entity ID:
                  </label>
                  <input
                    type="text"
                    value={sourceId}
                    onChange={(e) => setSourceId(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 10,
                      borderRadius: 6,
                      background: '#1e293b',
                      border: '1px solid #334155',
                      color: '#fff',
                    }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                  Simulated Event JSON (Passed to Condition Evaluator & Step Handlers):
                </label>
                <textarea
                  rows={6}
                  value={triggerPayload}
                  onChange={(e) => setTriggerPayload(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 10,
                    borderRadius: 6,
                    background: '#0f172a',
                    border: '1px solid #334155',
                    color: '#38bdf8',
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                <button
                  type="button"
                  className="soar-btn"
                  onClick={() => setShowTriggerModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="soar-btn soar-btn-primary"
                  disabled={triggering}
                >
                  {triggering ? 'Executing Playbook...' : 'Execute Simulation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
