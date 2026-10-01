import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { InvestigationBriefItem, TrainingPriority } from '../../types/soc'
import '../../components/soc/soc.css'

export const InvestigationListPage: React.FC = () => {
  const navigate = useNavigate()
  const [investigations, setInvestigations] = useState<InvestigationBriefItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')

  // New Investigation Modal State
  const [showModal, setShowModal] = useState<boolean>(false)
  const [newTitle, setNewTitle] = useState<string>('')
  const [newDescription, setNewDescription] = useState<string>('')
  const [newPriority, setNewPriority] = useState<TrainingPriority>('P3')
  const [creating, setCreating] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const fetchInvestigations = async () => {
    try {
      setLoading(true)
      const data = await socApi.listInvestigations({
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
      })
      setInvestigations(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch investigations.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInvestigations()
  }, [statusFilter, priorityFilter])

  const handleCreateInvestigation = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim()) return
    try {
      setCreating(true)
      setError(null)
      const inv = await socApi.createInvestigation({
        title: newTitle.trim(),
        description: newDescription.trim() || 'Manual investigation initiated by analyst.',
        priority: newPriority,
      })
      setShowModal(false)
      setNewTitle('')
      setNewDescription('')
      navigate(`/soc/investigations/${inv.id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create investigation.')
    } finally {
      setCreating(false)
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

  return (
    <div className="soc-container">
      <SocHeader
        title="Forensic Investigations Workspace"
        subtitle="Manage structured case investigations, formulate hypotheses, bind evidence, and compile incident findings"
        actionButton={
          <button className="soc-btn soc-btn-primary" onClick={() => setShowModal(true)}>
            + New Investigation
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

        {(statusFilter || priorityFilter) && (
          <button
            type="button"
            className="soc-btn soc-btn-secondary"
            style={{ fontSize: '0.78rem' }}
            onClick={() => {
              setStatusFilter('')
              setPriorityFilter('')
            }}
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Investigations Table */}
      <div className="soc-card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
            Loading investigations...
          </div>
        ) : investigations.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
            No investigations found. Open an alert or click &quot;+ New Investigation&quot; to begin.
          </div>
        ) : (
          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Investigation ID</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Classification</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {investigations.map((inv) => (
                  <tr key={inv.id}>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#38bdf8' }}>
                      {inv.investigation_id}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)' }}>{inv.title}</div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: 'var(--soc-text-secondary)' }}>{inv.status}</span>
                    </td>
                    <td>{getPriorityBadge(inv.priority)}</td>
                    <td>
                      <span className="soc-badge soc-badge-unreviewed">{inv.classification}</span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--soc-text-muted)' }}>
                      {new Date(inv.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <Link
                        to={`/soc/investigations/${inv.id}`}
                        className="soc-btn soc-btn-primary"
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                      >
                        Open Workspace →
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
            <h3 style={{ margin: '0 0 1rem 0', color: 'var(--soc-text-primary)' }}>Initiate New SOC Investigation</h3>
            <form onSubmit={handleCreateInvestigation} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                  Investigation Title *
                </label>
                <input
                  type="text"
                  className="soc-input"
                  style={{ width: '100%' }}
                  placeholder="e.g., Investigation: Suspicious TCP SYN Scan & Port Sweep"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                  Initial Priority
                </label>
                <select
                  className="soc-select"
                  style={{ width: '100%' }}
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as TrainingPriority)}
                  aria-label="Initial Priority"
                >
                  <option value="P1">P1 Critical</option>
                  <option value="P2">P2 High</option>
                  <option value="P3">P3 Medium</option>
                  <option value="P4">P4 Low</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                  Scope & Objective
                </label>
                <textarea
                  className="soc-textarea"
                  rows={3}
                  style={{ width: '100%' }}
                  placeholder="Describe the hypothesis or triggered detection pattern under analysis..."
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
                  {creating ? 'Creating...' : 'Create Investigation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
