import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  HelpCircle,
  Send,
  Target,
  AlertTriangle,
} from 'lucide-react';
import { socScenarioApi } from '../../services/socScenarioApi';
import type {
  ScenarioAttempt,
  ScenarioStage,
  SocScenarioDetail,
} from '../../types/socScenario';
import '../../components/soc_scenarios/socScenarios.css';

const STAGES: ScenarioStage[] = [
  'INITIAL_SIGNAL',
  'EVIDENCE_SELECTION',
  'CORRELATION',
  'HYPOTHESIS',
  'VALIDATION',
  'MITRE_MAPPING',
  'RESPONSE_DECISION',
  'OUTCOME',
  'LESSONS_LEARNED',
];

const STAGE_LABELS: Record<ScenarioStage, string> = {
  INITIAL_SIGNAL: '1. Initial Signal',
  EVIDENCE_SELECTION: '2. Evidence Selection',
  CORRELATION: '3. Correlation',
  HYPOTHESIS: '4. Threat Hypothesis',
  VALIDATION: '5. Validation',
  MITRE_MAPPING: '6. MITRE Mapping',
  RESPONSE_DECISION: '7. Response Decision',
  OUTCOME: '8. Simulated Outcome',
  LESSONS_LEARNED: '9. Lessons Learned',
};

export const SocScenarioWorkspacePage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<ScenarioAttempt | null>(null);
  const [scenario, setScenario] = useState<SocScenarioDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Current stage state
  const [currentStage, setCurrentStage] = useState<ScenarioStage>('INITIAL_SIGNAL');
  const [stageData, setStageData] = useState<Record<string, any>>({});
  const [savingStage, setSavingStage] = useState(false);

  // Progressive Hint State
  const [hints, setHints] = useState<string[]>([]);
  const [hintLoading, setHintLoading] = useState(false);
  const [showHintModal, setShowHintModal] = useState(false);

  // Parsed scenario components
  const [initialSignal, setInitialSignal] = useState<any>({});
  const [availableEvidence, setAvailableEvidence] = useState<any[]>([]);
  const [correlationTargets, setCorrelationTargets] = useState<any[]>([]);
  const [hypothesesOptions, setHypothesesOptions] = useState<any[]>([]);
  const [mitreOptions, setMitreOptions] = useState<any[]>([]);
  const [responseOptions, setResponseOptions] = useState<any[]>([]);

  useEffect(() => {
    if (!attemptId) return;
    const fetchAttemptAndScenario = async () => {
      setLoading(true);
      setError(null);
      try {
        const att = await socScenarioApi.getAttempt(attemptId);
        setAttempt(att);
        setCurrentStage(att.current_stage);

        let parsedStageData: Record<string, any> = {};
        try {
          if (att.stage_data_json) parsedStageData = JSON.parse(att.stage_data_json);
        } catch {}
        setStageData(parsedStageData);

        // Fetch Scenario Detail
        const scen = await socScenarioApi.getScenarioDetail(att.scenario_id);
        setScenario(scen);

        // Parse scenario definitions
        try {
          if (scen.initial_signal_json) setInitialSignal(JSON.parse(scen.initial_signal_json));
          if (scen.available_evidence_json) setAvailableEvidence(JSON.parse(scen.available_evidence_json));
          if (scen.correlation_targets_json) setCorrelationTargets(JSON.parse(scen.correlation_targets_json));
          if (scen.hypotheses_options_json) setHypothesesOptions(JSON.parse(scen.hypotheses_options_json));
          if (scen.mitre_techniques_json) setMitreOptions(JSON.parse(scen.mitre_techniques_json));
          if (scen.response_options_json) setResponseOptions(JSON.parse(scen.response_options_json));
        } catch (e) {
          console.error('Error parsing scenario JSON:', e);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load scenario attempt');
      } finally {
        setLoading(false);
      }
    };
    fetchAttemptAndScenario();
  }, [attemptId]);

  const handleSaveStage = async (advance: boolean = false) => {
    if (!attemptId) return;
    setSavingStage(true);
    try {
      const currentPayload = stageData[currentStage] || {};
      const updated = await socScenarioApi.updateStage(attemptId, {
        stage_name: currentStage,
        data: currentPayload,
        advance_stage: advance,
      });
      setAttempt(updated);
      if (advance) {
        setCurrentStage(updated.current_stage);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save stage progress');
    } finally {
      setSavingStage(false);
    }
  };

  const handleUnlockHint = async () => {
    if (!attemptId) return;
    setHintLoading(true);
    try {
      const res = await socScenarioApi.unlockHint(attemptId);
      setHints((prev) => [...prev, res.hint]);
      if (attempt) {
        setAttempt({ ...attempt, hints_used: res.hints_used });
      }
      setShowHintModal(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to unlock hint');
    } finally {
      setHintLoading(false);
    }
  };

  const handleSubmitFinalInvestigation = async () => {
    if (!attemptId) return;
    const confirm = window.confirm(
      'Are you ready to submit your investigation for evaluation? Your response will be scored using the transparent 7-factor rubric.'
    );
    if (!confirm) return;

    try {
      await socScenarioApi.submitAttempt(attemptId);
      navigate(`/soc/scenarios/results/${attemptId}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to submit investigation');
    }
  };

  const updateCurrentStageData = (key: string, value: any) => {
    setStageData((prev) => ({
      ...prev,
      [currentStage]: {
        ...(prev[currentStage] || {}),
        [key]: value,
      },
    }));
  };

  const currentIdx = STAGES.indexOf(currentStage);

  if (loading) {
    return (
      <div className="scen-container" style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>
        Loading incident investigation workspace...
      </div>
    );
  }

  if (error || !attempt || !scenario) {
    return (
      <div className="scen-container">
        <div style={{ padding: 20, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5' }}>
          {error || 'Scenario or attempt not found.'}
        </div>
        <div style={{ marginTop: 16 }}>
          <Link to="/soc/scenarios" className="soar-btn">
            &larr; Back to Scenarios Catalog
          </Link>
        </div>
      </div>
    );
  }

  const stageForm = stageData[currentStage] || {};

  return (
    <div className="scen-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <span>
          <strong>Synthetic Investigation Sandbox:</strong> All telemetry, process logs, and alerts are simulated offline data. Zero live production systems are touched.
        </span>
        <span className="soar-safety-badge">Simulation Mode</span>
      </div>

      {/* Header */}
      <div className="scen-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 700 }}>
              {scenario.scenario_id}
            </span>
            <span className={`scen-diff-badge ${scenario.difficulty}`}>{scenario.difficulty}</span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              Hints Used: <strong>{attempt.hints_used}</strong>
            </span>
          </div>
          <h1 className="scen-title">{scenario.title}</h1>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button
            className="soar-btn"
            onClick={() => setShowHintModal(true)}
            style={{ color: '#fbbf24', borderColor: 'rgba(245, 158, 11, 0.4)' }}
          >
            <HelpCircle size={16} /> Get Hint (-5% penalty)
          </button>
          <button
            className="soar-btn soar-btn-primary"
            onClick={() => handleSaveStage(false)}
            disabled={savingStage}
          >
            {savingStage ? 'Saving...' : 'Save Draft'}
          </button>
        </div>
      </div>

      {/* 9-Stage Stepper Navigation */}
      <div className="scen-stepper">
        {STAGES.map((stg, idx) => {
          const isActive = stg === currentStage;
          const isCompleted = STAGES.indexOf(attempt.current_stage) > idx;

          return (
            <button
              key={stg}
              className={`scen-step-node ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
              onClick={() => setCurrentStage(stg)}
            >
              <span className="scen-step-num">{idx + 1}</span>
              <span>{STAGE_LABELS[stg].split('. ')[1]}</span>
            </button>
          );
        })}
      </div>

      {/* Main Workspace Layout */}
      <div className="scen-workspace-layout">
        {/* Left Column: Interactive Stage Content */}
        <div className="scen-main-panel">
          {/* Stage 1: Initial Signal */}
          {currentStage === 'INITIAL_SIGNAL' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 1: Initial Security Signal &amp; Alert Triage
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Review the incoming SOC alert details and initial detection telemetry.
              </p>

              <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: 18, marginBottom: 20 }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14, marginBottom: 16 }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Alert Name</span>
                    <div style={{ fontWeight: 600, color: '#f8fafc' }}>{initialSignal.alert_name || 'Suspicious Activity Detected'}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Target Host</span>
                    <div style={{ fontWeight: 600, color: '#38bdf8', fontFamily: 'monospace' }}>{initialSignal.target_host || 'SRV-CORP-01'}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Reported Severity</span>
                    <div style={{ fontWeight: 600, color: '#fb923c' }}>{initialSignal.severity || 'HIGH'}</div>
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Detection Summary</span>
                  <p style={{ margin: '4px 0 0 0', color: '#cbd5e1', fontSize: '0.9rem', lineHeight: 1.5 }}>
                    {initialSignal.summary || scenario.description}
                  </p>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                  Analyst Initial Assessment &amp; Triage Notes:
                </label>
                <textarea
                  rows={4}
                  className="scen-input"
                  style={{ width: '100%' }}
                  placeholder="Record your initial impressions, priority assessment, and potential attack vectors to explore..."
                  value={stageForm.triage_notes || ''}
                  onChange={(e) => updateCurrentStageData('triage_notes', e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Stage 2: Evidence Selection */}
          {currentStage === 'EVIDENCE_SELECTION' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 2: Evidence Selection &amp; Artifact Identification
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Analyze the collected host and network artifacts. Select all evidence items relevant to the ongoing incident while filtering out background benign noise.
              </p>

              <div className="scen-evidence-grid">
                {availableEvidence.map((ev, i) => {
                  const selectedItems = stageForm.selected_evidence || [];
                  const isSelected = selectedItems.includes(ev.id || i);

                  return (
                    <div
                      key={ev.id || i}
                      className={`scen-evidence-card ${isSelected ? 'selected' : ''}`}
                      onClick={() => {
                        const newSelected = isSelected
                          ? selectedItems.filter((id: any) => id !== (ev.id || i))
                          : [...selectedItems, ev.id || i];
                        updateCurrentStageData('selected_evidence', newSelected);
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontFamily: 'monospace' }}>
                          {ev.type || 'ARTIFACT'}
                        </span>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          readOnly
                          style={{ accentColor: '#06b6d4' }}
                        />
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4 }}>
                        {ev.title || ev.name}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                        {ev.details || ev.description}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Stage 3: Correlation */}
          {currentStage === 'CORRELATION' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 3: Multi-Source Correlation
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Correlate the selected artifacts across host telemetry, network traffic, user identity, and parent-child execution chains.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {correlationTargets.map((target, idx) => (
                  <div key={idx} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 14 }}>
                    <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: 6 }}>
                      {target.label || `Correlation Link ${idx + 1}`}
                    </div>
                    <p style={{ margin: '0 0 10px 0', fontSize: '0.82rem', color: '#94a3b8' }}>
                      {target.prompt || 'Explain how this artifact connects to the primary compromised asset.'}
                    </p>
                    <input
                      type="text"
                      className="scen-input"
                      style={{ width: '100%' }}
                      placeholder="Enter correlation deduction..."
                      value={stageForm[`corr_${idx}`] || ''}
                      onChange={(e) => updateCurrentStageData(`corr_${idx}`, e.target.value)}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stage 4: Hypothesis */}
          {currentStage === 'HYPOTHESIS' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 4: Formulate Threat Hypothesis
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Based on correlation and identified artifacts, what is the most likely root-cause and adversary attack vector?
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 20 }}>
                {hypothesesOptions.map((h, i) => (
                  <label
                    key={i}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                      padding: 14,
                      background: stageForm.hypothesis === (h.id || i) ? 'rgba(6, 182, 212, 0.1)' : '#1e293b',
                      border: `1px solid ${stageForm.hypothesis === (h.id || i) ? '#06b6d4' : '#334155'}`,
                      borderRadius: 8,
                      cursor: 'pointer',
                    }}
                  >
                    <input
                      type="radio"
                      name="hypothesis"
                      checked={stageForm.hypothesis === (h.id || i)}
                      onChange={() => updateCurrentStageData('hypothesis', h.id || i)}
                      style={{ marginTop: 3, accentColor: '#06b6d4' }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
                        {h.title || h.statement}
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: 4 }}>
                        {h.details || h.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Stage 5: Validation */}
          {currentStage === 'VALIDATION' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 5: Hypothesis Validation &amp; Verification
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Validate your hypothesis with secondary indicators, log timestamps, and verification queries.
              </p>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                  Validation Findings &amp; Evidence Confirmation:
                </label>
                <textarea
                  rows={5}
                  className="scen-input"
                  style={{ width: '100%' }}
                  placeholder="Document how secondary log sources and IOC checks prove or disprove the hypothesis..."
                  value={stageForm.validation_notes || ''}
                  onChange={(e) => updateCurrentStageData('validation_notes', e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Stage 6: MITRE ATT&CK Mapping */}
          {currentStage === 'MITRE_MAPPING' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 6: MITRE ATT&amp;CK Framework Mapping
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Select all ATT&amp;CK Tactics and Techniques observed during the incident lifecycle.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
                {mitreOptions.map((m, idx) => {
                  const selectedTechniques = stageForm.selected_mitre || [];
                  const isSelected = selectedTechniques.includes(m.technique_id || m.id || idx);

                  return (
                    <div
                      key={idx}
                      style={{
                        padding: 12,
                        background: isSelected ? 'rgba(6, 182, 212, 0.1)' : '#1e293b',
                        border: `1px solid ${isSelected ? '#06b6d4' : '#334155'}`,
                        borderRadius: 6,
                        cursor: 'pointer',
                      }}
                      onClick={() => {
                        const val = m.technique_id || m.id || idx;
                        const updated = isSelected
                          ? selectedTechniques.filter((t: any) => t !== val)
                          : [...selectedTechniques, val];
                        updateCurrentStageData('selected_mitre', updated);
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                        <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 700, fontSize: '0.85rem' }}>
                          {m.technique_id || `T10${idx + 50}`}
                        </span>
                        <input type="checkbox" checked={isSelected} readOnly style={{ accentColor: '#06b6d4' }} />
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{m.name || m.title}</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{m.tactic || 'Execution / Persistence'}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Stage 7: Response Decision */}
          {currentStage === 'RESPONSE_DECISION' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 7: Incident Response Actions
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Select appropriate containment, eradication, and recovery response actions to halt the adversary.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {responseOptions.map((resp, i) => {
                  const selectedActions = stageForm.selected_responses || [];
                  const isSelected = selectedActions.includes(resp.id || i);

                  return (
                    <div
                      key={i}
                      style={{
                        padding: 14,
                        background: isSelected ? 'rgba(16, 185, 129, 0.1)' : '#1e293b',
                        border: `1px solid ${isSelected ? '#10b981' : '#334155'}`,
                        borderRadius: 8,
                        cursor: 'pointer',
                      }}
                      onClick={() => {
                        const val = resp.id || i;
                        const updated = isSelected
                          ? selectedActions.filter((r: any) => r !== val)
                          : [...selectedActions, val];
                        updateCurrentStageData('selected_responses', updated);
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                        <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.95rem' }}>
                          {resp.action_title || resp.title || resp.name}
                        </span>
                        <input type="checkbox" checked={isSelected} readOnly style={{ accentColor: '#10b981' }} />
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                        {resp.description || resp.details}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Stage 8: Simulated Outcome */}
          {currentStage === 'OUTCOME' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 8: Simulated Response Execution &amp; Impact
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Simulating containment triggers, DNS blackholing, credential resets, and endpoint isolation.
              </p>

              <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: 18, marginBottom: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#34d399', marginBottom: 10 }}>
                  <CheckCircle2 size={20} />
                  <strong>Simulated Remediation Actions Deployed Successfully</strong>
                </div>
                <p style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: 1.5, margin: 0 }}>
                  Endpoint isolation rules simulated on host telemetry. Malicious C2 egress IP blocked at virtual perimeter. Malicious process trees flagged for termination.
                </p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                  Analyst Outcome Evaluation Notes:
                </label>
                <textarea
                  rows={4}
                  className="scen-input"
                  style={{ width: '100%' }}
                  placeholder="Record verification notes confirming the threat has been neutralized without unintended business downtime..."
                  value={stageForm.outcome_notes || ''}
                  onChange={(e) => updateCurrentStageData('outcome_notes', e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Stage 9: Lessons Learned */}
          {currentStage === 'LESSONS_LEARNED' && (
            <div>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: 12 }}>
                Stage 9: Post-Incident Review &amp; Lessons Learned
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: 20 }}>
                Final step: Document preventative controls and posture recommendations before submitting your investigation for grading.
              </p>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: 6 }}>
                  Preventative Security Recommendations (Gaps &amp; Hardening):
                </label>
                <textarea
                  rows={5}
                  className="scen-input"
                  style={{ width: '100%' }}
                  placeholder="What controls (MFA, EDR rules, network segmentation, least privilege) would prevent recurrence?"
                  value={stageForm.lessons_notes || ''}
                  onChange={(e) => updateCurrentStageData('lessons_notes', e.target.value)}
                />
              </div>

              <div style={{
                background: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid #06b6d4',
                borderRadius: 8,
                padding: 16,
                marginBottom: 20,
              }}>
                <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: 4 }}>
                  Ready to Complete Scenario?
                </div>
                <p style={{ fontSize: '0.85rem', color: '#cbd5e1', margin: '0 0 12px 0' }}>
                  Submitting will evaluate all 9 stages against the scenario scoring rubric (Signal Analysis, Evidence Relevance, Correlation Accuracy, Hypothesis Correctness, MITRE Mapping, Response Actions, and Hint Penalties).
                </p>
                <button
                  className="soar-btn soar-btn-success"
                  onClick={handleSubmitFinalInvestigation}
                >
                  <Send size={16} /> Submit Investigation for Rubric Evaluation
                </button>
              </div>
            </div>
          )}

          {/* Stage Footer Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 32, paddingTop: 20, borderTop: '1px solid #334155' }}>
            <button
              className="soar-btn"
              disabled={currentIdx === 0}
              onClick={() => setCurrentStage(STAGES[currentIdx - 1])}
            >
              <ArrowLeft size={16} /> Previous Stage
            </button>

            {currentIdx < STAGES.length - 1 ? (
              <button
                className="soar-btn soar-btn-primary"
                onClick={() => handleSaveStage(true)}
              >
                Save &amp; Advance to {STAGE_LABELS[STAGES[currentIdx + 1]].split('. ')[1]} <ArrowRight size={16} />
              </button>
            ) : (
              <button
                className="soar-btn soar-btn-success"
                onClick={handleSubmitFinalInvestigation}
              >
                Submit Investigation &rarr;
              </button>
            )}
          </div>
        </div>

        {/* Right Column: Scenario Objectives & Unlocked Hints */}
        <div className="scen-side-panel">
          <div className="scen-side-card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Target size={16} color="#06b6d4" /> Learning Objectives
            </h3>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
              {scenario.learning_objectives}
            </div>
          </div>

          <div className="scen-side-card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
              <HelpCircle size={16} color="#fbbf24" /> Progressive Hints ({hints.length})
            </h3>
            {hints.length === 0 ? (
              <div style={{ fontSize: '0.82rem', color: '#64748b' }}>
                No hints unlocked yet. Need help? Click &quot;Get Hint&quot; at the top.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {hints.map((hintText, hIdx) => (
                  <div
                    key={hIdx}
                    style={{
                      padding: 10,
                      background: 'rgba(245, 158, 11, 0.1)',
                      border: '1px solid rgba(245, 158, 11, 0.3)',
                      borderRadius: 6,
                      fontSize: '0.82rem',
                      color: '#fde68a',
                    }}
                  >
                    <strong>Hint #{hIdx + 1}:</strong> {hintText}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Hint Confirmation Modal */}
      {showHintModal && (
        <div className="soar-modal-backdrop" onClick={() => setShowHintModal(false)}>
          <div className="soar-modal" onClick={(e) => e.stopPropagation()}>
            <div className="soar-modal-header">
              <h2 style={{ margin: 0, fontSize: '1.2rem', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={20} /> Unlock Progressive Hint
              </h2>
              <button
                onClick={() => setShowHintModal(false)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1.2rem', cursor: 'pointer' }}
              >
                &times;
              </button>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', lineHeight: 1.5, marginBottom: 20 }}>
              Unlocking a hint will provide guidance tailored to the next investigation phase.
              Each unlocked hint applies a <strong>-5.0 point penalty</strong> to your final scenario score.
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button className="soar-btn" onClick={() => setShowHintModal(false)}>
                Cancel
              </button>
              <button
                className="soar-btn"
                style={{ background: '#d97706', borderColor: '#d97706', color: '#000', fontWeight: 700 }}
                onClick={handleUnlockHint}
                disabled={hintLoading}
              >
                {hintLoading ? 'Unlocking...' : 'Accept Penalty & Unlock Hint'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
