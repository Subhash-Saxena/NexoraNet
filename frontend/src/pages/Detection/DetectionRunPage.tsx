import React, { useState, useEffect } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import {
  Play,
  ArrowLeft,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Sliders,
  FileCheck2,
} from 'lucide-react'
import { detectionApi } from '../../services/detectionApi'
import { pcapApi } from '../../services/pcapApi'
import type { DetectionRule, DetectionRunResponse } from '../../types/detection'
import type { CaptureSummary } from '../../types/pcap'
import '../../components/detection/detection.css'

export const DetectionRunPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const initialCaptureId = searchParams.get('captureId')

  const [captures, setCaptures] = useState<CaptureSummary[]>([])
  const [rules, setRules] = useState<DetectionRule[]>([])
  const [selectedCaptureId, setSelectedCaptureId] = useState<number | ''>(
    initialCaptureId ? parseInt(initialCaptureId, 10) : ''
  )
  const [useAllRules, setUseAllRules] = useState<boolean>(true)
  const [selectedRuleIds, setSelectedRuleIds] = useState<string[]>([])
  
  const [loading, setLoading] = useState<boolean>(true)
  const [running, setRunning] = useState<boolean>(false)
  const [runResult, setRunResult] = useState<DetectionRunResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadPrerequisites() {
      setLoading(true)
      try {
        const [caps, ruleList] = await Promise.all([
          pcapApi.listCaptures(),
          detectionApi.listRules(),
        ])
        setCaptures(caps.filter((c) => c.status === 'READY'))
        setRules(ruleList)
        if (!selectedCaptureId && caps.length > 0) {
          const readyCap = caps.find((c) => c.status === 'READY')
          if (readyCap) setSelectedCaptureId(readyCap.id)
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load captures or rules')
      } finally {
        setLoading(false)
      }
    }
    loadPrerequisites()
  }, [])

  const handleToggleRule = (ruleId: string) => {
    setSelectedRuleIds((prev) =>
      prev.includes(ruleId) ? prev.filter((r) => r !== ruleId) : [...prev, ruleId]
    )
  }

  const handleExecuteRun = async () => {
    if (!selectedCaptureId) {
      setError('Please select a parsed PCAP capture to analyze.')
      return
    }

    setRunning(true)
    setError(null)
    setRunResult(null)

    try {
      const payload = {
        source_type: 'PCAP' as const,
        capture_id: Number(selectedCaptureId),
        rule_ids: useAllRules ? undefined : selectedRuleIds,
      }
      const result = await detectionApi.createRun(payload)
      setRunResult(result)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Detection run failed')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="detection-container">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Link to="/detection" className="flex items-center gap-1 hover:text-sky-400">
          <ArrowLeft size={16} /> Back to Detection Dashboard
        </Link>
      </div>

      <div className="detection-header">
        <div className="detection-header-title">
          <Play size={28} className="text-sky-400" />
          <div>
            <h1>Execute Offline Detection Run</h1>
            <p className="text-sm text-slate-400">
              Run deterministic detection rules over parsed packet captures to identify noteworthy behaviors.
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="pcap-notice-banner danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="det-card det-empty">
          <RefreshCw size={24} className="animate-spin inline-block mr-2" />
          Loading captures and detection rule set...
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Form */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Step 1: Select Capture */}
            <div className="det-card">
              <div className="det-card-title">
                <span className="flex items-center gap-2">
                  <FileCheck2 size={18} className="text-sky-400" />
                  1. Select Target PCAP Capture
                </span>
                <span className="text-xs text-slate-400">Telemetry Source</span>
              </div>

              {captures.length === 0 ? (
                <div className="det-empty">
                  No parsed captures available. Please upload a PCAP in the{' '}
                  <Link to="/packet-analysis" className="text-sky-400 underline">
                    Packet Analysis engine
                  </Link>{' '}
                  first.
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-300">
                    Available Offline Captures
                  </label>
                  <select
                    className="det-select w-full"
                    value={selectedCaptureId}
                    onChange={(e) => setSelectedCaptureId(Number(e.target.value))}
                  >
                    {captures.map((cap) => (
                      <option key={cap.id} value={cap.id}>
                        #{cap.id} — {cap.name} ({cap.packet_count} packets, {cap.format.toUpperCase()})
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-slate-400 mt-1">
                    NexoraNet scans the indexed packet metadata offline. No raw sockets or external network
                    connections are initialized.
                  </p>
                </div>
              )}
            </div>

            {/* Step 2: Select Rules */}
            <div className="det-card">
              <div className="det-card-title">
                <span className="flex items-center gap-2">
                  <Sliders size={18} className="text-sky-400" />
                  2. Detection Rule Scope
                </span>
                <span className="text-xs text-slate-400">{rules.length} Rules in Catalog</span>
              </div>

              <div className="flex flex-col gap-3">
                <label className="flex items-center gap-2 cursor-pointer text-sm">
                  <input
                    type="radio"
                    name="ruleScope"
                    checked={useAllRules}
                    onChange={() => setUseAllRules(true)}
                    className="accent-sky-500"
                  />
                  <span>Run all enabled detection rules (Recommended for full triage)</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-sm">
                  <input
                    type="radio"
                    name="ruleScope"
                    checked={!useAllRules}
                    onChange={() => setUseAllRules(false)}
                    className="accent-sky-500"
                  />
                  <span>Select specific rules manually</span>
                </label>

                {!useAllRules && (
                  <div className="max-h-60 overflow-y-auto border border-slate-800 rounded p-3 flex flex-col gap-2 bg-slate-950/40">
                    {rules.map((rule) => (
                      <label
                        key={rule.rule_id}
                        className="flex items-start gap-2 text-xs cursor-pointer hover:bg-slate-900/50 p-1.5 rounded"
                      >
                        <input
                          type="checkbox"
                          checked={selectedRuleIds.includes(rule.rule_id)}
                          onChange={() => handleToggleRule(rule.rule_id)}
                          className="mt-0.5 accent-sky-500"
                        />
                        <div>
                          <div className="font-semibold text-slate-200">
                            {rule.rule_id} — {rule.name}
                          </div>
                          <div className="text-slate-400 text-[11px]">{rule.description}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Action Button */}
            <div>
              <button
                className="det-btn det-btn-primary w-full py-3 text-base"
                onClick={handleExecuteRun}
                disabled={running || !selectedCaptureId || (!useAllRules && selectedRuleIds.length === 0)}
              >
                {running ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    Executing Detection Rules...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Launch Detection Run
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Sidebar */}
          <div className="flex flex-col gap-6">
            <div className="det-card">
              <div className="det-card-title">
                <span>Detection Results</span>
                {runResult && <CheckCircle size={18} className="text-emerald-400" />}
              </div>

              {!runResult && !running && (
                <div className="det-empty">
                  Select a capture and click &quot;Launch Detection Run&quot; to inspect rule matches.
                </div>
              )}

              {running && (
                <div className="det-empty">
                  <RefreshCw size={24} className="animate-spin inline-block mb-2 text-sky-400" />
                  <p className="text-sm">Evaluating feature aggregation & signatures...</p>
                </div>
              )}

              {runResult && (
                <div className="flex flex-col gap-4">
                  <div className="p-3 bg-emerald-950/20 border border-emerald-800/40 rounded flex items-center gap-2 text-emerald-400 text-sm">
                    <ShieldCheck size={18} />
                    <span>Detection Run #{runResult.id} Completed!</span>
                  </div>

                  <div className="flex flex-col gap-2 text-sm">
                    <div className="flex justify-between py-1 border-b border-slate-800">
                      <span className="text-slate-400">Packets Analyzed:</span>
                      <span className="font-mono font-bold text-slate-200">
                        {runResult.packets_analyzed}
                      </span>
                    </div>

                    <div className="flex justify-between py-1 border-b border-slate-800">
                      <span className="text-slate-400">Alerts Generated:</span>
                      <span className="font-mono font-bold text-sky-400">
                        {runResult.alerts_generated}
                      </span>
                    </div>

                    <div className="flex justify-between py-1 border-b border-slate-800">
                      <span className="text-slate-400">Execution Time:</span>
                      <span className="font-mono text-slate-200">
                        {runResult.execution_time_ms} ms
                      </span>
                    </div>

                    <div className="flex justify-between py-1 border-b border-slate-800">
                      <span className="text-slate-400">Status:</span>
                      <span className="text-emerald-400 font-semibold">{runResult.status}</span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 mt-2">
                    <button
                      className="det-btn det-btn-primary w-full"
                      onClick={() => navigate(`/detection?run_id=${runResult.id}`)}
                    >
                      View Generated Alerts in Triage Queue →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
