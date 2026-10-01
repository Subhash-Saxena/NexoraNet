import React, { useState } from 'react'
import type {
  AttackTechnique,
  IncidentTechniqueMapping,
  MatrixCoverageResponse,
  MatrixTechniqueCoverage,
} from '../../types/incidentResponse'

interface MitreMatrixProps {
  coverage: MatrixCoverageResponse | null
  incidentId?: number
  currentMappings?: IncidentTechniqueMapping[]
  onMapTechnique?: (techniqueId: string, confidence: string, summary: string) => Promise<void>
  onUnmapTechnique?: (techniqueId: string) => Promise<void>
  allTechniques?: AttackTechnique[]
}

export const MitreMatrix: React.FC<MitreMatrixProps> = ({
  coverage,
  incidentId,
  currentMappings = [],
  onMapTechnique,
  onUnmapTechnique,
  allTechniques = [],
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [showMappedOnly, setShowMappedOnly] = useState(false)
  const [selectedTech, setSelectedTech] = useState<AttackTechnique | null>(null)
  const [confidence, setConfidence] = useState('OBSERVED_EVIDENCE')
  const [evidenceSummary, setEvidenceSummary] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  if (!coverage) {
    return <div style={{ padding: '24px', color: '#9ca3af' }}>Loading MITRE ATT&CK Matrix...</div>
  }

  const handleTileClick = (techCoverage: MatrixTechniqueCoverage) => {
    const fullTech = allTechniques.find((t) => t.technique_id === techCoverage.technique_id)
    if (fullTech) {
      setSelectedTech(fullTech)
      const existing = currentMappings.find((m) => m.technique?.technique_id === fullTech.technique_id)
      if (existing) {
        setConfidence(existing.mapping_confidence)
        setEvidenceSummary(existing.evidence_summary || '')
      } else {
        setConfidence('OBSERVED_EVIDENCE')
        setEvidenceSummary('')
      }
    } else {
      setSelectedTech({
        id: techCoverage.id,
        technique_id: techCoverage.technique_id,
        tactic_id: 0,
        name: techCoverage.name,
        description: 'Technique details available in MITRE Enterprise knowledge base.',
        is_subtechnique: techCoverage.is_subtechnique,
      })
    }
  }

  const handleSaveMapping = async () => {
    if (!selectedTech || !onMapTechnique) return
    setActionLoading(true)
    try {
      await onMapTechnique(selectedTech.technique_id, confidence, evidenceSummary)
      setSelectedTech(null)
    } finally {
      setActionLoading(false)
    }
  }

  const handleRemoveMapping = async () => {
    if (!selectedTech || !onUnmapTechnique) return
    setActionLoading(true)
    try {
      await onUnmapTechnique(selectedTech.technique_id)
      setSelectedTech(null)
    } finally {
      setActionLoading(false)
    }
  }

  const isCurrentTechMapped = selectedTech
    ? currentMappings.some((m) => m.technique?.technique_id === selectedTech.technique_id)
    : false

  return (
    <div>
      {/* Controls & Metrics Header */}
      <div className="ir-filter-bar">
        <input
          type="text"
          className="ir-search-input"
          placeholder="Filter techniques by name or ID (e.g. T1059, PowerShell)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.88rem' }}>
          <input
            type="checkbox"
            checked={showMappedOnly}
            onChange={(e) => setShowMappedOnly(e.target.checked)}
          />
          Show Observed Techniques Only
        </label>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '14px', fontSize: '0.85rem' }}>
          <span>
            Observed: <strong style={{ color: '#06b6d4' }}>{coverage.covered_techniques}</strong> / {coverage.total_techniques}
          </span>
          <span>
            Coverage: <strong style={{ color: '#10b981' }}>{coverage.coverage_percentage}%</strong>
          </span>
        </div>
      </div>

      {/* 14-Column Matrix Grid */}
      <div className="mitre-matrix-container">
        {coverage.tactics.map((col) => {
          const filteredTechs = col.techniques.filter((t) => {
            if (showMappedOnly && !t.is_mapped) return false
            if (searchTerm) {
              const term = searchTerm.toLowerCase()
              return t.technique_id.toLowerCase().includes(term) || t.name.toLowerCase().includes(term)
            }
            return true
          })

          return (
            <div key={col.tactic_id} className="mitre-tactic-col">
              <div className="mitre-tactic-header">
                <div>{col.name}</div>
                <small>
                  {col.tactic_id} • {col.mapped_count}/{col.total_count}
                </small>
              </div>
              <div className="mitre-tech-list">
                {filteredTechs.map((tech) => (
                  <div
                    key={tech.technique_id}
                    className={`mitre-tech-tile ${tech.is_mapped ? 'mapped' : ''}`}
                    onClick={() => handleTileClick(tech)}
                    title={`${tech.technique_id}: ${tech.name}`}
                  >
                    <div className="mitre-tech-id">{tech.technique_id}</div>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {tech.name}
                    </div>
                  </div>
                ))}
                {filteredTechs.length === 0 && (
                  <div style={{ padding: '8px', fontSize: '0.75rem', color: '#6b7280', textAlign: 'center' }}>
                    No matches
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Technique Detail Modal */}
      {selectedTech && (
        <div className="ir-modal-backdrop" onClick={() => setSelectedTech(null)}>
          <div className="ir-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="ir-modal-header">
              <div>
                <span className="ir-pill badge-cyan">{selectedTech.technique_id}</span>
                <h3 style={{ marginTop: '6px' }}>{selectedTech.name}</h3>
              </div>
              <button className="ir-modal-close" onClick={() => setSelectedTech(null)}>
                &times;
              </button>
            </div>

            <div style={{ marginBottom: '16px', fontSize: '0.9rem', lineHeight: '1.5', color: '#d1d5db' }}>
              <p>{selectedTech.description}</p>
            </div>

            {selectedTech.platforms && (
              <div style={{ marginBottom: '12px', fontSize: '0.85rem' }}>
                <strong style={{ color: '#9ca3af' }}>Platforms: </strong>
                <span>{selectedTech.platforms}</span>
              </div>
            )}

            {selectedTech.data_sources && (
              <div style={{ marginBottom: '12px', fontSize: '0.85rem' }}>
                <strong style={{ color: '#9ca3af' }}>Data Sources: </strong>
                <span>{selectedTech.data_sources}</span>
              </div>
            )}

            {selectedTech.detection_guidance && (
              <div style={{ marginBottom: '14px', background: '#1e293b', padding: '12px', borderRadius: '6px' }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#38bdf8', marginBottom: '4px' }}>
                  🔍 Detection Guidance
                </div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{selectedTech.detection_guidance}</div>
              </div>
            )}

            {selectedTech.mitigation_guidance && (
              <div style={{ marginBottom: '16px', background: '#1e293b', padding: '12px', borderRadius: '6px' }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#4ade80', marginBottom: '4px' }}>
                  🛡️ Mitigation Strategy
                </div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{selectedTech.mitigation_guidance}</div>
              </div>
            )}

            {incidentId && onMapTechnique && (
              <div style={{ borderTop: '1px solid #374151', paddingTop: '16px', marginTop: '16px' }}>
                <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem' }}>
                  {isCurrentTechMapped ? 'Update Technique Mapping' : 'Map to Current Incident'}
                </h4>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                  <select
                    className="ir-select"
                    value={confidence}
                    onChange={(e) => setConfidence(e.target.value)}
                  >
                    <option value="OBSERVED_EVIDENCE">Observed Evidence (High)</option>
                    <option value="HYPOTHESIS_SUGGESTED">Hypothesis Suggested (Medium)</option>
                    <option value="ANALYST_INFERRED">Analyst Inferred (Low)</option>
                  </select>
                </div>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '70px', marginBottom: '12px' }}
                  placeholder="Evidence summary / justification for this mapping..."
                  value={evidenceSummary}
                  onChange={(e) => setEvidenceSummary(e.target.value)}
                />
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  {isCurrentTechMapped && onUnmapTechnique && (
                    <button
                      className="ir-btn-secondary"
                      style={{ color: '#ef4444', borderColor: '#ef4444' }}
                      onClick={handleRemoveMapping}
                      disabled={actionLoading}
                    >
                      Remove Mapping
                    </button>
                  )}
                  <button className="ir-btn-primary" onClick={handleSaveMapping} disabled={actionLoading}>
                    {actionLoading ? 'Saving...' : isCurrentTechMapped ? 'Update Mapping' : 'Map Technique'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
