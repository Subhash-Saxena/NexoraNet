import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { EndpointNav } from '../components/endpoint_security/EndpointNav'
import type { EndpointHost, EndpointHostSummary } from '../types/endpointSecurity'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import '../components/endpoint_security/endpointSecurity.css'

export const EndpointDashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<EndpointHostSummary | null>(null)
  const [hosts, setHosts] = useState<EndpointHost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [sumData, hostData] = await Promise.all([
          endpointSecurityApi.getOverview(),
          endpointSecurityApi.listHosts({ limit: 6 }),
        ])
        setSummary(sumData)
        setHosts(hostData.items)
      } catch (err: any) {
        console.error('Failed to load endpoint dashboard:', err)
        setError(err.message || 'Failed to connect to endpoint telemetry service')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <div className="endpoint-container">
      {/* Synthetic Training Banner */}
      <div className="endpoint-synthetic-banner">
        <div className="banner-left">
          <span className="banner-icon">🛡️</span>
          <div>
            <div className="banner-title">
              NexoraNet Endpoint Lab — Synthetic Training Environment
            </div>
            <div className="banner-subtitle">
              All host telemetry, processes, files, memory spaces, and network traces are safely simulated for educational analysis.
            </div>
          </div>
        </div>
        <span className="banner-badge">OFFLINE-FIRST SIMULATION</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
          Endpoint Security & Host Investigation Engine
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Investigate endpoint telemetry across processes, parent-child trees, authentication events, network connections, file operations, and persistence mechanisms.
        </p>
      </div>

      <EndpointNav />

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '8px', padding: '1rem', color: '#fca5a5', marginBottom: '1.5rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
          Loading endpoint telemetry overview...
        </div>
      ) : summary ? (
        <>
          {/* KPI Metrics */}
          <div className="endpoint-stats-grid">
            <div className="endpoint-stat-card">
              <div className="stat-label">Monitored Hosts</div>
              <div className="stat-value">{summary.total_hosts}</div>
              <div className="stat-sub">Synthetic Workstations & Servers</div>
            </div>

            <div className="endpoint-stat-card">
              <div className="stat-label">Telemetry Events</div>
              <div className="stat-value">{summary.total_events}</div>
              <div className="stat-sub">Across All Event Categories</div>
            </div>

            <div className="endpoint-stat-card">
              <div className="stat-label">Active Investigations</div>
              <div className="stat-value" style={{ color: '#38bdf8' }}>
                {summary.active_investigations}
              </div>
              <div className="stat-sub">Student Analytical Cases</div>
            </div>

            <div className="endpoint-stat-card">
              <div className="stat-label">Critical / High Risk</div>
              <div className="stat-value" style={{ color: '#f87171' }}>
                {(summary.risk_levels['CRITICAL'] || 0) + (summary.risk_levels['HIGH'] || 0)}
              </div>
              <div className="stat-sub">Requiring Analyst Triage</div>
            </div>
          </div>

          {/* Quick Actions & Educational Workflow */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
            {/* Host Highlights */}
            <div className="investigation-section">
              <div className="section-header">
                <span className="section-title">
                  <span>💻</span> Monitored Hosts in Synthetic Fleet
                </span>
                <Link to="/endpoint-security/hosts" className="btn-cyber-secondary" style={{ fontSize: '0.8rem' }}>
                  View All Hosts ➔
                </Link>
              </div>

              <div className="host-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
                {hosts.map((host) => {
                  const platClass = host.platform.toLowerCase()
                  const riskClass = host.risk_level.toLowerCase()
                  return (
                    <div key={host.id} className="host-card" style={{ padding: '1rem' }}>
                      <div>
                        <div className="host-card-header">
                          <div>
                            <span className="host-card-title" style={{ fontSize: '1rem' }}>
                              <span className={`status-dot ${host.status.toLowerCase()}`} />
                              {host.hostname}
                            </span>
                            <div className="host-card-sub">{host.display_name || host.environment}</div>
                          </div>
                          <span className={`platform-badge ${platClass}`}>{host.platform}</span>
                        </div>

                        <div className="host-card-meta" style={{ margin: '0.5rem 0' }}>
                          <div className="meta-item">
                            <span className="meta-label">IP Address</span>
                            <span className="meta-val">{host.ip_address}</span>
                          </div>
                          <div className="meta-item">
                            <span className="meta-label">Risk Level</span>
                            <span className={`risk-badge ${riskClass}`} style={{ width: 'fit-content' }}>
                              {host.risk_level}
                            </span>
                          </div>
                        </div>
                      </div>

                      <Link
                        to={`/endpoint-security/hosts/${host.stable_id}`}
                        className="btn-cyber-primary"
                        style={{ width: '100%', justifyContent: 'center', marginTop: '0.75rem', fontSize: '0.8rem' }}
                      >
                        Open Workbench ➔
                      </Link>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Educational SOC Guidance Card */}
            <div className="investigation-section" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div className="section-header">
                  <span className="section-title">
                    <span>🎓</span> Host Investigation Methodology
                  </span>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
                  In modern SOC workflows, an endpoint investigation is an analytical process to prove or refute a hypothesis:
                </p>

                <div style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.85rem', margin: '1rem 0', fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: '#38bdf8', lineHeight: 1.7 }}>
                  HOST<br />
                  &nbsp;&nbsp;↓ TELEMETRY<br />
                  &nbsp;&nbsp;↓ PROCESS TREE<br />
                  &nbsp;&nbsp;↓ HYPOTHESIS FORMATION<br />
                  &nbsp;&nbsp;↓ EVIDENCE COLLECTION<br />
                  &nbsp;&nbsp;↓ CONCLUSION & VERDICT
                </div>

                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Begin by investigating suspicious process executions, checking network egress, and identifying persistence artifacts.
                </div>
              </div>

              <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <Link to="/endpoint-security/scenarios" className="btn-cyber-primary" style={{ justifyContent: 'center' }}>
                  🎯 Launch Guided Investigation Scenarios
                </Link>
                <Link to="/endpoint-security/events" className="btn-cyber-secondary" style={{ justifyContent: 'center' }}>
                  📋 Search All Telemetry Events
                </Link>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  )
}
