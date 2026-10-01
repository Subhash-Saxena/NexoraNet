import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  Sliders,
  Play,
  Search,
  Filter,
  AlertTriangle,
  RefreshCw,
  Code2,
  X,
} from 'lucide-react'
import { detectionApi } from '../../services/detectionApi'
import { pcapApi } from '../../services/pcapApi'
import type {
  DetectionRule,
  DetectionRuleTestResponse,
  RuleCategory,
  AlertSeverity,
} from '../../types/detection'
import type { CaptureSummary } from '../../types/pcap'
import '../../components/detection/detection.css'

export const DetectionRulesPage: React.FC = () => {
  const [rules, setRules] = useState<DetectionRule[]>([])
  const [captures, setCaptures] = useState<CaptureSummary[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<string>('')

  // Selected rule for detail modal
  const [inspectRule, setInspectRule] = useState<DetectionRule | null>(null)

  // Test Sandbox state
  const [testModalRule, setTestModalRule] = useState<DetectionRule | null>(null)
  const [testCaptureId, setTestCaptureId] = useState<number | ''>('')
  const [testingRule, setTestingRule] = useState<boolean>(false)
  const [testResult, setTestResult] = useState<DetectionRuleTestResponse | null>(null)
  const [testError, setTestError] = useState<string | null>(null)

  const fetchRulesAndCaptures = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [rulesData, capturesData] = await Promise.all([
        detectionApi.listRules({
          category: categoryFilter ? (categoryFilter as RuleCategory) : undefined,
          severity: severityFilter ? (severityFilter as AlertSeverity) : undefined,
        }),
        pcapApi.listCaptures(),
      ])
      setRules(rulesData)
      setCaptures(capturesData.filter((c) => c.status === 'READY'))
      if (capturesData.length > 0 && !testCaptureId) {
        const ready = capturesData.find((c) => c.status === 'READY')
        if (ready) setTestCaptureId(ready.id)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch detection rules')
    } finally {
      setLoading(false)
    }
  }, [categoryFilter, severityFilter, testCaptureId])

  useEffect(() => {
    fetchRulesAndCaptures()
  }, [fetchRulesAndCaptures])

  const filteredRules = rules.filter((rule) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      rule.rule_id.toLowerCase().includes(q) ||
      rule.name.toLowerCase().includes(q) ||
      rule.description.toLowerCase().includes(q) ||
      (rule.mitre_attack_id && rule.mitre_attack_id.toLowerCase().includes(q))
    )
  })

  const handleOpenTestSandbox = (rule: DetectionRule) => {
    setTestModalRule(rule)
    setTestResult(null)
    setTestError(null)
  }

  const handleRunTest = async () => {
    if (!testModalRule || !testCaptureId) return
    setTestingRule(true)
    setTestError(null)
    setTestResult(null)
    try {
      const res = await detectionApi.testRule({
        rule_id: testModalRule.rule_id,
        capture_id: Number(testCaptureId),
      })
      setTestResult(res)
    } catch (err: unknown) {
      setTestError(err instanceof Error ? err.message : 'Simulation dry run failed')
    } finally {
      setTestingRule(false)
    }
  }

  return (
    <div className="detection-container">
      {/* Navigation */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Link to="/detection" className="flex items-center gap-1 hover:text-sky-400">
          <ArrowLeft size={16} /> Back to Detection Dashboard
        </Link>
      </div>

      {/* Header */}
      <div className="detection-header">
        <div className="detection-header-title">
          <Sliders size={32} className="text-sky-400" />
          <div>
            <h1>Detection Rule Catalog & Sandbox</h1>
            <p className="text-sm text-slate-400">
              Deterministic detection rules covering TCP, DNS, ARP, ICMP, HTTP, and Reconnaissance patterns.
            </p>
          </div>
        </div>

        <div className="detection-actions">
          <Link to="/detection/run" className="det-btn det-btn-primary">
            <Play size={16} /> Run Detection
          </Link>
        </div>
      </div>

      {error && (
        <div className="pcap-notice-banner danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Search & Filter Toolbar */}
      <div className="det-toolbar">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search size={16} className="text-slate-400" />
          <input
            type="text"
            className="det-input w-full"
            placeholder="Search rules by rule ID, name, description, or MITRE technique..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={16} className="text-slate-400" />
          <select
            className="det-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="TCP">TCP</option>
            <option value="UDP">UDP</option>
            <option value="DNS">DNS</option>
            <option value="ARP">ARP</option>
            <option value="ICMP">ICMP</option>
            <option value="HTTP">HTTP</option>
            <option value="RECON">Reconnaissance</option>
            <option value="SUSPICIOUS_PORT">Suspicious Port</option>
            <option value="TRAFFIC">Traffic Anomaly</option>
          </select>

          <select
            className="det-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Info</option>
          </select>
        </div>
      </div>

      {/* Rules Table */}
      <div className="det-table-wrapper">
        <table className="det-table">
          <thead>
            <tr>
              <th>Rule ID</th>
              <th>Rule Name & Description</th>
              <th>Category</th>
              <th>Severity</th>
              <th>MITRE ATT&CK</th>
              <th>Logic Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="det-empty">
                  <RefreshCw size={24} className="animate-spin inline-block mr-2" />
                  Loading detection rules...
                </td>
              </tr>
            ) : filteredRules.length === 0 ? (
              <tr>
                <td colSpan={7} className="det-empty">
                  No detection rules matched the search filters.
                </td>
              </tr>
            ) : (
              filteredRules.map((rule) => (
                <tr key={rule.rule_id}>
                  <td className="font-mono font-bold text-sky-400 text-xs">
                    {rule.rule_id}
                  </td>
                  <td>
                    <div className="font-semibold text-slate-100">{rule.name}</div>
                    <div className="text-xs text-slate-400 line-clamp-1">{rule.description}</div>
                  </td>
                  <td>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {rule.category}
                    </span>
                  </td>
                  <td>
                    <span className={`sev-badge ${rule.severity}`}>{rule.severity}</span>
                  </td>
                  <td>
                    {rule.mitre_attack_id ? (
                      <span className="mitre-badge" title={rule.mitre_technique || ''}>
                        {rule.mitre_attack_id}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-500">-</span>
                    )}
                  </td>
                  <td className="font-mono text-xs text-slate-400">
                    {rule.logic_type}
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <button
                        className="det-btn det-btn-secondary text-xs py-1 px-2.5"
                        onClick={() => setInspectRule(rule)}
                        title="View Rule Specification"
                      >
                        Inspect
                      </button>
                      <button
                        className="det-btn det-btn-primary text-xs py-1 px-2.5"
                        onClick={() => handleOpenTestSandbox(rule)}
                        title="Dry Run Rule on Capture"
                      >
                        Test
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Inspect Rule Modal */}
      {inspectRule && (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-sky-400">{inspectRule.rule_id}</span>
                <h2 className="text-lg font-bold text-slate-100">{inspectRule.name}</h2>
              </div>
              <button
                className="text-slate-400 hover:text-slate-200"
                onClick={() => setInspectRule(null)}
              >
                <X size={20} />
              </button>
            </div>

            <p className="text-sm text-slate-300">{inspectRule.description}</p>

            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950 p-3 rounded border border-slate-800">
              <div>
                <span className="text-slate-500 block">Category:</span>
                <span className="font-semibold text-slate-200">{inspectRule.category}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Severity:</span>
                <span className={`sev-badge ${inspectRule.severity}`}>{inspectRule.severity}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Logic Type:</span>
                <span className="font-mono text-slate-200">{inspectRule.logic_type}</span>
              </div>
              <div>
                <span className="text-slate-500 block">MITRE ATT&CK:</span>
                <span className="text-red-400 font-mono">
                  {inspectRule.mitre_attack_id ? `${inspectRule.mitre_attack_id} (${inspectRule.mitre_technique})` : 'N/A'}
                </span>
              </div>
            </div>

            {/* Threshold Configuration */}
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase block mb-1">
                Threshold & Evaluation Parameters
              </span>
              <pre className="text-xs font-mono text-emerald-400 bg-slate-950 p-3 rounded border border-slate-800 overflow-x-auto">
                {JSON.stringify(inspectRule.threshold_config, null, 2)}
              </pre>
            </div>

            {/* Investigation Steps */}
            {inspectRule.investigation_steps && inspectRule.investigation_steps.length > 0 && (
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase block mb-2">
                  SOC Analyst Investigation Steps
                </span>
                <ol className="list-decimal list-inside text-xs text-slate-300 flex flex-col gap-1.5 pl-1">
                  {inspectRule.investigation_steps.map((st, i) => (
                    <li key={i}>{st}</li>
                  ))}
                </ol>
              </div>
            )}

            <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
              <button
                className="det-btn det-btn-secondary"
                onClick={() => setInspectRule(null)}
              >
                Close
              </button>
              <button
                className="det-btn det-btn-primary"
                onClick={() => {
                  const rule = inspectRule
                  setInspectRule(null)
                  handleOpenTestSandbox(rule)
                }}
              >
                Test in Sandbox
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Test Sandbox Modal */}
      {testModalRule && (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg max-w-xl w-full p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Code2 size={20} className="text-sky-400" />
                <h2 className="text-lg font-bold text-slate-100">
                  Simulate Rule Test: {testModalRule.rule_id}
                </h2>
              </div>
              <button
                className="text-slate-400 hover:text-slate-200"
                onClick={() => setTestModalRule(null)}
              >
                <X size={20} />
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Run this rule in dry-run mode against an offline capture. This tests signature
              logic without saving persistent alerts to the database.
            </p>

            {testError && (
              <div className="pcap-notice-banner danger text-xs">
                <span>{testError}</span>
              </div>
            )}

            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-300">
                Select Offline Target Capture
              </label>
              {captures.length === 0 ? (
                <div className="text-xs text-amber-400">
                  No captures available to test against.
                </div>
              ) : (
                <select
                  className="det-select w-full text-xs"
                  value={testCaptureId}
                  onChange={(e) => setTestCaptureId(Number(e.target.value))}
                >
                  {captures.map((c) => (
                    <option key={c.id} value={c.id}>
                      #{c.id} — {c.name} ({c.packet_count} packets)
                    </option>
                  ))}
                </select>
              )}
            </div>

            <button
              className="det-btn det-btn-primary"
              onClick={handleRunTest}
              disabled={testingRule || !testCaptureId}
            >
              {testingRule ? (
                <>
                  <RefreshCw size={14} className="animate-spin" /> Simulating...
                </>
              ) : (
                'Run Simulation'
              )}
            </button>

            {/* Dry Run Results */}
            {testResult && (
              <div className="mt-2 p-3 bg-slate-950 rounded border border-slate-800 flex flex-col gap-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Rule Matches Found:</span>
                  <span className="font-bold text-sky-400 text-sm">
                    {testResult.matches_found}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Execution Time:</span>
                  <span className="font-mono text-slate-200">
                    {testResult.execution_time_ms} ms
                  </span>
                </div>

                {testResult.matches_found > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-800">
                    <span className="text-slate-400 block mb-1">Simulated Alert Previews:</span>
                    <div className="max-h-36 overflow-y-auto flex flex-col gap-1.5">
                      {testResult.simulated_alerts.map((a, i) => (
                        <div key={i} className="p-2 bg-slate-900 rounded border border-slate-800 text-[11px]">
                          <div className="font-semibold text-slate-200">{a.title}</div>
                          <div className="text-slate-400 font-mono text-[10px]">
                            {a.source_ip || '*'} → {a.destination_ip || '*'} ({a.packet_count} pkts)
                          </div>
                        </div>
                      ))}
                    </div>
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
