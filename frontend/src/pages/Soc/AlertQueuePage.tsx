import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { SocHeader } from '../../components/soc/SocHeader'
import { socApi } from '../../services/socApi'
import type { SocAlertItem, TriageClassification } from '../../types/soc'
import '../../components/soc/soc.css'


export const AlertQueuePage: React.FC = () => {
  const [alerts, setAlerts] = useState<SocAlertItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [selectedAlertIds, setSelectedAlertIds] = useState<number[]>([])

  // Filters
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [classificationFilter, setClassificationFilter] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Bulk action state
  const [bulkAction, setBulkAction] = useState<string>('ACKNOWLEDGE')
  const [bulkClassification, setBulkClassification] = useState<TriageClassification>('BENIGN')
  const [bulkReason, setBulkReason] = useState<string>('Bulk triage by analyst.')
  const [bulkProcessing, setBulkProcessing] = useState<boolean>(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const data = await socApi.listAlerts({
        priority: priorityFilter || undefined,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        classification: classificationFilter || undefined,
        category: categoryFilter || undefined,
        q: searchQuery || undefined,
        limit: 100,
      })
      setAlerts(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [priorityFilter, severityFilter, statusFilter, classificationFilter, categoryFilter])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchAlerts()
  }

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedAlertIds(alerts.map((a) => a.id))
    } else {
      setSelectedAlertIds([])
    }
  }

  const handleToggleSelect = (id: number) => {
    setSelectedAlertIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )
  }

  const handleExecuteBulkAction = async () => {
    if (selectedAlertIds.length === 0) return
    try {
      setBulkProcessing(true)
      setMessage(null)
      setError(null)
      const res = await socApi.bulkAlertAction({
        alert_ids: selectedAlertIds,
        action: bulkAction as 'ACKNOWLEDGE' | 'ASSIGN' | 'CLOSE' | 'SET_CLASSIFICATION',
        classification: bulkAction === 'SET_CLASSIFICATION' ? bulkClassification : undefined,
        reason: bulkReason,
      })
      setMessage(`Bulk operation completed: modified ${res.modified_count} alerts.`)
      setSelectedAlertIds([])
      await fetchAlerts()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Bulk action failed.')
    } finally {
      setBulkProcessing(false)
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
        title="Alert Queue & Triage Workbench"
        subtitle="Filter, prioritize, inspect evidence, and classify detected network anomalies"
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

      {/* Filter Toolbar */}
      <div className="soc-card" style={{ padding: '1rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="text"
            className="soc-input"
            placeholder="Search alerts (rule, title, IP, keyword)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ minWidth: '240px', flex: 1 }}
          />

          <select
            className="soc-select"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            aria-label="Priority Filter"
          >
            <option value="">All Priorities</option>
            <option value="P1">P1 Critical</option>
            <option value="P2">P2 High</option>
            <option value="P3">P3 Medium</option>
            <option value="P4">P4 Low</option>
          </select>

          <select
            className="soc-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            aria-label="Severity Filter"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Info</option>
          </select>

          <select
            className="soc-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Status Filter"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CLOSED">Closed</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>

          <select
            className="soc-select"
            value={classificationFilter}

            onChange={(e) => setClassificationFilter(e.target.value)}
            aria-label="Classification Filter"
          >
            <option value="">All Classifications</option>
            <option value="UNREVIEWED">Unreviewed</option>
            <option value="BENIGN">Benign</option>
            <option value="SUSPICIOUS">Suspicious</option>
            <option value="FALSE_POSITIVE">False Positive</option>
            <option value="REQUIRES_MORE_DATA">Requires More Data</option>
            <option value="CLOSED">Closed</option>
          </select>

          <select
            className="soc-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Category Filter"
          >
            <option value="">All Categories</option>
            <option value="TCP">TCP</option>
            <option value="UDP">UDP</option>
            <option value="DNS">DNS</option>
            <option value="ARP">ARP</option>
            <option value="ICMP">ICMP</option>
            <option value="HTTP">HTTP</option>
          </select>

          <button type="submit" className="soc-btn soc-btn-primary">
            Apply Filter
          </button>

          {(priorityFilter || severityFilter || classificationFilter || categoryFilter || searchQuery) && (
            <button
              type="button"
              className="soc-btn soc-btn-secondary"
              onClick={() => {
                setPriorityFilter('')
                setSeverityFilter('')
                setClassificationFilter('')
                setCategoryFilter('')
                setSearchQuery('')
              }}
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {/* Bulk Action Bar */}
      {selectedAlertIds.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '6px', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ fontSize: '0.9rem', color: '#38bdf8', fontWeight: 600 }}>
            {selectedAlertIds.length} alert{selectedAlertIds.length > 1 ? 's' : ''} selected
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <select
              className="soc-select"
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
              aria-label="Bulk Action Selector"
            >
              <option value="ACKNOWLEDGE">Acknowledge</option>
              <option value="SET_CLASSIFICATION">Set Classification</option>
              <option value="CLOSE">Close</option>
            </select>

            {bulkAction === 'SET_CLASSIFICATION' && (
              <select
                className="soc-select"
                value={bulkClassification}
                onChange={(e) => setBulkClassification(e.target.value as TriageClassification)}
                aria-label="Bulk Classification Selector"
              >
                <option value="BENIGN">Benign</option>
                <option value="SUSPICIOUS">Suspicious</option>
                <option value="FALSE_POSITIVE">False Positive</option>
                <option value="REQUIRES_MORE_DATA">Requires More Data</option>
                <option value="CLOSED">Closed</option>
              </select>
            )}

            <input
              type="text"
              className="soc-input"
              placeholder="Reason for triage log..."
              value={bulkReason}
              onChange={(e) => setBulkReason(e.target.value)}
              style={{ width: '200px' }}
            />

            <button
              className="soc-btn soc-btn-primary"
              onClick={handleExecuteBulkAction}
              disabled={bulkProcessing}
            >
              {bulkProcessing ? 'Applying...' : 'Apply Bulk Action'}
            </button>
          </div>
        </div>
      )}

      {/* Alerts Table */}
      <div className="soc-card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-secondary)' }}>
            Filtering and loading alerts...
          </div>
        ) : alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--soc-text-muted)' }}>
            No alerts found matching your criteria. Try adjusting filters or reloading a dataset from the overview.
          </div>
        ) : (
          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={selectedAlertIds.length === alerts.length && alerts.length > 0}
                      onChange={handleSelectAll}
                      aria-label="Select all alerts"
                    />
                  </th>
                  <th>Priority</th>
                  <th>Alert Title & Rule</th>
                  <th>Severity</th>
                  <th>Classification</th>
                  <th>Status</th>
                  <th>Source → Destination</th>
                  <th>Packets</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => (
                  <tr key={a.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedAlertIds.includes(a.id)}
                        onChange={() => handleToggleSelect(a.id)}
                        aria-label={`Select alert ${a.id}`}
                      />
                    </td>
                    <td>
                      {getPriorityBadge(a.priority)}
                      {a.priority_reason && (
                        <div style={{ fontSize: '0.72rem', color: 'var(--soc-text-muted)', marginTop: '0.2rem', maxWidth: '140px' }}>
                          {a.priority_reason}
                        </div>
                      )}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--soc-text-primary)' }}>{a.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--soc-text-muted)' }}>
                        {a.rule_code || 'DETECTION'} • Confidence: {a.confidence}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{a.severity}</span>
                    </td>
                    <td>{getClassificationBadge(a.classification)}</td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--soc-text-secondary)' }}>{a.status}</span>
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {a.source_ip || '*'}:{a.source_port || '*'} → {a.destination_ip || '*'}:{a.destination_port || '*'}
                    </td>
                    <td>
                      <span style={{ fontSize: '0.82rem' }}>{a.packet_count ?? 1} pkts</span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
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
    </div>
  )
}
