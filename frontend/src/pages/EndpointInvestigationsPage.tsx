import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { EndpointNav } from '../components/endpoint_security/EndpointNav'
import type {
  EndpointInvestigation,
  EndpointVerdict,
  EvidenceRelevance,
  ThreatConfidence,
} from '../types/endpointSecurity'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import '../components/endpoint_security/endpointSecurity.css'

export const EndpointInvestigationsPage: React.FC = () => {
  const { investigationId } = useParams<{ investigationId: string }>()

  // Cases List state
  const [investigations, setInvestigations] = useState<EndpointInvestigation[]>([])
  const [loadingList, setLoadingList] = useState(true)

  // Active case state
  const [activeCase, setActiveCase] = useState<EndpointInvestigation | null>(null)
  const [loadingCase, setLoadingCase] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form states
  const [newHypStatement, setNewHypStatement] = useState('')
  const [newHypConfidence, setNewHypConfidence] = useState<ThreatConfidence>('MEDIUM')
  const [newHypNotes, setNewHypNotes] = useState('')

  const [newEvEventId, setNewEvEventId] = useState('')
  const [newEvType, setNewEvType] = useState('PROCESS')
  const [newEvValue, setNewEvValue] = useState('')
  const [newEvDesc, setNewEvDesc] = useState('')
  const [newEvRelevance, setNewEvRelevance] = useState<EvidenceRelevance>('SUPPORTING')

  const [newFindingTitle, setNewFindingTitle] = useState('')
  const [newFindingDesc, setNewFindingDesc] = useState('')
  const [newFindingSev, setNewFindingSev] = useState('HIGH')
  const [newFindingMitre, setNewFindingMitre] = useState('')

  const [concSummary, setConcSummary] = useState('')
  const [concVerdict, setConcVerdict] = useState<EndpointVerdict>('CONFIRMED_COMPROMISE')
  const [concLessons, setConcLessons] = useState('')
  const [submittingConc, setSubmittingConc] = useState(false)

  // Load cases list
  useEffect(() => {
    const fetchList = async () => {
      try {
        setLoadingList(true)
        const data = await endpointSecurityApi.listInvestigations()
        setInvestigations(data.items)
      } catch (err: any) {
        console.error('Failed to list cases:', err)
      } finally {
        setLoadingList(false)
      }
    }
    fetchList()
  }, [])

  // Load active case
  useEffect(() => {
    if (!investigationId) {
      setActiveCase(null)
      return
    }
    const fetchCase = async () => {
      try {
        setLoadingCase(true)
        setError(null)
        const c = await endpointSecurityApi.getInvestigation(Number(investigationId))
        setActiveCase(c)
        if (c.conclusion) {
          setConcSummary(c.conclusion.summary)
          setConcVerdict(c.conclusion.verdict)
          setConcLessons(c.conclusion.lessons_learned || '')
        }
      } catch (err: any) {
        console.error('Failed to load case:', err)
        setError(err.message || 'Investigation case not found or access denied')
      } finally {
        setLoadingCase(false)
      }
    }
    fetchCase()
  }, [investigationId])

  // Handlers
  const handleAddHypothesis = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!activeCase || !newHypStatement.trim()) return
    try {
      await endpointSecurityApi.addHypothesis(activeCase.id, {
        statement: newHypStatement,
        confidence: newHypConfidence,
        analyst_notes: newHypNotes || undefined,
      })
      setNewHypStatement('')
      setNewHypNotes('')
      // Refresh case
      const updated = await endpointSecurityApi.getInvestigation(activeCase.id)
      setActiveCase(updated)
    } catch (err: any) {
      alert(`Failed to add hypothesis: ${err.message}`)
    }
  }

  const handleUpdateHypothesisStatus = async (hypId: number, status: string) => {
    if (!activeCase) return
    try {
      await endpointSecurityApi.updateHypothesis(activeCase.id, hypId, { status })
      const updated = await endpointSecurityApi.getInvestigation(activeCase.id)
      setActiveCase(updated)
    } catch (err: any) {
      alert(`Failed to update hypothesis: ${err.message}`)
    }
  }

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!activeCase || !newEvDesc.trim() || !newEvValue.trim()) return
    try {
      await endpointSecurityApi.addEvidence(activeCase.id, {
        event_id: newEvEventId || `MANUAL-${Date.now().toString().slice(-4)}`,
        observable_type: newEvType,
        observable_value: newEvValue,
        description: newEvDesc,
        relevance: newEvRelevance,
      })
      setNewEvEventId('')
      setNewEvValue('')
      setNewEvDesc('')
      const updated = await endpointSecurityApi.getInvestigation(activeCase.id)
      setActiveCase(updated)
    } catch (err: any) {
      alert(`Failed to record evidence: ${err.message}`)
    }
  }

  const handleAddFinding = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!activeCase || !newFindingTitle.trim()) return
    try {
      await endpointSecurityApi.addFinding(activeCase.id, {
        title: newFindingTitle,
        description: newFindingDesc,
        severity: newFindingSev,
        mitre_technique: newFindingMitre || undefined,
      })
      setNewFindingTitle('')
      setNewFindingDesc('')
      setNewFindingMitre('')
      const updated = await endpointSecurityApi.getInvestigation(activeCase.id)
      setActiveCase(updated)
    } catch (err: any) {
      alert(`Failed to save finding: ${err.message}`)
    }
  }

  const handleSubmitConclusion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!activeCase || !concSummary.trim()) return
    try {
      setSubmittingConc(true)
      await endpointSecurityApi.submitConclusion(activeCase.id, {
        summary: concSummary,
        verdict: concVerdict,
        lessons_learned: concLessons || undefined,
      })
      const updated = await endpointSecurityApi.getInvestigation(activeCase.id)
      setActiveCase(updated)
    } catch (err: any) {
      alert(`Failed to finalize case conclusion: ${err.message}`)
    } finally {
      setSubmittingConc(false)
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
              Endpoint Security Investigation Workspace
            </div>
            <div className="banner-subtitle">
              Form hypotheses, attach corroborated host telemetry evidence, and submit analytical case conclusions.
            </div>
          </div>
        </div>
        <span className="banner-badge">SOC CASE WORKBENCH</span>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
          Host Investigation Cases
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Manage structured endpoint security investigations with hypothesis testing, evidence logging, and automated rubric scoring.
        </p>
      </div>

      <EndpointNav currentInvestigationId={investigationId} />

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '8px', padding: '1rem', color: '#fca5a5', marginBottom: '1.5rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Case List View (if no investigationId selected) */}
      {!investigationId && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: '#f1f5f9', margin: 0 }}>
              Active Investigations ({investigations.length})
            </h2>
            <Link to="/endpoint-security/hosts" className="btn-cyber-primary">
              + New Investigation (from Host)
            </Link>
          </div>

          {loadingList ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
              Loading investigation cases...
            </div>
          ) : investigations.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', background: '#111827', borderRadius: '8px', color: '#64748b' }}>
              <p>No endpoint investigations found. Navigate to any host in the fleet and click "Start Host Investigation".</p>
              <Link to="/endpoint-security/hosts" className="btn-cyber-primary" style={{ marginTop: '1rem' }}>
                Browse Host Inventory ➔
              </Link>
            </div>
          ) : (
            <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Case ID</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Title</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Host</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Priority</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Training Score</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {investigations.map((inv) => (
                    <tr key={inv.id} style={{ borderBottom: '1px solid #1f2937' }}>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontWeight: 600, color: '#38bdf8' }}>
                        {inv.stable_id}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#f8fafc' }}>
                        {inv.title}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: '#cbd5e1' }}>
                        {inv.host?.hostname || `Host-${inv.host_id}`}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span className={`risk-badge ${inv.priority === 'P1' ? 'critical' : inv.priority === 'P2' ? 'high' : 'medium'}`}>
                          {inv.priority}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span className="platform-badge windows">{inv.status}</span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono' }}>
                        {inv.conclusion ? (
                          <span style={{ color: '#10b981', fontWeight: 700 }}>
                            {inv.conclusion.training_score}/100
                          </span>
                        ) : (
                          <span style={{ color: '#64748b' }}>In Progress</span>
                        )}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <Link
                          to={`/endpoint-security/investigations/${inv.id}`}
                          className="btn-cyber-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem' }}
                        >
                          Open Case ➔
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Active Case Workspace */}
      {investigationId && loadingCase && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
          Loading investigation case...
        </div>
      )}

      {investigationId && !loadingCase && activeCase && (
        <div>
          {/* Case Header */}
          <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '10px', padding: '1.25rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.85rem', color: '#38bdf8', fontWeight: 700 }}>
                  {activeCase.stable_id}
                </span>
                <span className={`risk-badge ${activeCase.priority === 'P1' ? 'critical' : activeCase.priority === 'P2' ? 'high' : 'medium'}`}>
                  {activeCase.priority}
                </span>
                <span className="platform-badge windows">{activeCase.status}</span>
                {activeCase.conclusion && (
                  <span className="risk-badge critical">
                    VERDICT: {activeCase.conclusion.verdict}
                  </span>
                )}
              </div>
              <h2 style={{ fontSize: '1.35rem', color: '#f8fafc', margin: '0 0 0.35rem 0' }}>
                {activeCase.title}
              </h2>
              <div style={{ fontSize: '0.825rem', color: '#94a3b8' }}>
                Target Host:{' '}
                {activeCase.host ? (
                  <Link
                    to={`/endpoint-security/hosts/${activeCase.host.stable_id}`}
                    style={{ color: '#38bdf8', fontWeight: 600 }}
                  >
                    {activeCase.host.hostname} ({activeCase.host.ip_address})
                  </Link>
                ) : (
                  `Host #${activeCase.host_id}`
                )}
              </div>
            </div>

            {activeCase.conclusion && (
              <div style={{ background: '#0f172a', border: '1px solid #10b981', borderRadius: '8px', padding: '0.75rem 1.25rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: '#6ee7b7', textTransform: 'uppercase' }}>Training Score</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10b981', fontFamily: 'JetBrains Mono' }}>
                  {activeCase.conclusion.training_score} <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>/ 100</span>
                </div>
              </div>
            )}
          </div>

          {/* 3-Section Investigation Workflow */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Section 1: Hypotheses */}
            <div className="investigation-section">
              <div className="section-header">
                <span className="section-title">
                  <span>💡</span> Hypotheses ({activeCase.hypotheses?.length || 0})
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
                {(activeCase.hypotheses || []).map((hyp) => (
                  <div key={hyp.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                      <span className={`risk-badge ${hyp.status === 'SUPPORTED' ? 'critical' : hyp.status === 'REFUTED' ? 'none' : 'medium'}`}>
                        {hyp.status}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Confidence: {hyp.confidence}</span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#f1f5f9', margin: '0.25rem 0' }}>
                      {hyp.statement}
                    </p>
                    {hyp.analyst_notes && (
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontStyle: 'italic', marginTop: '0.3rem' }}>
                        Notes: {hyp.analyst_notes}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                      <button
                        type="button"
                        className="btn-cyber-secondary"
                        style={{ fontSize: '0.7rem', padding: '0.2rem 0.45rem' }}
                        onClick={() => handleUpdateHypothesisStatus(hyp.id, 'SUPPORTED')}
                      >
                        ✓ Mark Supported
                      </button>
                      <button
                        type="button"
                        className="btn-cyber-secondary"
                        style={{ fontSize: '0.7rem', padding: '0.2rem 0.45rem' }}
                        onClick={() => handleUpdateHypothesisStatus(hyp.id, 'REFUTED')}
                      >
                        ✕ Mark Refuted
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Add Hypothesis Form */}
              <form onSubmit={handleAddHypothesis} style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                  + Add Working Hypothesis
                </div>
                <input
                  type="text"
                  placeholder="e.g. Attacker leveraged PowerShell to download payload..."
                  value={newHypStatement}
                  onChange={(e) => setNewHypStatement(e.target.value)}
                  required
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#f8fafc', fontSize: '0.8rem', marginBottom: '0.5rem' }}
                />
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    value={newHypConfidence}
                    onChange={(e) => setNewHypConfidence(e.target.value as ThreatConfidence)}
                    style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.35rem 0.5rem', color: '#cbd5e1', fontSize: '0.75rem' }}
                  >
                    <option value="HIGH">High Confidence</option>
                    <option value="MEDIUM">Medium Confidence</option>
                    <option value="LOW">Low Confidence</option>
                  </select>
                  <button type="submit" className="btn-cyber-primary" style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}>
                    Save Hypothesis
                  </button>
                </div>
              </form>
            </div>

            {/* Section 2: Evidence */}
            <div className="investigation-section">
              <div className="section-header">
                <span className="section-title">
                  <span>📎</span> Corroborating Evidence ({activeCase.evidence?.length || 0})
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
                {(activeCase.evidence || []).map((ev) => (
                  <div key={ev.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <span className="platform-badge windows">{ev.observable_type}</span>
                      <span className={`risk-badge ${ev.relevance === 'SUPPORTING' ? 'critical' : 'none'}`}>
                        {ev.relevance}
                      </span>
                    </div>
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: '#38bdf8', margin: '0.25rem 0' }}>
                      {ev.observable_value}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                      {ev.description}
                    </div>
                  </div>
                ))}
              </div>

              {/* Add Evidence Form */}
              <form onSubmit={handleAddEvidence} style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                  + Record Evidence Artifact
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <select
                    value={newEvType}
                    onChange={(e) => setNewEvType(e.target.value)}
                    style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.35rem 0.5rem', color: '#cbd5e1', fontSize: '0.75rem' }}
                  >
                    <option value="PROCESS">Process Execution</option>
                    <option value="FILE_HASH">File Hash</option>
                    <option value="IP_ADDRESS">IP Address</option>
                    <option value="DOMAIN">Domain Name</option>
                    <option value="PERSISTENCE">Persistence</option>
                    <option value="PRIVILEGE">Privilege Elevation</option>
                  </select>
                  <select
                    value={newEvRelevance}
                    onChange={(e) => setNewEvRelevance(e.target.value as EvidenceRelevance)}
                    style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.35rem 0.5rem', color: '#cbd5e1', fontSize: '0.75rem' }}
                  >
                    <option value="SUPPORTING">Supporting</option>
                    <option value="REFUTING">Refuting</option>
                    <option value="INCONCLUSIVE">Inconclusive</option>
                  </select>
                </div>
                <input
                  type="text"
                  placeholder="Observable value (e.g. powershell.exe, 198.51.100.45)..."
                  value={newEvValue}
                  onChange={(e) => setNewEvValue(e.target.value)}
                  required
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#f8fafc', fontSize: '0.8rem', marginBottom: '0.5rem' }}
                />
                <input
                  type="text"
                  placeholder="Analyst reasoning / evidence description..."
                  value={newEvDesc}
                  onChange={(e) => setNewEvDesc(e.target.value)}
                  required
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#f8fafc', fontSize: '0.8rem', marginBottom: '0.5rem' }}
                />
                <button type="submit" className="btn-cyber-primary" style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}>
                  Attach Evidence
                </button>
              </form>
            </div>
          </div>

          {/* Section 3: Findings & Case Conclusion */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {/* Findings */}
            <div className="investigation-section">
              <div className="section-header">
                <span className="section-title">
                  <span>🚩</span> Key Findings ({activeCase.findings?.length || 0})
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
                {(activeCase.findings || []).map((f) => (
                  <div key={f.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.85rem' }}>{f.title}</span>
                      <span className={`risk-badge ${f.severity.toLowerCase()}`}>{f.severity}</span>
                    </div>
                    {f.mitre_technique && (
                      <div style={{ fontSize: '0.75rem', color: '#a855f7', marginBottom: '0.3rem' }}>
                        MITRE ATT&CK: {f.mitre_technique}
                      </div>
                    )}
                    <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>{f.description}</div>
                  </div>
                ))}
              </div>

              {/* Add Finding Form */}
              <form onSubmit={handleAddFinding} style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                  + Record Security Finding
                </div>
                <input
                  type="text"
                  placeholder="Finding title (e.g. Ingress tool transfer via PowerShell)..."
                  value={newFindingTitle}
                  onChange={(e) => setNewFindingTitle(e.target.value)}
                  required
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#f8fafc', fontSize: '0.8rem', marginBottom: '0.5rem' }}
                />
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    placeholder="MITRE Technique (optional, e.g. T1059.001)..."
                    value={newFindingMitre}
                    onChange={(e) => setNewFindingMitre(e.target.value)}
                    style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#f8fafc', fontSize: '0.8rem' }}
                  />
                  <select
                    value={newFindingSev}
                    onChange={(e) => setNewFindingSev(e.target.value)}
                    style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#cbd5e1', fontSize: '0.8rem' }}
                  >
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
                <textarea
                  placeholder="Detailed finding observations..."
                  value={newFindingDesc}
                  onChange={(e) => setNewFindingDesc(e.target.value)}
                  required
                  rows={2}
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem 0.65rem', color: '#f8fafc', fontSize: '0.8rem', marginBottom: '0.5rem' }}
                />
                <button type="submit" className="btn-cyber-primary" style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}>
                  Save Finding
                </button>
              </form>
            </div>

            {/* Case Conclusion */}
            <div className="investigation-section">
              <div className="section-header">
                <span className="section-title">
                  <span>🏁</span> Final Conclusion & Rubric Scoring
                </span>
              </div>

              <form onSubmit={handleSubmitConclusion}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                    Analytical Verdict:
                  </label>
                  <select
                    value={concVerdict}
                    onChange={(e) => setConcVerdict(e.target.value as EndpointVerdict)}
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.5rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  >
                    <option value="CONFIRMED_COMPROMISE">CONFIRMED_COMPROMISE - Malicious execution & adversary activity confirmed</option>
                    <option value="SUSPICIOUS">SUSPICIOUS - Anomalous behaviors observed, requiring monitoring</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE - Legitimate administrative or developer action</option>
                    <option value="BENIGN">BENIGN - Normal baseline operating activity</option>
                  </select>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                    Executive Investigation Summary:
                  </label>
                  <textarea
                    value={concSummary}
                    onChange={(e) => setConcSummary(e.target.value)}
                    required
                    rows={4}
                    placeholder="Synthesize the facts, timeline of process execution, egress destinations, and impact..."
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.5rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                    Lessons Learned & Hardening Recommendations:
                  </label>
                  <textarea
                    value={concLessons}
                    onChange={(e) => setConcLessons(e.target.value)}
                    rows={2}
                    placeholder="e.g. Enforce script block logging, AppLocker policies, egress filtering..."
                    style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.5rem 0.75rem', color: '#f8fafc', fontSize: '0.85rem' }}
                  />
                </div>

                <button
                  type="submit"
                  className="btn-cyber-primary"
                  disabled={submittingConc}
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  {submittingConc ? 'Evaluating Rubric...' : 'Finalize Investigation & Score ➔'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
