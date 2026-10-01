import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ThreatHuntingNav } from '../components/threat_hunting/ThreatHuntingNav'
import '../components/threat_hunting/threat_hunting.css'
import { threatHuntingApi } from '../services/threatHuntingApi'
import type {
  HuntDataset,
  HuntOverviewResponse,
  HuntScenario,
  ThreatHunt,
} from '../types/threat_hunting'

export const ThreatHuntingDashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [overview, setOverview] = useState<HuntOverviewResponse | null>(null)
  const [datasets, setDatasets] = useState<HuntDataset[]>([])
  const [scenarios, setScenarios] = useState<HuntScenario[]>([])
  const [hunts, setHunts] = useState<ThreatHunt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Custom Hunt Modal State
  const [showModal, setShowModal] = useState(false)
  const [modalTitle, setModalTitle] = useState('')
  const [modalDesc, setModalDesc] = useState('')
  const [modalObj, setModalObj] = useState('')
  const [modalDatasetId, setModalDatasetId] = useState<number | undefined>(undefined)
  const [modalDiff, setModalDiff] = useState('BEGINNER')
  const [modalPivotType, setModalPivotType] = useState('IP')
  const [modalPivotVal, setModalPivotVal] = useState('')
  const [creating, setCreating] = useState(false)

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [ovData, dsData, scData, huntsData] = await Promise.all([
        threatHuntingApi.getOverview(),
        threatHuntingApi.listDatasets(),
        threatHuntingApi.listScenarios(),
        threatHuntingApi.listHunts({ limit: 15 }),
      ])
      setOverview(ovData)
      setDatasets(dsData)
      setScenarios(scData)
      setHunts(huntsData)
      if (dsData.length > 0) {
        setModalDatasetId(dsData[0].id)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load threat hunting dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
  }, [])

  const handleCreateCustomHunt = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!modalTitle || !modalObj) return
    try {
      setCreating(true)
      const newHunt = await threatHuntingApi.createHunt({
        title: modalTitle,
        description: modalDesc || modalTitle,
        objective: modalObj,
        dataset_id: modalDatasetId,
        difficulty: modalDiff,
        initial_pivot_type: modalPivotType,
        initial_pivot_value: modalPivotVal || undefined,
      })
      setShowModal(false)
      navigate(`/threat-hunting/hunts/${newHunt.id}`)
    } catch (err: any) {
      alert(`Error creating hunt: ${err.message}`)
    } finally {
      setCreating(false)
    }
  }

  const handleLaunchScenario = async (slug: string) => {
    try {
      const launched = await threatHuntingApi.launchScenario(slug)
      navigate(`/threat-hunting/hunts/${launched.id}`)
    } catch (err: any) {
      alert(`Error launching scenario: ${err.message}`)
    }
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status.toUpperCase()) {
      case 'RUNNING':
        return 'badge-status-running'
      case 'READY':
        return 'badge-status-ready'
      case 'PAUSED':
        return 'badge-status-paused'
      case 'COMPLETED':
        return 'badge-status-completed'
      default:
        return 'badge-status-ready'
    }
  }

  const getDifficultyBadgeClass = (diff: string) => {
    switch (diff.toUpperCase()) {
      case 'BEGINNER':
        return 'badge-diff-beginner'
      case 'INTERMEDIATE':
        return 'badge-diff-intermediate'
      case 'ADVANCED':
        return 'badge-diff-advanced'
      default:
        return 'badge-diff-beginner'
    }
  }

  return (
    <div className="threat-hunting-container">
      {/* Header */}
      <div className="threat-hunting-header">
        <div className="threat-hunting-title-group">
          <h1>
            <span>🛡️</span> Threat Hunting & Investigation Workspace
          </h1>
          <div className="threat-hunting-subtitle">
            Hunt proactively across network telemetry, formulate scientific hypotheses, correlate IOCs, and validate attack behaviors.
          </div>
        </div>
        <div className="threat-hunting-actions">
          <button className="btn-cyber-primary" onClick={() => setShowModal(true)}>
            <span>+</span> New Threat Hunt
          </button>
          <Link to="/threat-hunting/scenarios" className="btn-cyber-secondary">
            <span>🎯</span> Browse Scenarios
          </Link>
        </div>
      </div>

      <ThreatHuntingNav />

      {error && (
        <div style={{ background: '#7f1d1d', color: '#fecaca', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Initializing Threat Hunting Workspace telemetry...
        </div>
      ) : (
        <>
          {/* Key Metrics */}
          <div className="hunting-stats-grid">
            <div className="hunting-stat-card">
              <div className="hunting-stat-header">
                <span>Active Hunts</span>
                <span>🔥</span>
              </div>
              <div className="hunting-stat-value">{overview?.active_hunts ?? 0}</div>
              <div className="hunting-stat-subtext">Currently investigating</div>
            </div>

            <div className="hunting-stat-card">
              <div className="hunting-stat-header">
                <span>Completed Hunts</span>
                <span>✅</span>
              </div>
              <div className="hunting-stat-value">{overview?.completed_hunts ?? 0}</div>
              <div className="hunting-stat-subtext">Defensible conclusions</div>
            </div>

            <div className="hunting-stat-card">
              <div className="hunting-stat-header">
                <span>Telemetry Datasets</span>
                <span>💾</span>
              </div>
              <div className="hunting-stat-value">{overview?.total_datasets ?? 0}</div>
              <div className="hunting-stat-subtext">PCAP, alerts & NetFlow</div>
            </div>

            <div className="hunting-stat-card">
              <div className="hunting-stat-header">
                <span>Indexed Events</span>
                <span>⚡</span>
              </div>
              <div className="hunting-stat-value">{overview?.total_events.toLocaleString() ?? 0}</div>
              <div className="hunting-stat-subtext">Queryable security logs</div>
            </div>

            <div className="hunting-stat-card">
              <div className="hunting-stat-header">
                <span>Guided Scenarios</span>
                <span>🎯</span>
              </div>
              <div className="hunting-stat-value">{overview?.total_scenarios ?? 8}</div>
              <div className="hunting-stat-subtext">Mapped to MITRE ATT&CK</div>
            </div>
          </div>

          {/* Quick Launch Scenarios */}
          <div style={{ marginBottom: '2.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', margin: 0 }}>
                🎯 Guided Threat Hunting Scenarios
              </h2>
              <Link to="/threat-hunting/scenarios" style={{ color: '#38bdf8', fontSize: '0.9rem', textDecoration: 'none' }}>
                View All 8 Scenarios →
              </Link>
            </div>
            <div className="scenarios-grid">
              {scenarios.slice(0, 3).map((sc) => (
                <div key={sc.slug} className="scenario-card">
                  <div>
                    <div className="scenario-header">
                      <h3 className="scenario-title">{sc.title}</h3>
                      <span className={`hunt-badge ${getDifficultyBadgeClass(sc.difficulty)}`}>
                        {sc.difficulty}
                      </span>
                    </div>
                    <div className="scenario-brief">{sc.brief}</div>
                    <div className="scenario-meta">
                      <span className="scenario-tag">{sc.category}</span>
                      <span className="scenario-tag">⏱️ {sc.estimated_minutes} min</span>
                      {sc.initial_pivot_value && (
                        <span className="scenario-tag" style={{ borderColor: '#0284c7' }}>
                          Pivot: {sc.initial_pivot_value}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    className="btn-cyber-primary"
                    style={{ width: '100%', justifyContent: 'center' }}
                    onClick={() => handleLaunchScenario(sc.slug)}
                  >
                    <span>🔬</span> Launch Investigation
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Telemetry Datasets */}
          <div style={{ marginBottom: '2.5rem' }} id="datasets">
            <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', marginBottom: '1rem' }}>
              💾 Available Telemetry Datasets
            </h2>
            <div className="telemetry-table-wrapper">
              <table className="cyber-table">
                <thead>
                  <tr>
                    <th>Dataset Code</th>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Event Count</th>
                    <th>Source</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map((ds) => (
                    <tr key={ds.id}>
                      <td style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{ds.dataset_id}</td>
                      <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                        {ds.name}
                        <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 400 }}>
                          {ds.description}
                        </div>
                      </td>
                      <td>
                        <span className="hunt-badge" style={{ background: '#334155', color: '#94a3b8' }}>
                          {ds.dataset_type}
                        </span>
                      </td>
                      <td style={{ fontWeight: 600 }}>{ds.event_count.toLocaleString()}</td>
                      <td style={{ color: '#94a3b8' }}>{ds.source}</td>
                      <td>
                        <span className="hunt-badge badge-status-ready">{ds.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Threat Hunts */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.3rem', color: '#f8fafc', margin: 0 }}>
                📋 Your Threat Hunt Investigations
              </h2>
            </div>
            {hunts.length === 0 ? (
              <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                No active threat hunts yet. Launch a scenario above or create a new custom investigation session!
              </div>
            ) : (
              <div className="telemetry-table-wrapper">
                <table className="cyber-table">
                  <thead>
                    <tr>
                      <th>Hunt ID</th>
                      <th>Investigation Title</th>
                      <th>Status</th>
                      <th>Difficulty</th>
                      <th>Initial Pivot</th>
                      <th>Score</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {hunts.map((h) => (
                      <tr key={h.id}>
                        <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontWeight: 600 }}>
                          {h.hunt_id}
                        </td>
                        <td>
                          <div style={{ fontWeight: 600, color: '#f8fafc' }}>{h.title}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{h.description.slice(0, 80)}...</div>
                        </td>
                        <td>
                          <span className={`hunt-badge ${getStatusBadgeClass(h.status)}`}>
                            {h.status}
                          </span>
                        </td>
                        <td>
                          <span className={`hunt-badge ${getDifficultyBadgeClass(h.difficulty)}`}>
                            {h.difficulty}
                          </span>
                        </td>
                        <td>
                          {h.initial_pivot_value ? (
                            <span style={{ fontSize: '0.8rem', background: '#0f172a', padding: '0.2rem 0.5rem', borderRadius: '4px', border: '1px solid #334155' }}>
                              {h.initial_pivot_type}: {h.initial_pivot_value}
                            </span>
                          ) : (
                            <span style={{ color: '#64748b' }}>—</span>
                          )}
                        </td>
                        <td>
                          {h.score != null ? (
                            <span style={{ fontWeight: 700, color: h.score >= 80 ? '#34d399' : '#fbbf24' }}>
                              {h.score}/100
                            </span>
                          ) : (
                            <span style={{ color: '#64748b' }}>In Progress</span>
                          )}
                        </td>
                        <td>
                          <button
                            className="btn-cyber-secondary"
                            style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                            onClick={() => navigate(`/threat-hunting/hunts/${h.id}`)}
                          >
                            Open Workspace →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {/* New Threat Hunt Modal */}
      {showModal && (
        <div className="score-modal-overlay">
          <div className="score-modal-card" style={{ maxWidth: '600px' }}>
            <h2 style={{ color: '#f8fafc', marginTop: 0, marginBottom: '1.25rem' }}>
              🔬 Create New Threat Hunt Campaign
            </h2>
            <form onSubmit={handleCreateCustomHunt}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Hunt Title *
                </label>
                <input
                  type="text"
                  required
                  className="cyber-input"
                  style={{ width: '100%' }}
                  placeholder="e.g. Investigation: Suspected Kerberoasting Activity"
                  value={modalTitle}
                  onChange={(e) => setModalTitle(e.target.value)}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Description (Optional)
                </label>
                <input
                  type="text"
                  className="cyber-input"
                  style={{ width: '100%' }}
                  placeholder="Additional context or background details..."
                  value={modalDesc}
                  onChange={(e) => setModalDesc(e.target.value)}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Objective *
                </label>
                <textarea
                  required
                  rows={2}
                  className="cyber-input"
                  style={{ width: '100%', resize: 'vertical' }}
                  placeholder="What question are you attempting to answer or validate?"
                  value={modalObj}
                  onChange={(e) => setModalObj(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Telemetry Dataset
                  </label>
                  <select
                    className="cyber-select"
                    style={{ width: '100%' }}
                    value={modalDatasetId}
                    onChange={(e) => setModalDatasetId(Number(e.target.value))}
                  >
                    {datasets.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name} ({d.event_count} evts)
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Difficulty
                  </label>
                  <select
                    className="cyber-select"
                    style={{ width: '100%' }}
                    value={modalDiff}
                    onChange={(e) => setModalDiff(e.target.value)}
                  >
                    <option value="BEGINNER">BEGINNER</option>
                    <option value="INTERMEDIATE">INTERMEDIATE</option>
                    <option value="ADVANCED">ADVANCED</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Initial Pivot
                  </label>
                  <select
                    className="cyber-select"
                    style={{ width: '100%' }}
                    value={modalPivotType}
                    onChange={(e) => setModalPivotType(e.target.value)}
                  >
                    <option value="IP">IP</option>
                    <option value="DOMAIN">DOMAIN</option>
                    <option value="PORT">PORT</option>
                    <option value="ALERT">ALERT</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Pivot Value (Optional)
                  </label>
                  <input
                    type="text"
                    className="cyber-input"
                    style={{ width: '100%' }}
                    placeholder="e.g. 192.168.1.105 or evil-domain.test"
                    value={modalPivotVal}
                    onChange={(e) => setModalPivotVal(e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  className="btn-cyber-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="btn-cyber-primary"
                >
                  {creating ? 'Creating Session...' : 'Create & Open Workspace'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
