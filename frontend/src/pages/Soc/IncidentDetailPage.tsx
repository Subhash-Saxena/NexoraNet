import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { IncidentNav, type WorkbenchTab } from '../../components/incident_response/IncidentNav'
import { MitreMatrix } from '../../components/incident_response/MitreMatrix'
import { IncidentTimeline } from '../../components/incident_response/IncidentTimeline'
import { EvidenceDrawer } from '../../components/incident_response/EvidenceDrawer'
import { ResponseSimulator } from '../../components/incident_response/ResponseSimulator'
import { ReportView } from '../../components/incident_response/ReportView'
import { incidentResponseApi } from '../../services/incidentResponseApi'
import type {
  AttackTechnique,
  Incident,
  IncidentPlaybook,
  IncidentReport,
  MatrixCoverageResponse,
} from '../../types/incidentResponse'
import '../../components/incident_response/incidentResponse.css'

export const IncidentDetailPage: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>()
  const [activeTab, setActiveTab] = useState<WorkbenchTab>('overview')
  const [incident, setIncident] = useState<Incident | null>(null)
  const [coverage, setCoverage] = useState<MatrixCoverageResponse | null>(null)
  const [allTechniques, setAllTechniques] = useState<AttackTechnique[]>([])
  const [playbooks, setPlaybooks] = useState<IncidentPlaybook[]>([])
  const [report, setReport] = useState<IncidentReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [reportLoading, setReportLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Overview edit states
  const [editingAnalysis, setEditingAnalysis] = useState(false)
  const [summary, setSummary] = useState('')
  const [impactAssessment, setImpactAssessment] = useState('')
  const [rootCause, setRootCause] = useState('')
  const [lessonsLearned, setLessonsLearned] = useState('')
  const [recommendations, setRecommendations] = useState('')
  const [newNote, setNewNote] = useState('')

  // Hypotheses & Findings states
  const [hypStatement, setHypStatement] = useState('')
  const [hypConfidence, setHypConfidence] = useState('MEDIUM')
  const [hypRationale, setHypRationale] = useState('')
  const [findingTitle, setFindingTitle] = useState('')
  const [findingDesc, setFindingDesc] = useState('')
  const [findingSeverity, setFindingSeverity] = useState('MEDIUM')
  const [findingTech, setFindingTech] = useState('')

  const loadIncident = async () => {
    if (!incidentId) return
    setLoading(true)
    setError(null)
    try {
      const data = await incidentResponseApi.getIncident(incidentId)
      setIncident(data)
      setSummary(data.summary || '')
      setImpactAssessment(data.impact_assessment || '')
      setRootCause(data.root_cause || '')
      setLessonsLearned(data.lessons_learned || '')
      setRecommendations(data.recommendations || '')

      // Load matrix coverage for this incident
      const [covData, techs, pbList] = await Promise.all([
        incidentResponseApi.getMatrixCoverage(data.id),
        incidentResponseApi.listTechniques(),
        incidentResponseApi.listPlaybooks(),
      ])
      setCoverage(covData)
      setAllTechniques(techs)
      setPlaybooks(pbList)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incident')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadIncident()
  }, [incidentId])

  useEffect(() => {
    if (activeTab === 'report' && incident) {
      setReportLoading(true)
      incidentResponseApi
        .getIncidentReport(incident.incident_id)
        .then(setReport)
        .catch((e) => console.error(e))
        .finally(() => setReportLoading(false))
    }
  }, [activeTab, incident?.incident_id])

  if (loading) {
    return <div className="ir-container" style={{ padding: '48px', color: '#9ca3af' }}>Loading Incident Workbench...</div>
  }

  if (error || !incident) {
    return (
      <div className="ir-container">
        <div style={{ color: '#ef4444', marginBottom: '16px' }}>{error || 'Incident not found'}</div>
        <Link to="/soc/incidents" className="ir-btn-secondary">
          ← Return to Incidents
        </Link>
      </div>
    )
  }

  // Handlers
  const handleStatusChange = async (newStatus: string) => {
    try {
      const updated = await incidentResponseApi.updateIncident(incident.incident_id, { status: newStatus as any })
      setIncident(updated)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Status update failed')
    }
  }

  const handleSaveAnalysis = async () => {
    try {
      const updated = await incidentResponseApi.updateIncident(incident.incident_id, {
        summary,
        impact_assessment: impactAssessment,
        root_cause: rootCause,
        lessons_learned: lessonsLearned,
        recommendations,
      })
      setIncident(updated)
      setEditingAnalysis(false)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Save failed')
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newNote.trim()) return
    try {
      await incidentResponseApi.addNote(incident.incident_id, newNote)
      setNewNote('')
      loadIncident()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Note failed')
    }
  }

  const handleAttachPlaybook = async (pbId: string) => {
    try {
      const updated = await incidentResponseApi.attachPlaybook(incident.incident_id, pbId)
      setIncident(updated)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to attach playbook')
    }
  }

  const handleCreateHypothesis = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!hypStatement.trim()) return
    try {
      await incidentResponseApi.createHypothesis(incident.id, {
        statement: hypStatement,
        confidence: hypConfidence,
        rationale: hypRationale || undefined,
      })
      setHypStatement('')
      setHypRationale('')
      loadIncident()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Hypothesis creation failed')
    }
  }

  const handleUpdateHypothesisStatus = async (hypId: string, newStatus: string) => {
    try {
      await incidentResponseApi.updateHypothesis(incident.id, hypId, { status: newStatus })
      loadIncident()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Hypothesis update failed')
    }
  }

  const handleRecordFinding = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!findingTitle.trim()) return
    try {
      await incidentResponseApi.recordFinding(incident.id, {
        title: findingTitle,
        description: findingDesc,
        severity: findingSeverity,
        mitre_technique: findingTech || undefined,
      })
      setFindingTitle('')
      setFindingDesc('')
      setFindingTech('')
      loadIncident()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Finding recording failed')
    }
  }

  const parsedChecklist = incident.playbook ? JSON.parse(incident.playbook.checklist_json || '[]') : []
  const parsedPhases = incident.playbook ? JSON.parse(incident.playbook.phases_definition || '{}') : {}

  return (
    <div className="ir-container">
      {/* Simulation Safety Banner */}
      <div className="ir-safety-banner">
        <div>
          <span className="shield-icon">🛡️</span>
          <strong>NexoraNet Incident Response Lab — Synthetic Training Environment</strong>
          <span style={{ marginLeft: '12px', color: '#67e8f9', fontSize: '0.8rem' }}>
            All defensive actions executed within this workbench are non-destructive and simulated.
          </span>
        </div>
        <span className="ir-safety-badge">Active Case: {incident.incident_id}</span>
      </div>

      {/* Breadcrumb & Title */}
      <div style={{ marginBottom: '16px' }}>
        <Link to="/soc/incidents" style={{ color: '#06b6d4', textDecoration: 'none', fontSize: '0.85rem' }}>
          ← Back to Incident Queue
        </Link>
      </div>

      <div className="ir-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <span className="ir-table-id" style={{ fontSize: '1.25rem' }}>{incident.incident_id}</span>
            <span
              className={`ir-pill ${
                incident.severity === 'CRITICAL'
                  ? 'badge-crit'
                  : incident.severity === 'HIGH'
                  ? 'badge-high'
                  : incident.severity === 'MEDIUM'
                  ? 'badge-med'
                  : 'badge-low'
              }`}
            >
              {incident.severity}
            </span>
            <span className="ir-pill badge-cyan">{incident.incident_type.replace(/_/g, ' ')}</span>
            <span className="ir-pill badge-emerald">{incident.classification}</span>
          </div>
          <h1 style={{ margin: '0 0 6px 0', fontSize: '1.75rem', color: '#fff' }}>{incident.title}</h1>
          <p style={{ margin: 0, color: '#9ca3af', fontSize: '0.9rem' }}>{incident.description}</p>
        </div>

        {/* Status Dropdown */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
          <label style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase' }}>Workflow Status</label>
          <select
            className="ir-select"
            value={incident.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            style={{ fontWeight: 600 }}
          >
            <option value="NEW">NEW</option>
            <option value="TRIAGED">TRIAGED</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="CONTAINMENT">CONTAINMENT</option>
            <option value="ERADICATION">ERADICATION</option>
            <option value="RECOVERY">RECOVERY</option>
            <option value="MONITORING">MONITORING</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="CLOSED">CLOSED</option>
            <option value="FALSE_POSITIVE">FALSE POSITIVE</option>
          </select>
        </div>
      </div>

      {/* NIST SP 800-61 Lifecycle Progress Bar */}
      <div className="ir-lifecycle-bar">
        <div className={`ir-lifecycle-step ${incident.phase === 'PREPARATION' ? 'active' : 'completed'}`}>
          <span>1.</span> Preparation
        </div>
        <div className={`ir-lifecycle-step ${incident.phase === 'DETECTION_ANALYSIS' ? 'active' : incident.phase !== 'PREPARATION' ? 'completed' : ''}`}>
          <span>2.</span> Detection & Analysis
        </div>
        <div className={`ir-lifecycle-step ${incident.phase === 'CONTAINMENT_ERADICATION_RECOVERY' ? 'active' : incident.phase === 'POST_INCIDENT_ACTIVITY' ? 'completed' : ''}`}>
          <span>3.</span> Containment, Eradication & Recovery
        </div>
        <div className={`ir-lifecycle-step ${incident.phase === 'POST_INCIDENT_ACTIVITY' ? 'active' : ''}`}>
          <span>4.</span> Post-Incident Activity & Lessons Learned
        </div>
      </div>

      {/* Workbench Tab Navigation */}
      <IncidentNav
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        counts={{
          evidence: incident.evidence?.length || 0,
          timeline: incident.timeline_events?.length || 0,
          hypotheses: incident.hypotheses?.length || 0,
          mitre: incident.technique_mappings?.length || 0,
          actions: incident.response_actions?.length || 0,
        }}
      />

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
            <div>
              {/* Analysis & Findings Card */}
              <div className="ir-kpi-card" style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Executive Incident Summary & Root Cause</h3>
                  <button
                    className="ir-btn-secondary"
                    style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                    onClick={() => {
                      if (editingAnalysis) handleSaveAnalysis()
                      else setEditingAnalysis(true)
                    }}
                  >
                    {editingAnalysis ? '💾 Save Changes' : '✏️ Edit Analysis'}
                  </button>
                </div>

                {editingAnalysis ? (
                  <div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ display: 'block', fontSize: '0.82rem', color: '#9ca3af', marginBottom: '4px' }}>
                        Executive Summary
                      </label>
                      <textarea
                        className="ir-search-input"
                        style={{ width: '100%', height: '70px' }}
                        value={summary}
                        onChange={(e) => setSummary(e.target.value)}
                      />
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ display: 'block', fontSize: '0.82rem', color: '#9ca3af', marginBottom: '4px' }}>
                        Impact Assessment
                      </label>
                      <textarea
                        className="ir-search-input"
                        style={{ width: '100%', height: '60px' }}
                        value={impactAssessment}
                        onChange={(e) => setImpactAssessment(e.target.value)}
                      />
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ display: 'block', fontSize: '0.82rem', color: '#9ca3af', marginBottom: '4px' }}>
                        Root Cause
                      </label>
                      <textarea
                        className="ir-search-input"
                        style={{ width: '100%', height: '60px' }}
                        value={rootCause}
                        onChange={(e) => setRootCause(e.target.value)}
                      />
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ display: 'block', fontSize: '0.82rem', color: '#9ca3af', marginBottom: '4px' }}>
                        Lessons Learned
                      </label>
                      <textarea
                        className="ir-search-input"
                        style={{ width: '100%', height: '60px' }}
                        value={lessonsLearned}
                        onChange={(e) => setLessonsLearned(e.target.value)}
                      />
                    </div>
                  </div>
                ) : (
                  <div style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: '1.6' }}>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#9ca3af' }}>Summary: </strong>
                      <p style={{ margin: '4px 0 0 0' }}>{incident.summary || 'No summary recorded yet.'}</p>
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#9ca3af' }}>Business & Technical Impact: </strong>
                      <p style={{ margin: '4px 0 0 0' }}>{incident.impact_assessment || 'Pending assessment.'}</p>
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#9ca3af' }}>Root Cause: </strong>
                      <p style={{ margin: '4px 0 0 0' }}>{incident.root_cause || 'Root cause under investigation.'}</p>
                    </div>
                    <div>
                      <strong style={{ color: '#9ca3af' }}>Lessons Learned: </strong>
                      <p style={{ margin: '4px 0 0 0' }}>{incident.lessons_learned || 'Document during post-incident review.'}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Analyst Work Log Notes */}
              <div className="ir-kpi-card">
                <h3 style={{ margin: '0 0 12px 0', fontSize: '1.1rem', color: '#fff' }}>Analyst Work Log</h3>
                <form onSubmit={handleAddNote} style={{ marginBottom: '16px', display: 'flex', gap: '10px' }}>
                  <input
                    type="text"
                    className="ir-search-input"
                    placeholder="Log investigative notes, hypotheses, or external updates..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                  />
                  <button type="submit" className="ir-btn-primary">
                    Post Note
                  </button>
                </form>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {incident.notes?.map((n) => (
                    <div
                      key={n.id}
                      style={{
                        background: '#0f172a',
                        border: '1px solid #1e293b',
                        borderRadius: '6px',
                        padding: '10px 14px',
                        fontSize: '0.85rem',
                      }}
                    >
                      <div style={{ fontSize: '0.72rem', color: '#06b6d4', marginBottom: '4px' }}>
                        {new Date(n.created_at).toLocaleString()}
                      </div>
                      <div style={{ color: '#e2e8f0' }}>{n.note}</div>
                    </div>
                  ))}
                  {(!incident.notes || incident.notes.length === 0) && (
                    <div style={{ color: '#6b7280', fontSize: '0.85rem' }}>No notes logged yet.</div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column: Metadata & Playbook Info */}
            <div>
              <div className="ir-kpi-card" style={{ marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: '#fff' }}>Incident Metadata</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Detected: </span>
                    <strong>{new Date(incident.detected_at).toLocaleString()}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Contained: </span>
                    <strong>{incident.contained_at ? new Date(incident.contained_at).toLocaleString() : 'Not Yet'}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Closed: </span>
                    <strong>{incident.closed_at ? new Date(incident.closed_at).toLocaleString() : 'Open'}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Lead Analyst: </span>
                    <strong>{incident.lead_analyst || 'Unassigned'}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#9ca3af' }}>Attached Playbook: </span>
                    <strong style={{ color: '#38bdf8' }}>{incident.playbook?.title || 'None Attached'}</strong>
                  </div>
                </div>

                {!incident.playbook && (
                  <div style={{ marginTop: '14px', borderTop: '1px solid #374151', paddingTop: '12px' }}>
                    <label style={{ display: 'block', fontSize: '0.78rem', color: '#9ca3af', marginBottom: '4px' }}>
                      Attach Standard Playbook
                    </label>
                    <select
                      className="ir-select"
                      style={{ width: '100%' }}
                      onChange={(e) => {
                        if (e.target.value) handleAttachPlaybook(e.target.value)
                      }}
                      defaultValue=""
                    >
                      <option value="" disabled>Select Playbook...</option>
                      {playbooks.map((pb) => (
                        <option key={pb.playbook_id} value={pb.playbook_id}>
                          {pb.title} ({pb.category})
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              {/* Linked Alerts */}
              <div className="ir-kpi-card">
                <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: '#fff' }}>
                  Linked Alerts ({incident.alerts?.length || 0})
                </h4>
                {incident.alerts?.map((a) => (
                  <div
                    key={a.id}
                    style={{
                      background: '#1e293b',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '0.8rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span>Alert #{a.alert_id}</span>
                    <span className="ir-pill badge-cyan">{a.role}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Evidence & Chain of Custody */}
      {activeTab === 'evidence' && (
        <EvidenceDrawer
          evidenceList={incident.evidence || []}
          onAddEvidence={async (data) => {
            await incidentResponseApi.addEvidence(incident.id, data)
            loadIncident()
          }}
          onVerifyHash={(evId) => incidentResponseApi.verifyEvidenceHash(incident.id, evId)}
          onUpdateEvidence={async (evId, data) => {
            await incidentResponseApi.updateEvidence(incident.id, evId, data)
            loadIncident()
          }}
        />
      )}

      {/* Tab 3: Timeline */}
      {activeTab === 'timeline' && (
        <IncidentTimeline
          events={incident.timeline_events || []}
          onAddEvent={async (data) => {
            await incidentResponseApi.addTimelineEvent(incident.id, data)
            loadIncident()
          }}
          onSyncSources={async () => {
            await incidentResponseApi.syncTimeline(incident.id)
            loadIncident()
          }}
        />
      )}

      {/* Tab 4: Hypotheses & Findings */}
      {activeTab === 'hypotheses' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Hypotheses Column */}
          <div>
            <div className="ir-kpi-card" style={{ marginBottom: '16px' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '1.05rem', color: '#fff' }}>
                Formulate Investigative Hypothesis
              </h3>
              <form onSubmit={handleCreateHypothesis}>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '60px', marginBottom: '8px' }}
                  placeholder="e.g. Attacker accessed database via stolen credentials on FIN-SRV-01..."
                  value={hypStatement}
                  onChange={(e) => setHypStatement(e.target.value)}
                  required
                />
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <select
                    className="ir-select"
                    value={hypConfidence}
                    onChange={(e) => setHypConfidence(e.target.value)}
                  >
                    <option value="LOW">Low Confidence</option>
                    <option value="MEDIUM">Medium Confidence</option>
                    <option value="HIGH">High Confidence</option>
                  </select>
                  <button type="submit" className="ir-btn-primary">
                    + Propose Hypothesis
                  </button>
                </div>
              </form>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {incident.hypotheses?.map((h) => (
                <div
                  key={h.id}
                  style={{
                    background: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    padding: '14px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span className="ir-table-id">{h.hypothesis_id}</span>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <span className="ir-pill badge-cyan">{h.confidence} Confidence</span>
                      <span
                        className={`ir-pill ${
                          h.status === 'SUPPORTED'
                            ? 'badge-emerald'
                            : h.status === 'NOT_SUPPORTED'
                            ? 'badge-crit'
                            : 'badge-med'
                        }`}
                      >
                        {h.status}
                      </span>
                    </div>
                  </div>
                  <p style={{ margin: '0 0 8px 0', fontSize: '0.88rem', color: '#fff' }}>{h.statement}</p>
                  {h.rationale && (
                    <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginBottom: '8px' }}>
                      Rationale: {h.rationale}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end', borderTop: '1px solid #1f2937', paddingTop: '6px' }}>
                    <button
                      className="ir-btn-secondary"
                      style={{ padding: '2px 8px', fontSize: '0.75rem', color: '#10b981' }}
                      onClick={() => handleUpdateHypothesisStatus(h.hypothesis_id, 'SUPPORTED')}
                    >
                      ✓ Supported
                    </button>
                    <button
                      className="ir-btn-secondary"
                      style={{ padding: '2px 8px', fontSize: '0.75rem', color: '#ef4444' }}
                      onClick={() => handleUpdateHypothesisStatus(h.hypothesis_id, 'NOT_SUPPORTED')}
                    >
                      ✗ Not Supported
                    </button>
                    <button
                      className="ir-btn-secondary"
                      style={{ padding: '2px 8px', fontSize: '0.75rem', color: '#eab308' }}
                      onClick={() => handleUpdateHypothesisStatus(h.hypothesis_id, 'INCONCLUSIVE')}
                    >
                      Inconclusive
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Validated Findings Column */}
          <div>
            <div className="ir-kpi-card" style={{ marginBottom: '16px' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '1.05rem', color: '#fff' }}>
                Record Validated Finding
              </h3>
              <form onSubmit={handleRecordFinding}>
                <input
                  type="text"
                  className="ir-search-input"
                  style={{ width: '100%', marginBottom: '8px' }}
                  placeholder="Finding Title (e.g. Ransomware staged in Temp folder)"
                  value={findingTitle}
                  onChange={(e) => setFindingTitle(e.target.value)}
                  required
                />
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '50px', marginBottom: '8px' }}
                  placeholder="Detailed factual finding supported by evidence..."
                  value={findingDesc}
                  onChange={(e) => setFindingDesc(e.target.value)}
                  required
                />
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <input
                    type="text"
                    className="ir-search-input"
                    style={{ width: '120px' }}
                    placeholder="MITRE (T1486)"
                    value={findingTech}
                    onChange={(e) => setFindingTech(e.target.value)}
                  />
                  <select
                    className="ir-select"
                    value={findingSeverity}
                    onChange={(e) => setFindingSeverity(e.target.value)}
                  >
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                  <button type="submit" className="ir-btn-primary">
                    Record Finding
                  </button>
                </div>
              </form>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {incident.findings?.map((f) => (
                <div
                  key={f.id}
                  style={{
                    background: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    padding: '14px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span className="ir-table-id">{f.finding_id}</span>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {f.mitre_technique && <span className="ir-pill badge-cyan">{f.mitre_technique}</span>}
                      <span className="ir-pill badge-high">{f.severity}</span>
                    </div>
                  </div>
                  <h4 style={{ margin: '0 0 4px 0', fontSize: '0.95rem', color: '#fff' }}>{f.title}</h4>
                  <p style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: '#cbd5e1' }}>{f.description}</p>
                  {f.affected_systems && (
                    <div style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                      Systems: <code>{f.affected_systems}</code>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: MITRE ATT&CK Matrix */}
      {activeTab === 'mitre' && (
        <MitreMatrix
          coverage={coverage}
          incidentId={incident.id}
          currentMappings={incident.technique_mappings || []}
          allTechniques={allTechniques}
          onMapTechnique={async (techId, conf, summary) => {
            await incidentResponseApi.mapTechnique(incident.id, {
              technique_id_or_code: techId,
              mapping_confidence: conf,
              evidence_summary: summary,
            })
            loadIncident()
          }}
          onUnmapTechnique={async (techId) => {
            await incidentResponseApi.unmapTechnique(incident.id, techId)
            loadIncident()
          }}
        />
      )}

      {/* Tab 6: Response Simulator */}
      {activeTab === 'response' && (
        <ResponseSimulator
          actions={incident.response_actions || []}
          onProposeAction={async (data) => {
            await incidentResponseApi.proposeAction(incident.id, data)
            loadIncident()
          }}
          onExecuteAction={async (actionId) => {
            await incidentResponseApi.executeAction(incident.id, actionId)
            loadIncident()
          }}
          onRevertAction={async (actionId) => {
            await incidentResponseApi.revertAction(incident.id, actionId)
            loadIncident()
          }}
        />
      )}

      {/* Tab 7: Playbook Guide */}
      {activeTab === 'playbook' && (
        <div>
          {incident.playbook ? (
            <div>
              <div className="ir-filter-bar">
                <div>
                  <span className="ir-pill badge-cyan">{incident.playbook.playbook_id}</span>
                  <strong style={{ marginLeft: '10px', color: '#fff', fontSize: '1.1rem' }}>
                    {incident.playbook.title}
                  </strong>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                  <span className="ir-pill badge-high">Category: {incident.playbook.category}</span>
                </div>
              </div>

              {/* Checklist */}
              <div className="ir-kpi-card" style={{ marginBottom: '20px' }}>
                <h3 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: '#38bdf8' }}>
                  📋 Key Investigative Questions & Checklist
                </h3>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#cbd5e1', lineHeight: '1.7', fontSize: '0.9rem' }}>
                  {parsedChecklist.map((item: string, i: number) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* NIST SP 800-61 Phase Steps */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
                {Object.entries(parsedPhases).map(([phaseName, steps]: [string, any]) => (
                  <div key={phaseName} className="ir-kpi-card">
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '0.92rem', color: '#a5f3fc', textTransform: 'uppercase' }}>
                      {phaseName.replace(/_/g, ' ')}
                    </h4>
                    <ol style={{ margin: 0, paddingLeft: '20px', color: '#9ca3af', fontSize: '0.85rem', lineHeight: '1.5' }}>
                      {(steps as string[]).map((step: string, sIdx: number) => (
                        <li key={sIdx} style={{ marginBottom: '6px' }}>{step}</li>
                      ))}
                    </ol>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', background: '#111827', borderRadius: '8px' }}>
              <p style={{ color: '#9ca3af', marginBottom: '16px' }}>
                No standard playbook is attached to this incident yet.
              </p>
              <Link to="/soc/playbooks" className="ir-btn-primary">
                Browse Playbooks Catalog
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Tab 8: Executive Report */}
      {activeTab === 'report' && <ReportView report={report} loading={reportLoading} />}
    </div>
  )
}
