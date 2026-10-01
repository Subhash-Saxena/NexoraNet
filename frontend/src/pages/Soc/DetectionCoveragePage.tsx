import React, { useEffect, useState } from 'react'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { DetectionCoverageResponse } from '../../types/soc'
import '../../components/soc/soc.css'

export const DetectionCoveragePage: React.FC = () => {
  const [coverage, setCoverage] = useState<DetectionCoverageResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCoverage = async () => {
      try {
        setLoading(true)
        const data = await socApi.getDetectionCoverage()
        setCoverage(data)
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to fetch detection coverage matrix.')
      } finally {
        setLoading(false)
      }
    }
    fetchCoverage()
  }, [])

  return (
    <div className="soc-container">
      <SocHeader
        title="Detection Rule Coverage & MITRE ATT&CK Mapping"
        subtitle="Review defensive sensor rule distribution, monitored network protocols, and simulated adversary technique mapping"
      />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#f87171', fontSize: '0.88rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
          Loading detection coverage matrix...
        </div>
      ) : !coverage ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          Coverage matrix unavailable.
        </div>
      ) : (
        <>
          {/* Summary Stat Cards */}
          <div className="soc-metrics-grid">
            <div className="soc-metric-card">
              <div className="soc-metric-label">Monitored Categories</div>
              <div className="soc-metric-value" style={{ color: '#38bdf8' }}>{coverage.total_categories}</div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">Total Detection Rules</div>
              <div className="soc-metric-value">{coverage.total_rules}</div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">Telemetry Alerts Generated</div>
              <div className="soc-metric-value" style={{ color: '#f97316' }}>{coverage.total_alerts}</div>
            </div>
          </div>

          {/* Category Coverage Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
            {coverage.categories.map((cat) => (
              <div key={cat.category} className="soc-card">
                <div className="soc-card-header">
                  <div className="soc-card-title">
                    <span>🛡️</span> {cat.category} Detection Protocol
                  </div>
                  <span className="soc-badge soc-badge-p4">{cat.rule_count} Rules</span>
                </div>

                <div style={{ fontSize: '0.82rem', color: 'var(--soc-text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  <div>
                    <strong>Total Alerts Fired:</strong> {cat.alert_count}
                  </div>
                  <div>
                    <strong>Mapped MITRE ATT&CK Tactics:</strong>{' '}
                    {cat.mitre_tactics.length > 0 ? (
                      <span style={{ color: '#38bdf8' }}>{cat.mitre_tactics.join(', ')}</span>
                    ) : (
                      <span style={{ color: 'var(--soc-text-muted)' }}>Baseline Inspection</span>
                    )}
                  </div>
                </div>

                {/* Rules List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', borderTop: '1px solid var(--soc-border)', paddingTop: '0.75rem' }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--soc-text-muted)', textTransform: 'uppercase' }}>
                    Active Built-in Signatures
                  </div>
                  {cat.rules.map((r) => (
                    <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.6)', padding: '0.5rem 0.65rem', borderRadius: '4px', fontSize: '0.82rem' }}>
                      <div>
                        <span style={{ fontFamily: 'monospace', fontWeight: 600, color: '#38bdf8', marginRight: '0.5rem' }}>
                          {r.rule_id}
                        </span>
                        <span style={{ color: 'var(--soc-text-primary)' }}>{r.name}</span>
                      </div>
                      <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--soc-text-muted)' }}>
                        {r.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
