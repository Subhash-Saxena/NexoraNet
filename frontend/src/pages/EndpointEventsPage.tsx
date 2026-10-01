import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { EndpointNav } from '../components/endpoint_security/EndpointNav'
import type { EndpointEvent } from '../types/endpointSecurity'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import '../components/endpoint_security/endpointSecurity.css'

export const EndpointEventsPage: React.FC = () => {
  const [events, setEvents] = useState<EndpointEvent[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [category, setCategory] = useState<string>('')
  const [severity, setSeverity] = useState<string>('')
  const [search, setSearch] = useState<string>('')
  const [page, setPage] = useState(0)
  const limit = 25

  // Event modal & pivots
  const [selectedEvent, setSelectedEvent] = useState<EndpointEvent | null>(null)
  const [pivotLoading, setPivotLoading] = useState(false)
  const [pivotResult, setPivotResult] = useState<string | null>(null)

  const fetchEvents = async () => {
    try {
      setLoading(true)
      const data = await endpointSecurityApi.listEvents({
        category: category || undefined,
        severity: severity || undefined,
        search: search || undefined,
        skip: page * limit,
        limit,
      })
      setEvents(data.items)
      setTotal(data.total)
    } catch (err: any) {
      console.error('Failed to list events:', err)
      setError(err.message || 'Failed to fetch telemetry events')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [category, severity, page])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(0)
    fetchEvents()
  }

  const handlePivotIntel = async (eventId: string) => {
    setPivotLoading(true)
    setPivotResult(null)
    try {
      const res = await endpointSecurityApi.pivotToIntel(eventId)
      setPivotResult(
        `Threat Intel Analyzed: ${res.observables.length} observable(s) checked. ${res.analyst_guidance}`
      )
    } catch (err: any) {
      setPivotResult(`Threat Intel Error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  const handleStartThreatHunt = async (eventId: string) => {
    setPivotLoading(true)
    setPivotResult(null)
    try {
      const res = await endpointSecurityApi.startThreatHunt(eventId)
      setPivotResult(
        `Threat Hunt Initiated: ${res.hunt_id} ("${res.title}"). Status: ${res.status}. Initial Pivot: ${res.initial_pivot_type} ${res.initial_pivot_value}`
      )
    } catch (err: any) {
      setPivotResult(`Threat Hunt Error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  const handleEscalateSoc = async (eventId: string) => {
    setPivotLoading(true)
    setPivotResult(null)
    try {
      const res = await endpointSecurityApi.investigateInSoc(eventId)
      setPivotResult(
        `SOC Case Created: ${res.investigation_id} ("${res.title}"). Priority: ${res.priority}`
      )
    } catch (err: any) {
      setPivotResult(`SOC Escalation Error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  const handleCorrelateSiem = async (eventId: string) => {
    setPivotLoading(true)
    setPivotResult(null)
    try {
      const res = await endpointSecurityApi.correlateSiem(eventId)
      setPivotResult(
        `SIEM Temporal Correlation: Found ${res.length} correlated log events in temporal window.`
      )
    } catch (err: any) {
      setPivotResult(`SIEM Correlation Error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  const handleCorrelatePcap = async (eventId: string) => {
    setPivotLoading(true)
    setPivotResult(null)
    try {
      const res = await endpointSecurityApi.correlatePcap(eventId)
      setPivotResult(
        `PCAP Packet Correlation: Found ${res.length} packet matches in offline captures.`
      )
    } catch (err: any) {
      setPivotResult(`PCAP Correlation Error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  return (
    <div className="endpoint-container">
      {/* Synthetic Warning */}
      <div className="endpoint-synthetic-banner">
        <div className="banner-left">
          <span className="banner-icon">🛡️</span>
          <div>
            <div className="banner-title">
              NexoraNet Endpoint Lab — Synthetic Telemetry Events Explorer
            </div>
            <div className="banner-subtitle">
              All telemetry records are pre-generated synthetic events conforming to RFC 5737 and RFC 2606.
            </div>
          </div>
        </div>
        <span className="banner-badge">MULTI-HOST TELEMETRY</span>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
          Endpoint Events Explorer
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Query, filter, and pivot across synthetic endpoint telemetry spanning processes, authentication, network connections, DNS, and file activities.
        </p>
      </div>

      <EndpointNav />

      {/* Filter and Search Bar */}
      <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', flex: 1, minWidth: '280px' }}>
          <input
            type="text"
            placeholder="Search command, process, user, IP, domain, hash..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 0.85rem',
              color: '#f8fafc',
              fontSize: '0.85rem',
              width: '100%',
            }}
          />
          <button type="submit" className="btn-cyber-primary">
            Search
          </button>
        </form>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value)
              setPage(0)
            }}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 0.75rem',
              color: '#cbd5e1',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All Categories</option>
            <option value="PROCESS">Process</option>
            <option value="AUTHENTICATION">Authentication</option>
            <option value="NETWORK">Network</option>
            <option value="DNS">DNS</option>
            <option value="FILE">File</option>
            <option value="PERSISTENCE">Persistence</option>
            <option value="PRIVILEGE">Privilege</option>
            <option value="SERVICE">Service</option>
            <option value="REGISTRY">Registry</option>
          </select>

          <select
            value={severity}
            onChange={(e) => {
              setSeverity(e.target.value)
              setPage(0)
            }}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 0.75rem',
              color: '#cbd5e1',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Info</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '8px', padding: '1rem', color: '#fca5a5', marginBottom: '1.5rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
          Loading telemetry events...
        </div>
      ) : events.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: '#111827', borderRadius: '8px', color: '#64748b' }}>
          No telemetry events match query filters.
        </div>
      ) : (
        <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem' }}>Host</th>
                <th style={{ padding: '0.75rem 1rem' }}>Category</th>
                <th style={{ padding: '0.75rem 1rem' }}>Event Type</th>
                <th style={{ padding: '0.75rem 1rem' }}>Severity</th>
                <th style={{ padding: '0.75rem 1rem' }}>Process / Summary</th>
                <th style={{ padding: '0.75rem 1rem' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {events.map((evt) => {
                const sevClass = (evt.severity || 'low').toLowerCase()
                return (
                  <tr key={evt.id} style={{ borderBottom: '1px solid #1f2937' }}>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
                      {new Date(evt.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <Link
                        to={`/endpoint-security/hosts/${evt.host_id}`}
                        style={{ color: '#38bdf8', textDecoration: 'none', fontWeight: 600 }}
                      >
                        {evt.host_hostname || `Host-${evt.host_id}`}
                      </Link>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: '#94a3b8' }}>
                      {evt.event_category}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#f1f5f9' }}>
                      {evt.event_type}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span className={`risk-badge ${sevClass}`}>{evt.severity}</span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', maxWidth: '350px' }}>
                      <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#cbd5e1' }}>
                        {evt.command_summary || evt.command_line || evt.raw_event_reference || 'N/A'}
                      </div>
                      {evt.process_name && (
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          Process: {evt.process_name} (PID: {evt.process_id})
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <button
                        type="button"
                        className="btn-cyber-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem' }}
                        onClick={() => {
                          setSelectedEvent(evt)
                          setPivotResult(null)
                        }}
                      >
                        Inspect ➔
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {/* Pagination */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#0f172a', borderTop: '1px solid #1f2937', fontSize: '0.85rem', color: '#94a3b8' }}>
            <div>
              Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total} events
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                type="button"
                className="btn-cyber-secondary"
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(p - 1, 0))}
                style={{ fontSize: '0.8rem', padding: '0.3rem 0.65rem' }}
              >
                Previous
              </button>
              <button
                type="button"
                className="btn-cyber-secondary"
                disabled={(page + 1) * limit >= total}
                onClick={() => setPage((p) => p + 1)}
                style={{ fontSize: '0.8rem', padding: '0.3rem 0.65rem' }}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Selected Event Details & Pivots Modal */}
      {selectedEvent && (
        <div className="endpoint-modal-overlay" onClick={() => setSelectedEvent(null)}>
          <div className="endpoint-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #1f2937', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ margin: 0, color: '#f8fafc' }}>
                  Event Details: {selectedEvent.event_id}
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  {selectedEvent.event_type} | Category: {selectedEvent.event_category}
                </span>
              </div>
              <button
                type="button"
                className="btn-cyber-secondary"
                onClick={() => setSelectedEvent(null)}
              >
                ✕ Close
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem', fontSize: '0.85rem' }}>
              <div><strong>Timestamp:</strong> {new Date(selectedEvent.timestamp).toLocaleString()}</div>
              <div><strong>Severity:</strong> <span className={`risk-badge ${selectedEvent.severity.toLowerCase()}`}>{selectedEvent.severity}</span></div>
              <div><strong>Process:</strong> {selectedEvent.process_name || 'N/A'} (PID: {selectedEvent.process_id || 'N/A'})</div>
              <div><strong>User:</strong> {selectedEvent.username || 'SYSTEM'}</div>
              <div><strong>Destination IP:</strong> {selectedEvent.destination_ip ? `${selectedEvent.destination_ip}:${selectedEvent.destination_port}` : 'N/A'}</div>
              <div><strong>Domain:</strong> {selectedEvent.domain || 'N/A'}</div>
              <div><strong>File Path:</strong> {selectedEvent.file_path || 'N/A'}</div>
              <div><strong>SHA256 Hash:</strong> {selectedEvent.file_hash ? `${selectedEvent.file_hash.substring(0, 16)}...` : 'N/A'}</div>
            </div>

            {selectedEvent.command_line && (
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  Command Execution:
                </label>
                <div className="code-block" style={{ fontSize: '0.775rem' }}>
                  {selectedEvent.command_line}
                </div>
              </div>
            )}

            {/* 1-Click Pivot Actions */}
            <div style={{ borderTop: '1px solid #1f2937', paddingTop: '1rem', marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.65rem' }}>
                Investigative Pivots & Cross-Correlations:
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  className="btn-cyber-pivot"
                  disabled={pivotLoading}
                  onClick={() => handlePivotIntel(selectedEvent.event_id)}
                >
                  🔎 Threat Intel
                </button>
                <button
                  type="button"
                  className="btn-cyber-pivot"
                  disabled={pivotLoading}
                  onClick={() => handleStartThreatHunt(selectedEvent.event_id)}
                >
                  🎯 Threat Hunt
                </button>
                <button
                  type="button"
                  className="btn-cyber-pivot"
                  disabled={pivotLoading}
                  onClick={() => handleEscalateSoc(selectedEvent.event_id)}
                >
                  🚨 Escalate to SOC
                </button>
                <button
                  type="button"
                  className="btn-cyber-pivot"
                  disabled={pivotLoading}
                  onClick={() => handleCorrelateSiem(selectedEvent.event_id)}
                >
                  ⚡ Correlate SIEM
                </button>
                <button
                  type="button"
                  className="btn-cyber-pivot"
                  disabled={pivotLoading}
                  onClick={() => handleCorrelatePcap(selectedEvent.event_id)}
                >
                  📦 Correlate PCAP
                </button>
              </div>
            </div>

            {pivotLoading && (
              <div style={{ color: '#38bdf8', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Executing pivot action...
              </div>
            )}

            {pivotResult && (
              <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.75rem', fontSize: '0.825rem', color: '#38bdf8', marginBottom: '1rem' }}>
                {pivotResult}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
