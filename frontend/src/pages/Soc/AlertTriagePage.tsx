import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { SocAlertDetailResponse, TriageClassification } from '../../types/soc'
import '../../components/soc/soc.css'

export const AlertTriagePage: React.FC = () => {
  const { alertId } = useParams<{ alertId: string }>()
  const navigate = useNavigate()
  const [alert, setAlert] = useState<SocAlertDetailResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  // 12-Step Checklist State
  const [checkedSteps, setCheckedSteps] = useState<Record<number, boolean>>({})

  // Form State
  const [selectedClassification, setSelectedClassification] = useState<TriageClassification>('SUSPICIOUS')
  const [reason, setReason] = useState<string>('')
  const [targetStatus, setTargetStatus] = useState<string>('INVESTIGATING')
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const triageChecklist = [
    { step: 1, title: 'Check Alert Metadata', desc: 'Verify detection rule name, severity, confidence, and generated priority.' },
    { step: 2, title: 'Inspect Source Endpoint', desc: 'Identify source IP, port, device role, and packet volume in telemetry.' },
    { step: 3, title: 'Inspect Destination Endpoint', desc: 'Identify target service, expected port, and whether it is an internal host or external server.' },
    { step: 4, title: 'Review Protocol & Flags', desc: 'Analyze TCP flags (SYN/RST), DNS query types, ARP bindings, or HTTP headers.' },
    { step: 5, title: 'Inspect Packet Timeline', desc: 'Review packet timestamps to see if activity is bursty, periodic, or isolated.' },
    { step: 6, title: 'Check Volume & Packet Frequency', desc: 'Determine if packet rate is abnormal compared to baseline traffic.' },
    { step: 7, title: 'Check MITRE ATT&CK Mapping', desc: 'Understand the adversary tactic or technique simulated by this pattern.' },
    { step: 8, title: 'Correlate with Source Alerts', desc: 'Check if this source has generated scans, probes, or authentication errors.' },
    { step: 9, title: 'Correlate with Destination Alerts', desc: 'Check if other hosts are targeting or receiving traffic from this target.' },
    { step: 10, title: 'Formulate Working Hypothesis', desc: 'Articulate whether this represents benign testing, an FP, or suspicious anomaly.' },
    { step: 11, title: 'Select Triage Classification', desc: 'Choose Benign, Suspicious, False Positive, or Requires More Data.' },
    { step: 12, title: 'Record Justification & Audit Trail', desc: 'Write a concise technical rationale in the analyst audit note.' },
  ]

  const fetchAlert = async () => {
    if (!alertId) return
    try {
      setLoading(true)
      const data = await socApi.getAlertDetail(Number(alertId))
      setAlert(data)
      setSelectedClassification(data.classification !== 'UNREVIEWED' ? data.classification : 'SUSPICIOUS')
      setTargetStatus(data.status)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alert.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlert()
  }, [alertId])

  const toggleStep = (stepNumber: number) => {
    setCheckedSteps((prev) => ({
      ...prev,
      [stepNumber]: !prev[stepNumber],
    }))
  }

  const handleSubmitTriage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!alert) return
    if (!reason.trim()) {
      setError('A justification note is required to document analyst triage findings.')
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      await socApi.updateClassification(
        alert.id,
        selectedClassification,
        reason.trim(),
        targetStatus || undefined
      )
      setMessage('Triage decision submitted successfully! Audit log and alert status updated.')
      setTimeout(() => {
        navigate(`/soc/alerts/${alert.id}`)
      }, 1200)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit triage classification.')
    } finally {
      setSubmitting(false)
    }
  }

  const completedStepsCount = Object.values(checkedSteps).filter(Boolean).length

  return (
    <div className="soc-container">
      <SocHeader
        title={`Guided Alert Triage: Alert #${alertId}`}
        subtitle="Follow the 12-step SOC analyst investigation methodology to analyze evidence and classify this alert"
        actionButton={
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Link to={`/soc/alerts/${alertId}`} className="soc-btn soc-btn-secondary">
              ← View Full Alert
            </Link>
            <Link to="/soc/alerts" className="soc-btn soc-btn-secondary">
              Alert Queue
            </Link>
          </div>
        }
      />

      {message && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '6px', color: '#4ade80', fontSize: '0.88rem' }}>
          {message}
        </div>
      )}

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#f87171', fontSize: '0.88rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
          Loading alert triage checklist...
        </div>
      ) : !alert ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          Alert not found.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: '1.5rem' }}>
          {/* Left Column: 12-Step Guided Checklist */}
          <div className="soc-card">
            <div className="soc-card-header">
              <div className="soc-card-title">
                <span>📋</span> 12-Step Triage Checklist ({completedStepsCount}/12 Complete)
              </div>
              <button
                type="button"
                className="soc-btn soc-btn-secondary"
                style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                onClick={() => {
                  const allDone: Record<number, boolean> = {}
                  triageChecklist.forEach((s) => {
                    allDone[s.step] = true
                  })
                  setCheckedSteps(allDone)
                }}
              >
                Mark All Done
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {triageChecklist.map((item) => (
                <div
                  key={item.step}
                  onClick={() => toggleStep(item.step)}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    padding: '0.65rem 0.75rem',
                    background: checkedSteps[item.step] ? 'rgba(34, 197, 94, 0.05)' : 'rgba(15, 23, 42, 0.5)',
                    border: checkedSteps[item.step] ? '1px solid rgba(34, 197, 94, 0.25)' : '1px solid var(--soc-border)',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={!!checkedSteps[item.step]}
                    onChange={() => {}} // handled by parent onClick
                    style={{ marginTop: '0.2rem', cursor: 'pointer' }}
                    aria-label={`Step ${item.step}: ${item.title}`}
                  />
                  <div>
                    <div style={{ fontSize: '0.88rem', fontWeight: 600, color: checkedSteps[item.step] ? '#4ade80' : 'var(--soc-text-primary)' }}>
                      Step {item.step}: {item.title}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--soc-text-secondary)', marginTop: '0.15rem' }}>
                      {item.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Alert Snapshot & Classification Submission Form */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Quick Alert Snapshot */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🔍</span> Alert Evidence Summary
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--soc-text-muted)' }}>
                  Rule: {alert.rule_code || 'DETECTION'}
                </span>
              </div>

              <div style={{ fontSize: '0.85rem', color: 'var(--soc-text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <div><strong>Title:</strong> {alert.title}</div>
                <div><strong>Severity:</strong> {alert.severity} • <strong>Priority:</strong> {alert.priority}</div>
                <div><strong>Source:</strong> {alert.source_ip || '*'}:{alert.source_port || '*'}</div>
                <div><strong>Destination:</strong> {alert.destination_ip || '*'}:{alert.destination_port || '*'}</div>
                <div><strong>Packets Observed:</strong> {alert.packet_count ?? 1} pkts</div>
                {alert.mitre_attack_id && (
                  <div><strong>MITRE:</strong> {alert.mitre_attack_id} {alert.mitre_technique ? `(${alert.mitre_technique})` : ''}</div>
                )}
              </div>
            </div>

            {/* Classification Decision Form */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>⚖️</span> Triage Classification Decision
                </div>
              </div>

              <form onSubmit={handleSubmitTriage} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    Triage Classification *
                  </label>
                  <select
                    className="soc-select"
                    value={selectedClassification}
                    onChange={(e) => setSelectedClassification(e.target.value as TriageClassification)}
                    style={{ width: '100%' }}
                    aria-label="Triage Classification"
                  >
                    <option value="BENIGN">BENIGN (Authorized activity / Normal operational traffic)</option>
                    <option value="SUSPICIOUS">SUSPICIOUS (Anomalous activity warranting investigation)</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE (Detection fired inappropriately on benign telemetry)</option>
                    <option value="REQUIRES_MORE_DATA">REQUIRES_MORE_DATA (Need additional captures / packet context)</option>
                    <option value="CLOSED">CLOSED (Resolved / No further analyst action needed)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    Alert Status Transition
                  </label>
                  <select
                    className="soc-select"
                    value={targetStatus}
                    onChange={(e) => setTargetStatus(e.target.value)}
                    style={{ width: '100%' }}
                    aria-label="Alert Status Transition"
                  >
                    <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                    <option value="INVESTIGATING">INVESTIGATING</option>
                    <option value="CLOSED">CLOSED</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    Analyst Justification & Technical Reasoning *
                  </label>
                  <textarea
                    className="soc-textarea"
                    rows={4}
                    placeholder="Document your evidence, packets analyzed, and why this classification is appropriate..."
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    style={{ width: '100%', resize: 'vertical' }}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="soc-btn soc-btn-primary"
                  disabled={submitting || !reason.trim()}
                  style={{ width: '100%', padding: '0.75rem' }}
                >
                  {submitting ? 'Submitting Triage Decision...' : 'Commit Triage Classification'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
