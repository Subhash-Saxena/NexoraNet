import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { CaseDetailResponse, CaseStatus } from '../../types/soc'
import '../../components/soc/soc.css'

export const CaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const [caseItem, setCaseItem] = useState<CaseDetailResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [statusVal, setStatusVal] = useState<CaseStatus>('OPEN')
  const [newNote, setNewNote] = useState<string>('')
  const [submittingNote, setSubmittingNote] = useState<boolean>(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)


  const fetchCase = async () => {
    if (!caseId) return
    try {
      setLoading(true)
      const data = await socApi.getCase(Number(caseId))
      setCaseItem(data)
      setStatusVal(data.status)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch case detail.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCase()
  }, [caseId])

  const handleUpdateStatus = async (newStatus: CaseStatus) => {
    if (!caseItem) return
    try {
      const updated = await socApi.updateCase(caseItem.id, { status: newStatus })
      setCaseItem(updated)
      setStatusVal(updated.status)
      setMessage(`Case status transitioned to ${newStatus}.`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update case status.')
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!caseItem || !newNote.trim()) return
    try {
      setSubmittingNote(true)
      await socApi.addCaseNote(caseItem.id, newNote.trim())
      setNewNote('')
      setMessage('Case note recorded.')
      await fetchCase()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add note.')
    } finally {
      setSubmittingNote(false)
    }
  }

  return (

    <div className="soc-container">
      <SocHeader
        title={`${caseItem?.case_id || 'Case'}: ${caseItem?.title || 'Incident Detail'}`}
        subtitle="Manage aggregated multi-alert incidents, shared forensic findings, and resolution status"
        actionButton={
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Link to="/soc/cases" className="soc-btn soc-btn-secondary">
              ← Cases List
            </Link>
            {caseItem && (
              <select
                className="soc-select"
                value={statusVal}
                onChange={(e) => handleUpdateStatus(e.target.value as CaseStatus)}
                aria-label="Update Case Status"
              >
                <option value="OPEN">Status: OPEN</option>
                <option value="INVESTIGATING">Status: INVESTIGATING</option>
                <option value="PENDING">Status: PENDING</option>
                <option value="RESOLVED">Status: RESOLVED</option>
                <option value="CLOSED">Status: CLOSED</option>
              </select>
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
          Loading incident case details...
        </div>
      ) : !caseItem ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          Case not found.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem' }}>
          {/* Left Column: Linked Investigations & Alerts */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Case Overview */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Case Overview</div>
                <span className="soc-badge soc-badge-p3">{caseItem.priority}</span>
              </div>
              <div style={{ fontSize: '0.88rem', color: 'var(--soc-text-secondary)', lineHeight: 1.6 }}>
                {caseItem.description}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--soc-text-muted)', borderTop: '1px solid var(--soc-border)', paddingTop: '0.5rem' }}>
                Created: {new Date(caseItem.created_at).toLocaleString()} • Owner: {caseItem.created_by_name || 'SOC Analyst'}
              </div>
            </div>

            {/* Linked Investigations */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🔬</span> Linked Investigations ({caseItem.investigations.length})
                </div>
              </div>

              {caseItem.investigations.length === 0 ? (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--soc-text-muted)', fontSize: '0.85rem' }}>
                  No investigations linked to this case yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {caseItem.investigations.map((inv) => (
                    <div key={inv.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)', fontSize: '0.88rem' }}>
                          [{inv.investigation_code}] {inv.title}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>Status: {inv.status}</div>
                      </div>
                      <Link to={`/soc/investigations/${inv.investigation_id}`} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        Open →
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Linked Alerts */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🚨</span> Linked Alerts ({caseItem.alerts.length})
                </div>
              </div>

              {caseItem.alerts.length === 0 ? (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--soc-text-muted)', fontSize: '0.85rem' }}>
                  No alerts linked to this case yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {caseItem.alerts.map((alt) => (
                    <div key={alt.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)', fontSize: '0.88rem' }}>
                          Alert #{alt.alert_id}: {alt.title}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                          Severity: {alt.severity} • Classification: {alt.classification}
                        </div>
                      </div>
                      <Link to={`/soc/alerts/${alt.alert_id}`} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        Inspect →
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Case Notes */}
          <div className="soc-card">
            <div className="soc-card-header">
              <div className="soc-card-title">
                <span>📝</span> Case Activity Notes ({caseItem.notes.length})
              </div>
            </div>

            <form onSubmit={handleAddNote} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="soc-input"
                placeholder="Add note to case activity log..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                style={{ flex: 1 }}
              />
              <button type="submit" className="soc-btn soc-btn-primary" disabled={submittingNote || !newNote.trim()}>
                Save
              </button>
            </form>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem', maxHeight: '450px', overflowY: 'auto' }}>
              {caseItem.notes.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                  No case notes recorded yet.
                </div>
              ) : (
                caseItem.notes.map((n) => (
                  <div key={n.id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--soc-text-muted)', marginBottom: '0.25rem' }}>
                      <span>{n.author_name || 'SOC Analyst'}</span>
                      <span>{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--soc-text-secondary)' }}>{n.note}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
