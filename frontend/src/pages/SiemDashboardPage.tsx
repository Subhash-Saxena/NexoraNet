import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  Flame,
  Layers,
  Radio,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
} from 'lucide-react'
import { SiemNav } from '../components/siem/SiemNav'
import { siemApi } from '../services/siemApi'
import type { CorrelationAlert, SiemAggregations } from '../types/siem'
import '../components/siem/siem.css'

export const SiemDashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [aggregations, setAggregations] = useState<SiemAggregations | null>(null)
  const [recentAlerts, setRecentAlerts] = useState<CorrelationAlert[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [timePreset, setTimePreset] = useState<string>('ALL')

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [aggData, alertsData] = await Promise.all([
        siemApi.getAggregations({ time_preset: timePreset }),
        siemApi.listAlerts({ status: 'NEW' }),
      ])
      setAggregations(aggData)
      setRecentAlerts(alertsData)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load SIEM telemetry')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [timePreset])

  const handleEscalateToSoc = async (alertItem: CorrelationAlert) => {
    try {
      const res = await siemApi.investigateInSoc(undefined, alertItem.id)
      if (res.redirect_url) {
        navigate(res.redirect_url)
      } else {
        window.alert('Alert escalated to SOC Investigation!')
        loadData()
      }
    } catch (err: unknown) {
      window.alert(`Escalation failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  return (
    <div className="siem-container">
      {/* Header */}
      <div className="siem-header">
        <div className="siem-header-left">
          <div className="siem-title-row">
            <h1>
              <Shield className="text-cyan-400" size={26} />
              SIEM & Security Log Analysis
            </h1>
            <span className="siem-tag">STEP 15</span>
          </div>
          <p className="siem-subtitle">
            Centralized synthetic telemetry ingestion, normalized event querying, and behavioral correlation engine.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select
            className="condition-select"
            value={timePreset}
            onChange={(e) => setTimePreset(e.target.value)}
          >
            <option value="ALL">All Recorded Time</option>
            <option value="LAST_15M">Last 15 Minutes</option>
            <option value="LAST_1H">Last 1 Hour</option>
            <option value="LAST_24H">Last 24 Hours</option>
            <option value="LAST_7D">Last 7 Days</option>
          </select>

          <button className="siem-btn-secondary" onClick={loadData} title="Refresh Telemetry">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <SiemNav />

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239,68,68,0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', color: '#f87171' }}>
          {error}
        </div>
      )}

      {/* KPI Cards */}
      <div className="siem-stats-grid">
        <div className="siem-kpi-card info">
          <div className="siem-kpi-header">
            <span>Total Ingested Events</span>
            <Layers size={18} color="#0284c7" />
          </div>
          <div className="siem-kpi-val">{aggregations?.total_events.toLocaleString() || '0'}</div>
          <div className="siem-kpi-footer">Across all normalized log sources</div>
        </div>

        <div className="siem-kpi-card alert">
          <div className="siem-kpi-header">
            <span>High/Critical Alerts</span>
            <Flame size={18} color="#ef4444" />
          </div>
          <div className="siem-kpi-val">{aggregations?.high_severity_count.toLocaleString() || '0'}</div>
          <div className="siem-kpi-footer">Requiring analyst investigation</div>
        </div>

        <div className="siem-kpi-card warn">
          <div className="siem-kpi-header">
            <span>Auth Failures & Blocks</span>
            <AlertTriangle size={18} color="#f59e0b" />
          </div>
          <div className="siem-kpi-val">
            {((aggregations?.auth_failures || 0) + (aggregations?.firewall_blocks || 0)).toLocaleString()}
          </div>
          <div className="siem-kpi-footer">
            {aggregations?.auth_failures || 0} Logon Failures / {aggregations?.firewall_blocks || 0} Network Drops
          </div>
        </div>

        <div className="siem-kpi-card success">
          <div className="siem-kpi-header">
            <span>Active Correlation Alerts</span>
            <Radio size={18} color="#10b981" />
          </div>
          <div className="siem-kpi-val">{recentAlerts.length}</div>
          <div className="siem-kpi-footer">Behavioral multi-event rule triggers</div>
        </div>
      </div>

      {/* Activity Timeline / Histogram */}
      {aggregations?.timeline && aggregations.timeline.length > 0 && (
        <div className="timeline-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '0.9375rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity size={16} color="#38bdf8" />
              Event Telemetry Timeline
            </h3>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Hourly Distribution</span>
          </div>

          <div className="timeline-bars">
            {aggregations.timeline.map((bucket, idx) => {
              const maxTotal = Math.max(...aggregations.timeline.map((t) => t.total), 1)
              const heightPct = Math.min(Math.round((bucket.total / maxTotal) * 100), 100)
              return (
                <div key={idx} className="timeline-col" title={`${bucket.timestamp}: ${bucket.total} events (${bucket.auth_failures} auth failures)`}>
                  <div
                    className={`timeline-bar-segment ${bucket.auth_failures > 0 ? 'auth' : ''}`}
                    style={{ height: `${Math.max(heightPct, 6)}%` }}
                  />
                  <span className="timeline-bar-label">{bucket.bucket}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Two Column Layout: Top Entities and Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.25rem' }}>
        {/* Top Entities */}
        <div className="siem-table-container">
          <div className="siem-table-toolbar">
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>Top Suspicious Entities</span>
            <span>Frequency Analysis</span>
          </div>
          <table className="siem-events-table">
            <thead>
              <tr>
                <th>Entity Type</th>
                <th>Observable</th>
                <th style={{ textAlign: 'right' }}>Event Count</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {aggregations?.top_source_ips?.slice(0, 4).map((item, idx) => (
                <tr key={`ip-${idx}`}>
                  <td><span className="cat-badge">SRC_IP</span></td>
                  <td className="mono-cell" style={{ color: '#38bdf8' }}>{item.name}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600 }}>{item.count}</td>
                  <td>
                    <button
                      className="siem-btn-secondary"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      onClick={() => navigate(`/siem/search?field=source_ip&value=${encodeURIComponent(item.name)}`)}
                    >
                      <Search size={12} /> Filter
                    </button>
                  </td>
                </tr>
              ))}
              {aggregations?.top_users?.slice(0, 3).map((item, idx) => (
                <tr key={`user-${idx}`}>
                  <td><span className="cat-badge">USER</span></td>
                  <td className="mono-cell" style={{ color: '#a78bfa' }}>{item.name}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600 }}>{item.count}</td>
                  <td>
                    <button
                      className="siem-btn-secondary"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      onClick={() => navigate(`/siem/search?field=username&value=${encodeURIComponent(item.name)}`)}
                    >
                      <Search size={12} /> Filter
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Severity & Category Breakdown */}
        <div className="siem-table-container">
          <div className="siem-table-toolbar">
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>Telemetry Category Distribution</span>
            <span>Normalized Taxonomy</span>
          </div>
          <div style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {aggregations?.by_category &&
              Object.entries(aggregations.by_category).map(([cat, count]) => {
                const total = aggregations.total_events || 1
                const pct = Math.round((count / total) * 100)
                return (
                  <div key={cat} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem' }}>
                      <span className="cat-badge">{cat}</span>
                      <span style={{ color: '#94a3b8' }}>
                        {count.toLocaleString()} ({pct}%)
                      </span>
                    </div>
                    <div style={{ width: '100%', height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                      <div
                        style={{
                          width: `${pct}%`,
                          height: '100%',
                          background: cat === 'AUTHENTICATION' ? '#f59e0b' : cat === 'FIREWALL' ? '#ef4444' : '#0284c7',
                        }}
                      />
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      </div>

      {/* Recent Correlation Alerts */}
      <div className="siem-table-container">
        <div className="siem-table-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={16} color="#ef4444" />
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>Recent Correlation Rule Triggers</span>
          </div>
          <button
            className="siem-btn-secondary"
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
            onClick={() => navigate('/siem/rules')}
          >
            Manage Correlation Rules &rarr;
          </button>
        </div>

        <table className="siem-events-table">
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Timestamp</th>
              <th>Title</th>
              <th>Category</th>
              <th>Severity</th>
              <th>Matched Events</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recentAlerts.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  No active unreviewed correlation alerts.
                </td>
              </tr>
            ) : (
              recentAlerts.slice(0, 5).map((alert) => (
                <tr key={alert.id}>
                  <td className="mono-cell" style={{ color: '#38bdf8' }}>{alert.alert_id}</td>
                  <td className="mono-cell">{new Date(alert.timestamp).toLocaleTimeString()}</td>
                  <td style={{ fontWeight: 500, color: '#f1f5f9' }}>{alert.title}</td>
                  <td><span className="cat-badge">{alert.category}</span></td>
                  <td><span className={`sev-badge sev-${alert.severity}`}>{alert.severity}</span></td>
                  <td style={{ fontWeight: 600 }}>{alert.event_count} events</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn-escalate-soc"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => handleEscalateToSoc(alert)}
                        title="Escalate directly to Step 12 SOC Investigation"
                      >
                        Investigate in SOC
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
