import React, { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ShieldAlert,
  CheckCircle2,
  Clock,
  Send,
  FileCode,
  CheckSquare,
  Square,
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { detectionApi } from '../../services/detectionApi'
import { threatHuntingApi } from '../../services/threatHuntingApi'
import type {
  DetectionAlertDetail,
  AlertStatus,
  AlertEvidenceItem,
} from '../../types/detection'
import '../../components/detection/detection.css'

export const AlertDetailsPage: React.FC = () => {
  const navigate = useNavigate()
  const { alertId } = useParams<{ alertId: string }>()
  const [alert, setAlert] = useState<DetectionAlertDetail | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Triage update form state
  const [selectedStatus, setSelectedStatus] = useState<AlertStatus>('NEW')
  const [statusReason, setStatusReason] = useState<string>('')
  const [updatingStatus, setUpdatingStatus] = useState<boolean>(false)

  // Note form state
  const [newNote, setNewNote] = useState<string>('')
  const [submittingNote, setSubmittingNote] = useState<boolean>(false)

  // Interactive investigation checklist state (local state for tracking completed steps)
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({})

  // Expanded evidence payload viewer
  const [expandedEvidenceId, setExpandedEvidenceId] = useState<number | null>(null)

  const fetchAlert = useCallback(async () => {
    if (!alertId) return
    setLoading(true)
    setError(null)
    try {
      const data = await detectionApi.getAlert(Number(alertId))
      setAlert(data)
      setSelectedStatus(data.status as AlertStatus)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load alert details')
    } finally {
      setLoading(false)
    }
  }, [alertId])

  useEffect(() => {
    fetchAlert()
  }, [fetchAlert])

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!alert) return
    setUpdatingStatus(true)
    try {
      const updated = await detectionApi.updateAlertStatus(alert.id, {
        status: selectedStatus,
        reason: statusReason.trim() || undefined,
      })
      setAlert(updated)
      setStatusReason('')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update alert status')
    } finally {
      setUpdatingStatus(false)
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!alert || !newNote.trim()) return
    setSubmittingNote(true)
    try {
      const noteItem = await detectionApi.addAlertNote(alert.id, newNote.trim())
      setAlert({
        ...alert,
        notes: [noteItem, ...alert.notes],
      })
      setNewNote('')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit investigation note')
    } finally {
      setSubmittingNote(false)
    }
  }

  const toggleStep = (index: number) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [index]: !prev[index],
    }))
  }

  const toggleEvidencePayload = (evidenceId: number) => {
    setExpandedEvidenceId((prev) => (prev === evidenceId ? null : evidenceId))
  }

  if (loading) {
    return (
      <div className="detection-container det-empty">
        <RefreshCw size={28} className="animate-spin inline-block mr-2 text-sky-400" />
        Loading alert and evidence details...
      </div>
    )
  }

  if (error || !alert) {
    return (
      <div className="detection-container">
        <Link to="/detection" className="flex items-center gap-1 text-sm text-slate-400 hover:text-sky-400 mb-4">
          <ArrowLeft size={16} /> Back to Detection Dashboard
        </Link>
        <div className="pcap-notice-banner danger">
          <AlertTriangle size={18} />
          <span>{error || 'Alert not found'}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="detection-container">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center justify-between text-sm text-slate-400">
        <Link to="/detection" className="flex items-center gap-1 hover:text-sky-400">
          <ArrowLeft size={16} /> Back to Detection Dashboard
        </Link>
        <div className="flex items-center gap-3">
          {alert.capture_id && (
            <Link
              to={`/packet-analysis/captures/${alert.capture_id}`}
              className="flex items-center gap-1 text-sky-400 hover:underline text-xs"
            >
              Inspect Capture #{alert.capture_id} <ExternalLink size={14} />
            </Link>
          )}
          <button
            onClick={async () => {
              try {
                const hunt = await threatHuntingApi.launchFromAlert({ alert_id: alert.id })
                navigate(`/threat-hunting/hunts/${hunt.id}`)
              } catch (e: any) {
                window.alert(`Error launching threat hunt: ${e.message}`)
              }
            }}
            className="flex items-center gap-1 text-xs px-2.5 py-1 bg-sky-600 hover:bg-sky-500 text-white rounded font-medium transition cursor-pointer"
          >
            <span>🔬</span> Launch Threat Hunt
          </button>
        </div>
      </div>

      {/* Main Alert Header */}
      <div className="det-card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex flex-col gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`sev-badge ${alert.severity}`}>{alert.severity}</span>
              <span className={`status-badge ${alert.status}`}>{alert.status.replace('_', ' ')}</span>
              <span className="conf-badge">Confidence: {alert.confidence}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {alert.category}
              </span>
              {alert.mitre_attack_id && (
                <span className="mitre-badge" title={alert.mitre_technique || ''}>
                  MITRE {alert.mitre_attack_id}
                </span>
              )}
            </div>

            <h1 className="text-2xl font-bold text-slate-100 mt-1">{alert.title}</h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
              <span className="font-mono">Rule ID: {alert.rule_code || `#${alert.rule_id}`}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock size={14} /> Created: {new Date(alert.created_at).toLocaleString()}
              </span>
              <span>•</span>
              <span>Packets Flagged: {alert.packet_count}</span>
            </div>
          </div>
        </div>

        {/* Network Flow Context */}
        <div className="det-flow-box">
          <div className="det-flow-node">
            <div className="text-xs text-slate-400 uppercase font-semibold">Source</div>
            <div className="text-sm font-mono font-bold text-sky-400">
              {alert.source_ip || 'Any IP'}
              {alert.source_port ? `:${alert.source_port}` : ''}
            </div>
          </div>

          <div className="text-center">
            <div className="det-flow-arrow">→</div>
            <div className="text-[11px] text-slate-400 uppercase font-semibold">
              {alert.protocol || 'IP'}
            </div>
          </div>

          <div className="det-flow-node">
            <div className="text-xs text-slate-400 uppercase font-semibold">Destination</div>
            <div className="text-sm font-mono font-bold text-amber-400">
              {alert.destination_ip || 'Any IP'}
              {alert.destination_port ? `:${alert.destination_port}` : ''}
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Explanation & Steps (Left) + Triage & Notes (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols) */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Neutral Educational Explanation */}
          <div className="det-card">
            <div className="det-card-title">
              <span className="flex items-center gap-2">
                <ShieldAlert size={18} className="text-sky-400" />
                Detection Analysis & Educational Context
              </span>
            </div>
            <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/40 p-4 rounded border border-slate-800">
              {alert.explanation}
            </div>
          </div>

          {/* Interactive SOC Investigation Steps Checklist */}
          {alert.investigation_steps && alert.investigation_steps.length > 0 && (
            <div className="det-card">
              <div className="det-card-title">
                <span className="flex items-center gap-2">
                  <CheckCircle2 size={18} className="text-emerald-400" />
                  Recommended SOC Investigation Steps
                </span>
                <span className="text-xs text-slate-400">
                  {Object.values(completedSteps).filter(Boolean).length} /{' '}
                  {alert.investigation_steps.length} Completed
                </span>
              </div>

              <div className="det-checklist">
                {alert.investigation_steps.map((step, idx) => {
                  const isChecked = !!completedSteps[idx]
                  return (
                    <div
                      key={idx}
                      className={`det-check-item ${isChecked ? 'completed' : ''}`}
                      onClick={() => toggleStep(idx)}
                    >
                      {isChecked ? (
                        <CheckSquare size={16} className="text-emerald-400 mt-0.5 shrink-0" />
                      ) : (
                        <Square size={16} className="text-slate-400 mt-0.5 shrink-0" />
                      )}
                      <span className="text-sm text-slate-200">
                        <strong>Step {idx + 1}:</strong> {step}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Concrete Packet & Flow Evidence Table */}
          <div className="det-card">
            <div className="det-card-title">
              <span className="flex items-center gap-2">
                <FileCode size={18} className="text-sky-400" />
                Linked Evidence ({alert.evidence.length} items)
              </span>
              <span className="text-xs text-slate-400">Deterministic telemetry artifacts</span>
            </div>

            {alert.evidence.length === 0 ? (
              <div className="det-empty">No telemetry evidence artifacts recorded for this alert.</div>
            ) : (
              <div className="det-table-wrapper">
                <table className="det-table">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Pkt #</th>
                      <th>Time</th>
                      <th>Protocol</th>
                      <th>Summary</th>
                      <th>Inspect</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alert.evidence.map((item: AlertEvidenceItem) => (
                      <React.Fragment key={item.id}>
                        <tr>
                          <td>
                            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                              {item.evidence_type}
                            </span>
                          </td>
                          <td className="font-mono text-xs">{item.packet_number ?? '-'}</td>
                          <td className="font-mono text-xs text-slate-400">
                            {item.timestamp ? `${item.timestamp.toFixed(3)}s` : '-'}
                          </td>
                          <td className="font-mono text-xs">{item.protocol ?? '-'}</td>
                          <td className="text-xs text-slate-200">{item.summary}</td>
                          <td>
                            {item.evidence_payload && Object.keys(item.evidence_payload).length > 0 ? (
                              <button
                                className="det-btn det-btn-secondary text-[11px] py-0.5 px-2"
                                onClick={() => toggleEvidencePayload(item.id)}
                              >
                                {expandedEvidenceId === item.id ? (
                                  <>
                                    <ChevronDown size={12} /> Hide
                                  </>
                                ) : (
                                  <>
                                    <ChevronRight size={12} /> View
                                  </>
                                )}
                              </button>
                            ) : (
                              <span className="text-xs text-slate-500">-</span>
                            )}
                          </td>
                        </tr>
                        {expandedEvidenceId === item.id && item.evidence_payload && (
                          <tr>
                            <td colSpan={6} className="bg-slate-950 p-3">
                              <pre className="text-xs font-mono text-emerald-400 overflow-x-auto max-h-48 p-2 bg-slate-900 rounded border border-slate-800">
                                {JSON.stringify(item.evidence_payload, null, 2)}
                              </pre>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Triage Controller & Notes Thread */}
        <div className="flex flex-col gap-6">
          {/* Triage Status Update Card */}
          <div className="det-card">
            <div className="det-card-title">
              <span>SOC Triage Lifecycle</span>
            </div>

            <form onSubmit={handleStatusUpdate} className="flex flex-col gap-3">
              <label className="text-xs font-semibold text-slate-300">Update Alert Status</label>
              <select
                className="det-select w-full"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as AlertStatus)}
              >
                <option value="NEW">New (Unreviewed)</option>
                <option value="ACKNOWLEDGED">Acknowledged (Queued)</option>
                <option value="INVESTIGATING">Investigating (In Progress)</option>
                <option value="CLOSED">Closed (Resolved / Verified)</option>
                <option value="FALSE_POSITIVE">False Positive (Benign Traffic)</option>
              </select>

              <label className="text-xs font-semibold text-slate-300">Triage Rationale / Reason</label>
              <textarea
                className="det-input w-full min-h-[70px] text-xs resize-y"
                placeholder="Document your findings or justification for status change..."
                value={statusReason}
                onChange={(e) => setStatusReason(e.target.value)}
              />

              <button
                type="submit"
                className="det-btn det-btn-primary w-full"
                disabled={updatingStatus}
              >
                {updatingStatus ? 'Updating Status...' : 'Apply Status Change'}
              </button>
            </form>

            {/* Status History Timeline */}
            {alert.status_history && alert.status_history.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                <span className="text-xs font-semibold text-slate-400 block mb-2">
                  Status Transition Audit History
                </span>
                <div className="flex flex-col gap-2">
                  {alert.status_history.map((hist) => (
                    <div key={hist.id} className="text-xs bg-slate-950/60 p-2 rounded border border-slate-800">
                      <div className="flex justify-between text-slate-400 text-[10px]">
                        <span>
                          {hist.old_status ? `${hist.old_status} → ` : ''}
                          <strong className="text-slate-200">{hist.new_status}</strong>
                        </span>
                        <span>{new Date(hist.created_at).toLocaleTimeString()}</span>
                      </div>
                      {hist.reason && <p className="text-slate-300 mt-1 italic">&quot;{hist.reason}&quot;</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Analyst Notes Thread */}
          <div className="det-card">
            <div className="det-card-title">
              <span>Analyst Notes ({alert.notes.length})</span>
            </div>

            <form onSubmit={handleAddNote} className="flex flex-col gap-2">
              <textarea
                className="det-input w-full min-h-[80px] text-xs resize-y"
                placeholder="Add observations, Wireshark filter syntax, or IOC details..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
              />
              <button
                type="submit"
                className="det-btn det-btn-secondary text-xs self-end"
                disabled={submittingNote || !newNote.trim()}
              >
                <Send size={12} />
                {submittingNote ? 'Saving...' : 'Add Note'}
              </button>
            </form>

            <div className="det-notes-list mt-2">
              {alert.notes.length === 0 ? (
                <div className="det-empty text-xs py-4">No notes recorded yet.</div>
              ) : (
                alert.notes.map((note) => (
                  <div key={note.id} className="det-note-item">
                    <div className="det-note-meta">
                      <span className="font-semibold text-slate-300">
                        {note.author_name || 'SOC Analyst'}
                      </span>
                      <span>{new Date(note.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-slate-200 whitespace-pre-wrap">{note.note}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
