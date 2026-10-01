import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type {
  ChallengeAttempt,
  ChallengeFeedback,
  ThreatIntelChallengeDetail,
} from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const ThreatIntelChallengeDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const [challenge, setChallenge] = useState<ThreatIntelChallengeDetail | null>(null)
  const [attempts, setAttempts] = useState<ChallengeAttempt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form
  const [selectedClass, setSelectedClass] = useState('MALICIOUS')
  const [hypothesis, setHypothesis] = useState('')
  const [evidenceNotes, setEvidenceNotes] = useState('')
  const [conclusion, setConclusion] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [latestAttempt, setLatestAttempt] = useState<ChallengeAttempt | null>(null)

  useEffect(() => {
    if (slug) {
      loadData(slug)
    }
  }, [slug])

  const loadData = async (challengeSlug: string) => {
    try {
      setLoading(true)
      const [chData, attData] = await Promise.all([
        threatIntelApi.getChallenge(challengeSlug),
        threatIntelApi.getChallengeAttempts(challengeSlug),
      ])
      setChallenge(chData)
      setAttempts(attData)
      if (attData.length > 0) {
        setLatestAttempt(attData[0])
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load challenge details')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!slug) return

    try {
      setSubmitting(true)
      const res = await threatIntelApi.submitChallengeAttempt(slug, {
        selected_classification: selectedClass,
        hypothesis_text: hypothesis.trim(),
        evidence_notes: evidenceNotes.trim(),
        conclusion: conclusion.trim(),
      })
      setLatestAttempt(res)
      setAttempts((prev) => [res, ...prev])
      window.scrollTo({ top: 300, behavior: 'smooth' })
    } catch (err: any) {
      alert(`Submission failed: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="threat-intel-container">
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading challenge details...</p>
      </div>
    )
  }

  if (error || !challenge) {
    return (
      <div className="threat-intel-container">
        <ThreatIntelNav />
        <div className="ioc-panel" style={{ textAlign: 'center', padding: '3rem' }}>
          <h2 style={{ color: '#ef4444' }}>Challenge Not Found</h2>
          <p style={{ color: '#94a3b8' }}>{error || 'Unable to load challenge scenario.'}</p>
          <Link to="/threat-intelligence/challenges" style={{ color: '#38bdf8' }}>
            ← Return to Challenges
          </Link>
        </div>
      </div>
    )
  }

  let parsedFeedback: ChallengeFeedback | null = null
  if (latestAttempt?.feedback) {
    try {
      parsedFeedback = JSON.parse(latestAttempt.feedback)
    } catch {
      parsedFeedback = null
    }
  }

  return (
    <div className="threat-intel-container">
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>
            <span>🏆</span> {challenge.title}
          </h1>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginTop: '0.5rem' }}>
            <span className="ioc-badge ioc-badge-type">{challenge.difficulty}</span>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>{challenge.category}</span>
          </div>
        </div>

        <div className="threat-intel-actions">
          <Link
            to="/threat-intelligence/challenges"
            style={{
              background: '#334155',
              color: '#f8fafc',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              textDecoration: 'none',
              fontSize: '0.875rem',
            }}
          >
            ← All Challenges
          </Link>
        </div>
      </div>

      <ThreatIntelNav />

      {/* Evaluation Results Banner (if evaluated) */}
      {parsedFeedback && latestAttempt && (
        <div
          style={{
            background: latestAttempt.passed ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
            border: `1px solid ${latestAttempt.passed ? '#10b981' : '#ef4444'}`,
            borderRadius: '0.75rem',
            padding: '1.5rem',
            marginBottom: '2rem',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h2 style={{ margin: 0, color: latestAttempt.passed ? '#34d399' : '#f87171' }}>
                {latestAttempt.passed ? '✅ Challenge Passed' : '⚠️ Practice Needed'} (Score: {latestAttempt.score}/100)
              </h2>
              <p style={{ margin: '0.25rem 0 0 0', color: '#cbd5e1', fontSize: '0.9rem' }}>
                Passing threshold: 70%. Evaluated across 5 defensive SOC dimensions.
              </p>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: latestAttempt.passed ? '#34d399' : '#f87171' }}>
              {latestAttempt.score}%
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
            {Object.entries(parsedFeedback.breakdown).map(([dimKey, dim]) => (
              <div
                key={dimKey}
                style={{
                  background: '#1e293b',
                  padding: '0.75rem',
                  borderRadius: '0.375rem',
                  border: '1px solid #334155',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  <span style={{ textTransform: 'capitalize' }}>{dimKey.replace('_', ' ')}</span>
                  <strong>{dim.score}/{dim.max}</strong>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>{dim.feedback}</div>
              </div>
            ))}
          </div>

          <div style={{ fontSize: '0.85rem', color: '#94a3b8', fontStyle: 'italic' }}>
            💡 <strong>Pedagogical Insight:</strong> {parsedFeedback.educational_takeaway}
          </div>
        </div>
      )}

      {/* Grid: Scenario & Submission */}
      <div className="ioc-detail-grid">
        {/* Left: Scenario & Telemetry Scope */}
        <div>
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Investigation Scenario Brief</h3>
            <p style={{ color: '#cbd5e1', lineHeight: 1.6, fontSize: '0.95rem' }}>
              {challenge.scenario_description}
            </p>

            <div
              style={{
                marginTop: '1.25rem',
                background: '#0f172a',
                padding: '1rem',
                borderRadius: '0.5rem',
                border: '1px solid #334155',
              }}
            >
              <div className="threat-stat-label">Target Artifact in Scope</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '1.1rem', color: '#38bdf8', fontWeight: 600 }}>
                  {challenge.target_indicator_value}
                </span>
                <Link
                  to={`/threat-intelligence/search?q=${encodeURIComponent(challenge.target_indicator_value)}`}
                  target="_blank"
                  style={{
                    background: '#334155',
                    color: '#f8fafc',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '0.25rem',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                  }}
                >
                  Search in Threat Intel ↗
                </Link>
              </div>
            </div>
          </div>

          {/* Submission Form */}
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Submit SOC Investigation Findings</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  1. Final Analyst Classification:
                </label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                >
                  <option value="MALICIOUS">Malicious (Confirmed Threat)</option>
                  <option value="SUSPICIOUS">Suspicious (Requires Escalation / Monitoring)</option>
                  <option value="BENIGN">Benign (Legitimate Activity)</option>
                  <option value="FALSE_POSITIVE">False Positive (Tuned / Heuristic Mismatch)</option>
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  2. Threat Intelligence Hypothesis (Evaluate source reliability and confidence):
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. Synthetic commercial threat feed indicates high-confidence beaconing associated with simulated Cobalt Strike..."
                  value={hypothesis}
                  onChange={(e) => setHypothesis(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  3. Observed Telemetry & Artifact Evidence Review:
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. Internal host 10.0.0.45 communicated outbound on port 8080 every 60 seconds matching heartbeat patterns..."
                  value={evidenceNotes}
                  onChange={(e) => setEvidenceNotes(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  4. SOC Disposition & Defensive Action Plan:
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. Recommend perimeter firewall containment, adding IP to analyst watchlist, and escalating for host isolation..."
                  value={conclusion}
                  onChange={(e) => setConclusion(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                style={{
                  background: '#0284c7',
                  color: '#fff',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  width: '100%',
                }}
              >
                {submitting ? 'Submitting & Evaluating Rubric...' : 'Submit for Rubric Evaluation'}
              </button>
            </form>
          </div>
        </div>

        {/* Right: Past Attempts */}
        <div>
          <div className="ioc-panel">
            <h3 className="ioc-panel-title">Previous Evaluation Attempts</h3>
            {attempts.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                No prior attempts recorded for this challenge. Complete the form to submit your first analysis.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {attempts.map((att) => (
                  <div
                    key={att.id}
                    onClick={() => setLatestAttempt(att)}
                    style={{
                      background: '#0f172a',
                      padding: '0.75rem 1rem',
                      borderRadius: '0.375rem',
                      border: `1px solid ${att.passed ? '#10b981' : '#ef4444'}`,
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, color: att.passed ? '#34d399' : '#f87171' }}>
                        {att.passed ? 'PASSED' : 'NEEDS PRACTICE'} ({att.score}%)
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {new Date(att.created_at).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                      Classification: <strong>{att.selected_classification}</strong>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
