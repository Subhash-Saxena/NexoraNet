import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type { WatchlistItem } from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const WatchlistPage: React.FC = () => {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadWatchlist()
  }, [])

  const loadWatchlist = async () => {
    try {
      setLoading(true)
      const data = await threatIntelApi.getWatchlist()
      setWatchlist(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load watchlist')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (id: number) => {
    try {
      await threatIntelApi.removeFromWatchlist(id)
      setWatchlist((prev) => prev.filter((item) => item.id !== id))
    } catch (err: any) {
      alert(`Failed to remove item: ${err.message}`)
    }
  }

  return (
    <div className="threat-intel-container">
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>👁️ Analyst Indicator Watchlist</h1>
          <p className="threat-intel-subtitle">
            Monitored threat artifacts under elevated observation by SOC analysts.
          </p>
        </div>
      </div>

      <ThreatIntelNav />

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
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading watchlist...</p>
      ) : watchlist.length === 0 ? (
        <div className="ioc-panel" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#94a3b8' }}>No indicators are currently on your watchlist.</p>
          <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
            To monitor an indicator, visit its detail page and click &quot;Watch&quot;.
          </p>
          <Link to="/threat-intelligence/indicators" style={{ color: '#38bdf8' }}>
            Browse Indicators →
          </Link>
        </div>
      ) : (
        <div className="ioc-table-container">
          <table className="ioc-table">
            <thead>
              <tr>
                <th>Indicator</th>
                <th>Type</th>
                <th>Monitoring Reason</th>
                <th>Added By</th>
                <th>Expires</th>
                <th>Date Added</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {watchlist.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link
                      to={`/threat-intelligence/indicators/${item.indicator_id}`}
                      style={{
                        fontFamily: 'monospace',
                        color: '#38bdf8',
                        textDecoration: 'none',
                        fontWeight: 600,
                      }}
                    >
                      {item.indicator?.display_value || `IOC #${item.indicator_id}`}
                    </Link>
                  </td>
                  <td>
                    <span className="ioc-badge ioc-badge-type">
                      {item.indicator?.indicator_type || 'IOC'}
                    </span>
                  </td>
                  <td style={{ maxWidth: '300px' }}>{item.reason}</td>
                  <td style={{ color: '#94a3b8' }}>{item.added_by}</td>
                  <td style={{ color: '#64748b', fontSize: '0.8rem' }}>
                    {item.expires_at ? new Date(item.expires_at).toLocaleDateString() : 'Never'}
                  </td>
                  <td style={{ color: '#64748b', fontSize: '0.8rem' }}>
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <button
                      onClick={() => handleRemove(item.id)}
                      style={{
                        background: 'rgba(239, 68, 68, 0.2)',
                        color: '#f87171',
                        border: '1px solid rgba(239, 68, 68, 0.4)',
                        padding: '0.25rem 0.6rem',
                        borderRadius: '0.25rem',
                        cursor: 'pointer',
                        fontSize: '0.75rem',
                      }}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
