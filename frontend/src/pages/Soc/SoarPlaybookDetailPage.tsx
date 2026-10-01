import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Play, Sparkles, Layers } from 'lucide-react';
import { soarApi } from '../../services/soarApi';
import type { AutomationPlaybook, DryRunResponse } from '../../types/soar';
import '../../components/soar/soar.css';

export const SoarPlaybookDetailPage: React.FC = () => {
  const { playbookId } = useParams<{ playbookId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [playbook, setPlaybook] = useState<AutomationPlaybook | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'steps' | 'dry-run'>(
    searchParams.get('tab') === 'dry-run' ? 'dry-run' : 'steps'
  );

  // Dry-run simulator
  const [sampleEventJson, setSampleEventJson] = useState<string>(
    JSON.stringify(
      {
        ip: '198.51.100.25',
        hostname: 'FIN-SRV-02',
        username: 'victim_user',
        severity: 'HIGH',
        confidence: 85,
        threat_score: 90,
      },
      null,
      2
    )
  );
  const [dryRunLoading, setDryRunLoading] = useState(false);
  const [dryRunResult, setDryRunResult] = useState<DryRunResponse | null>(null);

  useEffect(() => {
    if (!playbookId) return;
    const fetchPlaybook = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await soarApi.getPlaybookDetail(playbookId);
        setPlaybook(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load playbook');
      } finally {
        setLoading(false);
      }
    };
    fetchPlaybook();
  }, [playbookId]);

  const handleExecuteDryRun = async () => {
    if (!playbook) return;
    let parsed: Record<string, any> = {};
    try {
      parsed = JSON.parse(sampleEventJson);
    } catch {
      alert('Sample Event must be valid JSON');
      return;
    }

    setDryRunLoading(true);
    try {
      const res = await soarApi.dryRunPlaybook(playbook.id, parsed);
      setDryRunResult(res);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Dry-run failed');
    } finally {
      setDryRunLoading(false);
    }
  };

  const handleLaunchSimulation = async () => {
    if (!playbook) return;
    let parsed: Record<string, any> = {};
    try {
      parsed = JSON.parse(sampleEventJson);
    } catch {
      parsed = {};
    }

    try {
      const exec = await soarApi.triggerPlaybook({
        playbook_identifier: playbook.playbook_id,
        trigger_source: 'PLAYBOOK_DETAIL_VIEW',
        source_id: `ALT-MANUAL-${Math.floor(1000 + Math.random() * 9000)}`,
        trigger_data: parsed,
        requested_by: 'soc_analyst',
      });
      navigate(`/soc/automation/executions/${exec.execution_id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to trigger execution');
    }
  };

  if (loading) {
    return (
      <div className="soar-container" style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>
        Loading playbook specifications...
      </div>
    );
  }

  if (error || !playbook) {
    return (
      <div className="soar-container">
        <div style={{ padding: 20, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5' }}>
          {error || 'Playbook not found.'}
        </div>
        <div style={{ marginTop: 16 }}>
          <Link to="/soc/automation/playbooks" className="soar-btn">
            &larr; Back to Playbooks
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
          <strong>Safe Simulation Environment:</strong> Inspect step triggers, condition logic, and dry-run execution traces without altering production systems.
        </span>
        <span className="soar-safety-badge">Offline Simulation</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <Link to="/soc/automation/playbooks" style={{ color: '#06b6d4', textDecoration: 'none', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
          <ArrowLeft size={16} /> Back to Playbook Catalog
        </Link>
        <div className="soar-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 700, fontSize: '0.95rem' }}>
                {playbook.playbook_id}
              </span>
              <span className={`soar-badge ${playbook.risk_level}`}>{playbook.risk_level} Risk</span>
              <span className={`soar-badge ${playbook.status}`}>{playbook.status}</span>
            </div>
            <h1 className="soar-title">{playbook.name}</h1>
            <p className="soar-subtitle">{playbook.description}</p>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="soar-btn soar-btn-primary" onClick={handleLaunchSimulation}>
              <Play size={16} /> Run Full Simulation
            </button>
          </div>
        </div>
      </div>

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
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Category</span>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: 2 }}>{playbook.category}</div>
        </div>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Trigger Type</span>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: 2 }}>{playbook.trigger_type}</div>
        </div>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Analyst Gate</span>
          <div style={{ fontWeight: 600, color: playbook.requires_approval ? '#fbbf24' : '#34d399', marginTop: 2 }}>
            {playbook.requires_approval ? 'Required (Human Approval)' : 'Fully Automated'}
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Total Steps</span>
          <div style={{ fontWeight: 600, color: '#38bdf8', marginTop: 2 }}>{playbook.steps?.length || 0} Sequential Steps</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="soar-nav-tabs">
        <button
          className={`soar-tab-btn ${activeTab === 'steps' ? 'active' : ''}`}
          onClick={() => setActiveTab('steps')}
        >
          <Layers size={16} /> Step Flowchart &amp; Conditions ({playbook.steps?.length || 0})
        </button>
        <button
          className={`soar-tab-btn ${activeTab === 'dry-run' ? 'active' : ''}`}
          onClick={() => setActiveTab('dry-run')}
        >
          <Sparkles size={16} /> Dry-Run Event Simulator
        </button>
      </div>

      {/* Step Sequence Tab */}
      {activeTab === 'steps' && (
        <div>
          <div className="soar-step-sequence">
            {playbook.steps && playbook.steps.map((step) => {
              let parsedParams = {};
              let parsedCond = null;
              try {
                if (step.parameters_json) parsedParams = JSON.parse(step.parameters_json);
                if (step.condition_json) parsedCond = JSON.parse(step.condition_json);
              } catch {}

              return (
                <div key={step.id} className="soar-step-item">
                  <div className="soar-step-order">{step.step_order}</div>
                  <div className="soar-step-content">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div className="soar-step-name">{step.name}</div>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <span style={{
                          fontSize: '0.75rem',
                          padding: '2px 8px',
                          borderRadius: 4,
                          background: '#1e293b',
                          color: '#38bdf8',
                          border: '1px solid #334155',
                          fontFamily: 'monospace'
                        }}>
                          {step.action_type}
                        </span>
                        {step.requires_approval && (
                          <span style={{
                            fontSize: '0.75rem',
                            padding: '2px 8px',
                            borderRadius: 4,
                            background: 'rgba(245, 158, 11, 0.2)',
                            color: '#fbbf24',
                            border: '1px solid rgba(245, 158, 11, 0.4)',
                            fontWeight: 600,
                          }}>
                            Approval Gate
                          </span>
                        )}
                        <span style={{
                          fontSize: '0.75rem',
                          padding: '2px 8px',
                          borderRadius: 4,
                          background: step.on_failure === 'CONTINUE' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                          color: step.on_failure === 'CONTINUE' ? '#60a5fa' : '#f87171',
                        }}>
                          On Failure: {step.on_failure}
                        </span>
                      </div>
                    </div>

                    {step.description && (
                      <p style={{ margin: '0 0 10px 0', fontSize: '0.88rem', color: '#94a3b8' }}>
                        {step.description}
                      </p>
                    )}

                    {/* Step Details & Conditions Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: parsedCond ? '1fr 1fr' : '1fr', gap: 12, marginTop: 10 }}>
                      <div style={{ background: '#0f172a', padding: 10, borderRadius: 6, fontSize: '0.8rem' }}>
                        <div style={{ color: '#64748b', marginBottom: 4, fontWeight: 600 }}>Action Parameters:</div>
                        <pre style={{ margin: 0, color: '#cbd5e1', overflowX: 'auto', fontFamily: 'monospace' }}>
                          {JSON.stringify(parsedParams, null, 2)}
                        </pre>
                      </div>

                      {parsedCond && (
                        <div style={{ background: '#0f172a', padding: 10, borderRadius: 6, fontSize: '0.8rem', borderLeft: '3px solid #06b6d4' }}>
                          <div style={{ color: '#06b6d4', marginBottom: 4, fontWeight: 600 }}>Condition Gate:</div>
                          <pre style={{ margin: 0, color: '#a5f3fc', overflowX: 'auto', fontFamily: 'monospace' }}>
                            {JSON.stringify(parsedCond, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Dry Run Simulator Tab */}
      {activeTab === 'dry-run' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div className="soar-card">
            <div className="soar-card-title">Sample Event Payload</div>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '0 0 12px 0' }}>
              Modify the JSON payload to test how the condition evaluator determines whether each step executes or is bypassed.
            </p>
            <textarea
              rows={14}
              value={sampleEventJson}
              onChange={(e) => setSampleEventJson(e.target.value)}
              style={{
                width: '100%',
                padding: 12,
                borderRadius: 8,
                background: '#0f172a',
                border: '1px solid #334155',
                color: '#38bdf8',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                marginBottom: 16,
              }}
            />
            <button
              className="soar-btn soar-btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={handleExecuteDryRun}
              disabled={dryRunLoading}
            >
              <Sparkles size={16} /> {dryRunLoading ? 'Evaluating Conditions...' : 'Run Dry-Run Evaluation'}
            </button>
          </div>

          <div className="soar-card">
            <div className="soar-card-title">Dry-Run Evaluation Preview</div>
            {!dryRunResult ? (
              <div style={{ textAlign: 'center', padding: 60, color: '#64748b', fontSize: '0.9rem' }}>
                Click &quot;Run Dry-Run Evaluation&quot; on the left to simulate condition evaluation for all steps in this playbook.
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14, fontSize: '0.85rem', color: '#94a3b8' }}>
                  <span>Total Steps: <strong>{dryRunResult.total_steps}</strong></span>
                  <span>Would Execute: <strong style={{ color: '#34d399' }}>{dryRunResult.executable_steps}</strong></span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {dryRunResult.simulated_steps.map((s) => (
                    <div
                      key={s.step_order}
                      style={{
                        padding: 12,
                        background: '#1e293b',
                        borderRadius: 6,
                        border: '1px solid #334155',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>
                          Step {s.step_order}: {s.step_name}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          {s.action_type}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        <span
                          style={{
                            fontSize: '0.75rem',
                            padding: '3px 8px',
                            borderRadius: 4,
                            fontWeight: 600,
                            background: s.condition_met ? 'rgba(16, 185, 129, 0.2)' : 'rgba(100, 116, 139, 0.2)',
                            color: s.condition_met ? '#34d399' : '#94a3b8',
                          }}
                        >
                          {s.condition_met ? 'Condition Passed' : 'Condition Skipped'}
                        </span>
                        {s.requires_approval && (
                          <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: 4, background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', fontWeight: 600 }}>
                            Pause for Approval
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
