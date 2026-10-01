import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type {
  FindingConfidence,
  HypothesisStatus,
  InvestigationDetailResponse,
  InvestigationStatus,
  TrainingPriority,
  TriageClassification,
} from '../../types/soc'
import '../../components/soc/soc.css'

export const InvestigationWorkspacePage: React.FC = () => {
  const { investigationId } = useParams<{ investigationId: string }>()
  const [inv, setInv] = useState<InvestigationDetailResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'ALERTS' | 'EVIDENCE' | 'HYPOTHESES' | 'FINDINGS' | 'NOTES' | 'REPORT'>('OVERVIEW')

  // Forms State
  const [conclusion, setConclusion] = useState<string>('')
  const [recommendations, setRecommendations] = useState<string>('')
  const [statusVal, setStatusVal] = useState<InvestigationStatus>('OPEN')
  const [classVal, setClassVal] = useState<TriageClassification>('UNREVIEWED')
  const [priorityVal, setPriorityVal] = useState<TrainingPriority>('P3')

  // New Hypothesis
  const [newHypText, setNewHypText] = useState<string>('')
  const [newHypReasoning, setNewHypReasoning] = useState<string>('')

  // New Finding
  const [newFindingTitle, setNewFindingTitle] = useState<string>('')
  const [newFindingDesc, setNewFindingDesc] = useState<string>('')
  const [newFindingConf, setNewFindingConf] = useState<FindingConfidence>('HIGH')

  // New Note
  const [newNote, setNewNote] = useState<string>('')

  // New Evidence
  const [newEvType, setNewEvType] = useState<string>('PACKET')
  const [newEvDesc, setNewEvDesc] = useState<string>('')
  const [newEvPktNum, setNewEvPktNum] = useState<string>('')

  // Link Alert
  const [linkAlertId, setLinkAlertId] = useState<string>('')

  // Export JSON Report Modal / View
  const [reportData, setReportData] = useState<Record<string, unknown> | null>(null)
  const [loadingReport, setLoadingReport] = useState<boolean>(false)

  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchInvestigation = async () => {
    if (!investigationId) return
    try {
      setLoading(true)
      const data = await socApi.getInvestigation(Number(investigationId))
      setInv(data)
      setConclusion(data.conclusion || '')
      setRecommendations(data.recommendations || '')
      setStatusVal(data.status)
      setClassVal(data.classification)
      setPriorityVal(data.priority)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch investigation details.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInvestigation()
  }, [investigationId])

  const handleSaveOverview = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inv) return
    try {
      setError(null)
      const updated = await socApi.updateInvestigation(inv.id, {
        status: statusVal,
        classification: classVal,
        priority: priorityVal,
        conclusion: conclusion.trim() || undefined,
        recommendations: recommendations.trim() || undefined,
      })
      setInv(updated)
      setMessage('Investigation overview and conclusions saved successfully.')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save changes.')
    }
  }

  const handleAddHypothesis = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inv || !newHypText.trim()) return
    try {
      setError(null)
      await socApi.addHypothesis(inv.id, {
        hypothesis_text: newHypText.trim(),
        reasoning: newHypReasoning.trim() || undefined,
      })
      setNewHypText('')
      setNewHypReasoning('')
      setMessage('New hypothesis registered.')
      await fetchInvestigation()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add hypothesis.')
    }
  }

  const handleUpdateHypothesisStatus = async (hypId: number, newStatus: HypothesisStatus) => {
    if (!inv) return
    try {
      await socApi.updateHypothesis(inv.id, hypId, { status: newStatus })
      setMessage(`Hypothesis marked as ${newStatus}.`)
      await fetchInvestigation()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update hypothesis status.')
    }
  }

  const handleAddFinding = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inv || !newFindingTitle.trim()) return
    try {
      setError(null)
      await socApi.addInvestigationFinding(inv.id, {
        title: newFindingTitle.trim(),
        description: newFindingDesc.trim(),
        confidence: newFindingConf,
      })
      setNewFindingTitle('')
      setNewFindingDesc('')
      setMessage('Finding recorded.')
      await fetchInvestigation()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to record finding.')
    }
  }

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inv || !newEvDesc.trim()) return
    try {
      setError(null)
      await socApi.addInvestigationEvidence(inv.id, {
        evidence_type: newEvType,
        description: newEvDesc.trim(),
        packet_number: newEvPktNum ? Number(newEvPktNum) : undefined,
      })
      setNewEvDesc('')
      setNewEvPktNum('')
      setMessage('Evidence bound to investigation.')
      await fetchInvestigation()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add evidence.')
    }
  }

  const handleLinkAlert = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inv || !linkAlertId.trim()) return
    try {
      setError(null)
      await socApi.linkAlertToInvestigation(inv.id, Number(linkAlertId))
      setLinkAlertId('')
      setMessage(`Alert #${linkAlertId} linked.`)
      await fetchInvestigation()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to link alert.')
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inv || !newNote.trim()) return
    try {
      setError(null)
      await socApi.addInvestigationNote(inv.id, newNote.trim())
      setNewNote('')
      setMessage('Analyst note saved.')
      await fetchInvestigation()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to record note.')
    }
  }

  const handleFetchReport = async () => {
    if (!inv) return
    try {
      setLoadingReport(true)
      const rep = await socApi.exportInvestigationReport(inv.id)
      setReportData(rep)
      setActiveTab('REPORT')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate report.')
    } finally {
      setLoadingReport(false)
    }
  }

  return (
    <div className="soc-container">
      <SocHeader
        title={`${inv?.investigation_id || 'Investigation'}: ${inv?.title || 'Forensic Workspace'}`}
        subtitle="Formulate hypotheses, bind packet evidence, record verified findings, and produce forensic conclusion reports"
        actionButton={
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Link to="/soc/investigations" className="soc-btn soc-btn-secondary">
              ← Investigations List
            </Link>
            <Link to="/threat-intelligence/search" className="soc-btn soc-btn-secondary">
              🎯 Search IOCs
            </Link>
            <button className="soc-btn soc-btn-primary" onClick={handleFetchReport} disabled={loadingReport}>
              {loadingReport ? 'Compiling...' : 'Export JSON Report 📄'}
            </button>
          </div>
        }
      />

      {message && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '6px', color: '#4ade80', fontSize: '0.88rem' }}>
          {message}
        </div>
      )}

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#f87171', fontSize: '0.88rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
          Loading investigation workspace...
        </div>
      ) : !inv ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
          Investigation not found.
        </div>
      ) : (
        <>
          {/* Workspace Sub-tabs */}
          <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--soc-border)', paddingBottom: '0.5rem', flexWrap: 'wrap' }}>
            <button
              className={`soc-btn ${activeTab === 'OVERVIEW' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('OVERVIEW')}
            >
              Overview & Conclusion
            </button>
            <button
              className={`soc-btn ${activeTab === 'ALERTS' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('ALERTS')}
            >
              Linked Alerts ({inv.alerts.length})
            </button>
            <button
              className={`soc-btn ${activeTab === 'EVIDENCE' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('EVIDENCE')}
            >
              Bound Evidence ({inv.evidence.length})
            </button>
            <button
              className={`soc-btn ${activeTab === 'HYPOTHESES' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('HYPOTHESES')}
            >
              Hypotheses ({inv.hypotheses.length})
            </button>
            <button
              className={`soc-btn ${activeTab === 'FINDINGS' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('FINDINGS')}
            >
              Findings ({inv.findings.length})
            </button>
            <button
              className={`soc-btn ${activeTab === 'NOTES' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('NOTES')}
            >
              Forensic Notes ({inv.notes.length})
            </button>
            <button
              className={`soc-btn ${activeTab === 'REPORT' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
              onClick={() => setActiveTab('REPORT')}
            >
              Forensic Report View
            </button>
          </div>

          {/* TAB 1: OVERVIEW & CONCLUSION */}
          {activeTab === 'OVERVIEW' && (
            <div className="soc-card">
              <form onSubmit={handleSaveOverview} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.3rem' }}>
                      Investigation Status
                    </label>
                    <select
                      className="soc-select"
                      style={{ width: '100%' }}
                      value={statusVal}
                      onChange={(e) => setStatusVal(e.target.value as InvestigationStatus)}
                      aria-label="Investigation Status"
                    >
                      <option value="OPEN">OPEN</option>
                      <option value="INVESTIGATING">INVESTIGATING</option>
                      <option value="PENDING">PENDING</option>
                      <option value="RESOLVED">RESOLVED</option>
                      <option value="CLOSED">CLOSED</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.3rem' }}>
                      Overall Classification
                    </label>
                    <select
                      className="soc-select"
                      style={{ width: '100%' }}
                      value={classVal}
                      onChange={(e) => setClassVal(e.target.value as TriageClassification)}
                      aria-label="Overall Classification"
                    >
                      <option value="UNREVIEWED">UNREVIEWED</option>
                      <option value="BENIGN">BENIGN</option>
                      <option value="SUSPICIOUS">SUSPICIOUS</option>
                      <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                      <option value="REQUIRES_MORE_DATA">REQUIRES_MORE_DATA</option>
                      <option value="CLOSED">CLOSED</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--soc-text-muted)', marginBottom: '0.3rem' }}>
                      Priority
                    </label>
                    <select
                      className="soc-select"
                      style={{ width: '100%' }}
                      value={priorityVal}
                      onChange={(e) => setPriorityVal(e.target.value as TrainingPriority)}
                      aria-label="Priority"
                    >
                      <option value="P1">P1 Critical</option>
                      <option value="P2">P2 High</option>
                      <option value="P3">P3 Medium</option>
                      <option value="P4">P4 Low</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--soc-text-primary)', marginBottom: '0.35rem' }}>
                    Forensic Conclusion & Synthesis
                  </label>
                  <textarea
                    className="soc-textarea"
                    rows={4}
                    style={{ width: '100%' }}
                    placeholder="Provide a final analytical determination based on verified hypotheses and packet evidence..."
                    value={conclusion}
                    onChange={(e) => setConclusion(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--soc-text-primary)', marginBottom: '0.35rem' }}>
                    Remediation & Defensive Recommendations
                  </label>
                  <textarea
                    className="soc-textarea"
                    rows={3}
                    style={{ width: '100%' }}
                    placeholder="Defensive actions to recommend: firewall rules, tuning detection thresholds, updating firmware, etc..."
                    value={recommendations}
                    onChange={(e) => setRecommendations(e.target.value)}
                  />
                </div>

                <button type="submit" className="soc-btn soc-btn-primary" style={{ alignSelf: 'flex-start' }}>
                  Save Investigation Determinations
                </button>
              </form>
            </div>
          )}

          {/* TAB 2: LINKED ALERTS */}
          {activeTab === 'ALERTS' && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Associated Detection Alerts</div>
                <form onSubmit={handleLinkAlert} style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="number"
                    className="soc-input"
                    placeholder="Alert ID to link..."
                    value={linkAlertId}
                    onChange={(e) => setLinkAlertId(e.target.value)}
                    style={{ width: '160px' }}
                  />
                  <button type="submit" className="soc-btn soc-btn-primary" style={{ fontSize: '0.8rem' }}>
                    Link Alert
                  </button>
                </form>
              </div>

              {inv.alerts.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                  No alerts currently linked to this investigation.
                </div>
              ) : (
                <div className="soc-table-container">
                  <table className="soc-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Alert Title</th>
                        <th>Severity</th>
                        <th>Priority</th>
                        <th>Source → Destination</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {inv.alerts.map((a) => (
                        <tr key={a.id}>
                          <td>#{a.id}</td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)' }}>{a.title}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>{a.rule_code}</div>
                          </td>
                          <td>{a.severity}</td>
                          <td>{a.priority}</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                            {a.source_ip}:{a.source_port} → {a.destination_ip}:{a.destination_port}
                          </td>
                          <td>
                            <Link to={`/soc/alerts/${a.id}`} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                              Inspect
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

          {/* TAB 3: BOUND EVIDENCE */}
          {activeTab === 'EVIDENCE' && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Granular Telemetry Evidence</div>
              </div>

              <form onSubmit={handleAddEvidence} style={{ display: 'grid', gridTemplateColumns: '150px 120px 1fr auto', gap: '0.5rem', alignItems: 'center' }}>
                <select className="soc-select" value={newEvType} onChange={(e) => setNewEvType(e.target.value)} aria-label="Evidence Type">
                  <option value="PACKET">PACKET</option>
                  <option value="FLOW">FLOW</option>
                  <option value="STATISTIC">STATISTIC</option>
                  <option value="DNS_QUERY">DNS_QUERY</option>
                  <option value="TCP_FLAG">TCP_FLAG</option>
                  <option value="ARP_ENTRY">ARP_ENTRY</option>
                </select>
                <input
                  type="number"
                  className="soc-input"
                  placeholder="Pkt # (opt)"
                  value={newEvPktNum}
                  onChange={(e) => setNewEvPktNum(e.target.value)}
                />
                <input
                  type="text"
                  className="soc-input"
                  placeholder="Evidence description or observation..."
                  value={newEvDesc}
                  onChange={(e) => setNewEvDesc(e.target.value)}
                  required
                />
                <button type="submit" className="soc-btn soc-btn-primary">
                  Attach Evidence
                </button>
              </form>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', marginTop: '1rem' }}>
                {inv.evidence.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                    No evidence items bound yet.
                  </div>
                ) : (
                  inv.evidence.map((ev) => (
                    <div key={ev.id} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--soc-border)', borderRadius: '6px', padding: '0.85rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#38bdf8' }}>
                          Evidence #{ev.id} • [{ev.evidence_type}] {ev.packet_number ? `Packet #${ev.packet_number}` : ''}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                          {new Date(ev.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.88rem', color: 'var(--soc-text-secondary)', marginTop: '0.35rem' }}>
                        {ev.description}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 4: HYPOTHESES */}
          {activeTab === 'HYPOTHESES' && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Analytical Hypotheses & Validation</div>
              </div>

              {/* Add Hypothesis Form */}
              <form onSubmit={handleAddHypothesis} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.4)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                <input
                  type="text"
                  className="soc-input"
                  placeholder="Formulate working hypothesis (e.g. 'Attacker is probing for open SSH port via SYN scan')..."
                  value={newHypText}
                  onChange={(e) => setNewHypText(e.target.value)}
                  required
                />
                <input
                  type="text"
                  className="soc-input"
                  placeholder="Reasoning / expected corroborating evidence..."
                  value={newHypReasoning}
                  onChange={(e) => setNewHypReasoning(e.target.value)}
                />
                <button type="submit" className="soc-btn soc-btn-primary" style={{ alignSelf: 'flex-start' }}>
                  Register Hypothesis
                </button>
              </form>

              {/* Hypotheses List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
                {inv.hypotheses.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                    No hypotheses registered. Formulate one above to guide your investigation.
                  </div>
                ) : (
                  inv.hypotheses.map((h) => (
                    <div key={h.id} className="soc-hypothesis-card">
                      <div className="soc-hypothesis-header">
                        <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--soc-text-primary)' }}>
                          {h.hypothesis_text}
                        </div>
                        <div style={{ display: 'flex', gap: '0.35rem' }}>
                          <button
                            className={`soc-btn ${h.status === 'SUPPORTED' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
                            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                            onClick={() => handleUpdateHypothesisStatus(h.id, 'SUPPORTED')}
                          >
                            ✓ Supported
                          </button>
                          <button
                            className={`soc-btn ${h.status === 'NOT_SUPPORTED' ? 'soc-btn-danger' : 'soc-btn-secondary'}`}
                            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                            onClick={() => handleUpdateHypothesisStatus(h.id, 'NOT_SUPPORTED')}
                          >
                            ✗ Refuted
                          </button>
                          <button
                            className={`soc-btn ${h.status === 'INCONCLUSIVE' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
                            style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                            onClick={() => handleUpdateHypothesisStatus(h.id, 'INCONCLUSIVE')}
                          >
                            ? Inconclusive
                          </button>
                        </div>
                      </div>
                      {h.reasoning && (
                        <div style={{ fontSize: '0.85rem', color: 'var(--soc-text-secondary)' }}>
                          <strong>Reasoning:</strong> {h.reasoning}
                        </div>
                      )}
                      <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                        Status: <strong>{h.status}</strong> • Created by: {h.created_by_name || 'Analyst'}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 5: FINDINGS */}
          {activeTab === 'FINDINGS' && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Verified Forensic Findings</div>
              </div>

              {/* Add Finding Form */}
              <form onSubmit={handleAddFinding} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.4)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 140px', gap: '0.5rem' }}>
                  <input
                    type="text"
                    className="soc-input"
                    placeholder="Finding Title (e.g., 'Port Scanning Confirmed on Ports 22, 80, 443')..."
                    value={newFindingTitle}
                    onChange={(e) => setNewFindingTitle(e.target.value)}
                    required
                  />
                  <select
                    className="soc-select"
                    value={newFindingConf}
                    onChange={(e) => setNewFindingConf(e.target.value as FindingConfidence)}
                    aria-label="Finding Confidence"
                  >
                    <option value="HIGH">High Confidence</option>
                    <option value="MEDIUM">Medium Confidence</option>
                    <option value="LOW">Low Confidence</option>
                  </select>
                </div>
                <textarea
                  className="soc-textarea"
                  rows={2}
                  placeholder="Detailed description of substantiated finding..."
                  value={newFindingDesc}
                  onChange={(e) => setNewFindingDesc(e.target.value)}
                  required
                />
                <button type="submit" className="soc-btn soc-btn-primary" style={{ alignSelf: 'flex-start' }}>
                  Record Finding
                </button>
              </form>

              {/* Findings List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
                {inv.findings.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                    No findings substantiated yet. Verify hypotheses with evidence first.
                  </div>
                ) : (
                  inv.findings.map((f) => (
                    <div key={f.id} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--soc-border)', borderRadius: '6px', padding: '0.85rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--soc-text-primary)' }}>
                          {f.title}
                        </span>
                        <span className="soc-badge soc-badge-benign" style={{ fontSize: '0.75rem' }}>
                          Confidence: {f.confidence}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--soc-text-secondary)', marginTop: '0.35rem' }}>
                        {f.description}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 6: FORENSIC NOTES */}
          {activeTab === 'NOTES' && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Analyst Audit Notes</div>
              </div>

              <form onSubmit={handleAddNote} style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  className="soc-input"
                  placeholder="Append chronological analyst note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button type="submit" className="soc-btn soc-btn-primary" disabled={!newNote.trim()}>
                  Save Note
                </button>
              </form>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
                {inv.notes.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                    No notes recorded yet.
                  </div>
                ) : (
                  inv.notes.map((n) => (
                    <div key={n.id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--soc-text-muted)', marginBottom: '0.25rem' }}>
                        <span>{n.author_name || 'Analyst'}</span>
                        <span>{new Date(n.created_at).toLocaleString()}</span>
                      </div>
                      <div style={{ fontSize: '0.88rem', color: 'var(--soc-text-secondary)' }}>{n.note}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 7: REPORT VIEW */}
          {activeTab === 'REPORT' && (
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">Compiled Forensic Incident Report (JSON)</div>
                <button
                  className="soc-btn soc-btn-secondary"
                  onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(reportData, null, 2))
                    setMessage('Report JSON copied to clipboard!')
                  }}
                  disabled={!reportData}
                >
                  Copy JSON
                </button>
              </div>

              {!reportData ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                  Click &quot;Export JSON Report&quot; above to compile the forensic dossier.
                </div>
              ) : (
                <pre style={{ margin: 0, padding: '1rem', background: '#070b12', border: '1px solid var(--soc-border)', borderRadius: '6px', color: '#94a3b8', fontSize: '0.82rem', maxHeight: '550px', overflowY: 'auto' }}>
                  {JSON.stringify(reportData, null, 2)}
                </pre>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
