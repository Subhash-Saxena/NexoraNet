import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ThreatHuntingNav } from '../components/threat_hunting/ThreatHuntingNav'
import '../components/threat_hunting/threat_hunting.css'
import { threatHuntingApi } from '../services/threatHuntingApi'
import type {
  EntityGraphResponse,
  EventCondition,
  HuntQueryResponse,
  HuntScoreResponse,
  HuntTimelineResponse,
  PivotResponse,
  ThreatHuntDetail,
} from '../types/threat_hunting'

type WorkspaceTab =
  | 'telemetry'
  | 'timeline'
  | 'graph'
  | 'pivot'
  | 'hypotheses'
  | 'evidence'
  | 'journal'

export const HuntWorkspacePage: React.FC = () => {
  const { huntId } = useParams<{ huntId: string }>()
  const numericHuntId = Number(huntId)

  const [hunt, setHunt] = useState<ThreatHuntDetail | null>(null)
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('telemetry')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Tab 1: Query & Telemetry State
  const [conditions, setConditions] = useState<EventCondition[]>([])
  const [conjunction, setConjunction] = useState<'AND' | 'OR'>('AND')
  const [searchText, setSearchText] = useState('')
  const [queryResult, setQueryResult] = useState<HuntQueryResponse | null>(null)
  const [queryLoading, setQueryLoading] = useState(false)
  const [inspectEvent, setInspectEvent] = useState<any | null>(null)

  // Tab 2: Timeline State
  const [timeline, setTimeline] = useState<HuntTimelineResponse | null>(null)
  const [timelineInterval, setTimelineInterval] = useState('minute')

  // Tab 3: Entity Graph State
  const [graphData, setGraphData] = useState<EntityGraphResponse | null>(null)
  const [graphFocus, setGraphFocus] = useState('')

  // Tab 4: Pivot Correlator State
  const [pivotType, setPivotType] = useState('IP')
  const [pivotVal, setPivotVal] = useState('')
  const [pivotResult, setPivotResult] = useState<PivotResponse | null>(null)
  const [pivotLoading, setPivotLoading] = useState(false)

  // Tab 5: Hypothesis State
  const [hypTitle, setHypTitle] = useState('')
  const [hypDesc, setHypDesc] = useState('')
  const [hypConfidence, setHypConfidence] = useState('MEDIUM')

  // Tab 6: Evidence & Findings Form State
  const [evDesc, setEvDesc] = useState('')
  const [evSourceId, setEvSourceId] = useState('')
  const [evType, setEvType] = useState('EVENT')
  const [evRelevance, setEvRelevance] = useState('SUPPORTING')
  const [evNote, setEvNote] = useState('')
  const [evHypId, setEvHypId] = useState<number | undefined>(undefined)

  const [findTitle, setFindTitle] = useState('')
  const [findDesc, setFindDesc] = useState('')
  const [findType, setFindType] = useState('ANOMALY')
  const [findMitigation, setFindMitigation] = useState('')

  // Tab 7: Notes & Conclusion State
  const [noteContent, setNoteContent] = useState('')
  const [conclusionText, setConclusionText] = useState('')
  const [conclusionDisp, setConclusionDisp] = useState('SUPPORTED')
  const [showScoreModal, setShowScoreModal] = useState(false)
  const [scoreData, setScoreData] = useState<HuntScoreResponse | null>(null)

  const loadHunt = async () => {
    try {
      setLoading(true)
      const data = await threatHuntingApi.getHuntDetail(numericHuntId)
      setHunt(data)
      if (data.initial_pivot_value) {
        setPivotVal(data.initial_pivot_value)
        if (data.initial_pivot_type) {
          setPivotType(data.initial_pivot_type)
        }
      }
      if (data.conclusion) {
        setConclusionText(data.conclusion)
      }
      if (data.conclusion_disposition) {
        setConclusionDisp(data.conclusion_disposition)
      }
      if (data.hypotheses && data.hypotheses.length > 0) {
        setEvHypId(data.hypotheses[0].id)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load threat hunt session')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (numericHuntId) {
      loadHunt()
    }
  }, [numericHuntId])

  // Run initial query when hunt is loaded
  useEffect(() => {
    if (hunt) {
      runQuery()
    }
  }, [hunt?.id])

  const runQuery = async () => {
    try {
      setQueryLoading(true)
      const res = await threatHuntingApi.queryTelemetry(numericHuntId, {
        conditions: conditions.length > 0 ? conditions : undefined,
        conjunction,
        search_text: searchText || undefined,
        limit: 50,
      })
      setQueryResult(res)
    } catch (err: any) {
      console.error(err)
    } finally {
      setQueryLoading(false)
    }
  }

  const loadTimeline = async (interval: string = 'minute') => {
    try {
      const res = await threatHuntingApi.getTimeline(numericHuntId, interval)
      setTimeline(res)
    } catch (err: any) {
      console.error(err)
    }
  }

  const loadGraph = async (focusVal?: string) => {
    try {
      const res = await threatHuntingApi.getEntityGraph(numericHuntId, focusVal || undefined)
      setGraphData(res)
    } catch (err: any) {
      console.error(err)
    }
  }

  const handlePivot = async (e?: React.FormEvent, customType?: string, customVal?: string) => {
    if (e) e.preventDefault()
    const targetType = customType || pivotType
    const targetVal = customVal || pivotVal
    if (!targetVal) return
    try {
      setPivotLoading(true)
      const res = await threatHuntingApi.pivotEntity(numericHuntId, {
        entity_type: targetType,
        entity_value: targetVal,
      })
      setPivotResult(res)
    } catch (err: any) {
      alert(`Pivot error: ${err.message}`)
    } finally {
      setPivotLoading(false)
    }
  }

  // Lifecycle actions
  const handleStart = async () => {
    await threatHuntingApi.startHunt(numericHuntId)
    loadHunt()
  }

  const handlePause = async () => {
    await threatHuntingApi.pauseHunt(numericHuntId)
    loadHunt()
  }

  // Hypothesis creation
  const handleCreateHypothesis = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!hypTitle || !hypDesc) return
    try {
      await threatHuntingApi.createHypothesis(numericHuntId, {
        title: hypTitle,
        description: hypDesc,
        confidence: hypConfidence,
      })
      setHypTitle('')
      setHypDesc('')
      loadHunt()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleUpdateHypStatus = async (hypId: number, newStatus: string, reason?: string) => {
    try {
      await threatHuntingApi.updateHypothesis(hypId, {
        status: newStatus,
        analyst_reasoning: reason,
      })
      loadHunt()
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Evidence creation
  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!evSourceId || !evDesc) return
    try {
      await threatHuntingApi.addEvidence(numericHuntId, {
        source_id: evSourceId,
        description: evDesc,
        evidence_type: evType,
        relevance: evRelevance,
        analyst_note: evNote || undefined,
        hypothesis_id: evHypId,
      })
      setEvSourceId('')
      setEvDesc('')
      setEvNote('')
      loadHunt()
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Finding creation
  const handleCreateFinding = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!findTitle || !findDesc) return
    try {
      await threatHuntingApi.createFinding(numericHuntId, {
        title: findTitle,
        description: findDesc,
        finding_type: findType,
        mitigation_recommendation: findMitigation || undefined,
      })
      setFindTitle('')
      setFindDesc('')
      setFindMitigation('')
      loadHunt()
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Note creation
  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!noteContent) return
    try {
      await threatHuntingApi.addNote(numericHuntId, { content: noteContent })
      setNoteContent('')
      loadHunt()
    } catch (err: any) {
      alert(err.message)
    }
  }

  // Conclusion submission
  const handleSubmitConclusion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!conclusionText) return
    try {
      const res = await threatHuntingApi.submitConclusion(numericHuntId, {
        conclusion: conclusionText,
        conclusion_disposition: conclusionDisp,
      })
      setScoreData(res)
      setShowScoreModal(true)
      loadHunt()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleOpenScore = async () => {
    try {
      const res = await threatHuntingApi.getHuntScore(numericHuntId)
      setScoreData(res)
      setShowScoreModal(true)
    } catch (err: any) {
      alert(err.message)
    }
  }

  if (loading) {
    return (
      <div className="threat-hunting-container">
        <div style={{ textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
          Loading Threat Hunt Session Workspace...
        </div>
      </div>
    )
  }

  if (error || !hunt) {
    return (
      <div className="threat-hunting-container">
        <div style={{ background: '#7f1d1d', color: '#fecaca', padding: '1.5rem', borderRadius: '0.5rem' }}>
          {error || 'Hunt not found'}
        </div>
        <Link to="/threat-hunting" className="btn-cyber-secondary" style={{ marginTop: '1rem', display: 'inline-block' }}>
          ← Return to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="threat-hunting-container">
      {/* Workspace Top Banner */}
      <div className="workspace-banner">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <span style={{ fontFamily: 'monospace', fontWeight: 700, color: '#38bdf8', fontSize: '1.1rem' }}>
              {hunt.hunt_id}
            </span>
            <span className={`hunt-badge badge-status-${hunt.status.toLowerCase()}`}>
              {hunt.status}
            </span>
            <span className={`hunt-badge badge-diff-${hunt.difficulty.toLowerCase()}`}>
              {hunt.difficulty}
            </span>
          </div>
          <h1 style={{ fontSize: '1.5rem', color: '#f8fafc', margin: '0 0 0.25rem 0' }}>
            {hunt.title}
          </h1>
          <div style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
            <strong>Objective:</strong> {hunt.objective}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {hunt.status !== 'RUNNING' && hunt.status !== 'COMPLETED' && (
            <button className="btn-cyber-primary" onClick={handleStart}>
              <span>▶</span> Start Hunt
            </button>
          )}
          {hunt.status === 'RUNNING' && (
            <button className="btn-cyber-secondary" onClick={handlePause}>
              <span>⏸</span> Pause
            </button>
          )}
          <button
            className="btn-cyber-success"
            onClick={() => {
              setActiveTab('journal')
            }}
          >
            <span>🏁</span> Conclude & Score
          </button>
          {hunt.score != null && (
            <button className="btn-cyber-secondary" onClick={handleOpenScore}>
              <span>🏆</span> Score ({hunt.score}/100)
            </button>
          )}
        </div>
      </div>

      <ThreatHuntingNav currentHuntId={hunt.id} huntCode={hunt.hunt_id} />

      {/* Workspace Tabs */}
      <div className="workspace-tabs">
        <button
          className={`workspace-tab-btn ${activeTab === 'telemetry' ? 'active' : ''}`}
          onClick={() => setActiveTab('telemetry')}
        >
          <span>🔍</span> Query & Telemetry
        </button>
        <button
          className={`workspace-tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('timeline')
            loadTimeline(timelineInterval)
          }}
        >
          <span>⏱️</span> Timeline
        </button>
        <button
          className={`workspace-tab-btn ${activeTab === 'graph' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('graph')
            loadGraph()
          }}
        >
          <span>🕸️</span> Entity Graph
        </button>
        <button
          className={`workspace-tab-btn ${activeTab === 'pivot' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('pivot')
            if (hunt.initial_pivot_value && !pivotResult) {
              handlePivot(undefined, hunt.initial_pivot_type || 'IP', hunt.initial_pivot_value)
            }
          }}
        >
          <span>🔄</span> Pivot Correlator
        </button>
        <button
          className={`workspace-tab-btn ${activeTab === 'hypotheses' ? 'active' : ''}`}
          onClick={() => setActiveTab('hypotheses')}
        >
          <span>💡</span> Hypotheses ({hunt.hypotheses.length})
        </button>
        <button
          className={`workspace-tab-btn ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          <span>📦</span> Evidence & Findings ({hunt.evidence.length})
        </button>
        <button
          className={`workspace-tab-btn ${activeTab === 'journal' ? 'active' : ''}`}
          onClick={() => setActiveTab('journal')}
        >
          <span>📝</span> Journal & Conclusion ({hunt.notes.length})
        </button>
      </div>

      {/* TAB 1: Query & Telemetry */}
      {activeTab === 'telemetry' && (
        <div style={{ marginTop: '1rem' }}>
          {/* Query Builder Panel */}
          <div className="query-builder-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '1rem' }}>
                ⚡ Structured Telemetry Query Builder
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Logic:</span>
                <button
                  type="button"
                  className={`btn-cyber-secondary ${conjunction === 'AND' ? 'active' : ''}`}
                  style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem', borderColor: conjunction === 'AND' ? '#38bdf8' : undefined }}
                  onClick={() => setConjunction(conjunction === 'AND' ? 'OR' : 'AND')}
                >
                  {conjunction}
                </button>
                <button
                  type="button"
                  className="btn-cyber-secondary"
                  style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }}
                  onClick={() => setConditions([...conditions, { field: 'protocol', operator: '==', value: 'DNS' }])}
                >
                  + Add Condition
                </button>
              </div>
            </div>

            {/* Conditions List */}
            {conditions.map((cond, idx) => (
              <div key={idx} className="query-row">
                <select
                  className="cyber-select"
                  value={cond.field}
                  onChange={(e) => {
                    const copy = [...conditions]
                    copy[idx].field = e.target.value
                    setConditions(copy)
                  }}
                >
                  <option value="protocol">Protocol</option>
                  <option value="source_ip">Source IP</option>
                  <option value="destination_ip">Destination IP</option>
                  <option value="destination_port">Destination Port</option>
                  <option value="source_port">Source Port</option>
                  <option value="domain">Domain</option>
                  <option value="event_type">Event Type</option>
                  <option value="severity">Severity</option>
                  <option value="summary">Summary</option>
                </select>

                <select
                  className="cyber-select"
                  value={cond.operator}
                  onChange={(e) => {
                    const copy = [...conditions]
                    copy[idx].operator = e.target.value
                    setConditions(copy)
                  }}
                >
                  <option value="==">equals (==)</option>
                  <option value="!=">not equals (!=)</option>
                  <option value="contains">contains</option>
                  <option value="startswith">starts with</option>
                  <option value=">">greater than (&gt;)</option>
                  <option value="<">less than (&lt;)</option>
                  <option value="is_not_null">is not null</option>
                </select>

                <input
                  type="text"
                  className="cyber-input"
                  style={{ flex: 1 }}
                  placeholder="Value..."
                  value={cond.value ?? ''}
                  onChange={(e) => {
                    const copy = [...conditions]
                    copy[idx].value = e.target.value
                    setConditions(copy)
                  }}
                />

                <button
                  type="button"
                  className="btn-cyber-danger"
                  onClick={() => setConditions(conditions.filter((_, i) => i !== idx))}
                >
                  ✕
                </button>
              </div>
            ))}

            {/* Free text search & Presets */}
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <input
                type="text"
                className="cyber-input"
                style={{ flex: 1, minWidth: '220px' }}
                placeholder="Free text keyword search (e.g., DNS, base64, 443)..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && runQuery()}
              />
              <button className="btn-cyber-primary" disabled={queryLoading} onClick={runQuery}>
                <span>⚡</span> {queryLoading ? 'Executing...' : 'Run Hunt Query'}
              </button>
            </div>

            {/* Quick Presets */}
            <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Quick Presets:</span>
              {[
                { label: 'DNS Queries', field: 'protocol', op: '==', val: 'DNS' },
                { label: 'Port 445 (SMB)', field: 'destination_port', op: '==', val: 445 },
                { label: 'High/Critical Severity', field: 'severity', op: '==', val: 'HIGH' },
                { label: 'C2 Polling (TLS)', field: 'protocol', op: '==', val: 'TLS' },
              ].map((p, pIdx) => (
                <button
                  key={pIdx}
                  type="button"
                  style={{ background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', borderRadius: '4px', fontSize: '0.75rem', padding: '0.2rem 0.5rem', cursor: 'pointer' }}
                  onClick={() => {
                    setConditions([{ field: p.field, operator: p.op, value: p.val }])
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Explanation Banner */}
          {queryResult && (
            <div style={{ background: '#0f172a', border: '1px solid #334155', padding: '0.6rem 1rem', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.8rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
              <span>{queryResult.explanation}</span>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>{queryResult.took_ms} ms</span>
            </div>
          )}

          {/* Telemetry Table */}
          <div className="telemetry-table-wrapper">
            <table className="cyber-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event ID</th>
                  <th>Type</th>
                  <th>Source</th>
                  <th>Destination</th>
                  <th>Protocol</th>
                  <th>Summary / Domain</th>
                  <th>Severity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {queryResult?.events.map((evt) => (
                  <tr key={evt.id}>
                    <td style={{ fontSize: '0.75rem', whiteSpace: 'nowrap', color: '#94a3b8' }}>
                      {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '—'}
                    </td>
                    <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontSize: '0.8rem' }}>
                      {evt.event_id}
                    </td>
                    <td>
                      <span style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>{evt.event_type}</span>
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {evt.source_ip || '—'}{evt.source_port ? `:${evt.source_port}` : ''}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {evt.destination_ip || '—'}{evt.destination_port ? `:${evt.destination_port}` : ''}
                    </td>
                    <td>
                      <span className="scenario-tag" style={{ fontSize: '0.7rem' }}>
                        {evt.protocol || 'IP'}
                      </span>
                    </td>
                    <td style={{ maxWidth: '320px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {evt.domain ? (
                        <strong style={{ color: '#f8fafc' }}>{evt.domain}</strong>
                      ) : (
                        evt.summary
                      )}
                    </td>
                    <td>
                      {evt.severity ? (
                        <span
                          className="hunt-badge"
                          style={{
                            background: evt.severity === 'CRITICAL' || evt.severity === 'HIGH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.2)',
                            color: evt.severity === 'CRITICAL' || evt.severity === 'HIGH' ? '#f87171' : '#38bdf8',
                            fontSize: '0.7rem',
                          }}
                        >
                          {evt.severity}
                        </span>
                      ) : (
                        <span style={{ color: '#64748b' }}>INFO</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        <button
                          className="btn-cyber-secondary"
                          style={{ padding: '0.2rem 0.4rem', fontSize: '0.75rem' }}
                          onClick={() => setInspectEvent(evt)}
                        >
                          Inspect
                        </button>
                        <button
                          className="btn-cyber-secondary"
                          style={{ padding: '0.2rem 0.4rem', fontSize: '0.75rem' }}
                          onClick={() => {
                            setEvSourceId(evt.event_id)
                            setEvDesc(evt.summary || `Event ${evt.event_id}`)
                            setEvType('EVENT')
                            setActiveTab('evidence')
                          }}
                        >
                          + Evidence
                        </button>
                        {evt.source_ip && (
                          <button
                            className="btn-cyber-secondary"
                            style={{ padding: '0.2rem 0.4rem', fontSize: '0.75rem' }}
                            onClick={() => {
                              setPivotType('IP')
                              setPivotVal(evt.source_ip!)
                              setActiveTab('pivot')
                              handlePivot(undefined, 'IP', evt.source_ip!)
                            }}
                          >
                            Pivot
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Inspect Event Modal / Drawer */}
          {inspectEvent && (
            <div className="score-modal-overlay">
              <div className="score-modal-card" style={{ maxWidth: '700px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#f8fafc' }}>Event Inspection: {inspectEvent.event_id}</h3>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Type: {inspectEvent.event_type} | Protocol: {inspectEvent.protocol}</div>
                  </div>
                  <button className="btn-cyber-danger" onClick={() => setInspectEvent(null)}>✕</button>
                </div>

                <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.85rem' }}>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <span style={{ color: '#94a3b8' }}>Source: </span>
                    <strong style={{ color: '#38bdf8' }}>{inspectEvent.source_ip}:{inspectEvent.source_port}</strong>
                    <span style={{ color: '#94a3b8' }}> → Destination: </span>
                    <strong style={{ color: '#38bdf8' }}>{inspectEvent.destination_ip}:{inspectEvent.destination_port}</strong>
                  </div>
                  {inspectEvent.domain && (
                    <div style={{ marginBottom: '0.5rem' }}>
                      <span style={{ color: '#94a3b8' }}>Domain: </span>
                      <strong style={{ color: '#facc15' }}>{inspectEvent.domain}</strong>
                    </div>
                  )}
                  <div>
                    <span style={{ color: '#94a3b8' }}>Summary: </span>
                    <span>{inspectEvent.summary}</span>
                  </div>
                </div>

                {inspectEvent.payload_preview && (
                  <div style={{ marginBottom: '1.25rem' }}>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>Payload / Inspection Details:</div>
                    <pre style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '0.5rem', color: '#34d399', fontSize: '0.75rem', overflowX: 'auto', maxHeight: '180px' }}>
                      {inspectEvent.payload_preview}
                    </pre>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <button
                    className="btn-cyber-primary"
                    onClick={() => {
                      setEvSourceId(inspectEvent.event_id)
                      setEvDesc(inspectEvent.summary || `Event ${inspectEvent.event_id}`)
                      setInspectEvent(null)
                      setActiveTab('evidence')
                    }}
                  >
                    + Bind as Evidence
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Timeline Analysis */}
      {activeTab === 'timeline' && (
        <div style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.2rem', color: '#f8fafc', margin: 0 }}>
              ⏱️ Chronological Telemetry Density & Milestones
            </h2>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Bucket Interval:</span>
              <select
                className="cyber-select"
                value={timelineInterval}
                onChange={(e) => {
                  setTimelineInterval(e.target.value)
                  loadTimeline(e.target.value)
                }}
              >
                <option value="minute">Minute (5-min intervals)</option>
                <option value="hour">Hourly</option>
                <option value="day">Daily</option>
              </select>
            </div>
          </div>

          {timeline ? (
            <>
              {/* Density Bar Chart */}
              <div className="timeline-bar-chart">
                {timeline.buckets.map((b, idx) => {
                  const maxCount = Math.max(...timeline.buckets.map((x) => x.event_count), 1)
                  const heightPct = Math.max(10, Math.round((b.event_count / maxCount) * 100))
                  return (
                    <div key={idx} className="timeline-bar-col" title={`${b.time_slot}: ${b.event_count} events (${b.alert_count} alerts)`}>
                      <div
                        className={`timeline-bar ${b.alert_count > 0 ? 'has-alerts' : ''}`}
                        style={{ height: `${heightPct}%` }}
                      />
                      <span className="timeline-bar-label">{b.time_slot.split(' ')[1] || b.time_slot}</span>
                    </div>
                  )
                })}
              </div>

              {/* Milestones List */}
              <h3 style={{ fontSize: '1rem', color: '#f8fafc', marginBottom: '0.75rem' }}>
                🚨 Critical Security Milestones & Alert Triggers
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {timeline.milestones.map((m, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '0.5rem',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#38bdf8' }}>
                          {new Date(m.timestamp).toLocaleTimeString()}
                        </span>
                        <span className="hunt-badge" style={{ background: '#7f1d1d', color: '#fecaca', fontSize: '0.7rem' }}>
                          {m.severity}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{m.event_type}</span>
                      </div>
                      <div style={{ color: '#f8fafc', fontSize: '0.875rem' }}>{m.summary}</div>
                    </div>
                    {m.source_ip && (
                      <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#94a3b8' }}>
                        {m.source_ip} → {m.destination_ip}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ color: '#94a3b8' }}>Loading timeline analytics...</div>
          )}
        </div>
      )}

      {/* TAB 3: Entity Relationship Graph */}
      {activeTab === 'graph' && (
        <div style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h2 style={{ fontSize: '1.2rem', color: '#f8fafc', margin: 0 }}>
              🕸️ Bounded Entity Relationship Graph
            </h2>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <input
                type="text"
                className="cyber-input"
                placeholder="Filter by node (e.g., 192.168.1.105)..."
                value={graphFocus}
                onChange={(e) => setGraphFocus(e.target.value)}
              />
              <button className="btn-cyber-primary" onClick={() => loadGraph(graphFocus)}>
                Filter Graph
              </button>
            </div>
          </div>

          <div className="graph-container">
            <div>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                Discovered Entities ({graphData?.nodes.length ?? 0} nodes):
              </div>
              <div className="graph-nodes-grid">
                {graphData?.nodes.map((n) => (
                  <div
                    key={n.id}
                    className={`graph-node-pill graph-node-${n.type.toLowerCase()}`}
                    onClick={() => {
                      setPivotType(n.type === 'IP' ? 'IP' : 'DOMAIN')
                      setPivotVal(n.label)
                      setActiveTab('pivot')
                      handlePivot(undefined, n.type === 'IP' ? 'IP' : 'DOMAIN', n.label)
                    }}
                  >
                    <span>{n.type === 'IP' ? '💻' : n.type === 'DOMAIN' ? '🌐' : '🚨'}</span>
                    <span>{n.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginTop: '1.5rem' }}>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                Correlated Interactions & Connections ({graphData?.edges.length ?? 0} edges):
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '0.75rem' }}>
                {graphData?.edges.map((e, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '0.5rem',
                      padding: '0.6rem 0.75rem',
                      fontSize: '0.8rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <span style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{e.source.replace(/^(ip:|domain:|alert:|ioc:)/, '')}</span>
                    <span style={{ color: '#94a3b8', fontSize: '0.75rem', background: '#0f172a', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                      {e.relationship} ({e.label})
                    </span>
                    <span style={{ color: '#facc15', fontFamily: 'monospace' }}>{e.target.replace(/^(ip:|domain:|alert:|ioc:)/, '')}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Pivot Correlator */}
      {activeTab === 'pivot' && (
        <div style={{ marginTop: '1.5rem' }}>
          <h2 style={{ fontSize: '1.2rem', color: '#f8fafc', marginBottom: '1rem' }}>
            🔄 Cross-Entity Pivot Investigation Engine
          </h2>

          <form onSubmit={(e) => handlePivot(e)} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            <select className="cyber-select" value={pivotType} onChange={(e) => setPivotType(e.target.value)}>
              <option value="IP">IP Address</option>
              <option value="DOMAIN">Domain Name</option>
              <option value="PORT">Port Number</option>
            </select>
            <input
              type="text"
              required
              className="cyber-input"
              style={{ flex: 1, minWidth: '220px' }}
              placeholder="e.g., 192.168.1.105 or corp-sync.test"
              value={pivotVal}
              onChange={(e) => setPivotVal(e.target.value)}
            />
            <button type="submit" className="btn-cyber-primary" disabled={pivotLoading}>
              <span>🔄</span> {pivotLoading ? 'Correlating...' : 'Correlate Entity'}
            </button>
          </form>

          {pivotResult && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <div>
                <h3 style={{ fontSize: '1rem', color: '#f8fafc', marginBottom: '0.75rem' }}>
                  Matched Telemetry Events ({pivotResult.matched_events_count})
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '400px', overflowY: 'auto' }}>
                  {pivotResult.matched_events.map((evt) => (
                    <div key={evt.event_id} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.6rem 0.75rem', fontSize: '0.8rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#38bdf8', marginBottom: '0.2rem' }}>
                        <span>{evt.event_id}</span>
                        <span>{evt.protocol}</span>
                      </div>
                      <div style={{ color: '#cbd5e1' }}>{evt.summary}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 style={{ fontSize: '1rem', color: '#f8fafc', marginBottom: '0.75rem' }}>
                  Suggested SOC Investigative Inquiries
                </h3>
                <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1.5rem' }}>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.85rem', lineHeight: '1.8' }}>
                    {pivotResult.suggested_questions.map((q, idx) => (
                      <li key={idx}>{q}</li>
                    ))}
                  </ul>
                </div>

                <h3 style={{ fontSize: '1rem', color: '#f8fafc', marginBottom: '0.75rem' }}>
                  Correlated Indicators ({pivotResult.matched_iocs.length}) & Alerts ({pivotResult.matched_alerts.length})
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {pivotResult.matched_iocs.map((ioc) => (
                    <div key={ioc.id} style={{ background: '#0f172a', border: '1px solid #f59e0b', borderRadius: '0.5rem', padding: '0.5rem 0.75rem', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#facc15' }}>IOC: {ioc.value}</span>
                      <span className="hunt-badge" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' }}>{ioc.classification}</span>
                    </div>
                  ))}
                  {pivotResult.matched_alerts.map((al) => (
                    <div key={al.id} style={{ background: '#0f172a', border: '1px solid #ef4444', borderRadius: '0.5rem', padding: '0.5rem 0.75rem', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#f87171' }}>Alert: {al.title}</span>
                      <span className="hunt-badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171' }}>{al.severity}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Hypotheses Workbench */}
      {activeTab === 'hypotheses' && (
        <div style={{ marginTop: '1.5rem' }}>
          {/* New Hypothesis Form */}
          <div className="query-builder-panel" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#f8fafc', fontSize: '1rem' }}>
              💡 Formulate Analytical Hypothesis
            </h3>
            <form onSubmit={handleCreateHypothesis}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 140px', gap: '1rem', marginBottom: '0.75rem' }}>
                <input
                  type="text"
                  required
                  className="cyber-input"
                  placeholder="Hypothesis statement (e.g. Host 192.168.1.105 is exfiltrating data via DNS)..."
                  value={hypTitle}
                  onChange={(e) => setHypTitle(e.target.value)}
                />
                <select className="cyber-select" value={hypConfidence} onChange={(e) => setHypConfidence(e.target.value)}>
                  <option value="LOW">Confidence: LOW</option>
                  <option value="MEDIUM">Confidence: MEDIUM</option>
                  <option value="HIGH">Confidence: HIGH</option>
                </select>
              </div>
              <textarea
                required
                rows={2}
                className="cyber-input"
                style={{ width: '100%', marginBottom: '0.75rem' }}
                placeholder="What observable telemetry or condition will validate or refute this hypothesis?"
                value={hypDesc}
                onChange={(e) => setHypDesc(e.target.value)}
              />
              <button type="submit" className="btn-cyber-primary">
                <span>+</span> Add Hypothesis to Hunt
              </button>
            </form>
          </div>

          {/* List of Hypotheses */}
          <div>
            <h3 style={{ color: '#f8fafc', fontSize: '1.1rem', marginBottom: '1rem' }}>
              Active Hypotheses Under Investigation ({hunt.hypotheses.length})
            </h3>
            {hunt.hypotheses.map((h) => (
              <div key={h.id} className={`hypothesis-card status-${h.status.toLowerCase()}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <div>
                    <h4 style={{ margin: '0 0 0.25rem 0', color: '#f8fafc', fontSize: '1.05rem' }}>{h.title}</h4>
                    <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>{h.description}</div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className="scenario-tag" style={{ borderColor: '#64748b' }}>
                      Confidence: {h.confidence}
                    </span>
                    <select
                      className="cyber-select"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
                      value={h.status}
                      onChange={(e) => handleUpdateHypStatus(h.id, e.target.value, h.analyst_reasoning || '')}
                    >
                      <option value="OPEN">OPEN</option>
                      <option value="SUPPORTED">SUPPORTED</option>
                      <option value="NOT_SUPPORTED">NOT_SUPPORTED</option>
                      <option value="INCONCLUSIVE">INCONCLUSIVE</option>
                    </select>
                  </div>
                </div>

                {/* Analyst Reasoning */}
                <div style={{ marginTop: '0.75rem' }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>
                    Analyst Validation Rationale:
                  </label>
                  <input
                    type="text"
                    className="cyber-input"
                    style={{ width: '100%', fontSize: '0.8rem' }}
                    defaultValue={h.analyst_reasoning || ''}
                    placeholder="Document your findings and testing outcome..."
                    onBlur={(e) => handleUpdateHypStatus(h.id, h.status, e.target.value)}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 6: Evidence & Findings */}
      {activeTab === 'evidence' && (
        <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Evidence Vault */}
          <div>
            <h3 style={{ color: '#f8fafc', fontSize: '1.1rem', marginBottom: '1rem' }}>
              📦 Evidence Vault ({hunt.evidence.length})
            </h3>

            {/* Bind Evidence Form */}
            <div className="query-builder-panel" style={{ marginBottom: '1rem' }}>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                Add Corroborating Artifact
              </div>
              <form onSubmit={handleAddEvidence}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    required
                    className="cyber-input"
                    placeholder="Source ID (e.g. EVT-001)"
                    value={evSourceId}
                    onChange={(e) => setEvSourceId(e.target.value)}
                  />
                  <select className="cyber-select" value={evRelevance} onChange={(e) => setEvRelevance(e.target.value)}>
                    <option value="SUPPORTING">SUPPORTING</option>
                    <option value="CONTRADICTING">CONTRADICTING</option>
                    <option value="CONTEXT">CONTEXT</option>
                  </select>
                </div>
                <input
                  type="text"
                  required
                  className="cyber-input"
                  style={{ width: '100%', marginBottom: '0.5rem' }}
                  placeholder="Artifact Description"
                  value={evDesc}
                  onChange={(e) => setEvDesc(e.target.value)}
                />
                <input
                  type="text"
                  className="cyber-input"
                  style={{ width: '100%', marginBottom: '0.75rem' }}
                  placeholder="Analyst Annotation / Relevance Note"
                  value={evNote}
                  onChange={(e) => setEvNote(e.target.value)}
                />
                <button type="submit" className="btn-cyber-primary" style={{ width: '100%', justifyContent: 'center' }}>
                  Bind Evidence Item
                </button>
              </form>
            </div>

            {/* Evidence Items */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {hunt.evidence.map((ev) => (
                <div
                  key={ev.id}
                  style={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '0.5rem',
                    padding: '0.75rem 1rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                    <span style={{ fontFamily: 'monospace', color: '#38bdf8', fontSize: '0.8rem' }}>
                      {ev.source_id}
                    </span>
                    <span className={`hunt-badge badge-rel-${ev.relevance.toLowerCase()}`}>
                      {ev.relevance}
                    </span>
                  </div>
                  <div style={{ color: '#f8fafc', fontSize: '0.875rem' }}>{ev.description}</div>
                  {ev.analyst_note && (
                    <div style={{ fontSize: '0.8rem', color: '#34d399', marginTop: '0.35rem', fontStyle: 'italic' }}>
                      Note: {ev.analyst_note}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Documented Findings */}
          <div>
            <h3 style={{ color: '#f8fafc', fontSize: '1.1rem', marginBottom: '1rem' }}>
              🎯 Security Findings ({hunt.findings.length})
            </h3>

            {/* Log Finding Form */}
            <div className="query-builder-panel" style={{ marginBottom: '1rem' }}>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                Document New Finding
              </div>
              <form onSubmit={handleCreateFinding}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 140px', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    required
                    className="cyber-input"
                    placeholder="Finding Title"
                    value={findTitle}
                    onChange={(e) => setFindTitle(e.target.value)}
                  />
                  <select className="cyber-select" value={findType} onChange={(e) => setFindType(e.target.value)}>
                    <option value="ANOMALY">ANOMALY</option>
                    <option value="PATTERN">PATTERN</option>
                    <option value="DETECTION_GAP">DETECTION GAP</option>
                    <option value="NETWORK_BEHAVIOR">NETWORK BEHAVIOR</option>
                  </select>
                </div>
                <textarea
                  required
                  rows={2}
                  className="cyber-input"
                  style={{ width: '100%', marginBottom: '0.5rem' }}
                  placeholder="Detailed description of pattern or gap..."
                  value={findDesc}
                  onChange={(e) => setFindDesc(e.target.value)}
                />
                <input
                  type="text"
                  className="cyber-input"
                  style={{ width: '100%', marginBottom: '0.75rem' }}
                  placeholder="Defensive Mitigation Recommendation"
                  value={findMitigation}
                  onChange={(e) => setFindMitigation(e.target.value)}
                />
                <button type="submit" className="btn-cyber-primary" style={{ width: '100%', justifyContent: 'center' }}>
                  Log Finding
                </button>
              </form>
            </div>

            {/* Findings List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {hunt.findings.map((f) => (
                <div key={f.id} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.75rem 1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                    <strong style={{ color: '#f8fafc' }}>{f.title}</strong>
                    <span className="scenario-tag">{f.finding_type}</span>
                  </div>
                  <div style={{ color: '#cbd5e1', fontSize: '0.85rem' }}>{f.description}</div>
                  {f.mitigation_recommendation && (
                    <div style={{ marginTop: '0.5rem', background: '#0f172a', padding: '0.4rem 0.6rem', borderRadius: '4px', borderLeft: '3px solid #10b981', fontSize: '0.8rem', color: '#a7f3d0' }}>
                      <strong>Mitigation:</strong> {f.mitigation_recommendation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 7: Analyst Journal & Final Conclusion */}
      {activeTab === 'journal' && (
        <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Analyst Journal */}
          <div>
            <h3 style={{ color: '#f8fafc', fontSize: '1.1rem', marginBottom: '1rem' }}>
              📝 Analyst Journal & Pivot Log ({hunt.notes.length})
            </h3>
            <form onSubmit={handleAddNote} style={{ marginBottom: '1.5rem' }}>
              <textarea
                required
                rows={3}
                className="cyber-input"
                style={{ width: '100%', marginBottom: '0.5rem' }}
                placeholder="Record live analytical observations, pivot notes, or investigative hypotheses..."
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
              />
              <button type="submit" className="btn-cyber-primary">
                Add Journal Entry
              </button>
            </form>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {hunt.notes.map((n) => (
                <div key={n.id} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.75rem 1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
                    <span>By {n.author_name}</span>
                    <span>{new Date(n.created_at).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ color: '#f8fafc', fontSize: '0.875rem', lineHeight: '1.5' }}>{n.content}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Final Conclusion Form */}
          <div>
            <h3 style={{ color: '#f8fafc', fontSize: '1.1rem', marginBottom: '1rem' }}>
              🏁 Conclude Investigation & Evaluate Training Score
            </h3>
            <div className="query-builder-panel">
              <form onSubmit={handleSubmitConclusion}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Final Disposition *
                  </label>
                  <select
                    className="cyber-select"
                    style={{ width: '100%' }}
                    value={conclusionDisp}
                    onChange={(e) => setConclusionDisp(e.target.value)}
                  >
                    <option value="SUPPORTED">SUPPORTED (Malicious activity confirmed)</option>
                    <option value="NOT_SUPPORTED">NOT_SUPPORTED (Benign or false positive)</option>
                    <option value="INCONCLUSIVE">INCONCLUSIVE (Data insufficient to prove/disprove)</option>
                  </select>
                </div>

                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Executive Conclusion & Analytical Justification *
                  </label>
                  <textarea
                    required
                    rows={6}
                    className="cyber-input"
                    style={{ width: '100%' }}
                    placeholder="Provide detailed justification explaining how collected evidence supports or refutes your hypotheses..."
                    value={conclusionText}
                    onChange={(e) => setConclusionText(e.target.value)}
                  />
                </div>

                <button
                  type="submit"
                  className="btn-cyber-success"
                  style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
                >
                  <span>🏆</span> Submit Conclusion & Evaluate Training Score
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Score Modal */}
      {showScoreModal && scoreData && (
        <div className="score-modal-overlay">
          <div className="score-modal-card">
            <h2 style={{ textAlign: 'center', color: '#f8fafc', marginTop: 0 }}>
              Threat Hunt Evaluation Score
            </h2>

            <div className={`score-grade-circle grade-${scoreData.grade.toLowerCase()}`}>
              {scoreData.grade}
            </div>

            <div style={{ textAlign: 'center', fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1.5rem' }}>
              {scoreData.total_score} / 100 Points
            </div>

            {/* Rubric Dimensions */}
            <div style={{ marginBottom: '1.5rem' }}>
              {[
                { label: '1. Evidence Quality & Breadth', data: scoreData.breakdown.evidence_quality },
                { label: '2. Correlation & Pivoting', data: scoreData.breakdown.correlation_and_pivoting },
                { label: '3. Hypothesis Testing', data: scoreData.breakdown.hypothesis_testing },
                { label: '4. Documentation & Findings', data: scoreData.breakdown.documentation_and_findings },
                { label: '5. Conclusion Soundness', data: scoreData.breakdown.conclusion_soundness },
              ].map((dim, idx) => (
                <div key={idx} style={{ marginBottom: '0.75rem' }}>
                  <div className="score-bar-row">
                    <span className="score-bar-label">{dim.label}</span>
                    <div className="score-bar-track">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${((dim.data?.score ?? 0) / (dim.data?.max ?? 20)) * 100}%` }}
                      />
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#38bdf8', minWidth: '45px', textAlign: 'right' }}>
                      {dim.data?.score ?? 0} / {dim.data?.max ?? 20}
                    </span>
                  </div>
                  {dim.data?.feedback && dim.data.feedback.length > 0 && (
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginLeft: '180px' }}>
                      {dim.data.feedback.join(' ')}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <button className="btn-cyber-primary" onClick={() => setShowScoreModal(false)}>
                Continue Investigation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
