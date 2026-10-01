import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatHuntingApi } from '../../services/threatHuntingApi'
import { threatIntelApi } from '../../services/threatIntelApi'
import type {
  IndicatorClassification,
  IndicatorDetail,
} from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const IndicatorDetailPage: React.FC = () => {
  const navigate = useNavigate()
  const { indicatorId } = useParams<{ indicatorId: string }>()
  const [indicator, setIndicator] = useState<IndicatorDetail | null>(null)
  const [correlatedAlerts, setCorrelatedAlerts] = useState<any[]>([])
  const [correlatedInvs, setCorrelatedInvs] = useState<any[]>([])
  const [correlatedCases, setCorrelatedCases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Actions state
  const [isWatched, setIsWatched] = useState(false)
  const [newNote, setNewNote] = useState('')
  const [submittingNote, setSubmittingNote] = useState(false)

  // Classification Modal
  const [showClassModal, setShowClassModal] = useState(false)
  const [selectedClass, setSelectedClass] = useState<IndicatorClassification>('SUSPICIOUS')
  const [classReason, setClassReason] = useState('')
  const [updatingClass, setUpdatingClass] = useState(false)

  // Watchlist Modal
  const [showWatchModal, setShowWatchModal] = useState(false)
  const [watchReason, setWatchReason] = useState('')

  const idNum = parseInt(indicatorId || '0', 10)

  useEffect(() => {
    if (idNum) {
      loadAll()
    }
  }, [idNum])

  const loadAll = async () => {
    try {
      setLoading(true)
      const [ind, alerts, invs, cases] = await Promise.all([
        threatIntelApi.getIndicator(idNum),
        threatIntelApi.getCorrelatedAlerts(idNum),
        threatIntelApi.getCorrelatedInvestigations(idNum),
        threatIntelApi.getCorrelatedCases(idNum),
      ])
      setIndicator(ind)
      setIsWatched(ind.is_watched)
      setSelectedClass(ind.classification)
      setCorrelatedAlerts(alerts.alerts || [])
      setCorrelatedInvs(invs.investigations || [])
      setCorrelatedCases(cases.cases || [])
    } catch (err: any) {
      setError(err.message || 'Failed to load indicator details')
    } finally {
      setLoading(false)
    }
  }

  const handleEnrich = async () => {
    try {
      const updated = await threatIntelApi.enrichIndicator(idNum)
      setIndicator(updated)
      alert('Indicator enriched successfully against synthetic threat intelligence.')
    } catch (err: any) {
      alert(`Enrichment failed: ${err.message}`)
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newNote.trim()) return

    try {
      setSubmittingNote(true)
      await threatIntelApi.createNote(idNum, newNote.trim())
      setNewNote('')
      const updated = await threatIntelApi.getIndicator(idNum)
      setIndicator(updated)
    } catch (err: any) {
      alert(`Failed to add note: ${err.message}`)
    } finally {
      setSubmittingNote(false)
    }
  }

  const handleClassificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!classReason.trim()) return

    try {
      setUpdatingClass(true)
      const updated = await threatIntelApi.updateClassification(idNum, {
        classification: selectedClass,
        reason: classReason.trim(),
      })
      setIndicator(updated)
      setShowClassModal(false)
      setClassReason('')
    } catch (err: any) {
      alert(`Classification update failed: ${err.message}`)
    } finally {
      setUpdatingClass(false)
    }
  }

  const handleWatchToggle = async () => {
    if (isWatched) {
      // Find watchlist entry
      try {
        const list = await threatIntelApi.getWatchlist()
        const entry = list.find((w) => w.indicator_id === idNum)
        if (entry) {
          await threatIntelApi.removeFromWatchlist(entry.id)
          setIsWatched(false)
        }
      } catch (err: any) {
        alert(`Failed to unwatch: ${err.message}`)
      }
    } else {
      setShowWatchModal(true)
    }
  }

  const handleWatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!watchReason.trim()) return

    try {
      await threatIntelApi.addToWatchlist(idNum, { reason: watchReason.trim() })
      setIsWatched(true)
      setShowWatchModal(false)
      setWatchReason('')
    } catch (err: any) {
      alert(`Failed to add to watchlist: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <div className="threat-intel-container">
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Loading indicator details...
        </p>
      </div>
    )
  }

  if (error || !indicator) {
    return (
      <div className="threat-intel-container">
        <ThreatIntelNav />
        <div className="ioc-panel" style={{ textAlign: 'center', padding: '3rem' }}>
          <h2 style={{ color: '#ef4444' }}>Indicator Not Found</h2>
          <p style={{ color: '#94a3b8' }}>{error || 'Unable to retrieve requested indicator record.'}</p>
          <Link to="/threat-intelligence/indicators" style={{ color: '#38bdf8' }}>
            ← Return to Indicator Repository
          </Link>
        </div>
      </div>
    )
  }

  let clsBadge = 'ioc-badge-unknown'
  if (indicator.classification === 'MALICIOUS') clsBadge = 'ioc-badge-malicious'
  else if (indicator.classification === 'SUSPICIOUS') clsBadge = 'ioc-badge-suspicious'
  else if (indicator.classification === 'BENIGN') clsBadge = 'ioc-badge-benign'
  else if (indicator.classification === 'FALSE_POSITIVE') clsBadge = 'ioc-badge-false-positive'

  return (
    <div className="threat-intel-container">
      {/* Header */}
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>
            <span>🔍</span> {indicator.display_value}
          </h1>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginTop: '0.5rem' }}>
            <span style={{ fontFamily: 'monospace', color: '#94a3b8' }}>{indicator.indicator_id}</span>
            <span className="ioc-badge ioc-badge-type">{indicator.indicator_type}</span>
            <span className={`ioc-badge ${clsBadge}`}>{indicator.classification}</span>
            <span className={`confidence-pill confidence-${indicator.confidence.toLowerCase()}`}>
              {indicator.confidence} Confidence
            </span>
          </div>
        </div>

        <div className="threat-intel-actions">
          <button
            onClick={handleWatchToggle}
            style={{
              background: isWatched ? '#e11d48' : '#334155',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            {isWatched ? '👁️ Watching' : '➕ Watch'}
          </button>
          <button
            onClick={handleEnrich}
            style={{
              background: '#0ea5e9',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            ⚡ Re-Enrich
          </button>
          <button
            onClick={() => setShowClassModal(true)}
            style={{
              background: '#7c3aed',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            🏷️ Classify
          </button>
          <Link
            to={`/threat-intelligence/graph?root=${indicator.id}`}
            style={{
              background: '#334155',
              color: '#f8fafc',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              textDecoration: 'none',
              fontSize: '0.875rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            🕸️ View Graph
          </Link>
          <button
            onClick={async () => {
              try {
                const hunt = await threatHuntingApi.launchFromIOC({ ioc_id: indicator.id })
                navigate(`/threat-hunting/hunts/${hunt.id}`)
              } catch (e: any) {
                alert(`Error launching threat hunt: ${e.message}`)
              }
            }}
            style={{
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#fff',
              border: '1px solid #38bdf8',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontWeight: 600,
            }}
          >
            🔬 Launch Threat Hunt
          </button>
        </div>
      </div>

      <ThreatIntelNav />

      {/* Main Content Grid */}
      <div className="ioc-detail-grid">
        {/* Left Column: Intelligence, Observations, Telemetry */}
        <div>
          {/* Intelligence Profile */}
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Threat Intelligence Profile</h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.25rem' }}>
              {indicator.description || 'No descriptive threat narrative cataloged for this indicator.'}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div>
                <div className="threat-stat-label">Source Origin</div>
                <div style={{ color: '#f1f5f9', fontWeight: 500 }}>{indicator.source_name}</div>
              </div>
              <div>
                <div className="threat-stat-label">MITRE ATT&CK</div>
                <div style={{ color: '#f1f5f9', fontWeight: 500 }}>
                  {indicator.mitre_attack_id ? (
                    <span>
                      <strong style={{ color: '#38bdf8' }}>{indicator.mitre_attack_id}</strong> —{' '}
                      {indicator.mitre_technique}
                    </span>
                  ) : (
                    'None mapped'
                  )}
                </div>
              </div>
              <div>
                <div className="threat-stat-label">First Seen / Last Seen</div>
                <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                  {indicator.first_seen ? new Date(indicator.first_seen).toLocaleDateString() : '—'} /{' '}
                  {indicator.last_seen ? new Date(indicator.last_seen).toLocaleDateString() : '—'}
                </div>
              </div>
              <div>
                <div className="threat-stat-label">Normalized String</div>
                <div style={{ fontFamily: 'monospace', color: '#94a3b8', fontSize: '0.85rem' }}>
                  {indicator.normalized_value}
                </div>
              </div>
            </div>

            {indicator.false_positive_reason && (
              <div
                style={{
                  marginTop: '1rem',
                  padding: '0.75rem 1rem',
                  background: 'rgba(168, 85, 247, 0.1)',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  borderRadius: '0.375rem',
                }}
              >
                <div style={{ color: '#c084fc', fontWeight: 600, fontSize: '0.85rem' }}>
                  False Positive Justification:
                </div>
                <div style={{ color: '#e2e8f0', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                  {indicator.false_positive_reason}
                </div>
              </div>
            )}
          </div>

          {/* Correlated SOC Entities */}
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">
              <span>Operational Telemetry & Correlated Alerts</span>
              <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 400 }}>
                {correlatedAlerts.length} Alerts | {correlatedInvs.length} Invs | {correlatedCases.length} Cases
              </span>
            </h3>

            {correlatedAlerts.length === 0 && correlatedInvs.length === 0 && indicator.observations.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
                No direct packet observations or alerts matched this indicator yet.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {correlatedAlerts.map((a: any) => (
                  <div
                    key={a.id}
                    style={{
                      background: '#0f172a',
                      padding: '0.75rem 1rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #334155',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: '0.9rem' }}>
                        Alert #{a.id}: {a.title}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        Severity: {a.severity} | Priority: {a.priority}
                      </div>
                    </div>
                    <Link
                      to={`/soc/alerts/${a.id}`}
                      style={{
                        color: '#38bdf8',
                        textDecoration: 'none',
                        fontSize: '0.8rem',
                        fontWeight: 500,
                      }}
                    >
                      View in SOC →
                    </Link>
                  </div>
                ))}

                {indicator.observations.map((obs) => (
                  <div
                    key={obs.id}
                    style={{
                      background: '#0f172a',
                      padding: '0.75rem 1rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #334155',
                      fontSize: '0.85rem',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8' }}>
                      <span>Type: <strong>{obs.observation_type}</strong></span>
                      <span>{obs.observed_at ? new Date(obs.observed_at).toLocaleString() : ''}</span>
                    </div>
                    {obs.context_data && (
                      <pre
                        style={{
                          margin: '0.5rem 0 0 0',
                          padding: '0.5rem',
                          background: 'rgba(0,0,0,0.3)',
                          borderRadius: '0.25rem',
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          color: '#cbd5e1',
                          overflowX: 'auto',
                        }}
                      >
                        {obs.context_data}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Relationships, Timeline, Notes */}
        <div>
          {/* Structural Relationships */}
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Correlated Relationships</h3>
            {indicator.outgoing_relationships.length === 0 && indicator.incoming_relationships.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No structural relationships defined.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {indicator.outgoing_relationships.map((rel) => (
                  <div
                    key={rel.id}
                    style={{
                      background: '#0f172a',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #334155',
                      fontSize: '0.85rem',
                    }}
                  >
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>{rel.relationship_type}</span> →{' '}
                    <span style={{ fontFamily: 'monospace' }}>
                      {rel.target_indicator?.display_value || `IOC #${rel.target_indicator_id}`}
                    </span>
                  </div>
                ))}
                {indicator.incoming_relationships.map((rel) => (
                  <div
                    key={rel.id}
                    style={{
                      background: '#0f172a',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #334155',
                      fontSize: '0.85rem',
                    }}
                  >
                    <span style={{ color: '#a855f7', fontWeight: 600 }}>← {rel.relationship_type}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Activity Timeline */}
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Lifecycle Timeline</h3>
            <div className="ioc-timeline">
              {indicator.timeline_events.map((ev) => (
                <div key={ev.id} className="ioc-timeline-item">
                  <div className="ioc-timeline-node" />
                  <div className="ioc-timeline-title">{ev.title}</div>
                  <div className="ioc-timeline-meta">
                    {new Date(ev.event_timestamp).toLocaleString()} • {ev.actor_name}
                  </div>
                  {ev.description && <div className="ioc-timeline-desc">{ev.description}</div>}
                </div>
              ))}
            </div>
          </div>

          {/* Analyst Notes */}
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Analyst Notes</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
              {indicator.notes.length === 0 ? (
                <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No analyst notes logged yet.</p>
              ) : (
                indicator.notes.map((n) => (
                  <div
                    key={n.id}
                    style={{
                      background: '#0f172a',
                      padding: '0.75rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #334155',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>
                      {n.author_name} • {new Date(n.created_at).toLocaleDateString()}
                    </div>
                    <div style={{ color: '#e2e8f0', fontSize: '0.85rem' }}>{n.note}</div>
                  </div>
                ))
              )}
            </div>

            <form onSubmit={handleAddNote}>
              <textarea
                rows={2}
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Add documented observation..."
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.375rem',
                  color: '#f8fafc',
                  fontSize: '0.85rem',
                  marginBottom: '0.5rem',
                }}
              />
              <button
                type="submit"
                disabled={submittingNote || !newNote.trim()}
                style={{
                  background: '#334155',
                  color: '#f8fafc',
                  border: 'none',
                  padding: '0.35rem 0.75rem',
                  borderRadius: '0.25rem',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  float: 'right',
                }}
              >
                {submittingNote ? 'Saving...' : 'Add Note'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Classification Modal */}
      {showClassModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              width: '100%',
              maxWidth: '480px',
              color: '#f8fafc',
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: '1rem' }}>Update Analyst Classification</h3>
            <form onSubmit={handleClassificationSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Target Classification:
                </label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value as IndicatorClassification)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                >
                  <option value="MALICIOUS">Malicious</option>
                  <option value="SUSPICIOUS">Suspicious</option>
                  <option value="BENIGN">Benign</option>
                  <option value="FALSE_POSITIVE">False Positive</option>
                  <option value="UNKNOWN">Unknown</option>
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Analytical Rationale & Evidence (Mandatory):
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Document telemetry, sandboxing, or reputation justification..."
                  value={classReason}
                  onChange={(e) => setClassReason(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowClassModal(false)}
                  style={{
                    background: '#334155',
                    color: '#f8fafc',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updatingClass || !classReason.trim()}
                  style={{
                    background: '#7c3aed',
                    color: '#fff',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontWeight: 600,
                  }}
                >
                  {updatingClass ? 'Updating...' : 'Save Classification'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Watchlist Modal */}
      {showWatchModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              width: '100%',
              maxWidth: '480px',
              color: '#f8fafc',
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: '1rem' }}>Add to Analyst Watchlist</h3>
            <form onSubmit={handleWatchSubmit}>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Monitoring Reason:
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. Under active investigation for suspicious beaconing."
                  value={watchReason}
                  onChange={(e) => setWatchReason(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowWatchModal(false)}
                  style={{
                    background: '#334155',
                    color: '#f8fafc',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    background: '#0284c7',
                    color: '#fff',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontWeight: 600,
                  }}
                >
                  Add to Watchlist
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
