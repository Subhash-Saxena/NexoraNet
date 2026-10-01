import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  Bookmark,
  ExternalLink,
  Filter,
  Plus,
  RefreshCw,
  Search,
  Shield,
  Trash2,
  X,
} from 'lucide-react'
import { SiemNav } from '../components/siem/SiemNav'
import { siemApi } from '../services/siemApi'
import type {
  QueryCondition,
  SavedSearch,
  SecurityEvent,
  SecurityEventDetail,
  SecurityLogDataset,
  SiemSearchRequest,
  SiemSearchResponse,
} from '../types/siem'
import '../components/siem/siem.css'

export const SiemSearchPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  // State
  const [datasets, setDatasets] = useState<SecurityLogDataset[]>([])
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | undefined>(undefined)
  const [searchText, setSearchText] = useState<string>('')
  const [timePreset, setTimePreset] = useState<string>('ALL')
  const [logicalOp, setLogicalOp] = useState<'AND' | 'OR'>('AND')
  const [conditions, setConditions] = useState<QueryCondition[]>([])
  const [activeQuickFilter, setActiveQuickFilter] = useState<string | null>(null)

  const [searchResults, setSearchResults] = useState<SiemSearchResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  // Drawer
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null)
  const [eventDetail, setEventDetail] = useState<SecurityEventDetail | null>(null)
  const [drawerLoading, setDrawerLoading] = useState<boolean>(false)

  // Saved Searches
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [showSavedModal, setShowSavedModal] = useState<boolean>(false)
  const [saveName, setSaveName] = useState<string>('')

  // Escalation feedback
  const [escalationFeedback, setEscalationFeedback] = useState<string | null>(null)

  const executeSearch = async (overrideConditions?: QueryCondition[]) => {
    try {
      setLoading(true)
      setError(null)
      const req: SiemSearchRequest = {
        dataset_id: selectedDatasetId,
        conditions: overrideConditions || (conditions.length > 0 ? conditions : undefined),
        logical_op: logicalOp,
        search_text: searchText.trim() || undefined,
        time_preset: timePreset,
        quick_filter: activeQuickFilter || undefined,
        limit: 50,
      }
      const data = await siemApi.searchEvents(req)
      setSearchResults(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  // Load datasets and execute initial search on mount
  useEffect(() => {
    siemApi.listDatasets().then(setDatasets).catch(() => {})
    siemApi.listSavedSearches().then(setSavedSearches).catch(() => {})

    // URL query params pre-fill (e.g. ?field=source_ip&value=192.0.2.1)
    const sp = new URLSearchParams(location.search)
    const qField = sp.get('field')
    const qVal = sp.get('value')
    if (qField && qVal) {
      const initConds: QueryCondition[] = [{ field: qField, operator: '=', value: qVal }]
      setConditions(initConds)
      executeSearch(initConds)
    } else {
      executeSearch()
    }
  }, [])

  // Quick filters
  const handleQuickFilter = (filterKey: string, conds: QueryCondition[]) => {
    if (activeQuickFilter === filterKey) {
      setActiveQuickFilter(null)
      setConditions([])
      executeSearch([])
    } else {
      setActiveQuickFilter(filterKey)
      setConditions(conds)
      executeSearch(conds)
    }
  }

  // Condition Builder
  const addCondition = () => {
    setConditions([...conditions, { field: 'action', operator: '=', value: '' }])
  }

  const removeCondition = (index: number) => {
    const updated = conditions.filter((_, idx) => idx !== index)
    setConditions(updated)
  }

  const updateCondition = (index: number, key: keyof QueryCondition, val: string) => {
    const updated = [...conditions]
    updated[index] = { ...updated[index], [key]: val }
    setConditions(updated)
  }

  // Drawer event fetch
  const handleSelectEvent = async (event: SecurityEvent) => {
    setSelectedEventId(event.event_id)
    try {
      setDrawerLoading(true)
      const detail = await siemApi.getEvent(event.event_id)
      setEventDetail(detail)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load event details')
    } finally {
      setDrawerLoading(false)
    }
  }

  // Escalations
  const handleInvestigateInSoc = async () => {
    if (!selectedEventId) return
    try {
      const res = await siemApi.investigateInSoc(selectedEventId)
      if (res.redirect_url) {
        navigate(res.redirect_url)
      } else {
        setEscalationFeedback(`Escalated to SOC: ${res.investigation_code}`)
      }
    } catch (err: unknown) {
      setEscalationFeedback(`SOC escalation error: ${err instanceof Error ? err.message : 'Unknown'}`)
    }
  }

  const handleStartThreatHunt = async () => {
    if (!selectedEventId) return
    try {
      const res = await siemApi.startThreatHunt(selectedEventId, undefined, 'Anomalous log telemetry investigation')
      if (res.redirect_url) {
        navigate(res.redirect_url)
      } else {
        setEscalationFeedback(`Threat hunt created: ${res.hunt_code}`)
      }
    } catch (err: unknown) {
      setEscalationFeedback(`Hunt creation error: ${err instanceof Error ? err.message : 'Unknown'}`)
    }
  }

  const handleExtractIoc = async () => {
    if (!selectedEventId) return
    try {
      const res = await siemApi.extractIoc(selectedEventId)
      const count = res.extracted_iocs?.length || 0
      setEscalationFeedback(`Extracted and linked ${count} candidate IOC(s) into Step 13 Threat Intel!`)
    } catch (err: unknown) {
      setEscalationFeedback(`IOC extraction failed: ${err instanceof Error ? err.message : 'Unknown'}`)
    }
  }

  // Save search
  const handleSaveSearch = async () => {
    if (!saveName.trim()) return
    try {
      const queryDef = {
        conditions,
        logical_op: logicalOp,
        search_text: searchText,
        dataset_id: selectedDatasetId,
      }
      await siemApi.createSavedSearch({
        name: saveName.trim(),
        query_definition: queryDef,
      })
      setShowSavedModal(false)
      setSaveName('')
      const updated = await siemApi.listSavedSearches()
      setSavedSearches(updated)
    } catch (err: unknown) {
      window.alert(`Save failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  const handleLoadSavedSearch = (saved: SavedSearch) => {
    try {
      const q = JSON.parse(saved.query_definition)
      if (q.conditions) setConditions(q.conditions)
      if (q.logical_op) setLogicalOp(q.logical_op)
      if (q.search_text !== undefined) setSearchText(q.search_text)
      if (q.dataset_id) setSelectedDatasetId(q.dataset_id)
      executeSearch(q.conditions)
    } catch {
      window.alert('Unable to parse saved search query')
    }
  }

  return (
    <div className="siem-container">
      {/* Header */}
      <div className="siem-header">
        <div className="siem-header-left">
          <div className="siem-title-row">
            <h1>
              <Search className="text-cyan-400" size={26} />
              SIEM Log Search & Analytics
            </h1>
            <span className="siem-tag">QUERY BUILDER</span>
          </div>
          <p className="siem-subtitle">
            Explore normalized security event logs with structured condition filters, logical grouping, and pivot workflows.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            className="siem-btn-secondary"
            onClick={() => setShowSavedModal(true)}
            title="Save current search criteria"
          >
            <Bookmark size={14} /> Save Search
          </button>
        </div>
      </div>

      <SiemNav />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239,68,68,0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', color: '#f87171' }}>
          {error}
        </div>
      )}

      {escalationFeedback && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(16,185,129,0.1)', border: '1px solid #10b981', borderRadius: '0.5rem', color: '#34d399' }}>
          {escalationFeedback}
        </div>
      )}

      {/* Search & Query Builder Panel */}
      <div className="siem-search-panel">
        {/* Main Search Bar */}
        <div className="siem-search-bar-row">
          <input
            type="text"
            className="siem-input-main"
            placeholder="Search keywords, error messages, user IDs, or IP addresses (e.g. 'bad_actor', 'SSH', '198.51.100')..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && executeSearch()}
          />

          <select
            className="condition-select"
            value={selectedDatasetId ?? ''}
            onChange={(e) => setSelectedDatasetId(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">All Datasets</option>
            {datasets.map((ds) => (
              <option key={ds.id} value={ds.id}>
                {ds.stable_id} - {ds.name}
              </option>
            ))}
          </select>

          <select
            className="condition-select"
            value={timePreset}
            onChange={(e) => setTimePreset(e.target.value)}
          >
            <option value="ALL">All Recorded Time</option>
            <option value="LAST_15M">Last 15m</option>
            <option value="LAST_1H">Last 1h</option>
            <option value="LAST_24H">Last 24h</option>
            <option value="LAST_7D">Last 7d</option>
          </select>

          <button className="siem-btn-primary" onClick={() => executeSearch()}>
            <Search size={14} /> Search
          </button>
        </div>

        {/* Quick Filter Chips */}
        <div className="siem-quick-filters">
          <span className="quick-filter-label">Quick Filters:</span>

          <button
            className={`quick-filter-chip ${activeQuickFilter === 'FAILED_LOGINS' ? 'active' : ''}`}
            onClick={() => handleQuickFilter('FAILED_LOGINS', [{ field: 'action', operator: '=', value: 'LOGIN_FAILURE' }])}
          >
            Failed Logins
          </button>

          <button
            className={`quick-filter-chip ${activeQuickFilter === 'FIREWALL_DROPS' ? 'active' : ''}`}
            onClick={() => handleQuickFilter('FIREWALL_DROPS', [{ field: 'action', operator: '=', value: 'CONNECTION_BLOCKED' }])}
          >
            Firewall Blocks / Drops
          </button>

          <button
            className={`quick-filter-chip ${activeQuickFilter === 'SUDO_PRIVILEGE' ? 'active' : ''}`}
            onClick={() => handleQuickFilter('SUDO_PRIVILEGE', [{ field: 'event_category', operator: '=', value: 'PRIVILEGE' }])}
          >
            Privilege Changes (sudo)
          </button>

          <button
            className={`quick-filter-chip ${activeQuickFilter === 'DNS_QUERIES' ? 'active' : ''}`}
            onClick={() => handleQuickFilter('DNS_QUERIES', [{ field: 'event_category', operator: '=', value: 'DNS' }])}
          >
            DNS Traffic
          </button>

          <button
            className={`quick-filter-chip ${activeQuickFilter === 'CRITICAL_ONLY' ? 'active' : ''}`}
            onClick={() => handleQuickFilter('CRITICAL_ONLY', [{ field: 'severity', operator: '=', value: 'CRITICAL' }])}
          >
            Critical Severity
          </button>
        </div>

        {/* Visual Query Builder */}
        <div className="visual-builder">
          <div className="builder-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Filter size={14} />
              <span>Structured Field Conditions</span>
              <div style={{ display: 'flex', gap: '0.25rem', background: '#1e293b', borderRadius: '4px', padding: '2px' }}>
                <button
                  style={{
                    padding: '2px 8px',
                    fontSize: '0.75rem',
                    background: logicalOp === 'AND' ? '#0284c7' : 'transparent',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                  onClick={() => setLogicalOp('AND')}
                >
                  AND
                </button>
                <button
                  style={{
                    padding: '2px 8px',
                    fontSize: '0.75rem',
                    background: logicalOp === 'OR' ? '#0284c7' : 'transparent',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                  onClick={() => setLogicalOp('OR')}
                >
                  OR
                </button>
              </div>
            </div>

            <button
              className="siem-btn-secondary"
              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
              onClick={addCondition}
            >
              <Plus size={12} /> Add Condition
            </button>
          </div>

          {conditions.length === 0 ? (
            <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
              No field conditions configured. Click &quot;Add Condition&quot; or select a Quick Filter.
            </div>
          ) : (
            conditions.map((cond, idx) => (
              <div key={idx} className="condition-row">
                <select
                  className="condition-select"
                  value={cond.field}
                  onChange={(e) => updateCondition(idx, 'field', e.target.value)}
                >
                  <option value="action">action</option>
                  <option value="event_category">event_category</option>
                  <option value="source_type">source_type</option>
                  <option value="source_ip">source_ip</option>
                  <option value="destination_ip">destination_ip</option>
                  <option value="destination_port">destination_port</option>
                  <option value="username">username</option>
                  <option value="host">host</option>
                  <option value="protocol">protocol</option>
                  <option value="severity">severity</option>
                  <option value="domain">domain</option>
                  <option value="process_name">process_name</option>
                  <option value="status">status</option>
                </select>

                <select
                  className="condition-select"
                  value={cond.operator}
                  onChange={(e) => updateCondition(idx, 'operator', e.target.value as QueryCondition['operator'])}
                >
                  <option value="=">=</option>
                  <option value="!=">!=</option>
                  <option value="CONTAINS">CONTAINS</option>
                  <option value="STARTSWITH">STARTSWITH</option>
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                </select>

                <input
                  type="text"
                  className="condition-input"
                  placeholder="Filter value..."
                  value={cond.value}
                  onChange={(e) => updateCondition(idx, 'value', e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && executeSearch()}
                />

                <button
                  className="btn-icon-danger"
                  onClick={() => removeCondition(idx)}
                  title="Remove condition"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Saved Searches Drawer Bar (if any saved searches) */}
      {savedSearches.length > 0 && (
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', overflowX: 'auto', padding: '0.5rem 0' }}>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Bookmark size={12} /> Saved:
          </span>
          {savedSearches.map((s) => (
            <button
              key={s.id}
              className="quick-filter-chip"
              onClick={() => handleLoadSavedSearch(s)}
            >
              {s.name}
            </button>
          ))}
        </div>
      )}

      {/* Search Results Table */}
      <div className="siem-table-container">
        <div className="siem-table-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>
              Results ({searchResults?.total || 0} events)
            </span>
            {searchResults?.execution_time_ms !== undefined && (
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                executed in {searchResults.execution_time_ms} ms
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#38bdf8' }}>
            {searchResults?.human_readable || 'Showing latest telemetry'}
          </div>
        </div>

        <table className="siem-events-table">
          <thead>
            <tr>
              <th>Event ID</th>
              <th>Timestamp (UTC)</th>
              <th>Source Type</th>
              <th>Category</th>
              <th>Action</th>
              <th>Source Endpoint</th>
              <th>Destination Endpoint</th>
              <th>User / Host</th>
              <th>Severity</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
                  <RefreshCw className="animate-spin" size={20} style={{ margin: '0 auto 0.5rem auto' }} />
                  Executing query across normalized event indices...
                </td>
              </tr>
            ) : !searchResults || searchResults.events.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                  No security events matched the query criteria. Try adjusting filters or selecting &quot;All Datasets&quot;.
                </td>
              </tr>
            ) : (
              searchResults.events.map((evt) => {
                const isBlocked = evt.action === 'CONNECTION_BLOCKED' || evt.action === 'LOGIN_FAILURE'
                const isSelected = selectedEventId === evt.event_id
                return (
                  <tr
                    key={evt.id}
                    className={isSelected ? 'selected' : ''}
                    onClick={() => handleSelectEvent(evt)}
                  >
                    <td className="mono-cell" style={{ color: '#38bdf8' }}>{evt.event_id}</td>
                    <td className="mono-cell">{new Date(evt.timestamp).toLocaleString()}</td>
                    <td><span className="cat-badge">{evt.source_type}</span></td>
                    <td><span className="cat-badge">{evt.event_category}</span></td>
                    <td>
                      <span className={`act-badge ${isBlocked ? 'danger' : ''}`}>
                        {evt.action || evt.event_type}
                      </span>
                    </td>
                    <td className="mono-cell" style={{ color: '#38bdf8' }}>
                      {evt.source_ip ? `${evt.source_ip}${evt.source_port ? `:${evt.source_port}` : ''}` : '-'}
                    </td>
                    <td className="mono-cell">
                      {evt.destination_ip ? `${evt.destination_ip}${evt.destination_port ? `:${evt.destination_port}` : ''}` : evt.domain || '-'}
                    </td>
                    <td className="mono-cell" style={{ color: evt.username ? '#a78bfa' : '#cbd5e1' }}>
                      {evt.username || evt.host || '-'}
                    </td>
                    <td><span className={`sev-badge sev-${evt.severity}`}>{evt.severity}</span></td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Event Details Slide-out Drawer */}
      {selectedEventId && (
        <div className="event-drawer">
          <div className="drawer-header">
            <h3>
              <Shield size={18} color="#38bdf8" />
              Event Details: <span className="mono-cell" style={{ fontSize: '0.875rem' }}>{selectedEventId}</span>
            </h3>
            <button className="drawer-close" onClick={() => setSelectedEventId(null)}>
              <X size={18} />
            </button>
          </div>

          <div className="drawer-content">
            {drawerLoading ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
                Loading event metadata...
              </div>
            ) : eventDetail ? (
              <>
                <div>
                  <div className="drawer-section-title">Normalized Taxonomy</div>
                  <div className="drawer-grid">
                    <span className="drawer-key">Event Type:</span>
                    <span className="drawer-val mono-cell">{eventDetail.event_type}</span>

                    <span className="drawer-key">Category:</span>
                    <span className="drawer-val"><span className="cat-badge">{eventDetail.event_category}</span></span>

                    <span className="drawer-key">Action:</span>
                    <span className="drawer-val"><span className="act-badge">{eventDetail.action || 'N/A'}</span></span>

                    <span className="drawer-key">Status / Result:</span>
                    <span className="drawer-val mono-cell">{eventDetail.status || eventDetail.result || 'N/A'}</span>

                    <span className="drawer-key">Severity:</span>
                    <span className="drawer-val"><span className={`sev-badge sev-${eventDetail.severity}`}>{eventDetail.severity}</span></span>

                    <span className="drawer-key">Source Type:</span>
                    <span className="drawer-val mono-cell">{eventDetail.source_type}</span>
                  </div>
                </div>

                <div>
                  <div className="drawer-section-title">Identity & Endpoint Context</div>
                  <div className="drawer-grid">
                    <span className="drawer-key">Source IP:</span>
                    <span className="drawer-val mono-cell" style={{ color: '#38bdf8' }}>
                      {eventDetail.source_ip || '-'} {eventDetail.source_port ? `(port ${eventDetail.source_port})` : ''}
                    </span>

                    <span className="drawer-key">Destination IP:</span>
                    <span className="drawer-val mono-cell">
                      {eventDetail.destination_ip || '-'} {eventDetail.destination_port ? `(port ${eventDetail.destination_port})` : ''}
                    </span>

                    <span className="drawer-key">Host / Computer:</span>
                    <span className="drawer-val mono-cell">{eventDetail.host || '-'}</span>

                    <span className="drawer-key">User / Account:</span>
                    <span className="drawer-val mono-cell" style={{ color: '#a78bfa' }}>{eventDetail.username || '-'}</span>

                    {eventDetail.domain && (
                      <>
                        <span className="drawer-key">Domain:</span>
                        <span className="drawer-val mono-cell" style={{ color: '#34d399' }}>{eventDetail.domain}</span>
                      </>
                    )}

                    {eventDetail.process_name && (
                      <>
                        <span className="drawer-key">Process:</span>
                        <span className="drawer-val mono-cell">{eventDetail.process_name}</span>
                      </>
                    )}
                  </div>
                </div>

                {eventDetail.raw_message && (
                  <div>
                    <div className="drawer-section-title">Raw Ingested Log Record</div>
                    <div className="drawer-raw-box">{eventDetail.raw_message}</div>
                  </div>
                )}

                {eventDetail.metadata_json && eventDetail.metadata_json !== '{}' && (
                  <div>
                    <div className="drawer-section-title">Parsed Metadata Fields</div>
                    <div className="drawer-raw-box">{eventDetail.metadata_json}</div>
                  </div>
                )}
              </>
            ) : null}
          </div>

          {/* Action Bar with SOC / Threat Hunt / IOC Escalations */}
          <div className="drawer-actions">
            <button
              className="btn-escalate-soc"
              onClick={handleInvestigateInSoc}
              title="Escalate directly to Step 12 SOC Investigation"
            >
              <ExternalLink size={14} /> Investigate in SOC
            </button>

            <button
              className="btn-escalate-hunt"
              onClick={handleStartThreatHunt}
              title="Start a Step 14 Threat Hunting campaign pivoting on this entity"
            >
              <ExternalLink size={14} /> Start Threat Hunt
            </button>

            <button
              className="btn-escalate-ioc"
              onClick={handleExtractIoc}
              title="Extract candidate IPs/domains into Step 13 Threat Intelligence"
            >
              <ExternalLink size={14} /> Extract IOC
            </button>
          </div>
        </div>
      )}

      {/* Save Search Modal */}
      {showSavedModal && (
        <div className="siem-modal-backdrop">
          <div className="siem-modal-box">
            <div className="siem-modal-header">
              <h3 style={{ margin: 0, color: '#f8fafc' }}>Save Query Criteria</h3>
              <button className="drawer-close" onClick={() => setShowSavedModal(false)}>
                <X size={18} />
              </button>
            </div>
            <div className="siem-modal-body">
              <label style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
                Query Name:
                <input
                  type="text"
                  className="condition-input"
                  style={{ width: '100%', marginTop: '0.375rem' }}
                  placeholder="e.g., SSH Brute Force Detection Filter"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                />
              </label>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                This search definition will be saved to your profile for quick re-execution.
              </div>
            </div>
            <div className="siem-modal-footer">
              <button className="siem-btn-secondary" onClick={() => setShowSavedModal(false)}>
                Cancel
              </button>
              <button className="siem-btn-primary" onClick={handleSaveSearch}>
                Save Query
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
