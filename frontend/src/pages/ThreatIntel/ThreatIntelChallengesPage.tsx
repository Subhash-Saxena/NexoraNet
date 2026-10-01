import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type { ThreatIntelChallengeBrief } from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const ThreatIntelChallengesPage: React.FC = () => {
  const [challenges, setChallenges] = useState<ThreatIntelChallengeBrief[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadChallenges()
  }, [])

  const loadChallenges = async () => {
    try {
      setLoading(true)
      const data = await threatIntelApi.listChallenges()
      setChallenges(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load challenges')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="threat-intel-container">
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>🏆 Threat Intelligence Investigation Challenges</h1>
          <p className="threat-intel-subtitle">
            Hands-on SOC investigation scenarios evaluated against a 5-dimension pedagogical rubric.
          </p>
        </div>
      </div>

      <ThreatIntelNav />

      {/* Educational Guidance */}
      <div className="educational-callout">
        <strong>Challenge Rubric Criteria (100 Points Total):</strong>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', marginTop: '0.5rem' }}>
          <div>🎯 <strong>20% IOC Match:</strong> Correct classification</div>
          <div>📡 <strong>20% Evidence Review:</strong> Telemetry inspection</div>
          <div>🧠 <strong>20% Intel Interpretation:</strong> Source reliability</div>
          <div>🔗 <strong>20% Entity Correlation:</strong> Domain/IP links</div>
          <div>🛡️ <strong>20% SOC Conclusion:</strong> Defensible actions</div>
        </div>
      </div>

      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid #ef4444',
            color: '#f8fafc',
            padding: '1rem',
            borderRadius: '0.5rem',
            marginBottom: '1.5rem',
          }}
        >
          {error}
        </div>
      )}

      {loading ? (
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading challenges...</p>
      ) : (
        <div className="challenge-grid">
          {challenges.map((ch) => {
            let diffColor = '#38bdf8'
            if (ch.difficulty === 'INTERMEDIATE') diffColor = '#fbbf24'
            else if (ch.difficulty === 'ADVANCED') diffColor = '#f87171'

            return (
              <div key={ch.id} className="challenge-card">
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: diffColor,
                        border: `1px solid ${diffColor}`,
                        padding: '0.15rem 0.5rem',
                        borderRadius: '0.25rem',
                      }}
                    >
                      {ch.difficulty}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{ch.category}</span>
                  </div>

                  <h3 className="challenge-title">{ch.title}</h3>
                  <p className="challenge-desc">{ch.objective}</p>

                  <div style={{ marginBottom: '1rem', fontSize: '0.8rem', color: '#94a3b8' }}>
                    Target in Scope:{' '}
                    <strong style={{ color: '#f1f5f9', fontFamily: 'monospace' }}>
                      {ch.target_indicator_value}
                    </strong>
                  </div>
                </div>

                <Link
                  to={`/threat-intelligence/challenges/${ch.slug}`}
                  style={{
                    background: '#0284c7',
                    color: '#fff',
                    textAlign: 'center',
                    padding: '0.6rem 1rem',
                    borderRadius: '0.375rem',
                    textDecoration: 'none',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    display: 'block',
                  }}
                >
                  Start Investigation →
                </Link>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
