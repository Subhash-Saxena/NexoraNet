import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { SocAlertItem } from '../../types/soc'
import '../../components/soc/soc.css'


export const AnalystQueuePage: React.FC = () => {
  const [alerts, setAlerts] = useState<SocAlertItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [activeTab, setActiveTab] = useState<'P1' | 'P2' | 'UNREVIEWED' | 'ALL'>('P1')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const fetchQueueAlerts = async () => {
    try {
      setLoading(true)
      let pFilter: string | undefined = undefined
      let cFilter: string | undefined = undefined

      if (activeTab === 'P1') pFilter = 'P1'
      else if (activeTab === 'P2') pFilter = 'P2'
      else if (activeTab === 'UNREVIEWED') cFilter = 'UNREVIEWED'

      const data = await socApi.listAlerts({
        priority: pFilter,
        classification: cFilter,
        limit: 50,
      })
      setAlerts(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analyst queue.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQueueAlerts()
  }, [activeTab])

  const handleAcknowledge = async (id: number) => {
    try {
      await socApi.acknowledgeAlert(id, 'Analyst acknowledged alert from queue workbench.')
      setMessage(`Alert #${id} acknowledged.`)
      await fetchQueueAlerts()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to acknowledge alert.')
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

  return (
    <div className="soc-container">
      <SocHeader
        title="Analyst Workbench Queue"
        subtitle="Prioritized operational triage queue for active triage and immediate investigation"
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

      {/* Queue View Switcher */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--soc-border)', paddingBottom: '0.5rem' }}>
        <button
          className={`soc-btn ${activeTab === 'P1' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
          onClick={() => setActiveTab('P1')}
        >
          🚨 P1 Critical Queue
        </button>
        <button
          className={`soc-btn ${activeTab === 'P2' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
          onClick={() => setActiveTab('P2')}
        >
          ⚠️ P2 High Queue
        </button>
        <button
          className={`soc-btn ${activeTab === 'UNREVIEWED' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
          onClick={() => setActiveTab('UNREVIEWED')}
        >
          🔍 Unreviewed Alerts
        </button>
        <button
          className={`soc-btn ${activeTab === 'ALL' ? 'soc-btn-primary' : 'soc-btn-secondary'}`}
          onClick={() => setActiveTab('ALL')}
        >
          📋 All Work Items
        </button>
      </div>

      {/* Queue Card */}
      <div className="soc-card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
            Loading analyst queue items...
          </div>
        ) : alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
            No alerts pending in the {activeTab} queue. Outstanding triage targets cleared!
          </div>
        ) : (
          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Priority</th>
                  <th>Alert Title</th>
                  <th>Severity</th>
                  <th>Source IP</th>
                  <th>Target IP</th>
                  <th>Packets</th>
                  <th>Status</th>
                  <th>Triage Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => (
                  <tr key={a.id}>
                    <td>{getPriorityBadge(a.priority)}</td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)' }}>{a.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                        {a.rule_code || 'DETECTION'} • {a.protocol || 'IP'}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{a.severity}</span>
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {a.source_ip || '*'}:{a.source_port || '*'}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {a.destination_ip || '*'}:{a.destination_port || '*'}
                    </td>
                    <td>
                      <span style={{ fontSize: '0.82rem' }}>{a.packet_count ?? 1} pkts</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: 'var(--soc-text-secondary)' }}>{a.status}</span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        {a.status === 'NEW' && (
                          <button
                            className="soc-btn soc-btn-secondary"
                            style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                            onClick={() => handleAcknowledge(a.id)}
                          >
                            Ack
                          </button>
                        )}
                        <Link
                          to={`/soc/alerts/${a.id}/triage`}
                          className="soc-btn soc-btn-primary"
                          style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                        >
                          Triage →
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
    </div>
  )
}
