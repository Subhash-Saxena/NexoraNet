import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { incidentResponseApi } from '../../services/incidentResponseApi'
import type { IncidentPlaybook } from '../../types/incidentResponse'
import '../../components/incident_response/incidentResponse.css'

export const PlaybooksPage: React.FC = () => {
  const [playbooks, setPlaybooks] = useState<IncidentPlaybook[]>([])
  const [selectedPlaybook, setSelectedPlaybook] = useState<IncidentPlaybook | null>(null)
  const [categoryFilter, setCategoryFilter] = useState('ALL')
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    incidentResponseApi
      .listPlaybooks()
      .then((data) => {
        setPlaybooks(data)
        if (data.length > 0) setSelectedPlaybook(data[0])
      })
      .finally(() => setLoading(false))
  }, [])

  const filteredPlaybooks = playbooks.filter((p) => {
    if (categoryFilter !== 'ALL' && p.category !== categoryFilter) return false
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      return p.title.toLowerCase().includes(term) || p.playbook_id.toLowerCase().includes(term)
    }
    return true
  })

  const parsedPhases = selectedPlaybook ? JSON.parse(selectedPlaybook.phases_definition || '{}') : {}
  const parsedChecklist = selectedPlaybook ? JSON.parse(selectedPlaybook.checklist_json || '[]') : []
  const parsedActions = selectedPlaybook ? JSON.parse(selectedPlaybook.recommended_actions_json || '[]') : []

  return (
    <div className="ir-container">
      {/* Header */}
      <div className="ir-header">
        <div>
          <div style={{ marginBottom: '8px' }}>
            <Link to="/soc/incidents" style={{ color: '#06b6d4', textDecoration: 'none', fontSize: '0.85rem' }}>
              ← Back to Incident Queue
            </Link>
          </div>
          <h1>Standardized Incident Response Playbooks</h1>
          <p className="ir-subtitle">
            Structured NIST SP 800-61 standard operating procedures for triaging and containing critical incident types.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/soc/mitre" className="ir-btn-secondary">
            🎯 ATT&CK Matrix
          </Link>
          <Link to="/soc/incidents" className="ir-btn-primary">
            Active Incidents
          </Link>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="ir-filter-bar">
        <input
          type="text"
          className="ir-search-input"
          placeholder="Search playbooks (Ransomware, Phishing, Pass-the-Hash)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select
          className="ir-select"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="ALL">All Categories</option>
          <option value="MALWARE">Malware</option>
          <option value="CREDENTIALS">Credentials & Access</option>
          <option value="NETWORK">Network Exploitation</option>
          <option value="PHISHING">Phishing</option>
          <option value="EXFILTRATION">Exfiltration</option>
          <option value="ENDPOINT">Endpoint Abuse</option>
        </select>
      </div>

      {/* Main 2-column layout */}
      {loading ? (
        <div style={{ padding: '40px', color: '#9ca3af' }}>Loading Playbooks...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px' }}>
          {/* Left Playbook List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredPlaybooks.map((pb) => {
              const isSelected = selectedPlaybook?.playbook_id === pb.playbook_id
              return (
                <div
                  key={pb.playbook_id}
                  onClick={() => setSelectedPlaybook(pb)}
                  style={{
                    background: isSelected ? 'rgba(6, 182, 212, 0.15)' : '#111827',
                    border: `1px solid ${isSelected ? '#06b6d4' : '#374151'}`,
                    borderRadius: '8px',
                    padding: '12px 14px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span className="ir-table-id">{pb.playbook_id}</span>
                    <span className="ir-pill badge-cyan">{pb.category}</span>
                  </div>
                  <strong style={{ color: '#fff', fontSize: '0.9rem', display: 'block', marginBottom: '4px' }}>
                    {pb.title}
                  </strong>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {pb.description}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Right Playbook Detail */}
          {selectedPlaybook && (
            <div>
              <div className="ir-kpi-card" style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <div>
                    <span className="ir-pill badge-cyan">{selectedPlaybook.playbook_id}</span>
                    <h2 style={{ margin: '8px 0 6px 0', fontSize: '1.4rem', color: '#fff' }}>
                      {selectedPlaybook.title}
                    </h2>
                    <p style={{ margin: 0, color: '#9ca3af', fontSize: '0.9rem', lineHeight: '1.5' }}>
                      {selectedPlaybook.description}
                    </p>
                  </div>
                  <span
                    className={`ir-pill ${
                      selectedPlaybook.severity_guidance === 'CRITICAL'
                        ? 'badge-crit'
                        : selectedPlaybook.severity_guidance === 'HIGH'
                        ? 'badge-high'
                        : 'badge-med'
                    }`}
                  >
                    Recommended: {selectedPlaybook.severity_guidance}
                  </span>
                </div>

                {/* Recommended Simulated Actions */}
                <div style={{ marginTop: '12px', borderTop: '1px solid #1f2937', paddingTop: '10px' }}>
                  <small style={{ color: '#9ca3af', fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                    Recommended Defensive Actions (Simulation)
                  </small>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {parsedActions.map((actionCode: string, i: number) => (
                      <span key={i} className="ir-pill badge-emerald">
                        🛡️ {actionCode}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Checklist */}
              <div className="ir-kpi-card" style={{ marginBottom: '20px' }}>
                <h3 style={{ margin: '0 0 10px 0', fontSize: '1.05rem', color: '#38bdf8' }}>
                  📋 Key Triage Questions & Artifact Checklist
                </h3>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#cbd5e1', lineHeight: '1.7', fontSize: '0.9rem' }}>
                  {parsedChecklist.map((item: string, i: number) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* Phases */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                {Object.entries(parsedPhases).map(([phase, steps]: [string, any]) => (
                  <div key={phase} className="ir-kpi-card">
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '0.92rem', color: '#a5f3fc', textTransform: 'uppercase' }}>
                      {phase.replace(/_/g, ' ')}
                    </h4>
                    <ol style={{ margin: 0, paddingLeft: '20px', color: '#9ca3af', fontSize: '0.85rem', lineHeight: '1.5' }}>
                      {(steps as string[]).map((step: string, sIdx: number) => (
                        <li key={sIdx} style={{ marginBottom: '6px' }}>{step}</li>
                      ))}
                    </ol>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
