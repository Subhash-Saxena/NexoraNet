import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Clock,
  ExternalLink,
  Play,
  RefreshCw,
  ShieldAlert,
  X,
} from 'lucide-react'
import { SiemNav } from '../components/siem/SiemNav'
import { siemApi } from '../services/siemApi'
import type {
  CorrelationAlert,
  LogCorrelationRule,
  RuleEvaluationResult,
  SecurityLogDataset,
} from '../types/siem'
import '../components/siem/siem.css'

export const SiemRulesPage: React.FC = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'RULES' | 'ALERTS'>('RULES')

  const [rules, setRules] = useState<LogCorrelationRule[]>([])
  const [alerts, setAlerts] = useState<CorrelationAlert[]>([])
  const [datasets, setDatasets] = useState<SecurityLogDataset[]>([])
  const [error, setError] = useState<string | null>(null)

  // Status Filter for Alerts
  const [alertStatusFilter, setAlertStatusFilter] = useState<string>('ALL')

  // Rule Tester / Dry-Run Modal
  const [selectedRule, setSelectedRule] = useState<LogCorrelationRule | null>(null)
  const [testDatasetId, setTestDatasetId] = useState<number | undefined>(undefined)
  const [evalResult, setEvalResult] = useState<RuleEvaluationResult | null>(null)
  const [evaluating, setEvaluating] = useState<boolean>(false)

  const loadData = async () => {
    try {
      setError(null)
      const [rList, aList, dList] = await Promise.all([
        siemApi.listRules(),
        siemApi.listAlerts(alertStatusFilter !== 'ALL' ? { status: alertStatusFilter } : undefined),
        siemApi.listDatasets(),
      ])
      setRules(rList)
      setAlerts(aList)
      setDatasets(dList)
      if (dList.length > 0 && !testDatasetId) {
        setTestDatasetId(dList[0].id)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load rules and alerts')
    }
  }

  useEffect(() => {
    loadData()
  }, [alertStatusFilter])

  // Dry-run tester
  const handleOpenTester = (rule: LogCorrelationRule) => {
    setSelectedRule(rule)
    setEvalResult(null)
  }

  const handleExecuteDryRun = async () => {
    if (!selectedRule) return
    try {
      setEvaluating(true)
      const result = await siemApi.evaluateRule(selectedRule.id, testDatasetId)
      setEvalResult(result)
    } catch (err: unknown) {
      window.alert(`Dry-run evaluation failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setEvaluating(false)
    }
  }

  // Triage alert
  const handleUpdateStatus = async (alertId: number, newStatus: string) => {
    try {
      await siemApi.updateAlertStatus(alertId, newStatus)
      loadData()
    } catch (err: unknown) {
      window.alert(`Status update failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  const handleEscalateToSoc = async (alertItem: CorrelationAlert) => {
    try {
      const res = await siemApi.investigateInSoc(undefined, alertItem.id)
      if (res.redirect_url) {
        navigate(res.redirect_url)
      } else {
        window.alert(`Successfully escalated alert ${alertItem.alert_id} to SOC Investigation!`)
        loadData()
      }
    } catch (err: unknown) {
      window.alert(`SOC escalation failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  const handleStartThreatHunt = async (alertItem: CorrelationAlert) => {
    try {
      const res = await siemApi.startThreatHunt(
        undefined,
        alertItem.id,
        `Threat hunt investigating correlation alert: ${alertItem.title}`
      )
      if (res.redirect_url) {
        navigate(res.redirect_url)
      } else {
        window.alert(`Successfully initiated Threat Hunt: ${res.hunt_code}!`)
      }
    } catch (err: unknown) {
      window.alert(`Threat hunt initiation failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  return (
    <div className="siem-container">
      {/* Header */}
      <div className="siem-header">
        <div className="siem-header-left">
          <div className="siem-title-row">
            <h1>
              <ShieldAlert className="text-cyan-400" size={26} />
              Correlation Rules & Behavioral Alerts
            </h1>
            <span className="siem-tag">DETECTION LOGIC</span>
          </div>
          <p className="siem-subtitle">
            Configure multi-event aggregation rules, evaluate detection windows, dry-run against historical datasets, and triage alerts.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', background: '#111827', padding: '0.25rem', borderRadius: '0.5rem', border: '1px solid #1f2937' }}>
          <button
            className={`quick-filter-chip ${activeTab === 'RULES' ? 'active' : ''}`}
            onClick={() => setActiveTab('RULES')}
          >
            Correlation Rules ({rules.length})
          </button>
          <button
            className={`quick-filter-chip ${activeTab === 'ALERTS' ? 'active' : ''}`}
            onClick={() => setActiveTab('ALERTS')}
          >
            Correlation Alerts ({alerts.length})
          </button>
        </div>
      </div>

      <SiemNav />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239,68,68,0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', color: '#f87171' }}>
          {error}
        </div>
      )}

      {/* Tab 1: Rules List */}
      {activeTab === 'RULES' && (
        <div className="siem-table-container">
          <div className="siem-table-toolbar">
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>
              Educational Correlation Rules Catalog ({rules.length} Rules)
            </span>
            <span style={{ fontSize: '0.75rem' }}>Thresholds & Sliding Time Windows</span>
          </div>

          <table className="siem-events-table">
            <thead>
              <tr>
                <th>Rule Code</th>
                <th>Rule Name & Objective</th>
                <th>Category</th>
                <th>Severity</th>
                <th>Sliding Window</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule) => (
                <tr key={rule.id}>
                  <td className="mono-cell" style={{ color: '#38bdf8', fontWeight: 600 }}>{rule.stable_id}</td>
                  <td>
                    <div style={{ fontWeight: 500, color: '#f1f5f9' }}>{rule.name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>{rule.description}</div>
                  </td>
                  <td><span className="cat-badge">{rule.category}</span></td>
                  <td><span className={`sev-badge sev-${rule.severity}`}>{rule.severity}</span></td>
                  <td className="mono-cell">
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={12} /> {rule.time_window_seconds}s
                    </span>
                  </td>
                  <td>
                    <span style={{ color: rule.status === 'ENABLED' ? '#34d399' : '#94a3b8', fontSize: '0.75rem', fontWeight: 600 }}>
                      {rule.status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="siem-btn-secondary"
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                      onClick={() => handleOpenTester(rule)}
                      title="Dry-run this rule against a dataset without triggering real alerts"
                    >
                      <Play size={12} /> Dry-Run Test
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 2: Alerts Triage */}
      {activeTab === 'ALERTS' && (
        <div className="siem-table-container">
          <div className="siem-table-toolbar">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ fontWeight: 600, color: '#f8fafc' }}>
                Correlation Alerts ({alerts.length})
              </span>
              <select
                className="condition-select"
                value={alertStatusFilter}
                onChange={(e) => setAlertStatusFilter(e.target.value)}
              >
                <option value="ALL">All Triage Statuses</option>
                <option value="NEW">NEW</option>
                <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                <option value="ESCALATED">ESCALATED</option>
                <option value="RESOLVED">RESOLVED</option>
                <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
              </select>
            </div>
            <button className="siem-btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={loadData}>
              <RefreshCw size={12} /> Refresh
            </button>
          </div>

          <table className="siem-events-table">
            <thead>
              <tr>
                <th>Alert Code</th>
                <th>Timestamp</th>
                <th>Title & Findings</th>
                <th>Severity</th>
                <th>Event Count</th>
                <th>Triage Status</th>
                <th>Escalations</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                    No alerts found for selected status filter.
                  </td>
                </tr>
              ) : (
                alerts.map((al) => (
                  <tr key={al.id}>
                    <td className="mono-cell" style={{ color: '#38bdf8' }}>{al.alert_id}</td>
                    <td className="mono-cell">{new Date(al.timestamp).toLocaleTimeString()}</td>
                    <td>
                      <div style={{ fontWeight: 500, color: '#f8fafc' }}>{al.title}</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>{al.evidence_summary}</div>
                    </td>
                    <td><span className={`sev-badge sev-${al.severity}`}>{al.severity}</span></td>
                    <td style={{ fontWeight: 600 }}>{al.event_count} events</td>
                    <td>
                      <select
                        className="condition-select"
                        value={al.status}
                        onChange={(e) => handleUpdateStatus(al.id, e.target.value)}
                      >
                        <option value="NEW">NEW</option>
                        <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                        <option value="ESCALATED">ESCALATED</option>
                        <option value="RESOLVED">RESOLVED</option>
                        <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                      </select>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
                        <button
                          className="btn-escalate-soc"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={() => handleEscalateToSoc(al)}
                          title="Escalate directly into Step 12 SOC Investigation"
                        >
                          <ExternalLink size={12} /> SOC
                        </button>
                        <button
                          className="btn-escalate-hunt"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={() => handleStartThreatHunt(al)}
                          title="Start Step 14 Threat Hunt"
                        >
                          <ExternalLink size={12} /> Hunt
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Dry-Run Rule Tester Modal */}
      {selectedRule && (
        <div className="siem-modal-backdrop">
          <div className="siem-modal-box" style={{ width: '650px' }}>
            <div className="siem-modal-header">
              <h3 style={{ margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Play size={18} color="#38bdf8" />
                Dry-Run Rule Tester: {selectedRule.stable_id}
              </h3>
              <button className="drawer-close" onClick={() => setSelectedRule(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="siem-modal-body">
              <div>
                <strong style={{ color: '#f8fafc' }}>{selectedRule.name}</strong>
                <p style={{ fontSize: '0.8125rem', color: '#94a3b8', margin: '0.25rem 0' }}>{selectedRule.description}</p>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  Sliding Window: {selectedRule.time_window_seconds}s | Severity: {selectedRule.severity}
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.8125rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>
                  Target Dataset for Dry-Run:
                </label>
                <select
                  className="condition-select"
                  style={{ width: '100%' }}
                  value={testDatasetId ?? ''}
                  onChange={(e) => setTestDatasetId(Number(e.target.value))}
                >
                  {datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.stable_id} - {d.name} ({d.event_count} events)
                    </option>
                  ))}
                </select>
              </div>

              {evalResult && (
                <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '0.375rem', padding: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 600, color: '#38bdf8' }}>Evaluation Result</span>
                    <span className="cat-badge">{evalResult.matching_events_count} matching events</span>
                  </div>
                  <div style={{ fontSize: '0.8125rem', color: '#cbd5e1' }}>
                    {evalResult.evaluation_message}
                  </div>

                  {evalResult.sample_events && evalResult.sample_events.length > 0 && (
                    <div style={{ marginTop: '0.75rem' }}>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, marginBottom: '0.25rem' }}>
                        Sample Matching Telemetry Events:
                      </div>
                      <div style={{ maxHeight: '120px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        {evalResult.sample_events.slice(0, 5).map((ev) => (
                          <div key={ev.id} className="mono-cell" style={{ fontSize: '0.75rem', background: '#070a12', padding: '0.25rem 0.5rem', borderRadius: '2px', color: '#93c5fd' }}>
                            [{new Date(ev.timestamp).toLocaleTimeString()}] {ev.event_type} | host={ev.host || '-'} | user={ev.username || '-'} | src={ev.source_ip || '-'}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="siem-modal-footer">
              <button className="siem-btn-secondary" onClick={() => setSelectedRule(null)}>
                Close
              </button>
              <button
                className="siem-btn-primary"
                onClick={handleExecuteDryRun}
                disabled={evaluating}
              >
                {evaluating ? 'Testing...' : 'Execute Dry-Run'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
