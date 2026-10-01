import React, { useState } from 'react'
import type { EndpointEvent } from '../../types/endpointSecurity'
import { endpointSecurityApi } from '../../services/endpointSecurityApi'
import './endpointSecurity.css'

interface EndpointTimelineProps {
  events: EndpointEvent[]
  hostId?: string | number
  onRefresh?: () => void
}

const CATEGORIES: Array<{ key: string; label: string; icon: string }> = [
  { key: 'ALL', label: 'All Categories', icon: '🌐' },
  { key: 'PROCESS', label: 'Processes', icon: '⚙️' },
  { key: 'AUTHENTICATION', label: 'Auth', icon: '🔑' },
  { key: 'NETWORK', label: 'Network', icon: '📡' },
  { key: 'DNS', label: 'DNS', icon: '🔎' },
  { key: 'FILE', label: 'Files', icon: '📁' },
  { key: 'PERSISTENCE', label: 'Persistence', icon: '📌' },
  { key: 'PRIVILEGE', label: 'Privileges', icon: '🛡️' },
]

export const EndpointTimeline: React.FC<EndpointTimelineProps> = ({ events }) => {
  const [selectedCategory, setSelectedCategory] = useState('ALL')
  const [pivotEvent, setPivotEvent] = useState<EndpointEvent | null>(null)
  const [pivotStatus, setPivotStatus] = useState<string | null>(null)
  const [pivotLoading, setPivotLoading] = useState(false)

  const filteredEvents = events.filter((e) => {
    if (selectedCategory === 'ALL') return true
    return e.event_category === selectedCategory
  })

  const handlePivotIntel = async (eventId: string) => {
    setPivotLoading(true)
    setPivotStatus(null)
    try {
      const res = await endpointSecurityApi.pivotToIntel(eventId)
      setPivotStatus(
        `Threat Intel Pivot successful: ${res.observables.length} observable(s) analyzed. ${res.analyst_guidance}`
      )
    } catch (err: any) {
      setPivotStatus(`Intel pivot error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  const handleStartThreatHunt = async (eventId: string) => {
    setPivotLoading(true)
    setPivotStatus(null)
    try {
      const res = await endpointSecurityApi.startThreatHunt(eventId)
      setPivotStatus(
        `Threat Hunt initiated: ${res.hunt_id} ("${res.title}"). Status: ${res.status}. Initial pivot: ${res.initial_pivot_type} ${res.initial_pivot_value}`
      )
    } catch (err: any) {
      setPivotStatus(`Threat hunt error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  const handleEscalateSoc = async (eventId: string) => {
    setPivotLoading(true)
    setPivotStatus(null)
    try {
      const res = await endpointSecurityApi.investigateInSoc(eventId)
      setPivotStatus(
        `Escalated to SOC Case: ${res.investigation_id} ("${res.title}"). Priority: ${res.priority}`
      )
    } catch (err: any) {
      setPivotStatus(`SOC escalation error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  return (
    <div className="endpoint-timeline-container">
      {/* Category Filter Chips */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            type="button"
            className={selectedCategory === cat.key ? 'btn-cyber-primary' : 'btn-cyber-secondary'}
            onClick={() => setSelectedCategory(cat.key)}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
          >
            <span>{cat.icon}</span> {cat.label}
          </button>
        ))}
      </div>

      {/* Timeline Event Stream */}
      {filteredEvents.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2.5rem', background: '#111827', borderRadius: '8px', color: '#64748b' }}>
          No telemetry events recorded for category "{selectedCategory}".
        </div>
      ) : (
        <div className="timeline-list">
          {filteredEvents.map((evt) => {
            const sevClass = (evt.severity || 'low').toLowerCase()
            return (
              <div key={evt.id} className="timeline-entry">
                <div className="timeline-entry-bullet" />
                <div className="timeline-entry-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: '#94a3b8' }}>
                        {new Date(evt.timestamp).toLocaleString()}
                      </span>
                      <span className={`risk-badge ${sevClass}`}>
                        {evt.severity}
                      </span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#38bdf8' }}>
                        [{evt.event_category}]
                      </span>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f1f5f9' }}>
                        {evt.event_type}
                      </span>
                    </div>

                    <button
                      type="button"
                      className="btn-cyber-secondary"
                      style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                      onClick={() => {
                        setPivotEvent(evt)
                        setPivotStatus(null)
                      }}
                    >
                      Pivots & Actions ➔
                    </button>
                  </div>

                  {/* Summary / Command */}
                  <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.4rem' }}>
                    {evt.command_summary || evt.raw_event_reference || 'Telemetry entry'}
                  </div>

                  {evt.command_line && (
                    <div className="code-block" style={{ marginBottom: '0.4rem', fontSize: '0.75rem' }}>
                      {evt.command_line}
                    </div>
                  )}

                  {/* Meta details footer */}
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.75rem', color: '#64748b' }}>
                    {evt.process_name && (
                      <span>
                        Process: <strong style={{ color: '#94a3b8' }}>{evt.process_name}</strong> {evt.process_id ? `(PID: ${evt.process_id})` : ''}
                      </span>
                    )}
                    {evt.username && (
                      <span>
                        User: <strong style={{ color: '#94a3b8' }}>{evt.username}</strong>
                      </span>
                    )}
                    {evt.destination_ip && (
                      <span>
                        Dest: <strong style={{ color: '#38bdf8' }}>{evt.destination_ip}:{evt.destination_port}</strong>
                      </span>
                    )}
                    {evt.domain && (
                      <span>
                        Domain: <strong style={{ color: '#fbbf24' }}>{evt.domain}</strong>
                      </span>
                    )}
                    {evt.file_hash && (
                      <span>
                        Hash: <strong style={{ color: '#a855f7' }}>{evt.file_hash.substring(0, 16)}...</strong>
                      </span>
                    )}
                    {evt.result && (
                      <span>
                        Result: <strong style={{ color: evt.result === 'FAILURE' ? '#ef4444' : '#10b981' }}>{evt.result}</strong>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Pivot Action Modal */}
      {pivotEvent && (
        <div className="endpoint-modal-overlay" onClick={() => setPivotEvent(null)}>
          <div className="endpoint-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #1f2937', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ margin: 0, color: '#f8fafc' }}>
                  Investigative Pivots: Event {pivotEvent.event_id}
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Category: {pivotEvent.event_category} | Severity: {pivotEvent.severity}
                </span>
              </div>
              <button
                type="button"
                className="btn-cyber-secondary"
                onClick={() => setPivotEvent(null)}
              >
                ✕ Close
              </button>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.4rem' }}>
                Observed Event Payload:
              </div>
              <div className="code-block" style={{ fontSize: '0.775rem' }}>
                {pivotEvent.command_summary || pivotEvent.command_line || pivotEvent.event_type}
              </div>
            </div>

            {/* Pivot Buttons */}
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
              <button
                type="button"
                className="btn-cyber-pivot"
                disabled={pivotLoading}
                onClick={() => handlePivotIntel(pivotEvent.event_id)}
              >
                🔎 Query Threat Intel
              </button>

              <button
                type="button"
                className="btn-cyber-pivot"
                disabled={pivotLoading}
                onClick={() => handleStartThreatHunt(pivotEvent.event_id)}
              >
                🎯 Start Threat Hunt
              </button>

              <button
                type="button"
                className="btn-cyber-pivot"
                disabled={pivotLoading}
                onClick={() => handleEscalateSoc(pivotEvent.event_id)}
              >
                🚨 Escalate to SOC Case
              </button>
            </div>

            {pivotLoading && (
              <div style={{ color: '#38bdf8', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Pivoting observable through correlation pipelines...
              </div>
            )}

            {pivotStatus && (
              <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.75rem', fontSize: '0.825rem', color: '#38bdf8', marginBottom: '1rem' }}>
                {pivotStatus}
              </div>
            )}

            <div style={{ fontSize: '0.775rem', color: '#64748b', fontStyle: 'italic', borderTop: '1px solid #1f2937', paddingTop: '0.75rem' }}>
              NexoraNet Educational Note: Cross-domain correlation bridges host-level artifacts with network detections, IDS alerts, SIEM logs, and global threat intelligence.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
