import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type { IndicatorBrief } from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const ThreatIntelSearchPage: React.FC = () => {
  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [classFilter, setClassFilter] = useState('')
  const [results, setResults] = useState<IndicatorBrief[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    try {
      setLoading(true)
      setError(null)
      const data = await threatIntelApi.search(
        query.trim(),
        typeFilter || undefined,
        classFilter || undefined
      )
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="threat-intel-container">
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>🔍 Threat Intelligence Search & OSINT</h1>
          <p className="threat-intel-subtitle">
            Query local threat intelligence database for historical indicators, reputation ratings, and campaign attribution.
          </p>
        </div>
      </div>

      <ThreatIntelNav />

      {/* Search Input Box */}
      <div className="ioc-panel">
        <form onSubmit={handleSearch}>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <div style={{ flex: '1 1 300px' }}>
              <input
                type="text"
                required
                placeholder="Enter IP, domain, hash, URL, email, or keyword..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.375rem',
                  color: '#f8fafc',
                  fontSize: '1rem',
                }}
              />
            </div>

            <div>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                style={{
                  padding: '0.75rem',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.375rem',
                  color: '#f8fafc',
                }}
              >
                <option value="">Any Type</option>
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
                  padding: '0.75rem',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.375rem',
                  color: '#f8fafc',
                }}
              >
                <option value="">Any Classification</option>
                <option value="MALICIOUS">Malicious</option>
                <option value="SUSPICIOUS">Suspicious</option>
                <option value="BENIGN">Benign</option>
                <option value="FALSE_POSITIVE">False Positive</option>
                <option value="UNKNOWN">Unknown</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              style={{
                background: '#0ea5e9',
                color: '#fff',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.95rem',
              }}
            >
              {loading ? 'Searching...' : 'Search Intelligence'}
            </button>
          </div>
        </form>
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

      {/* Results */}
      {results !== null && (
        <div className="ioc-panel">
          <h3 className="ioc-panel-title">
            Search Results ({results.length} found)
          </h3>

          {results.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
              <p>No matching intelligence found for &quot;{query}&quot;.</p>
              <p style={{ fontSize: '0.85rem' }}>
                Note: In defensive SOC operations, lack of threat intelligence does NOT prove an artifact is benign.
                (Unknown ≠ Benign).
              </p>
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
                    <th>Source</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((ind) => {
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
          )}
        </div>
      )}
    </div>
  )
}
