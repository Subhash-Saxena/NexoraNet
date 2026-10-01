import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { SocAlertDetailResponse } from '../../types/soc'
import '../../components/soc/soc.css'

export const AlertDetailPage: React.FC = () => {
  const { alertId } = useParams<{ alertId: string }>()
  const navigate = useNavigate()
  const [alert, setAlert] = useState<SocAlertDetailResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [newNote, setNewNote] = useState<string>('')
  const [submittingNote, setSubmittingNote] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const fetchAlert = async () => {
    if (!alertId) return
    try {
      setLoading(true)
      const data = await socApi.getAlertDetail(Number(alertId))
      setAlert(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alert detail.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlert()
  }, [alertId])

  const handleAcknowledge = async () => {
    if (!alert) return
    try {
      await socApi.acknowledgeAlert(alert.id, 'Analyst acknowledged alert from detail inspector.')
      setMessage('Alert acknowledged successfully.')
      await fetchAlert()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to acknowledge alert.')
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!alert || !newNote.trim()) return
    try {
      setSubmittingNote(true)
      await socApi.addAlertNote(alert.id, newNote.trim())
      setNewNote('')
      setMessage('Analyst note appended to alert.')
      await fetchAlert()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add note.')
    } finally {
      setSubmittingNote(false)
    }
  }

  const handleCreateInvestigation = async () => {
    if (!alert) return
    try {
      const inv = await socApi.createInvestigation({
        title: `Investigation: ${alert.title}`,
        description: `Dedicated forensic investigation initiated for ${alert.title} (Alert #${alert.id}).`,
        priority: alert.priority,
        alert_ids: [alert.id],
      })
      navigate(`/soc/investigations/${inv.id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to initiate investigation.')
    }
  }

  const getPriorityBadge = (p: string) => {
    switch (p) {
      case 'P1':
        return <span className="soc-badge soc-badge-p1">P1 CRITICAL</span>
      case 'P2':
        return <span className="soc-badge soc-badge-p2">P2 HIGH</span>
      case 'P3':
        return <span className="soc-badge soc-badge-p3">P3 MEDIUM</span>
      default:
        return <span className="soc-badge soc-badge-p4">P4 LOW</span>
    }
  }

  const getClassificationBadge = (cls: string) => {
    switch (cls) {
      case 'BENIGN':
        return <span className="soc-badge soc-badge-benign">Benign</span>
      case 'SUSPICIOUS':
        return <span className="soc-badge soc-badge-suspicious">Suspicious</span>
      case 'FALSE_POSITIVE':
        return <span className="soc-badge soc-badge-fp">False Positive</span>
      case 'REQUIRES_MORE_DATA':
        return <span className="soc-badge soc-badge-more-data">Need Data</span>
      case 'CLOSED':
        return <span className="soc-badge soc-badge-closed">Closed</span>
      default:
        return <span className="soc-badge soc-badge-unreviewed">Unreviewed</span>
    }
  }

  return (
    <div className="soc-container">
      <SocHeader
        title={`Alert #${alertId}: ${alert?.title || 'Inspection'}`}
        subtitle={`Rule: ${alert?.rule_code || 'DETECTION'} • Severity: ${alert?.severity || 'UNKNOWN'} • Confidence: ${alert?.confidence || 'UNKNOWN'}`}
        actionButton={
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Link to="/soc/alerts" className="soc-btn soc-btn-secondary">
              ← Back to Queue
            </Link>
            {alert && alert.status === 'NEW' && (
              <button className="soc-btn soc-btn-secondary" onClick={handleAcknowledge}>
                Acknowledge
              </button>
            )}
            <Link to={`/soc/alerts/${alertId}/triage`} className="soc-btn soc-btn-primary">
              Launch Triage Workflow →
            </Link>
            <button className="soc-btn soc-btn-secondary" onClick={handleCreateInvestigation}>
              Open Investigation
            </button>
            {alert && (alert.source_ip || alert.destination_ip) && (
              <Link
                to={`/threat-intelligence/search?q=${encodeURIComponent(alert.destination_ip || alert.source_ip || '')}`}
                className="soc-btn soc-btn-secondary"
              >
                🎯 Threat Intel
              </Link>
            )}
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
          Loading alert evidence, network context, and timeline...
        </div>
      ) : !alert ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          Alert not found.
        </div>
      ) : (
        <>
          {/* Header Summary Card */}
          <div className="soc-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {getPriorityBadge(alert.priority)}
                {getClassificationBadge(alert.classification)}
                <span style={{ fontSize: '0.85rem', color: 'var(--soc-text-secondary)' }}>
                  Status: <strong>{alert.status}</strong>
                </span>
                {alert.assigned_to_name && (
                  <span style={{ fontSize: '0.85rem', color: 'var(--soc-text-muted)' }}>
                    Assigned: {alert.assigned_to_name}
                  </span>
                )}
              </div>

              {alert.mitre_attack_id && (
                <div style={{ fontSize: '0.85rem', color: '#38bdf8' }}>
                  MITRE ATT&CK: <strong>{alert.mitre_attack_id}</strong> {alert.mitre_technique ? `(${alert.mitre_technique})` : ''}
                </div>
              )}
            </div>

            <div style={{ fontSize: '0.95rem', color: 'var(--soc-text-secondary)', lineHeight: 1.6, borderTop: '1px solid var(--soc-border)', paddingTop: '0.75rem' }}>
              <strong>Educational Explanation:</strong> {alert.explanation}
            </div>

            {alert.investigation_steps && alert.investigation_steps.length > 0 && (
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '0.85rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.4rem' }}>
                  Recommended SOC Investigation Steps:
                </div>
                <ol style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--soc-text-secondary)', lineHeight: 1.6 }}>
                  {alert.investigation_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>

          {/* Network Context & Endpoint Telemetry */}
          <div className="soc-card">
            <div className="soc-card-header">
              <div className="soc-card-title">
                <span>🌐</span> Endpoint Context & Telemetry
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--soc-text-muted)' }}>
                {alert.network_context.conversation_summary || 'Passive packet telemetry'}
              </span>
            </div>

            <div className="soc-context-grid">
              {/* Source Context */}
              <div className="soc-context-box">
                <div className="soc-context-box-title">Source Endpoint</div>
                <div className="soc-context-ip">{alert.network_context.source?.ip || alert.source_ip || 'Unknown'}</div>
                <div className="soc-context-stat">
                  <span>Packet Volume:</span>
                  <strong>{alert.network_context.source?.packet_count ?? 0} pkts</strong>
                </div>
                <div className="soc-context-stat">
                  <span>Byte Volume:</span>
                  <strong>{alert.network_context.source?.byte_count ?? 0} bytes</strong>
                </div>
                <div className="soc-context-stat">
                  <span>Observed Protocols:</span>
                  <span>{alert.network_context.source?.protocols.join(', ') || 'None'}</span>
                </div>
                <div className="soc-context-stat">
                  <span>Observed Ports:</span>
                  <span>{alert.network_context.source?.ports.join(', ') || 'None'}</span>
                </div>
              </div>

              {/* Destination Context */}
              <div className="soc-context-box">
                <div className="soc-context-box-title">Destination Endpoint</div>
                <div className="soc-context-ip">{alert.network_context.destination?.ip || alert.destination_ip || 'Unknown'}</div>
                <div className="soc-context-stat">
                  <span>Packet Volume:</span>
                  <strong>{alert.network_context.destination?.packet_count ?? 0} pkts</strong>
                </div>
                <div className="soc-context-stat">
                  <span>Byte Volume:</span>
                  <strong>{alert.network_context.destination?.byte_count ?? 0} bytes</strong>
                </div>
                <div className="soc-context-stat">
                  <span>Observed Protocols:</span>
                  <span>{alert.network_context.destination?.protocols.join(', ') || 'None'}</span>
                </div>
                <div className="soc-context-stat">
                  <span>Observed Ports:</span>
                  <span>{alert.network_context.destination?.ports.join(', ') || 'None'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Packet Evidence & Timeline */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem' }}>
            {/* Packet Evidence List */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>📦</span> Supporting Packet Evidence ({alert.evidence.length})
                </div>
              </div>

              {alert.evidence.length === 0 ? (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--soc-text-muted)', fontSize: '0.85rem' }}>
                  No granular packet bindings attached.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {alert.evidence.map((ev) => (
                    <div key={ev.id} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--soc-border)', borderRadius: '6px', padding: '0.85rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#38bdf8' }}>
                          Evidence #{ev.id} • {ev.evidence_type}
                        </span>
                        {ev.packet_number && alert.capture_id && (
                          <Link
                            to={`/packet-analysis/inspect/${alert.capture_id}?packet=${ev.packet_number}`}
                            className="soc-btn soc-btn-secondary"
                            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                          >
                            Inspect Packet #{ev.packet_number} →
                          </Link>
                        )}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--soc-text-secondary)' }}>{ev.summary}</div>
                      {ev.evidence_payload && (
                        <pre style={{ margin: '0.5rem 0 0 0', padding: '0.5rem', background: '#070b12', borderRadius: '4px', fontSize: '0.75rem', overflowX: 'auto', color: '#94a3b8' }}>
                          {JSON.stringify(ev.evidence_payload, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Chronological Timeline */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>⏱️</span> Chronological Timeline ({alert.timeline.length})
                </div>
              </div>

              <div className="soc-timeline">
                {alert.timeline.map((te, idx) => (
                  <div key={idx} className="soc-timeline-item">
                    <div className="soc-timeline-marker" />
                    <div className="soc-timeline-title">{te.title}</div>
                    <div className="soc-timeline-meta">
                      {te.time_display} • {te.actor_name}
                    </div>
                    <div className="soc-timeline-desc">{te.description}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Related Alerts & Correlated Events */}
          {alert.related_alerts && alert.related_alerts.length > 0 && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🔗</span> Correlated Related Alerts ({alert.related_alerts.length})
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                {alert.related_alerts.map((rel) => (
                  <div key={rel.id} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--soc-border)', borderRadius: '6px', padding: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--soc-text-primary)' }}>{rel.title}</span>
                      {getPriorityBadge(rel.priority)}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--soc-text-muted)', margin: '0.35rem 0' }}>
                      Reason: {rel.correlation_reason}
                    </div>
                    <Link to={`/soc/alerts/${rel.id}`} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', marginTop: '0.25rem' }}>
                      Inspect Related Alert →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analyst Notes Section */}
          <div className="soc-card">
            <div className="soc-card-header">
              <div className="soc-card-title">
                <span>📝</span> Analyst Triage Notes ({alert.notes.length})
              </div>
            </div>

            {alert.notes.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
                {alert.notes.map((n) => (
                  <div key={n.id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--soc-text-muted)', marginBottom: '0.25rem' }}>
                      <span>{n.author}</span>
                      <span>{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                    <div style={{ fontSize: '0.88rem', color: 'var(--soc-text-secondary)' }}>{n.note}</div>
                  </div>
                ))}
              </div>
            )}

            <form onSubmit={handleAddNote} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="soc-input"
                placeholder="Append an analyst triage note..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                style={{ flex: 1 }}
              />
              <button type="submit" className="soc-btn soc-btn-primary" disabled={submittingNote || !newNote.trim()}>
                {submittingNote ? 'Saving...' : 'Add Note'}
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  )
}
