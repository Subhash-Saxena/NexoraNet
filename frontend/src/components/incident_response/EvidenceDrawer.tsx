import React, { useState } from 'react'
import type { IncidentEvidence } from '../../types/incidentResponse'

interface EvidenceDrawerProps {
  evidenceList: IncidentEvidence[]
  onAddEvidence: (data: {
    title: string
    description: string
    evidence_type: string
    source_engine: string
    source_id?: string
    relevance: string
    data_payload?: string
  }) => Promise<void>
  onVerifyHash: (evidenceId: number) => Promise<{ is_valid: boolean; stored_hash: string; computed_hash: string }>
  onUpdateEvidence: (evidenceId: number, data: { relevance?: string; is_contained?: boolean }) => Promise<void>
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  evidenceList,
  onAddEvidence,
  onVerifyHash,
  onUpdateEvidence,
}) => {
  const [filterType, setFilterType] = useState('ALL')
  const [showAddModal, setShowAddModal] = useState(false)
  const [verifyingId, setVerifyingId] = useState<number | null>(null)
  const [verificationResult, setVerificationResult] = useState<{ id: number; passed: boolean } | null>(null)
  const [expandedChainId, setExpandedChainId] = useState<number | null>(null)

  // Form states
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [evidenceType, setEvidenceType] = useState('ALERT')
  const [sourceEngine, setSourceEngine] = useState('DETECTION_ENGINE')
  const [sourceId, setSourceId] = useState('')
  const [relevance, setRelevance] = useState('SUPPORTING')
  const [payloadText, setPayloadText] = useState('')

  const handleVerify = async (evId: number) => {
    setVerifyingId(evId)
    try {
      const res = await onVerifyHash(evId)
      setVerificationResult({ id: evId, passed: res.is_valid })
    } finally {
      setVerifyingId(null)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    await onAddEvidence({
      title,
      description,
      evidence_type: evidenceType,
      source_engine: sourceEngine,
      source_id: sourceId || undefined,
      relevance,
      data_payload: payloadText || undefined,
    })
    setShowAddModal(false)
    setTitle('')
    setDescription('')
    setSourceId('')
    setPayloadText('')
  }

  const filteredEvidence = evidenceList.filter((ev) => {
    if (filterType !== 'ALL' && ev.evidence_type !== filterType) return false
    return true
  })

  return (
    <div>
      {/* Header bar */}
      <div className="ir-filter-bar">
        <select
          className="ir-select"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="ALL">All Evidence Types</option>
          <option value="ALERT">Detection Alerts</option>
          <option value="PROCESS_EVENT">Process Events</option>
          <option value="SIEM_EVENT">SIEM Logs</option>
          <option value="ENDPOINT_EVENT">Endpoint Telemetry</option>
          <option value="DNS_EVENT">DNS Events</option>
          <option value="IOC">Threat Indicators (IOC)</option>
          <option value="PCAP">PCAP Artifacts</option>
        </select>

        <div style={{ marginLeft: 'auto' }}>
          <button className="ir-btn-primary" onClick={() => setShowAddModal(true)}>
            + Attach Evidence
          </button>
        </div>
      </div>

      {/* Grid of Evidence Cards */}
      <div className="ir-evidence-grid">
        {filteredEvidence.map((ev) => {
          const isVerifying = verifyingId === ev.id
          const verifyStatus = verificationResult?.id === ev.id ? verificationResult.passed : null

          return (
            <div key={ev.id} className="ir-evidence-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <span className="ir-table-id">{ev.evidence_id}</span>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <span className="ir-pill badge-cyan">{ev.source_engine}</span>
                  <span
                    className={`ir-pill ${
                      ev.relevance === 'SUPPORTING'
                        ? 'badge-emerald'
                        : ev.relevance === 'CONTRADICTING'
                        ? 'badge-crit'
                        : 'badge-low'
                    }`}
                  >
                    {ev.relevance}
                  </span>
                </div>
              </div>

              <h4 style={{ margin: '0 0 6px 0', fontSize: '1rem', color: '#fff' }}>{ev.title}</h4>
              <p style={{ margin: '0 0 10px 0', fontSize: '0.85rem', color: '#9ca3af', lineHeight: '1.4' }}>
                {ev.description}
              </p>

              {/* Cryptographic Hash Section */}
              <div style={{ marginTop: 'auto', paddingTop: '10px', borderTop: '1px solid #1f2937' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <small style={{ color: '#6b7280', fontSize: '0.72rem', textTransform: 'uppercase' }}>
                    SHA-256 Hash Integrity
                  </small>
                  <button
                    className="ir-btn-secondary"
                    style={{ padding: '2px 8px', fontSize: '0.75rem' }}
                    onClick={() => handleVerify(ev.id)}
                    disabled={isVerifying}
                  >
                    {isVerifying ? 'Verifying...' : 'Verify Hash'}
                  </button>
                </div>
                <div className="ir-hash-badge">
                  {ev.hash_sha256 || 'No payload hash calculated'}
                </div>

                {verifyStatus !== null && (
                  <div
                    style={{
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      color: verifyStatus ? '#10b981' : '#ef4444',
                      marginBottom: '6px',
                    }}
                  >
                    {verifyStatus ? '✓ Cryptographic Hash Matches Stored Value' : '✗ Hash Verification Mismatch!'}
                  </div>
                )}

                {/* Chain of Custody & Actions */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
                  <button
                    style={{ background: 'none', border: 'none', color: '#06b6d4', fontSize: '0.78rem', cursor: 'pointer', padding: 0 }}
                    onClick={() => setExpandedChainId(expandedChainId === ev.id ? null : ev.id)}
                  >
                    {expandedChainId === ev.id ? '▼ Hide Chain of Custody' : '▶ Chain of Custody Logs'}
                  </button>

                  <select
                    className="ir-select"
                    style={{ padding: '2px 6px', fontSize: '0.75rem' }}
                    value={ev.relevance}
                    onChange={(e) => onUpdateEvidence(ev.id, { relevance: e.target.value })}
                  >
                    <option value="SUPPORTING">Supporting</option>
                    <option value="CONTRADICTING">Contradicting</option>
                    <option value="CONTEXT">Contextual</option>
                    <option value="INCONCLUSIVE">Inconclusive</option>
                  </select>
                </div>

                {/* Expanded Chain of Custody Logs */}
                {expandedChainId === ev.id && ev.audit_logs && (
                  <div style={{ marginTop: '8px', background: '#0f172a', padding: '8px', borderRadius: '4px', fontSize: '0.75rem' }}>
                    <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '4px' }}>
                      Audit Log ({ev.audit_logs.length} touches)
                    </div>
                    {ev.audit_logs.map((log) => (
                      <div key={log.id} style={{ marginBottom: '4px', color: '#cbd5e1' }}>
                        <span style={{ color: '#9ca3af' }}>
                          {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>{' '}
                        • <strong>{log.action}</strong>: {log.details}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {filteredEvidence.length === 0 && (
          <div style={{ gridColumn: '1 / -1', padding: '32px', textAlign: 'center', color: '#6b7280' }}>
            No evidence artifacts attached under the selected category.
          </div>
        )}
      </div>

      {/* Attach Evidence Modal */}
      {showAddModal && (
        <div className="ir-modal-backdrop" onClick={() => setShowAddModal(false)}>
          <div className="ir-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="ir-modal-header">
              <h3>Attach Cross-Engine Evidence</h3>
              <button className="ir-modal-close" onClick={() => setShowAddModal(false)}>
                &times;
              </button>
            </div>

            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Title</label>
                <input
                  type="text"
                  className="ir-search-input"
                  style={{ width: '100%' }}
                  placeholder="e.g. C2 Beacon NetFlow Record"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Source Engine</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={sourceEngine}
                    onChange={(e) => setSourceEngine(e.target.value)}
                  >
                    <option value="DETECTION_ENGINE">Detection Engine (IDS)</option>
                    <option value="SIEM">SIEM & Security Logs</option>
                    <option value="ENDPOINT_SECURITY">Endpoint Security</option>
                    <option value="THREAT_INTEL">Threat Intelligence</option>
                    <option value="PCAP_ANALYZER">PCAP Packet Capture</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Evidence Type</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={evidenceType}
                    onChange={(e) => setEvidenceType(e.target.value)}
                  >
                    <option value="ALERT">Alert</option>
                    <option value="SIEM_EVENT">SIEM Event</option>
                    <option value="PROCESS_EVENT">Process Event</option>
                    <option value="ENDPOINT_EVENT">Host Telemetry</option>
                    <option value="DNS_EVENT">DNS Query</option>
                    <option value="IOC">Threat Indicator</option>
                    <option value="PACKET">Network Packet</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Source ID / Ref</label>
                  <input
                    type="text"
                    className="ir-search-input"
                    style={{ width: '100%' }}
                    placeholder="e.g. LOG-99812 or HOST-FIN-01"
                    value={sourceId}
                    onChange={(e) => setSourceId(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Initial Relevance</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={relevance}
                    onChange={(e) => setRelevance(e.target.value)}
                  >
                    <option value="SUPPORTING">Supporting</option>
                    <option value="CONTRADICTING">Contradicting</option>
                    <option value="CONTEXT">Contextual</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Description</label>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '60px' }}
                  placeholder="Analytical reasoning for attaching this artifact..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Data Payload (Calculates SHA-256)</label>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '70px', fontFamily: 'monospace', fontSize: '0.8rem' }}
                  placeholder='{"timestamp": "2026-10-01T...", "ip": "198.51.100.23"}'
                  value={payloadText}
                  onChange={(e) => setPayloadText(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="ir-btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="ir-btn-primary">
                  Attach & Hash
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
