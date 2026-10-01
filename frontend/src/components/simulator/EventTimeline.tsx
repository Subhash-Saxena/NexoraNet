import React, { useState } from 'react'
import { AlertCircle, CheckCircle, Info, AlertTriangle, Shield, HelpCircle } from 'lucide-react'
import type { SimulationEvent } from '../../types/simulator'

interface EventTimelineProps {
  events: SimulationEvent[]
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null)

  if (events.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: '#64748b',
          fontSize: '0.8rem',
        }}
      >
        No simulation events yet. Transmit a packet or ping to observe real-time forwarding telemetry.
      </div>
    )
  }

  const toggleWhy = (eventId: string) => {
    setExpandedEventId((curr) => (curr === eventId ? null : eventId))
  }

  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'SUCCESS':
        return <CheckCircle size={14} color="#34d399" />
      case 'ERROR':
        return <AlertCircle size={14} color="#f87171" />
      case 'WARNING':
        return <AlertTriangle size={14} color="#fbbf24" />
      default:
        return <Info size={14} color="#38bdf8" />
    }
  }

  return (
    <div className="timeline-scroll" aria-label="Event Timeline">
      {events.map((evt) => {
        const isExpanded = expandedEventId === evt.id
        const sevClass = evt.severity.toLowerCase()

        return (
          <div key={evt.id} className="timeline-item">
            <div style={{ marginTop: '0.15rem' }}>{getSeverityIcon(evt.severity)}</div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                <span className={`timeline-severity-badge ${sevClass}`}>
                  {evt.severity}
                </span>
                <span style={{ fontSize: '0.72rem', color: '#64748b', fontFamily: 'monospace' }}>
                  +{evt.timestamp_ms}ms
                </span>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8' }}>
                  [{evt.device_name}]
                </span>
                <span style={{ fontSize: '0.7rem', color: '#94a3b8', background: '#1e293b', padding: '0.1rem 0.35rem', borderRadius: '0.2rem' }}>
                  {evt.type}
                </span>
              </div>

              <div className="timeline-msg">{evt.message}</div>

              {/* Accordion Explanation */}
              {isExpanded && (
                <div className="edu-explanation-box">
                  <div className="edu-header">
                    <HelpCircle size={14} /> Why Did This Happen?
                  </div>
                  <div className="edu-text">{evt.explanation}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.4rem' }}>
                    <strong>Networking Principle:</strong> {evt.why_reason}
                  </div>
                  <div className="edu-cyber">
                    <Shield size={12} style={{ display: 'inline', marginRight: '0.3rem' }} />
                    {evt.cyber_relevance}
                  </div>
                </div>
              )}
            </div>

            <button
              className="timeline-why-btn"
              onClick={() => toggleWhy(evt.id)}
              title="Learn why this network action occurred"
            >
              {isExpanded ? 'Hide' : 'Why?'}
            </button>
          </div>
        )
      })}
    </div>
  )
}
