import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  ShieldAlert,
  Play,
  Sliders,
  Search,
  Filter,
  RefreshCw,
  Info,
  CheckCircle,
  Clock,
  ArrowRight,
} from 'lucide-react'
import { detectionApi } from '../../services/detectionApi'
import type {
  DetectionStats,
  DetectionAlertListItem,
  DetectionRunResponse,
  AlertSeverity,
  AlertStatus,
  RuleCategory,
} from '../../types/detection'
import '../../components/detection/detection.css'

export const DetectionDashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DetectionStats | null>(null)
  const [alerts, setAlerts] = useState<DetectionAlertListItem[]>([])
  const [recentRuns, setRecentRuns] = useState<DetectionRunResponse[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsData, alertsData, runsData] = await Promise.all([
        detectionApi.getStats(),
        detectionApi.listAlerts({
          severity: severityFilter ? (severityFilter as AlertSeverity) : undefined,
          status: statusFilter ? (statusFilter as AlertStatus) : undefined,
          category: categoryFilter ? (categoryFilter as RuleCategory) : undefined,
          limit: 50,
        }),
        detectionApi.listRuns({ limit: 5 }),
      ])
      setStats(statsData)
      setAlerts(alertsData)
      setRecentRuns(runsData)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load detection data')
    } finally {
      setLoading(false)
    }
  }, [severityFilter, statusFilter, categoryFilter])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const filteredAlerts = alerts.filter((alert) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      alert.title.toLowerCase().includes(q) ||
      (alert.source_ip && alert.source_ip.toLowerCase().includes(q)) ||
      (alert.destination_ip && alert.destination_ip.toLowerCase().includes(q)) ||
      (alert.rule_code && alert.rule_code.toLowerCase().includes(q)) ||
      (alert.protocol && alert.protocol.toLowerCase().includes(q))
    )
  })

  return (
    <div className="detection-container">
      {/* Educational Notice Banner */}
      <div className="detection-banner">
        <div className="detection-banner-content">
          <Info size={20} className="text-sky-400" />
          <span>
            <strong>Defensive Educational Detection:</strong> NexoraNet analyzes packet and flow telemetry offline.
            It does not send live network traffic, sniff interfaces, or probe endpoints.
          </span>
        </div>
      </div>

      {/* Header */}
      <div className="detection-header">
        <div className="detection-header-title">
          <ShieldAlert size={32} className="text-sky-400" />
          <div>
            <h1>Network Detection & SOC Triage</h1>
            <p className="text-sm text-slate-400">
              Rule-based signature & anomaly detection engine for PCAP captures and network telemetry.
            </p>
          </div>
        </div>

        <div className="detection-actions">
          <button
            className="det-btn det-btn-secondary"
            onClick={fetchData}
            disabled={loading}
            title="Refresh Data"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <Link to="/detection/rules" className="det-btn det-btn-secondary">
            <Sliders size={16} />
            Rule Catalog
          </Link>
          <Link to="/detection/run" className="det-btn det-btn-primary">
            <Play size={16} />
            Run Detection
          </Link>
        </div>
      </div>

      {error && (
        <div className="pcap-notice-banner danger">
          <span>{error}</span>
        </div>
      )}

      {/* Stats Cards */}
      <div className="det-stats-grid">
        <div className="det-stat-card">
          <span className="det-stat-label">Active Triage Alerts</span>
          <span className="det-stat-value text-indigo-400">
            {stats ? stats.active_alerts : '-'}
          </span>
          <span className="det-stat-sub">Pending analyst review or investigation</span>
        </div>

        <div className="det-stat-card">
          <span className="det-stat-label">Total Alerts Generated</span>
          <span className="det-stat-value text-sky-400">
            {stats ? stats.total_alerts : '-'}
          </span>
          <span className="det-stat-sub">Across all offline runs</span>
        </div>

        <div className="det-stat-card">
          <span className="det-stat-label">Detection Runs</span>
          <span className="det-stat-value text-emerald-400">
            {stats ? stats.total_runs : '-'}
          </span>
          <span className="det-stat-sub">Telemetry analysis runs executed</span>
        </div>

        <div className="det-stat-card">
          <span className="det-stat-label">Active Rules</span>
          <span className="det-stat-value text-amber-400">
            {stats ? `${stats.active_rules} / ${stats.total_rules}` : '-'}
          </span>
          <span className="det-stat-sub">Deterministic signatures enabled</span>
        </div>
      </div>

      {/* Severity Breakdown Bar */}
      {stats && (
        <div className="det-card">
          <div className="det-card-title">
            <span>Alerts by Severity Level</span>
            <span className="text-xs text-slate-400">Prioritization overview</span>
          </div>
          <div className="grid grid-cols-5 gap-2 text-center">
            <div className="p-3 rounded bg-red-950/20 border border-red-800/40">
              <span className="block text-xl font-bold text-red-400">
                {stats.alerts_by_severity.CRITICAL || 0}
              </span>
              <span className="text-xs text-red-300 font-semibold">CRITICAL</span>
            </div>
            <div className="p-3 rounded bg-orange-950/20 border border-orange-800/40">
              <span className="block text-xl font-bold text-orange-400">
                {stats.alerts_by_severity.HIGH || 0}
              </span>
              <span className="text-xs text-orange-300 font-semibold">HIGH</span>
            </div>
            <div className="p-3 rounded bg-amber-950/20 border border-amber-800/40">
              <span className="block text-xl font-bold text-amber-400">
                {stats.alerts_by_severity.MEDIUM || 0}
              </span>
              <span className="text-xs text-amber-300 font-semibold">MEDIUM</span>
            </div>
            <div className="p-3 rounded bg-sky-950/20 border border-sky-800/40">
              <span className="block text-xl font-bold text-sky-400">
                {stats.alerts_by_severity.LOW || 0}
              </span>
              <span className="text-xs text-sky-300 font-semibold">LOW</span>
            </div>
            <div className="p-3 rounded bg-slate-900/40 border border-slate-700/40">
              <span className="block text-xl font-bold text-slate-400">
                {stats.alerts_by_severity.INFO || 0}
              </span>
              <span className="text-xs text-slate-400 font-semibold">INFO</span>
            </div>
          </div>
        </div>
      )}

      {/* Alerts Filter Toolbar */}
      <div className="det-toolbar">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search size={16} className="text-slate-400" />
          <input
            type="text"
            className="det-input w-full"
            placeholder="Search by title, IP address, protocol, or rule code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={16} className="text-slate-400" />
          <select
            className="det-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            aria-label="Filter by Severity"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Info</option>
          </select>

          <select
            className="det-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter by Status"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CLOSED">Closed</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>

          <select
            className="det-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Filter by Category"
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
        </div>
      </div>

      {/* Active Alerts Table */}
      <div className="det-table-wrapper">
        <table className="det-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Alert Title & Rule</th>
              <th>Category</th>
              <th>Source → Destination</th>
              <th>Packets</th>
              <th>Confidence</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading && alerts.length === 0 ? (
              <tr>
                <td colSpan={8} className="det-empty">
                  <RefreshCw size={24} className="animate-spin inline-block mr-2" />
                  Loading detection alerts...
                </td>
              </tr>
            ) : filteredAlerts.length === 0 ? (
              <tr>
                <td colSpan={8} className="det-empty">
                  No detection alerts found matching the selected filters.
                  <div className="mt-2">
                    <Link to="/detection/run" className="det-btn det-btn-primary">
                      Run Detection Engine on a Capture
                    </Link>
                  </div>
                </td>
              </tr>
            ) : (
              filteredAlerts.map((alert) => (
                <tr key={alert.id}>
                  <td>
                    <span className={`sev-badge ${alert.severity}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td>
                    <div className="font-semibold text-slate-100">{alert.title}</div>
                    <div className="text-xs text-slate-400 font-mono">
                      {alert.rule_code || `Rule #${alert.rule_id}`}
                    </div>
                  </td>
                  <td>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {alert.category}
                    </span>
                  </td>
                  <td className="font-mono text-xs">
                    {alert.source_ip || '*'}{alert.source_port ? `:${alert.source_port}` : ''}
                    {' → '}
                    {alert.destination_ip || '*'}{alert.destination_port ? `:${alert.destination_port}` : ''}
                    {alert.protocol && (
                      <span className="ml-1 text-[10px] text-slate-400">({alert.protocol})</span>
                    )}
                  </td>
                  <td className="text-center font-mono text-xs">
                    {alert.packet_count}
                  </td>
                  <td>
                    <span className="conf-badge">
                      {alert.confidence}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${alert.status}`}>
                      {alert.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <Link
                      to={`/detection/alerts/${alert.id}`}
                      className="det-btn det-btn-secondary text-xs py-1 px-2.5"
                    >
                      Triage <ArrowRight size={12} />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Recent Detection Runs Section */}
      {recentRuns.length > 0 && (
        <div className="det-card">
          <div className="det-card-title">
            <div className="flex items-center gap-2">
              <Clock size={18} className="text-sky-400" />
              <span>Recent Detection Runs</span>
            </div>
            <Link to="/detection/run" className="text-xs text-sky-400 hover:underline">
              New Run →
            </Link>
          </div>

          <div className="det-table-wrapper">
            <table className="det-table">
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Source</th>
                  <th>Packets Analyzed</th>
                  <th>Alerts</th>
                  <th>Time (ms)</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {recentRuns.map((run) => (
                  <tr key={run.id}>
                    <td className="font-mono text-xs">Run #{run.id}</td>
                    <td className="text-xs">
                      {run.source_type}
                      {run.capture_id ? ` (Capture #${run.capture_id})` : ''}
                    </td>
                    <td className="font-mono text-xs">{run.packets_analyzed}</td>
                    <td>
                      <span className="font-bold text-sky-400">{run.alerts_generated}</span>
                    </td>
                    <td className="font-mono text-xs">{run.execution_time_ms} ms</td>
                    <td>
                      <span className="inline-flex items-center gap-1 text-xs text-emerald-400">
                        <CheckCircle size={12} />
                        {run.status}
                      </span>
                    </td>
                    <td className="text-xs text-slate-400">
                      {new Date(run.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
