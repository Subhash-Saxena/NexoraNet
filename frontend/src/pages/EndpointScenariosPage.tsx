import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { EndpointNav } from '../components/endpoint_security/EndpointNav'
import type { EndpointScenario, ScenarioValidationResult } from '../types/endpointSecurity'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import '../components/endpoint_security/endpointSecurity.css'

export const EndpointScenariosPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()

  // Catalog state
  const [scenarios, setScenarios] = useState<EndpointScenario[]>([])
  const [loadingList, setLoadingList] = useState(true)

  // Active scenario state
  const [activeScenario, setActiveScenario] = useState<EndpointScenario | null>(null)
  const [loadingScenario, setLoadingScenario] = useState(false)
  const [revealedHints, setRevealedHints] = useState<number[]>([])

  // Validation form state
  const [valHost, setValHost] = useState('')
  const [valProc, setValProc] = useState('')
  const [valParent, setValParent] = useState('')
  const [valC2, setValC2] = useState('')
  const [valPersist, setValPersist] = useState('')
  const [valVerdict, setValVerdict] = useState('CONFIRMED_COMPROMISE')
  const [valNotes, setValNotes] = useState('')
  const [valResult, setValResult] = useState<ScenarioValidationResult | null>(null)
  const [validating, setValidating] = useState(false)

  // Load scenarios catalog
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        setLoadingList(true)
        const list = await endpointSecurityApi.listScenarios()
        setScenarios(list)
      } catch (err: any) {
        console.error('Failed to load scenarios:', err)
      } finally {
        setLoadingList(false)
      }
    }
    fetchCatalog()
  }, [])

  // Load selected scenario
  useEffect(() => {
    if (!slug) {
      setActiveScenario(null)
      setValResult(null)
      setRevealedHints([])
      return
    }
    const fetchDetail = async () => {
      try {
        setLoadingScenario(true)
        const s = await endpointSecurityApi.getScenario(slug)
        setActiveScenario(s)
        setValHost(s.target_host_stable_id)
        setValResult(null)
        setRevealedHints([])
      } catch (err: any) {
        console.error('Failed to load scenario detail:', err)
      } finally {
        setLoadingScenario(false)
      }
    }
    fetchDetail()
  }, [slug])

  const toggleHint = (idx: number) => {
    if (revealedHints.includes(idx)) {
      setRevealedHints(revealedHints.filter((i) => i !== idx))
    } else {
      setRevealedHints([...revealedHints, idx])
    }
  }

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!slug) return
    try {
      setValidating(true)
      const res = await endpointSecurityApi.validateScenario(slug, {
        target_host: valHost || undefined,
        identified_process: valProc || undefined,
        parent_process: valParent || undefined,
        c2_domain_or_ip: valC2 || undefined,
        persistence_mechanism: valPersist || undefined,
        verdict: valVerdict || undefined,
        analyst_notes: valNotes || undefined,
      })
      setValResult(res)
    } catch (err: any) {
      alert(`Validation error: ${err.message}`)
    } finally {
      setValidating(false)
    }
  }

  return (
    <div className="endpoint-container">
      {/* Synthetic Warning */}
      <div className="endpoint-synthetic-banner">
        <div className="banner-left">
          <span className="banner-icon">🛡️</span>
          <div>
            <div className="banner-title">
              Guided Endpoint Security Investigation Scenarios
            </div>
            <div className="banner-subtitle">
              Solve realistic SOC host investigation challenges with objective-based validation rubrics.
            </div>
          </div>
        </div>
        <span className="banner-badge">GUIDED LABS</span>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
          Endpoint Security Scenarios
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Hands-on host forensics and malware triage simulations. Analyze telemetry, spot malicious activity, and test your findings against the grading rubric.
        </p>
      </div>

      <EndpointNav />

      {/* Scenario Catalog */}
      {!slug && (
        <div>
          {loadingList ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
              Loading guided scenarios...
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
              {scenarios.map((sc) => {
                const diffClass = sc.difficulty.toLowerCase()
                return (
                  <div key={sc.id} className="host-card">
                    <div>
                      <div className="host-card-header">
                        <div>
                          <span style={{ fontSize: '0.8rem', color: '#38bdf8', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                            {sc.scenario_id}
                          </span>
                          <h3 style={{ fontSize: '1.15rem', color: '#f8fafc', margin: '0.2rem 0 0.4rem 0' }}>
                            {sc.title}
                          </h3>
                        </div>
                        <span className={`risk-badge ${diffClass === 'beginner' ? 'low' : diffClass === 'intermediate' ? 'medium' : 'critical'}`}>
                          {sc.difficulty}
                        </span>
                      </div>

                      <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5, margin: '0 0 1rem 0' }}>
                        {sc.description}
                      </p>

                      <div className="host-card-meta">
                        <div className="meta-item">
                          <span className="meta-label">Target Host</span>
                          <span className="meta-val" style={{ color: '#38bdf8' }}>{sc.target_host_stable_id}</span>
                        </div>
                        <div className="meta-item">
                          <span className="meta-label">Est. Time</span>
                          <span className="meta-val">{sc.estimated_minutes} mins</span>
                        </div>
                      </div>
                    </div>

                    <Link
                      to={`/endpoint-security/scenarios/${sc.slug}`}
                      className="btn-cyber-primary"
                      style={{ width: '100%', justifyContent: 'center', marginTop: '1rem' }}
                    >
                      Start Scenario ➔
                    </Link>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Active Scenario Detail & Validator */}
      {slug && loadingScenario && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
          Loading scenario investigation workspace...
        </div>
      )}

      {slug && !loadingScenario && activeScenario && (
        <div>
          {/* Header */}
          <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '10px', padding: '1.5rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.4rem' }}>
                  <span style={{ fontFamily: 'JetBrains Mono', color: '#38bdf8', fontWeight: 700 }}>
                    {activeScenario.scenario_id}
                  </span>
                  <span className="platform-badge windows">{activeScenario.category}</span>
                  <span className="risk-badge medium">{activeScenario.difficulty}</span>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>⏱️ {activeScenario.estimated_minutes} mins</span>
                </div>

                <h2 style={{ fontSize: '1.5rem', color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
                  {activeScenario.title}
                </h2>
                <div style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                  Target Host:{' '}
                  <Link
                    to={`/endpoint-security/hosts/${activeScenario.target_host_stable_id}`}
                    style={{ color: '#38bdf8', fontWeight: 600 }}
                  >
                    {activeScenario.target_host_stable_id} ➔ Open in Workbench
                  </Link>
                </div>
              </div>

              <Link
                to={`/endpoint-security/hosts/${activeScenario.target_host_stable_id}`}
                className="btn-cyber-primary"
              >
                🔬 Inspect Target Telemetry ➔
              </Link>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {/* Left: Background & Objectives */}
            <div>
              <div className="investigation-section" style={{ marginBottom: '1.5rem' }}>
                <div className="section-header">
                  <span className="section-title">Scenario Background</span>
                </div>
                <p style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                  {activeScenario.background}
                </p>
              </div>

              <div className="investigation-section" style={{ marginBottom: '1.5rem' }}>
                <div className="section-header">
                  <span className="section-title">Investigation Objectives</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {activeScenario.objectives.map((obj, i) => (
                    <label key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.85rem', color: '#f1f5f9', cursor: 'pointer' }}>
                      <input type="checkbox" style={{ accentColor: '#38bdf8' }} />
                      <span>{obj}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Hints */}
              {activeScenario.hints.length > 0 && (
                <div className="investigation-section">
                  <div className="section-header">
                    <span className="section-title">Analyst Hints</span>
                  </div>
                  {activeScenario.hints.map((hint, idx) => (
                    <div key={idx} style={{ marginBottom: '0.75rem' }}>
                      <button
                        type="button"
                        className="btn-cyber-secondary"
                        onClick={() => toggleHint(idx)}
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem' }}
                      >
                        {revealedHints.includes(idx) ? `Hide Hint #${idx + 1}` : `Reveal Hint #${idx + 1}`}
                      </button>
                      {revealedHints.includes(idx) && (
                        <div style={{ marginTop: '0.4rem', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.65rem', fontSize: '0.8rem', color: '#fbbf24' }}>
                          💡 {hint}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right: Solution Validator Form */}
            <div className="investigation-section">
              <div className="section-header">
                <span className="section-title">
                  <span>📝</span> Submit Analytical Findings
                </span>
              </div>

              <form onSubmit={handleValidate}>
                <div style={{ marginBottom: '0.85rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                    Identified Suspicious Process
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. powershell.exe or update.exe"
                    value={valProc}
                    onChange={(e) => setValProc(e.target.value)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.45rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <div style={{ marginBottom: '0.85rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                    Parent Process
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. explorer.exe or powershell.exe"
                    value={valParent}
                    onChange={(e) => setValParent(e.target.value)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.45rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <div style={{ marginBottom: '0.85rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                    C2 Domain or Egress IP
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. malicious-c2.training.test or 198.51.100.45"
                    value={valC2}
                    onChange={(e) => setValC2(e.target.value)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.45rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <div style={{ marginBottom: '0.85rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                    Persistence Mechanism (if any)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. SCHEDULED_TASK or REGISTRY_RUN_KEY"
                    value={valPersist}
                    onChange={(e) => setValPersist(e.target.value)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.45rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <div style={{ marginBottom: '0.85rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                    Analyst Verdict
                  </label>
                  <select
                    value={valVerdict}
                    onChange={(e) => setValVerdict(e.target.value)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.45rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  >
                    <option value="CONFIRMED_COMPROMISE">CONFIRMED_COMPROMISE</option>
                    <option value="SUSPICIOUS">SUSPICIOUS</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                    <option value="BENIGN">BENIGN</option>
                  </select>
                </div>

                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                    Analyst Justification & Evidence Summary
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Summarize your analytical rationale..."
                    value={valNotes}
                    onChange={(e) => setValNotes(e.target.value)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.45rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <button
                  type="submit"
                  className="btn-cyber-primary"
                  disabled={validating}
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  {validating ? 'Evaluating Rubric...' : 'Validate Findings Against Solution Rubric ➔'}
                </button>
              </form>

              {/* Validation Result Box */}
              {valResult && (
                <div style={{ marginTop: '1.5rem', background: '#0f172a', border: `1px solid ${valResult.passed ? '#10b981' : '#f59e0b'}`, borderRadius: '8px', padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem', color: valResult.passed ? '#10b981' : '#f59e0b' }}>
                      {valResult.passed ? '✓ Scenario Solved Successfully!' : '⚠️ Incomplete or Needs Revision'}
                    </span>
                    <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 800, fontSize: '1.25rem', color: valResult.passed ? '#10b981' : '#f59e0b' }}>
                      Score: {valResult.score}/100
                    </span>
                  </div>

                  {/* Checklist */}
                  <div style={{ marginBottom: '0.75rem' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                      Rubric Criteria Evaluated:
                    </div>
                    {Object.entries(valResult.rubric_evaluations).map(([k, passed]) => (
                      <div key={k} style={{ fontSize: '0.8rem', color: passed ? '#10b981' : '#ef4444', marginBottom: '0.15rem' }}>
                        {passed ? '✓' : '✗'} {k.replace(/_/g, ' ')}
                      </div>
                    ))}
                  </div>

                  {/* Feedback */}
                  {valResult.feedback.length > 0 && (
                    <div style={{ marginBottom: '0.75rem' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                        Feedback:
                      </div>
                      <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8rem', color: '#cbd5e1' }}>
                        {valResult.feedback.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {valResult.recommendations.length > 0 && (
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                        Analyst Recommendations:
                      </div>
                      <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8rem', color: '#94a3b8' }}>
                        {valResult.recommendations.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
