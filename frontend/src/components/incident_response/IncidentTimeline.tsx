import React, { useState } from 'react'
import type { IncidentTimelineEvent } from '../../types/incidentResponse'

interface IncidentTimelineProps {
  events: IncidentTimelineEvent[]
  onAddEvent: (data: {
    timestamp: string
    title: string
    description: string
    event_category: string
    is_milestone: boolean
  }) => Promise<void>
  onSyncSources: () => Promise<void>
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({
  events,
  onAddEvent,
  onSyncSources,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('ALL')
  const [milestonesOnly, setMilestonesOnly] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [syncing, setSyncing] = useState(false)

  // Form states
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('OBSERVATION')
  const [isMilestone, setIsMilestone] = useState(false)
  const [eventTime, setEventTime] = useState(() => new Date().toISOString().slice(0, 16))

  const handleSync = async () => {
    setSyncing(true)
    try {
      await onSyncSources()
    } finally {
      setSyncing(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    await onAddEvent({
      timestamp: new Date(eventTime).toISOString(),
      title,
      description,
      event_category: category,
      is_milestone: isMilestone,
    })
    setShowAddModal(false)
    setTitle('')
    setDescription('')
  }

  const filteredEvents = events.filter((ev) => {
    if (milestonesOnly && !ev.is_milestone) return false
    if (filterCategory !== 'ALL' && ev.event_category !== filterCategory) return false
    return true
  })

  return (
    <div>
      {/* Filter and Action Header */}
      <div className="ir-filter-bar">
        <select
          className="ir-select"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="ALL">All Event Categories</option>
          <option value="INITIAL_ACCESS">Initial Access</option>
          <option value="EXECUTION">Execution</option>
          <option value="DETECTION">Detection</option>
          <option value="TRIAGE">Triage</option>
          <option value="CONTAINMENT">Containment</option>
          <option value="ERADICATION">Eradication</option>
          <option value="RECOVERY">Recovery</option>
          <option value="OBSERVATION">Observation</option>
        </select>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.88rem' }}>
          <input
            type="checkbox"
            checked={milestonesOnly}
            onChange={(e) => setMilestonesOnly(e.target.checked)}
          />
          Milestones Only (★)
        </label>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
          <button className="ir-btn-secondary" onClick={handleSync} disabled={syncing}>
            {syncing ? 'Syncing...' : '🔄 Auto-Sync Sources'}
          </button>
          <button className="ir-btn-primary" onClick={() => setShowAddModal(true)}>
            + Add Event
          </button>
        </div>
      </div>

      {/* Timeline Tree */}
      <div className="ir-timeline">
        {filteredEvents.map((ev) => {
          const dateStr = new Date(ev.timestamp).toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })

          return (
            <div key={ev.id} className={`ir-timeline-event ${ev.is_milestone ? 'milestone' : ''}`}>
              <div className="ir-timeline-node" />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div className="ir-timeline-time">{dateStr}</div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <span className="ir-pill badge-cyan">{ev.event_category}</span>
                  {ev.mitre_technique_id && (
                    <span className="ir-pill badge-high">{ev.mitre_technique_id}</span>
                  )}
                  {ev.is_milestone && <span style={{ color: '#06b6d4' }}>★ Milestone</span>}
                </div>
              </div>

              <div className="ir-timeline-title">{ev.title}</div>
              <div style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: '1.45' }}>
                {ev.description}
              </div>

              {ev.source && (
                <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#6b7280' }}>
                  Source: <code>{ev.source}</code> {ev.source_id && `(${ev.source_id})`}
                </div>
              )}
            </div>
          )
        })}

        {filteredEvents.length === 0 && (
          <div style={{ padding: '24px', color: '#6b7280', textAlign: 'center' }}>
            No timeline events match the selected filters.
          </div>
        )}
      </div>

      {/* Add Event Modal */}
      {showAddModal && (
        <div className="ir-modal-backdrop" onClick={() => setShowAddModal(false)}>
          <div className="ir-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="ir-modal-header">
              <h3>Add Timeline Milestone / Event</h3>
              <button className="ir-modal-close" onClick={() => setShowAddModal(false)}>
                &times;
              </button>
            </div>

            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Event Timestamp</label>
                <input
                  type="datetime-local"
                  className="ir-search-input"
                  style={{ width: '100%' }}
                  value={eventTime}
                  onChange={(e) => setEventTime(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Title</label>
                <input
                  type="text"
                  className="ir-search-input"
                  style={{ width: '100%' }}
                  placeholder="e.g. Account lockout triggered on VPN gateway"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Category</label>
                <select
                  className="ir-select"
                  style={{ width: '100%' }}
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option value="TRIAGE">Triage</option>
                  <option value="INITIAL_ACCESS">Initial Access</option>
                  <option value="EXECUTION">Execution</option>
                  <option value="DETECTION">Detection</option>
                  <option value="CONTAINMENT">Containment</option>
                  <option value="ERADICATION">Eradication</option>
                  <option value="RECOVERY">Recovery</option>
                  <option value="OBSERVATION">General Observation</option>
                </select>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Description</label>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '80px' }}
                  placeholder="Detailed description of what occurred..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: '18px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={isMilestone}
                    onChange={(e) => setIsMilestone(e.target.checked)}
                  />
                  Mark as Key Investigation Milestone (★)
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  className="ir-btn-secondary"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="ir-btn-primary">
                  Save Event
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
