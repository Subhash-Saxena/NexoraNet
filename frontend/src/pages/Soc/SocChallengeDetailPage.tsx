import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type {
  SocChallengeDetailResponse,
  SocChallengeEvaluation,
  TriageClassification,
} from '../../types/soc'
import '../../components/soc/soc.css'

export const SocChallengeDetailPage: React.FC = () => {
  const { challengeSlug } = useParams<{ challengeSlug: string }>()
  const [challenge, setChallenge] = useState<SocChallengeDetailResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  // Submission Form State
  const [selectedClassification, setSelectedClassification] = useState<TriageClassification>('SUSPICIOUS')
  const [hypothesisText, setHypothesisText] = useState<string>('')
  const [packetNumbersInput, setPacketNumbersInput] = useState<string>('')
  const [conclusionText, setConclusionText] = useState<string>('')
  const [submitting, setSubmitting] = useState<boolean>(false)

  // Evaluation Result State
  const [evaluation, setEvaluation] = useState<SocChallengeEvaluation | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchChallenge = async () => {
      if (!challengeSlug) return
      try {
        setLoading(true)
        const data = await socApi.getChallenge(challengeSlug)
        setChallenge(data)
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to fetch challenge details.')
      } finally {
        setLoading(false)
      }
    }
    fetchChallenge()
  }, [challengeSlug])

  const handleSubmitAttempt = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!challengeSlug) return
    if (!hypothesisText.trim() || !conclusionText.trim()) {
      setError('Please provide both an analytical hypothesis and a forensic conclusion.')
      return
    }

    const pktNums = packetNumbersInput
      .split(',')
      .map((s) => Number(s.trim()))
      .filter((n) => !isNaN(n) && n > 0)

    try {
      setSubmitting(true)
      setError(null)
      const evalResult = await socApi.submitChallenge(challengeSlug, {
        selected_classification: selectedClassification,
        hypothesis_text: hypothesisText.trim(),
        evidence_packet_numbers: pktNums,
        conclusion: conclusionText.trim(),
      })
      setEvaluation(evalResult)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to evaluate challenge submission.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="soc-container">
      <SocHeader
        title={challenge?.title || 'SOC Challenge Investigation'}
        subtitle={`Category: ${challenge?.category || 'General'} • Difficulty: ${challenge?.difficulty || 'Beginner'}`}
        actionButton={
          <Link to="/soc/challenges" className="soc-btn soc-btn-secondary">
            ← Challenges Catalog
          </Link>
        }
      />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#f87171', fontSize: '0.88rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
          Loading challenge scenario...
        </div>
      ) : !challenge ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          Challenge scenario not found.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem' }}>
          {/* Left Column: Scenario & Expected Telemetry */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Scenario Card */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🎯</span> Scenario Briefing & Objective
                </div>
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--soc-text-secondary)', lineHeight: 1.6 }}>
                {challenge.scenario_description}
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)', fontSize: '0.85rem' }}>
                <strong style={{ color: '#38bdf8' }}>Objective:</strong> {challenge.objective}
              </div>
            </div>

            {/* Expected Observations */}
            {challenge.expected_observations && challenge.expected_observations.length > 0 && (
              <div className="soc-card">
                <div className="soc-card-header">
                  <div className="soc-card-title">
                    <span>💡</span> Key Telemetry Indicators to Investigate
                  </div>
                </div>
                <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--soc-text-secondary)', lineHeight: 1.6 }}>
                  {challenge.expected_observations.map((obs, idx) => (
                    <li key={idx}>{obs}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sample Alerts */}
            {challenge.sample_alerts && challenge.sample_alerts.length > 0 && (
              <div className="soc-card">
                <div className="soc-card-header">
                  <div className="soc-card-title">
                    <span>🚨</span> Scenario Alerts ({challenge.sample_alerts.length})
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {challenge.sample_alerts.map((alt) => (
                    <div key={alt.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.6)', padding: '0.65rem 0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)', fontSize: '0.85rem' }}>
                          Alert #{alt.id}: {alt.title}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                          {alt.source_ip || '*'}:{alt.source_port || '*'} → {alt.destination_ip || '*'}:{alt.destination_port || '*'}
                        </div>
                      </div>
                      <Link to={`/soc/alerts/${alt.id}`} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        Inspect Alert →
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Submission Form & Evaluation Card */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Submission Form */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>📝</span> Submit Analyst Findings
                </div>
              </div>

              <form onSubmit={handleSubmitAttempt} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    1. Triage Classification Determination *
                  </label>
                  <select
                    className="soc-select"
                    style={{ width: '100%' }}
                    value={selectedClassification}
                    onChange={(e) => setSelectedClassification(e.target.value as TriageClassification)}
                    aria-label="Triage Classification Determination"
                  >
                    <option value="SUSPICIOUS">SUSPICIOUS (True Positive anomalous activity)</option>
                    <option value="BENIGN">BENIGN (Authorized regular activity)</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE (Inappropriate trigger on benign telemetry)</option>
                    <option value="REQUIRES_MORE_DATA">REQUIRES_MORE_DATA (Insufficient packet evidence)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    2. Analytical Working Hypothesis *
                  </label>
                  <input
                    type="text"
                    className="soc-input"
                    style={{ width: '100%' }}
                    placeholder="e.g. Endpoint 192.168.1.100 is executing a TCP SYN stealth scan targeting ports 22, 80, 443..."
                    value={hypothesisText}
                    onChange={(e) => setHypothesisText(e.target.value)}
                    required
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    3. Corroborating Packet Numbers (Comma-separated)
                  </label>
                  <input
                    type="text"
                    className="soc-input"
                    style={{ width: '100%' }}
                    placeholder="e.g. 1, 2, 3, 5, 8"
                    value={packetNumbersInput}
                    onChange={(e) => setPacketNumbersInput(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.35rem' }}>
                    4. Forensic Conclusion & Technical Defense Plan *
                  </label>
                  <textarea
                    className="soc-textarea"
                    rows={4}
                    style={{ width: '100%' }}
                    placeholder="Summarize your conclusive proof and recommend concrete defensive remediation steps..."
                    value={conclusionText}
                    onChange={(e) => setConclusionText(e.target.value)}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="soc-btn soc-btn-primary"
                  disabled={submitting}
                  style={{ padding: '0.75rem' }}
                >
                  {submitting ? 'Grading Submission...' : 'Grade My Investigation 🎓'}
                </button>
              </form>
            </div>

            {/* Rubric Evaluation Result */}
            {evaluation && (
              <div className="soc-card" style={{ border: evaluation.passed ? '1px solid rgba(34, 197, 94, 0.4)' : '1px solid rgba(239, 68, 68, 0.4)', background: evaluation.passed ? 'rgba(34, 197, 94, 0.04)' : 'rgba(239, 68, 68, 0.04)' }}>
                <div className="soc-card-header">
                  <div className="soc-card-title">
                    <span>{evaluation.passed ? '🎉' : '⚠️'}</span> Investigation Rubric Scorecard
                  </div>
                  <span className={`soc-badge ${evaluation.passed ? 'soc-badge-benign' : 'soc-badge-p1'}`}>
                    {evaluation.percentage}% — {evaluation.passed ? 'PASSED' : 'RETRY'}
                  </span>
                </div>

                <div style={{ fontSize: '0.88rem', color: 'var(--soc-text-primary)', lineHeight: 1.5 }}>
                  {evaluation.feedback_summary}
                </div>

                {/* Score Breakdown (5 criteria, 20% each) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', margin: '0.5rem 0' }}>
                  <div className="soc-rubric-row">
                    <span>Alert Triage & Inspection (20%)</span>
                    <strong>{evaluation.alert_triaged_score} / 20</strong>
                  </div>
                  <div className="soc-rubric-row">
                    <span>Classification Accuracy (20%)</span>
                    <strong>{evaluation.classification_accuracy_score} / 20</strong>
                  </div>
                  <div className="soc-rubric-row">
                    <span>Hypothesis Validity (20%)</span>
                    <strong>{evaluation.hypothesis_validity_score} / 20</strong>
                  </div>
                  <div className="soc-rubric-row">
                    <span>Evidence Linking (20%)</span>
                    <strong>{evaluation.evidence_linking_score} / 20</strong>
                  </div>
                  <div className="soc-rubric-row">
                    <span>Conclusion & Synthesis Depth (20%)</span>
                    <strong>{evaluation.conclusion_depth_score} / 20</strong>
                  </div>
                </div>

                {evaluation.specific_tips && evaluation.specific_tips.length > 0 && (
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)', fontSize: '0.82rem' }}>
                    <strong style={{ color: '#38bdf8' }}>Analyst Guidance Tips:</strong>
                    <ul style={{ margin: '0.35rem 0 0 0', paddingLeft: '1.25rem', color: 'var(--soc-text-secondary)' }}>
                      {evaluation.specific_tips.map((tip, idx) => (
                        <li key={idx}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
