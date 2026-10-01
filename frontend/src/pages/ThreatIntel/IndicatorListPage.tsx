import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type { IndicatorBrief, IndicatorType } from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const IndicatorListPage: React.FC = () => {
  const [indicators, setIndicators] = useState<IndicatorBrief[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [classFilter, setClassFilter] = useState<string>('')
  const [search, setSearch] = useState<string>('')

  // New IOC Modal
  const [showAddModal, setShowAddModal] = useState(false)
  const [newVal, setNewVal] = useState('')
  const [newType, setNewType] = useState<string>('')
  const [newDesc, setNewDesc] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadIndicators()
  }, [typeFilter, classFilter, search])

  const loadIndicators = async () => {
    try {
      setLoading(true)
      const data = await threatIntelApi.listIndicators({
        indicator_type: typeFilter || undefined,
        classification: classFilter || undefined,
        search: search.trim() || undefined,
        limit: 100,
      })
      setIndicators(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load indicators')
    } finally {
      setLoading(false)
    }
  }

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newVal.trim()) return

    try {
      setSubmitting(true)
      await threatIntelApi.createIndicator({
        raw_value: newVal.trim(),
        indicator_type: (newType as IndicatorType) || null,
        description: newDesc.trim() || undefined,
      })
      setShowAddModal(false)
      setNewVal('')
      setNewType('')
      setNewDesc('')
      await loadIndicators()
    } catch (err: any) {
      alert(`Failed to add indicator: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="threat-intel-container">
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>🎯 Indicators of Compromise (IOCs)</h1>
          <p className="threat-intel-subtitle">
            Repository of observed IPs, domains, hashes, URLs, and emails.
          </p>
        </div>
        <div className="threat-intel-actions">
          <button
            onClick={() => setShowAddModal(true)}
            style={{
              background: '#0284c7',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.875rem',
            }}
          >
            + Ingest New IOC
          </button>
        </div>
      </div>

      <ThreatIntelNav />

      {/* Filter Bar */}
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
          marginBottom: '1.5rem',
          background: '#1e293b',
          padding: '1rem',
          borderRadius: '0.5rem',
          border: '1px solid #334155',
          alignItems: 'center',
        }}
      >
        <div style={{ flex: '1 1 250px' }}>
          <input
            type="text"
            placeholder="Search indicator value, ID, or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '0.375rem',
              color: '#f8fafc',
              fontSize: '0.875rem',
            }}
          />
        </div>

        <div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '0.375rem',
              color: '#f8fafc',
              fontSize: '0.875rem',
            }}
          >
            <option value="">All Types</option>
            <option value="IP_ADDRESS">IP Address</option>
            <option value="DOMAIN">Domain</option>
            <option value="URL">URL</option>
            <option value="FILE_HASH">File Hash</option>
            <option value="EMAIL_ADDRESS">Email Address</option>
          </select>
        </div>

        <div>
          <select
            value={classFilter}
            onChange={(e) => setClassFilter(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '0.375rem',
              color: '#f8fafc',
              fontSize: '0.875rem',
            }}
          >
            <option value="">All Classifications</option>
            <option value="MALICIOUS">Malicious</option>
            <option value="SUSPICIOUS">Suspicious</option>
            <option value="BENIGN">Benign</option>
            <option value="FALSE_POSITIVE">False Positive</option>
            <option value="UNKNOWN">Unknown</option>
          </select>
        </div>
      </div>

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

      {loading ? (
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading indicators...</p>
      ) : indicators.length === 0 ? (
        <div className="ioc-panel" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#94a3b8' }}>No indicators match the selected criteria.</p>
        </div>
      ) : (
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
                <th>Status</th>
                <th>Last Seen</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {indicators.map((ind) => {
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
                    <td>
                      <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{ind.status}</span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {ind.last_seen ? new Date(ind.last_seen).toLocaleDateString() : '—'}
                    </td>
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
      )}

      {/* Add IOC Modal */}
      {showAddModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              width: '100%',
              maxWidth: '500px',
              color: '#f8fafc',
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: '1rem' }}>Ingest Threat Indicator</h3>
            <form onSubmit={handleAddSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Raw Indicator Value (IP, Domain, URL, Hash, Email):
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 198.51.100.25 or hxxp://bad[.]test"
                  value={newVal}
                  onChange={(e) => setNewVal(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Explicit Type (Optional - Auto-detected if blank):
                </label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                >
                  <option value="">Auto-Detect</option>
                  <option value="IP_ADDRESS">IP Address</option>
                  <option value="DOMAIN">Domain</option>
                  <option value="URL">URL</option>
                  <option value="FILE_HASH">File Hash</option>
                  <option value="EMAIL_ADDRESS">Email Address</option>
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>
                  Investigative Notes / Context:
                </label>
                <textarea
                  rows={3}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Reason for ingestion, source artifact, or sensor location..."
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '0.375rem',
                    color: '#f8fafc',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{
                    background: '#334155',
                    color: '#f8fafc',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    background: '#0284c7',
                    color: '#fff',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontWeight: 600,
                  }}
                >
                  {submitting ? 'Ingesting...' : 'Ingest & Enrich'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
