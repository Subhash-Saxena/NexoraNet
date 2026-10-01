import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type { ThreatIntelOverview, ThreatIntelSource } from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const ThreatIntelDashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<ThreatIntelOverview | null>(null)
  const [sources, setSources] = useState<ThreatIntelSource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)
  const [importMsg, setImportMsg] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [ovData, srcData] = await Promise.all([
        threatIntelApi.getOverview(),
        threatIntelApi.getSources(),
      ])
      setOverview(ovData)
      setSources(srcData)
    } catch (err: any) {
      setError(err.message || 'Failed to load Threat Intelligence data')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const blob = await threatIntelApi.exportIndicators(format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `nexoranet_threat_intel.${format}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      alert(`Export failed: ${err.message}`)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      setImporting(true)
      setImportMsg(null)
      const res = await threatIntelApi.importIndicators(file)
      setImportMsg(`Successfully imported ${res.imported} indicators (${res.skipped} skipped).`)
      await loadData()
    } catch (err: any) {
      setImportMsg(`Import failed: ${err.message}`)
    } finally {
      setImporting(false)
      e.target.value = ''
    }
  }

  if (loading) {
    return (
      <div className="threat-intel-container">
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Loading Threat Intelligence Platform...
        </p>
      </div>
    )
  }

  return (
    <div className="threat-intel-container">
      {/* Header */}
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>🛡️ Threat Intelligence & IOC Investigation</h1>
          <p className="threat-intel-subtitle">
            Catalog, normalize, enrich, and correlate threat artifacts against operational telemetry.
          </p>
        </div>
        <div className="threat-intel-actions">
          <label
            style={{
              background: '#334155',
              color: '#f8fafc',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            📥 Import IOCs
            <input
              type="file"
              accept=".json,.csv,.jsonl,.ndjson"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              disabled={importing}
            />
          </label>
          <button
            onClick={() => handleExport('json')}
            style={{
              background: '#0284c7',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            📤 Export JSON
          </button>
          <button
            onClick={() => handleExport('csv')}
            style={{
              background: '#047857',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            📤 Export CSV
          </button>
        </div>
      </div>

      <ThreatIntelNav />

      {importMsg && (
        <div
          style={{
            background: importMsg.includes('failed') ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
            border: `1px solid ${importMsg.includes('failed') ? '#ef4444' : '#10b981'}`,
            color: '#f8fafc',
            padding: '0.75rem 1.25rem',
            borderRadius: '0.5rem',
            marginBottom: '1.5rem',
          }}
        >
          {importMsg}
        </div>
      )}

      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid #ef4444',
            color: '#f8fafc',
            padding: '1rem',
            borderRadius: '0.5rem',
            marginBottom: '1.5rem',
          }}
        >
          {error}
        </div>
      )}

      {/* Educational Banner */}
      <div className="educational-callout">
        <strong>SOC Analyst Directive:</strong> In NexoraNet, Indicators of Compromise (IOCs) represent observable data,
        never automated proof of breach. Always evaluate <em>source reliability</em>, consider <em>reputation confidence</em>,
        and corroborate with observed packet telemetry. <strong>Unknown ≠ Benign.</strong>
      </div>

      {/* Stats Grid */}
      <div className="threat-intel-stats-grid">
        <div className="threat-stat-card">
          <div className="threat-stat-label">Total Cataloged IOCs</div>
          <div className="threat-stat-value">{overview?.total_indicators || 0}</div>
          <div className="threat-stat-footer">Across all 5 indicator types</div>
        </div>

        <div className="threat-stat-card">
          <div className="threat-stat-label">Confirmed Malicious</div>
          <div className="threat-stat-value" style={{ color: '#f87171' }}>
            {overview?.by_classification['MALICIOUS'] || 0}
          </div>
          <div className="threat-stat-footer">High-fidelity active threats</div>
        </div>

        <div className="threat-stat-card">
          <div className="threat-stat-label">Suspicious / Under Review</div>
          <div className="threat-stat-value" style={{ color: '#fbbf24' }}>
            {overview?.by_classification['SUSPICIOUS'] || 0}
          </div>
          <div className="threat-stat-footer">Candidate triage items</div>
        </div>

        <div className="threat-stat-card">
          <div className="threat-stat-label">Active Watchlist Items</div>
          <div className="threat-stat-value" style={{ color: '#38bdf8' }}>
            {overview?.active_watchlists || 0}
          </div>
          <div className="threat-stat-footer">Monitored by analysts</div>
        </div>

        <div className="threat-stat-card">
          <div className="threat-stat-label">Hands-On Challenges</div>
          <div className="threat-stat-value" style={{ color: '#a855f7' }}>
            {overview?.total_challenges || 0}
          </div>
          <div className="threat-stat-footer">5 SOC practice scenarios</div>
        </div>
      </div>

      {/* Breakdown Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="ioc-panel">
          <h3 className="ioc-panel-title">Indicator Distribution by Type</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {overview &&
              Object.entries(overview.by_type).map(([type, count]) => (
                <div key={type} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="ioc-badge ioc-badge-type">{type}</span>
                  <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{count}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="ioc-panel">
          <h3 className="ioc-panel-title">Reputation Classifications</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {overview &&
              Object.entries(overview.by_classification).map(([cls, count]) => {
                let badgeCls = 'ioc-badge-unknown'
                if (cls === 'MALICIOUS') badgeCls = 'ioc-badge-malicious'
                else if (cls === 'SUSPICIOUS') badgeCls = 'ioc-badge-suspicious'
                else if (cls === 'BENIGN') badgeCls = 'ioc-badge-benign'
                else if (cls === 'FALSE_POSITIVE') badgeCls = 'ioc-badge-false-positive'

                return (
                  <div key={cls} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className={`ioc-badge ${badgeCls}`}>{cls}</span>
                    <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{count}</span>
                  </div>
                )
              })}
          </div>
        </div>

        <div className="ioc-panel">
          <h3 className="ioc-panel-title">Intelligence Sources</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {sources.map((src) => (
              <div key={src.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                <span style={{ color: '#cbd5e1' }}>{src.name}</span>
                <span className={`confidence-pill confidence-${src.reliability.toLowerCase()}`}>
                  {src.reliability}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Indicators Table */}
      <div className="ioc-panel">
        <div className="ioc-panel-title">
          <span>Recent Observable Threat Indicators</span>
          <Link
            to="/threat-intelligence/indicators"
            style={{ color: '#38bdf8', fontSize: '0.85rem', textDecoration: 'none' }}
          >
            View All Indicators →
          </Link>
        </div>

        <div className="ioc-table-container">
          <table className="ioc-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Indicator Value</th>
                <th>Classification</th>
                <th>Confidence</th>
                <th>Severity</th>
                <th>Source</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {overview?.recent_indicators.map((ind) => {
                let clsBadge = 'ioc-badge-unknown'
                if (ind.classification === 'MALICIOUS') clsBadge = 'ioc-badge-malicious'
                else if (ind.classification === 'SUSPICIOUS') clsBadge = 'ioc-badge-suspicious'
                else if (ind.classification === 'BENIGN') clsBadge = 'ioc-badge-benign'
                else if (ind.classification === 'FALSE_POSITIVE') clsBadge = 'ioc-badge-false-positive'

                return (
                  <tr key={ind.id}>
                    <td>
                      <span style={{ fontFamily: 'monospace', color: '#94a3b8' }}>{ind.indicator_id}</span>
                    </td>
                    <td>
                      <span className="ioc-badge ioc-badge-type">{ind.indicator_type}</span>
                    </td>
                    <td>
                      <div className="ioc-value-cell" title={ind.display_value}>
                        {ind.display_value}
                      </div>
                    </td>
                    <td>
                      <span className={`ioc-badge ${clsBadge}`}>{ind.classification}</span>
                    </td>
                    <td>
                      <span className={`confidence-pill confidence-${ind.confidence.toLowerCase()}`}>
                        {ind.confidence}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{ind.severity}</span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{ind.source_name}</td>
                    <td>
                      <Link
                        to={`/threat-intelligence/indicators/${ind.id}`}
                        style={{
                          background: '#334155',
                          color: '#f8fafc',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.25rem',
                          textDecoration: 'none',
                          fontSize: '0.75rem',
                        }}
                      >
                        Investigate
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
