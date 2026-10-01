import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ThreatHuntingNav } from '../components/threat_hunting/ThreatHuntingNav'
import '../components/threat_hunting/threat_hunting.css'
import { threatHuntingApi } from '../services/threatHuntingApi'
import type { HuntScenario } from '../types/threat_hunting'

export const HuntScenariosPage: React.FC = () => {
  const navigate = useNavigate()
  const [scenarios, setScenarios] = useState<HuntScenario[]>([])
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL')
  const [loading, setLoading] = useState(true)
  const [launchingSlug, setLaunchingSlug] = useState<string | null>(null)
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null)

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        setLoading(true)
        const data = await threatHuntingApi.listScenarios()
        setScenarios(data)
      } catch (err: any) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchScenarios()
  }, [])

  const filteredScenarios = scenarios.filter((sc) => {
    if (selectedDifficulty === 'ALL') return true
    return sc.difficulty.toUpperCase() === selectedDifficulty.toUpperCase()
  })

  const handleLaunch = async (slug: string) => {
    try {
      setLaunchingSlug(slug)
      const launched = await threatHuntingApi.launchScenario(slug)
      navigate(`/threat-hunting/hunts/${launched.id}`)
    } catch (err: any) {
      alert(`Error launching scenario: ${err.message}`)
    } finally {
      setLaunchingSlug(null)
    }
  }

  const getDifficultyBadgeClass = (diff: string) => {
    switch (diff.toUpperCase()) {
      case 'BEGINNER':
        return 'badge-diff-beginner'
      case 'INTERMEDIATE':
        return 'badge-diff-intermediate'
      case 'ADVANCED':
        return 'badge-diff-advanced'
      default:
        return 'badge-diff-beginner'
    }
  }

  return (
    <div className="threat-hunting-container">
      {/* Header */}
      <div className="threat-hunting-header">
        <div className="threat-hunting-title-group">
          <h1>
            <span>🎯</span> Threat Hunting Scenarios Catalog
          </h1>
          <div className="threat-hunting-subtitle">
            Hands-on guided investigations based on real-world adversary tactics, techniques, and procedures (MITRE ATT&CK).
          </div>
        </div>
      </div>

      <ThreatHuntingNav />

      {/* Difficulty Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        {['ALL', 'BEGINNER', 'INTERMEDIATE', 'ADVANCED'].map((d) => (
          <button
            key={d}
            className={`threat-hunting-nav-tab ${selectedDifficulty === d ? 'active' : ''}`}
            onClick={() => setSelectedDifficulty(d)}
            style={{ padding: '0.4rem 1rem', fontSize: '0.85rem' }}
          >
            {d === 'ALL' ? 'All Scenarios (8)' : `${d} (${scenarios.filter((s) => s.difficulty === d).length})`}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Loading curated training scenarios...
        </div>
      ) : (
        <div className="scenarios-grid">
          {filteredScenarios.map((sc) => (
            <div key={sc.slug} className="scenario-card">
              <div>
                <div className="scenario-header">
                  <h3 className="scenario-title">{sc.title}</h3>
                  <span className={`hunt-badge ${getDifficultyBadgeClass(sc.difficulty)}`}>
                    {sc.difficulty}
                  </span>
                </div>

                <div className="scenario-brief">{sc.brief}</div>

                <div className="scenario-meta">
                  <span className="scenario-tag">📂 {sc.category}</span>
                  <span className="scenario-tag">⏱️ {sc.estimated_minutes} min</span>
                  <span className="scenario-tag">💾 {sc.dataset_code}</span>
                </div>

                {/* MITRE ATT&CK */}
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                    MITRE ATT&CK
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {sc.mitre_techniques.map((tech) => (
                      <span
                        key={tech}
                        style={{
                          background: 'rgba(2, 132, 199, 0.15)',
                          color: '#38bdf8',
                          border: '1px solid #0284c7',
                          fontSize: '0.7rem',
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                        }}
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Initial Pivot Hint */}
                {sc.initial_pivot_value && (
                  <div
                    style={{
                      background: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: '0.5rem',
                      padding: '0.6rem 0.75rem',
                      marginBottom: '1rem',
                      fontSize: '0.8rem',
                    }}
                  >
                    <span style={{ color: '#94a3b8' }}>Recommended Initial Pivot: </span>
                    <strong style={{ color: '#f8fafc', fontFamily: 'monospace' }}>
                      {sc.initial_pivot_type}: {sc.initial_pivot_value}
                    </strong>
                  </div>
                )}

                {/* Guided Questions Toggle */}
                <div style={{ marginBottom: '1.25rem' }}>
                  <button
                    type="button"
                    onClick={() => setExpandedSlug(expandedSlug === sc.slug ? null : sc.slug)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#38bdf8',
                      fontSize: '0.8rem',
                      cursor: 'pointer',
                      padding: 0,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                    }}
                  >
                    <span>{expandedSlug === sc.slug ? '▼ Hide' : '▶ Show'} Guided Questions ({sc.guided_questions.length})</span>
                  </button>
                  {expandedSlug === sc.slug && (
                    <ul style={{ margin: '0.5rem 0 0 1rem', padding: 0, fontSize: '0.8rem', color: '#cbd5e1', lineHeight: '1.6' }}>
                      {sc.guided_questions.map((q, qIdx) => (
                        <li key={qIdx}>{q}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              <button
                className="btn-cyber-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                disabled={launchingSlug === sc.slug}
                onClick={() => handleLaunch(sc.slug)}
              >
                <span>🔬</span> {launchingSlug === sc.slug ? 'Launching Session...' : 'Start Threat Hunt'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
