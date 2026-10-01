import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { SocChallengeItem } from '../../types/soc'
import '../../components/soc/soc.css'

export const SocChallengesPage: React.FC = () => {
  const [challenges, setChallenges] = useState<SocChallengeItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchChallenges = async () => {
      try {
        setLoading(true)
        const data = await socApi.listChallenges()
        setChallenges(data)
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to fetch SOC challenges.')
      } finally {
        setLoading(false)
      }
    }
    fetchChallenges()
  }, [])

  const getDifficultyBadge = (d: string) => {
    switch (d.toUpperCase()) {
      case 'ADVANCED':
        return <span className="soc-badge soc-badge-p1">Advanced</span>
      case 'INTERMEDIATE':
        return <span className="soc-badge soc-badge-p2">Intermediate</span>
      default:
        return <span className="soc-badge soc-badge-benign">Beginner</span>
    }
  }

  return (
    <div className="soc-container">
      <SocHeader
        title="Educational SOC Triage Challenges"
        subtitle="Practice real-world analyst scenarios, formulate evidence-based hypotheses, and receive rubric-graded feedback"
      />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#f87171', fontSize: '0.88rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
          Loading SOC training challenges...
        </div>
      ) : challenges.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          No challenges found.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
          {challenges.map((ch) => (
            <div key={ch.id} className="soc-card" style={{ justifyContent: 'space-between' }}>
              <div>
                <div className="soc-card-header">
                  <div className="soc-card-title">{ch.title}</div>
                  {getDifficultyBadge(ch.difficulty)}
                </div>

                <div style={{ fontSize: '0.88rem', color: 'var(--soc-text-secondary)', margin: '0.75rem 0', lineHeight: 1.5 }}>
                  {ch.scenario_description}
                </div>

                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)', fontSize: '0.82rem', color: 'var(--soc-text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  <div>
                    <strong>Category:</strong> {ch.category}
                  </div>
                  <div>
                    <strong>Objective:</strong> {ch.objective}
                  </div>
                  {ch.mitre_attack_id && (
                    <div>
                      <strong>MITRE ATT&CK:</strong> <span style={{ color: '#38bdf8' }}>{ch.mitre_attack_id}</span>
                    </div>
                  )}
                </div>
              </div>

              <div style={{ marginTop: '1rem' }}>
                <Link
                  to={`/soc/challenges/${ch.slug}`}
                  className="soc-btn soc-btn-primary"
                  style={{ width: '100%' }}
                >
                  Start Scenario Challenge →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
