import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { CaseDetailResponse, TrainingPriority } from '../../types/soc'
import '../../components/soc/soc.css'

export const CaseListPage: React.FC = () => {
  const navigate = useNavigate()
  const [cases, setCases] = useState<CaseDetailResponse[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')

  // New Case Modal State
  const [showModal, setShowModal] = useState<boolean>(false)
  const [newTitle, setNewTitle] = useState<string>('')
  const [newDescription, setNewDescription] = useState<string>('')
  const [newPriority, setNewPriority] = useState<TrainingPriority>('P3')
  const [creating, setCreating] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const fetchCases = async () => {
    try {
      setLoading(true)
      const data = await socApi.listCases({
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
      })
      setCases(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cases.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCases()
  }, [statusFilter, priorityFilter])

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim()) return
    try {
      setCreating(true)
      setError(null)
      const c = await socApi.createCase({
        title: newTitle.trim(),
        description: newDescription.trim() || 'Case initiated by SOC team.',
        priority: newPriority,
      })
      setShowModal(false)
      setNewTitle('')
      setNewDescription('')
      navigate(`/soc/cases/${c.id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create case.')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="soc-container">
      <SocHeader
        title="Incident Case Management"
        subtitle="Group related investigations and alerts into unified defensive incident cases"
        actionButton={
          <button className="soc-btn soc-btn-primary" onClick={() => setShowModal(true)}>
            + New Case
          </button>
        }
      />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#f87171', fontSize: '0.88rem' }}>
          {error}
        </div>
      )}

      {/* Filter Row */}
      <div className="soc-card" style={{ padding: '0.75rem 1rem', flexDirection: 'row', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--soc-text-muted)' }}>Filters:</div>
        <select
          className="soc-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          aria-label="Status Filter"
        >
          <option value="">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="INVESTIGATING">Investigating</option>
          <option value="PENDING">Pending</option>
          <option value="RESOLVED">Resolved</option>
          <option value="CLOSED">Closed</option>
        </select>

        <select
          className="soc-select"
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          aria-label="Priority Filter"
        >
          <option value="">All Priorities</option>
          <option value="P1">P1 Critical</option>
          <option value="P2">P2 High</option>
          <option value="P3">P3 Medium</option>
          <option value="P4">P4 Low</option>
        </select>
      </div>

      {/* Cases List */}
      <div className="soc-card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
            Loading cases...
          </div>
        ) : cases.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
            No incident cases open. Click &quot;+ New Case&quot; to aggregate related investigations.
          </div>
        ) : (
          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Linked Investigations</th>
                  <th>Linked Alerts</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#38bdf8' }}>{c.case_id}</td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)' }}>{c.title}</div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: 'var(--soc-text-secondary)' }}>{c.status}</span>
                    </td>
                    <td>
                      <span className="soc-badge soc-badge-p3">{c.priority}</span>
                    </td>
                    <td>{c.investigations.length}</td>
                    <td>{c.alerts.length}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--soc-text-muted)' }}>
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <Link to={`/soc/cases/${c.id}`} className="soc-btn soc-btn-primary" style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}>
                        Open Case →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', border: '1px solid var(--soc-border)', borderRadius: '8px', padding: '1.5rem', width: '100%', maxWidth: '500px' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: 'var(--soc-text-primary)' }}>Create New Incident Case</h3>
            <form onSubmit={handleCreateCase} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                  Case Title *
                </label>
                <input
                  type="text"
                  className="soc-input"
                  style={{ width: '100%' }}
                  placeholder="e.g. Campaign Case: External Port Scanning & DNS Amplification"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                  Priority
                </label>
                <select
                  className="soc-select"
                  style={{ width: '100%' }}
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as TrainingPriority)}
                  aria-label="Priority"
                >
                  <option value="P1">P1 Critical</option>
                  <option value="P2">P2 High</option>
                  <option value="P3">P3 Medium</option>
                  <option value="P4">P4 Low</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                  Case Description
                </label>
                <textarea
                  className="soc-textarea"
                  rows={3}
                  style={{ width: '100%' }}
                  placeholder="Explain why these incidents are grouped together..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className="soc-btn soc-btn-secondary"
                  onClick={() => setShowModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="soc-btn soc-btn-primary"
                  disabled={creating || !newTitle.trim()}
                >
                  {creating ? 'Creating...' : 'Create Case'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
