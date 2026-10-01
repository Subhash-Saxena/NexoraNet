import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type {
  SocActivityItem,
  SocAlertItem,
  SocOverviewResponse,
  SocStatisticsResponse,
  TrainingDatasetItem,
} from '../../types/soc'
import '../../components/soc/soc.css'

export const SocDashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<SocOverviewResponse | null>(null)
  const [statistics, setStatistics] = useState<SocStatisticsResponse | null>(null)
  const [activities, setActivities] = useState<SocActivityItem[]>([])
  const [recentAlerts, setRecentAlerts] = useState<SocAlertItem[]>([])
  const [datasets, setDatasets] = useState<TrainingDatasetItem[]>([])
  const [selectedDataset, setSelectedDataset] = useState<string>('tcp_investigation')
  const [loading, setLoading] = useState<boolean>(true)
  const [resetting, setResetting] = useState<boolean>(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const [ov, stats, act, alerts, ds] = await Promise.all([
        socApi.getOverview().catch(() => null),
        socApi.getStatistics().catch(() => null),
        socApi.getActivityStream().catch(() => []),
        socApi.listAlerts({ limit: 6 }).catch(() => []),
        socApi.listDatasets().catch(() => []),
      ])
      setOverview(ov)
      setStatistics(stats)
      setActivities(act)
      setRecentAlerts(alerts)
      setDatasets(ds)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load SOC dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleResetDataset = async () => {
    try {
      setResetting(true)
      setMessage(null)
      setError(null)
      const res = await socApi.resetTrainingDataset(selectedDataset)
      setMessage(`Successfully loaded dataset: ${res.dataset}. Telemetry and detection alerts refreshed.`)
      await loadData()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to reset training dataset.')
    } finally {
      setResetting(false)
    }
  }

  const getPriorityBadge = (p: string) => {
    switch (p) {
      case 'P1':
        return <span className="soc-badge soc-badge-p1">P1 CRITICAL</span>
      case 'P2':
        return <span className="soc-badge soc-badge-p2">P2 HIGH</span>
      case 'P3':
        return <span className="soc-badge soc-badge-p3">P3 MEDIUM</span>
      default:
        return <span className="soc-badge soc-badge-p4">P4 LOW</span>
    }
  }

  const getClassificationBadge = (cls: string) => {
    switch (cls) {
      case 'BENIGN':
        return <span className="soc-badge soc-badge-benign">Benign</span>
      case 'SUSPICIOUS':
        return <span className="soc-badge soc-badge-suspicious">Suspicious</span>
      case 'FALSE_POSITIVE':
        return <span className="soc-badge soc-badge-fp">False Positive</span>
      case 'REQUIRES_MORE_DATA':
        return <span className="soc-badge soc-badge-more-data">Need Data</span>
      case 'CLOSED':
        return <span className="soc-badge soc-badge-closed">Closed</span>
      default:
        return <span className="soc-badge soc-badge-unreviewed">Unreviewed</span>
    }
  }

  return (
    <div className="soc-container">
      <SocHeader
        actionButton={
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <select
              className="soc-select"
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              disabled={resetting}
              aria-label="Training Dataset Selector"
            >
              {datasets.map((d) => (
                <option key={d.dataset_id} value={d.dataset_id}>
                  {d.name} ({d.category})
                </option>
              ))}
            </select>
            <button
              className="soc-btn soc-btn-primary"
              onClick={handleResetDataset}
              disabled={resetting}
            >
              {resetting ? 'Resetting...' : 'Load Scenario'}
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
          Loading SOC telemetry and queue metrics...
        </div>
      ) : (
        <>
          {/* Key Metrics Grid */}
          <div className="soc-metrics-grid">
            <div className="soc-metric-card">
              <div className="soc-metric-label">Total Alerts</div>
              <div className="soc-metric-value">{overview?.metrics.total_alerts ?? 0}</div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">P1 Critical Alerts</div>
              <div className="soc-metric-value soc-metric-p1">{overview?.metrics.p1_alerts ?? 0}</div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">P2 High Alerts</div>
              <div className="soc-metric-value soc-metric-p2">{overview?.metrics.p2_alerts ?? 0}</div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">Open / Unreviewed</div>
              <div className="soc-metric-value">{overview?.metrics.open_alerts ?? 0}</div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">Investigating</div>
              <div className="soc-metric-value" style={{ color: '#a855f7' }}>
                {overview?.metrics.investigating_alerts ?? 0}
              </div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">Active Investigations</div>
              <div className="soc-metric-value" style={{ color: '#38bdf8' }}>
                {overview?.metrics.open_investigations_count ?? 0}
              </div>
            </div>
            <div className="soc-metric-card">
              <div className="soc-metric-label">Open Cases</div>
              <div className="soc-metric-value" style={{ color: '#f59e0b' }}>
                {overview?.metrics.open_cases_count ?? 0}
              </div>
            </div>
          </div>

          {/* Quick Learning Recommendations */}
          {overview?.learning_recommendations && overview.learning_recommendations.length > 0 && (
            <div className="soc-card" style={{ background: 'rgba(56, 189, 248, 0.04)', borderColor: 'rgba(56, 189, 248, 0.2)' }}>
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🎓</span> Analyst Learning Recommendations
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
                {overview.learning_recommendations.map((rec, i) => (
                  <div key={i} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid var(--soc-border)' }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#38bdf8' }}>{rec.title}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--soc-text-secondary)', margin: '0.35rem 0' }}>{rec.reason}</div>
                    <Link to={rec.action_link} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.78rem', padding: '0.3rem 0.6rem', marginTop: '0.3rem' }}>
                      Practice Now →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alert Queue Preview & Activity Stream */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
            {/* Alert Queue Preview */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>🚨</span> Priority Alert Queue
                </div>
                <Link to="/soc/alerts" className="soc-btn soc-btn-secondary" style={{ fontSize: '0.8rem' }}>
                  View All ({overview?.metrics.total_alerts ?? 0}) →
                </Link>
              </div>

              {recentAlerts.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)' }}>
                  No alerts currently queued. Choose a training dataset above to seed telemetry.
                </div>
              ) : (
                <div className="soc-table-container">
                  <table className="soc-table">
                    <thead>
                      <tr>
                        <th>Priority</th>
                        <th>Alert Title</th>
                        <th>Severity</th>
                        <th>Classification</th>
                        <th>Source → Destination</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentAlerts.map((a) => (
                        <tr key={a.id}>
                          <td>{getPriorityBadge(a.priority)}</td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)' }}>{a.title}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                              {a.rule_code || 'DETECTION'} • {a.protocol || 'IP'}
                            </div>
                          </td>
                          <td>
                            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>{a.severity}</span>
                          </td>
                          <td>{getClassificationBadge(a.classification)}</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                            {a.source_ip || '*'}:{a.source_port || '*'} → {a.destination_ip || '*'}:{a.destination_port || '*'}
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.4rem' }}>
                              <Link to={`/soc/alerts/${a.id}`} className="soc-btn soc-btn-secondary" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}>
                                Inspect
                              </Link>
                              <Link to={`/soc/alerts/${a.id}/triage`} className="soc-btn soc-btn-primary" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}>
                                Triage
                              </Link>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* SOC Live Activity Stream */}
            <div className="soc-card">
              <div className="soc-card-header">
                <div className="soc-card-title">
                  <span>📡</span> Analyst Activity Log
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>Audit Stream</span>
              </div>

              {activities.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--soc-text-muted)', fontSize: '0.85rem' }}>
                  No recent audit transitions recorded.
                </div>
              ) : (
                <div className="soc-timeline" style={{ maxHeight: '420px', overflowY: 'auto' }}>
                  {activities.map((act) => (
                    <div key={act.id} className="soc-timeline-item">
                      <div className="soc-timeline-marker" />
                      <div className="soc-timeline-title">{act.title}</div>
                      <div className="soc-timeline-meta">
                        {act.actor_name} • {new Date(act.timestamp).toLocaleTimeString()}
                      </div>
                      <div className="soc-timeline-desc">{act.description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Breakdown Statistics */}
          {statistics && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              <div className="soc-card">
                <div className="soc-card-title" style={{ fontSize: '0.9rem' }}>Alerts by Classification</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {Object.entries(statistics.alerts_by_classification).map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <span style={{ color: 'var(--soc-text-secondary)' }}>{k}</span>
                      <span style={{ fontWeight: 600 }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="soc-card">
                <div className="soc-card-title" style={{ fontSize: '0.9rem' }}>Top Source Endpoints</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {statistics.top_sources.length === 0 ? (
                    <div style={{ color: 'var(--soc-text-muted)', fontSize: '0.85rem' }}>No telemetry sources</div>
                  ) : (
                    statistics.top_sources.map((s, idx) => (
                      <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{s.ip}</span>
                        <span style={{ fontWeight: 600 }}>{s.count} alerts</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="soc-card">
                <div className="soc-card-title" style={{ fontSize: '0.9rem' }}>Top Destination Endpoints</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {statistics.top_destinations.length === 0 ? (
                    <div style={{ color: 'var(--soc-text-muted)', fontSize: '0.85rem' }}>No telemetry destinations</div>
                  ) : (
                    statistics.top_destinations.map((d, idx) => (
                      <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{d.ip}</span>
                        <span style={{ fontWeight: 600 }}>{d.count} alerts</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
