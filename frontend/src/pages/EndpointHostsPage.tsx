import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { EndpointNav } from '../components/endpoint_security/EndpointNav'
import type { EndpointHost } from '../types/endpointSecurity'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import '../components/endpoint_security/endpointSecurity.css'

export const EndpointHostsPage: React.FC = () => {
  const [hosts, setHosts] = useState<EndpointHost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [platform, setPlatform] = useState<string>('')
  const [riskLevel, setRiskLevel] = useState<string>('')
  const [search, setSearch] = useState<string>('')

  const fetchHosts = async () => {
    try {
      setLoading(true)
      const data = await endpointSecurityApi.listHosts({
        platform: platform || undefined,
        risk_level: riskLevel || undefined,
        search: search || undefined,
      })
      setHosts(data.items)
    } catch (err: any) {
      console.error('Failed to list hosts:', err)
      setError(err.message || 'Failed to fetch host inventory')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHosts()
  }, [platform, riskLevel])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    fetchHosts()
  }

  return (
    <div className="endpoint-container">
      {/* Synthetic Warning */}
      <div className="endpoint-synthetic-banner">
        <div className="banner-left">
          <span className="banner-icon">🛡️</span>
          <div>
            <div className="banner-title">
              NexoraNet Endpoint Lab — Synthetic Host Inventory
            </div>
            <div className="banner-subtitle">
              All endpoints are simulated hosts with pre-populated telemetry datasets. Zero physical devices are monitored.
            </div>
          </div>
        </div>
        <span className="banner-badge">SYNTHETIC FLEET</span>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
          Endpoint Host Inventory
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
          Select any workstation or server to examine its process hierarchy, authentication history, socket connections, and persistence indicators.
        </p>
      </div>

      <EndpointNav />

      {/* Filter and Search Bar */}
      <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', padding: '1rem', marginBottom: '1.75rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', flex: 1, minWidth: '260px' }}>
          <input
            type="text"
            placeholder="Search hostname, IP, description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 0.85rem',
              color: '#f8fafc',
              fontSize: '0.85rem',
              width: '100%',
            }}
          />
          <button type="submit" className="btn-cyber-primary">
            Search
          </button>
        </form>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 0.75rem',
              color: '#cbd5e1',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All Platforms</option>
            <option value="WINDOWS">Windows</option>
            <option value="LINUX">Linux</option>
            <option value="MACOS">macOS</option>
          </select>

          <select
            value={riskLevel}
            onChange={(e) => setRiskLevel(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 0.75rem',
              color: '#cbd5e1',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All Risk Levels</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="NONE">None</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '8px', padding: '1rem', color: '#fca5a5', marginBottom: '1.5rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#38bdf8' }}>
          Loading host inventory...
        </div>
      ) : hosts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: '#111827', borderRadius: '8px', color: '#64748b' }}>
          No endpoint hosts found matching current filter parameters.
        </div>
      ) : (
        <div className="host-grid">
          {hosts.map((host) => {
            const platClass = host.platform.toLowerCase()
            const riskClass = host.risk_level.toLowerCase()
            return (
              <div key={host.id} className="host-card">
                <div>
                  <div className="host-card-header">
                    <div>
                      <span className="host-card-title">
                        <span className={`status-dot ${host.status.toLowerCase()}`} />
                        {host.hostname}
                      </span>
                      <div className="host-card-sub">{host.display_name || host.environment}</div>
                    </div>
                    <span className={`platform-badge ${platClass}`}>{host.platform}</span>
                  </div>

                  <p style={{ fontSize: '0.825rem', color: '#94a3b8', margin: '0.5rem 0' }}>
                    {host.description || 'Simulated workstation endpoint.'}
                  </p>

                  <div className="host-card-meta">
                    <div className="meta-item">
                      <span className="meta-label">IP Address</span>
                      <span className="meta-val">{host.ip_address}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">MAC Address</span>
                      <span className="meta-val">{host.mac_address}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">OS Version</span>
                      <span className="meta-val">{host.platform_version} ({host.architecture})</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Risk Level</span>
                      <span className={`risk-badge ${riskClass}`} style={{ width: 'fit-content' }}>
                        {host.risk_level}
                      </span>
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                  <Link
                    to={`/endpoint-security/hosts/${host.stable_id}`}
                    className="btn-cyber-primary"
                    style={{ flex: 1, justifyContent: 'center' }}
                  >
                    Investigate Host ➔
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
