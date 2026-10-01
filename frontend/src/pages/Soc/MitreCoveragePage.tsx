import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MitreMatrix } from '../../components/incident_response/MitreMatrix'
import { incidentResponseApi } from '../../services/incidentResponseApi'
import type { AttackTechnique, MatrixCoverageResponse } from '../../types/incidentResponse'
import '../../components/incident_response/incidentResponse.css'

export const MitreCoveragePage: React.FC = () => {
  const [coverage, setCoverage] = useState<MatrixCoverageResponse | null>(null)
  const [allTechniques, setAllTechniques] = useState<AttackTechnique[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      incidentResponseApi.getMatrixCoverage(),
      incidentResponseApi.listTechniques(),
    ])
      .then(([cov, techs]) => {
        setCoverage(cov)
        setAllTechniques(techs)
      })
      .finally(() => setLoading(false))
  }, [])

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
          <h1>MITRE ATT&CK Enterprise Matrix</h1>
          <p className="ir-subtitle">
            Navigate the 14 Enterprise Tactics, explore attacker techniques, and observe detection and mitigation guidance.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/soc/playbooks" className="ir-btn-secondary">
            📖 Browse Playbooks
          </Link>
          <Link to="/soc/incidents" className="ir-btn-primary">
            Active Incidents
          </Link>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '48px', color: '#9ca3af' }}>Loading ATT&CK Matrix...</div>
      ) : (
        <MitreMatrix coverage={coverage} allTechniques={allTechniques} />
      )}
    </div>
  )
}
