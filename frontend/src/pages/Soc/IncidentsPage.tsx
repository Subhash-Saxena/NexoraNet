import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { incidentResponseApi } from '../../services/incidentResponseApi'
import type { Incident, IncidentMetrics } from '../../types/incidentResponse'
import '../../components/incident_response/incidentResponse.css'

export const IncidentsPage: React.FC = () => {
  const navigate = useNavigate()
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [metrics, setMetrics] = useState<IncidentMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [statusFilter, setStatusFilter] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  // New incident modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [newSeverity, setNewSeverity] = useState('MEDIUM')
  const [newType, setNewType] = useState('NETWORK_INTRUSION')
  const [creating, setCreating] = useState(false)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [listRes, metricsRes] = await Promise.all([
        incidentResponseApi.listIncidents({
          status: statusFilter || undefined,
          severity: severityFilter || undefined,
          incident_type: typeFilter || undefined,
          search: searchTerm || undefined,
        }),
        incidentResponseApi.getMetrics(),
      ])
      setIncidents(listRes.items)
      setMetrics(metricsRes)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [statusFilter, severityFilter, typeFilter])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    loadData()
  }

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim()) return
    setCreating(true)
    try {
      const created = await incidentResponseApi.createIncident({
        title: newTitle,
        description: newDesc,
        severity: newSeverity,
        incident_type: newType,
      })
      setShowCreateModal(false)
      navigate(`/soc/incidents/${created.incident_id}`)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Creation failed')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="ir-container">
      {/* Educational Safety Banner */}
      <div className="ir-safety-banner">
        <div>
          <span className="shield-icon">🛡️</span>
          <strong>NexoraNet Incident Response Lab — Synthetic Training Environment</strong>
          <div style={{ fontSize: '0.78rem', color: '#67e8f9', marginTop: '2px' }}>
            NIST SP 800-61 Rev 2 incident management lifecycle simulator. Strictly offline training data.
          </div>
        </div>
        <span className="ir-safety-badge">Simulation Mode Only</span>
      </div>

      {/* Header */}
      <div className="ir-header">
        <div className="ir-title-group">
          <h1>Security Incident Queue</h1>
          <p className="ir-subtitle">
            Triage, investigate, contain, and report multi-vector security incidents aligned with MITRE ATT&CK.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/soc/mitre" className="ir-btn-secondary">
            🎯 ATT&CK Matrix
          </Link>
          <Link to="/soc/playbooks" className="ir-btn-secondary">
            📖 IR Playbooks
          </Link>
          <button className="ir-btn-primary" onClick={() => setShowCreateModal(true)}>
            + New Incident
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      {metrics && (
        <div className="ir-kpi-grid">
          <div className="ir-kpi-card">
            <div className="ir-kpi-label">Active Incidents</div>
            <div className="ir-kpi-val" style={{ color: '#f97316' }}>{metrics.active_incidents}</div>
          </div>
          <div className="ir-kpi-card">
            <div className="ir-kpi-label">Critical Severity</div>
            <div className="ir-kpi-val" style={{ color: '#ef4444' }}>
              {metrics.by_severity['CRITICAL'] || 0}
            </div>
          </div>
          <div className="ir-kpi-card">
            <div className="ir-kpi-label">In Containment / Recovery</div>
            <div className="ir-kpi-val" style={{ color: '#06b6d4' }}>
              {(metrics.by_status['CONTAINMENT'] || 0) + (metrics.by_status['RECOVERY'] || 0)}
            </div>
          </div>
          <div className="ir-kpi-card">
            <div className="ir-kpi-label">Resolved / Closed</div>
            <div className="ir-kpi-val" style={{ color: '#10b981' }}>{metrics.closed_incidents}</div>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <form onSubmit={handleSearchSubmit} className="ir-filter-bar">
        <input
          type="text"
          className="ir-search-input"
          placeholder="Search incident ID, title, description, analyst..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <select
          className="ir-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="NEW">New</option>
          <option value="TRIAGED">Triaged</option>
          <option value="INVESTIGATING">Investigating</option>
          <option value="CONTAINMENT">Containment</option>
          <option value="ERADICATION">Eradication</option>
          <option value="RECOVERY">Recovery</option>
          <option value="RESOLVED">Resolved</option>
          <option value="CLOSED">Closed</option>
          <option value="FALSE_POSITIVE">False Positive</option>
        </select>

        <select
          className="ir-select"
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>

        <select
          className="ir-select"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option value="">All Threat Types</option>
          <option value="MALWARE_INDICATOR">Malware / Ransomware</option>
          <option value="CREDENTIAL_ATTACK">Credential Attack</option>
          <option value="DATA_EXFILTRATION_PATTERN">Data Exfiltration</option>
          <option value="SUSPICIOUS_PROCESS">Suspicious Process (LotL)</option>
          <option value="ENDPOINT_COMPROMISE">Endpoint Compromise</option>
          <option value="POLICY_VIOLATION">Policy Violation</option>
        </select>

        <button type="submit" className="ir-btn-secondary">
          🔍 Filter
        </button>
      </form>

      {/* Table */}
      {error && <div style={{ color: '#ef4444', marginBottom: '16px' }}>{error}</div>}

      <div className="ir-table-wrapper">
        <table className="ir-table">
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Title & Overview</th>
              <th>Threat Type</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Phase</th>
              <th>Detected At</th>
              <th>Lead Analyst</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((inc) => (
              <tr key={inc.id} onClick={() => navigate(`/soc/incidents/${inc.incident_id}`)}>
                <td>
                  <span className="ir-table-id">{inc.incident_id}</span>
                </td>
                <td style={{ maxWidth: '320px' }}>
                  <strong style={{ color: '#fff', fontSize: '0.92rem' }}>{inc.title}</strong>
                  <div style={{ fontSize: '0.78rem', color: '#9ca3af', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {inc.description}
                  </div>
                </td>
                <td>
                  <span className="ir-pill badge-cyan">{inc.incident_type.replace(/_/g, ' ')}</span>
                </td>
                <td>
                  <span
                    className={`ir-pill ${
                      inc.severity === 'CRITICAL'
                        ? 'badge-crit'
                        : inc.severity === 'HIGH'
                        ? 'badge-high'
                        : inc.severity === 'MEDIUM'
                        ? 'badge-med'
                        : 'badge-low'
                    }`}
                  >
                    {inc.severity}
                  </span>
                </td>
                <td>
                  <span
                    className={`ir-pill ${
                      inc.status === 'CONTAINMENT'
                        ? 'badge-crit'
                        : inc.status === 'ERADICATION'
                        ? 'badge-high'
                        : inc.status === 'RESOLVED' || inc.status === 'CLOSED'
                        ? 'badge-emerald'
                        : 'badge-med'
                    }`}
                  >
                    {inc.status}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>
                    {(inc.phase || '').replace(/_/g, ' ')}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                    {inc.detected_at ? new Date(inc.detected_at).toLocaleDateString() : 'N/A'}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '0.82rem', color: '#cbd5e1' }}>
                    {inc.lead_analyst || 'Unassigned'}
                  </span>
                </td>
              </tr>
            ))}

            {!loading && incidents.length === 0 && (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '36px', color: '#6b7280' }}>
                  No security incidents match the current query.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* New Incident Modal */}
      {showCreateModal && (
        <div className="ir-modal-backdrop" onClick={() => setShowCreateModal(false)}>
          <div className="ir-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="ir-modal-header">
              <h3>Create Educational Security Incident Ticket</h3>
              <button className="ir-modal-close" onClick={() => setShowCreateModal(false)}>
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateIncident}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Incident Title</label>
                <input
                  type="text"
                  className="ir-search-input"
                  style={{ width: '100%' }}
                  placeholder="e.g. Active C2 Communication from Engineering Laptop"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Severity</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={newSeverity}
                    onChange={(e) => setNewSeverity(e.target.value)}
                  >
                    <option value="CRITICAL">Critical (P1)</option>
                    <option value="HIGH">High (P2)</option>
                    <option value="MEDIUM">Medium (P3)</option>
                    <option value="LOW">Low (P4)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Threat Type</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                  >
                    <option value="NETWORK_INTRUSION">Network Intrusion</option>
                    <option value="MALWARE_INDICATOR">Malware / Ransomware</option>
                    <option value="CREDENTIAL_ATTACK">Credential Attack</option>
                    <option value="PHISHING">Phishing / Social Eng</option>
                    <option value="DATA_EXFILTRATION_PATTERN">Data Exfiltration</option>
                    <option value="ENDPOINT_COMPROMISE">Endpoint Compromise</option>
                    <option value="SUSPICIOUS_PROCESS">Suspicious Process (LotL)</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Initial Description</label>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '80px' }}
                  placeholder="Observed telemetry, alerts, and anomalous indicators..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="ir-btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="ir-btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : 'Create Incident'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
