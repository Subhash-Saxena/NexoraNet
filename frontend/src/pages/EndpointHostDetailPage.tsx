import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { EndpointNav } from '../components/endpoint_security/EndpointNav'
import { ProcessTree } from '../components/endpoint_security/ProcessTree'
import { EndpointTimeline } from '../components/endpoint_security/EndpointTimeline'
import type {
  AuthenticationAnalysis,
  EndpointEvent,
  EndpointHost,
  EndpointHostOverview,
  ProcessTreeNode,
} from '../types/endpointSecurity'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import '../components/endpoint_security/endpointSecurity.css'

type TabKey =
  | 'overview'
  | 'processes'
  | 'timeline'
  | 'authentication'
  | 'network'
  | 'dns'
  | 'files'
  | 'persistence'
  | 'privileges'

export const EndpointHostDetailPage: React.FC = () => {
  const { hostId } = useParams<{ hostId: string }>()
  const navigate = useNavigate()

  const [host, setHost] = useState<EndpointHost | null>(null)
  const [overview, setOverview] = useState<EndpointHostOverview | null>(null)
  const [activeTab, setActiveTab] = useState<TabKey>('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Tab specific data
  const [processNodes, setProcessNodes] = useState<ProcessTreeNode[]>([])
  const [timelineEvents, setTimelineEvents] = useState<EndpointEvent[]>([])
  const [authData, setAuthData] = useState<{
    items: EndpointEvent[]
    summary: AuthenticationAnalysis | null
  }>({ items: [], summary: null })
  const [networkEvents, setNetworkEvents] = useState<EndpointEvent[]>([])
  const [dnsEvents, setDnsEvents] = useState<EndpointEvent[]>([])
  const [fileEvents, setFileEvents] = useState<EndpointEvent[]>([])
  const [persistenceEvents, setPersistenceEvents] = useState<EndpointEvent[]>([])
  const [privilegeEvents, setPrivilegeEvents] = useState<EndpointEvent[]>([])

  // Create investigation modal state
  const [showCreateInvModal, setShowCreateInvModal] = useState(false)
  const [invTitle, setInvTitle] = useState('')
  const [invDesc, setInvDesc] = useState('')
  const [invPriority, setInvPriority] = useState('P2')
  const [creatingInv, setCreatingInv] = useState(false)

  useEffect(() => {
    if (!hostId) return
    const fetchBase = async () => {
      try {
        setLoading(true)
        const [h, ov] = await Promise.all([
          endpointSecurityApi.getHost(hostId),
          endpointSecurityApi.getHostOverview(hostId),
        ])
        setHost(h)
        setOverview(ov)
        setInvTitle(`Investigation: Anomalous activity observed on ${h.hostname}`)
        setInvDesc(`Triage and root cause analysis of endpoint events on ${h.hostname} (${h.ip_address}).`)
      } catch (err: any) {
        console.error('Failed to load host detail:', err)
        setError(err.message || 'Host not found')
      } finally {
        setLoading(false)
      }
    }
    fetchBase()
  }, [hostId])

  // Fetch tab content on demand
  useEffect(() => {
    if (!hostId) return
    const fetchTabData = async () => {
      try {
        if (activeTab === 'processes' && processNodes.length === 0) {
          const trees = await endpointSecurityApi.getProcessTree(hostId)
          setProcessNodes(trees)
        } else if (activeTab === 'timeline' && timelineEvents.length === 0) {
          const res = await endpointSecurityApi.getHostTimeline(hostId, { limit: 100 })
          setTimelineEvents(res.items)
        } else if (activeTab === 'authentication' && authData.items.length === 0) {
          const res = await endpointSecurityApi.getHostAuthentication(hostId)
          setAuthData({ items: res.items, summary: res.summary })
        } else if (activeTab === 'network' && networkEvents.length === 0) {
          const res = await endpointSecurityApi.getHostNetwork(hostId)
          setNetworkEvents(res.items)
        } else if (activeTab === 'dns' && dnsEvents.length === 0) {
          const res = await endpointSecurityApi.getHostDns(hostId)
          setDnsEvents(res.items)
        } else if (activeTab === 'files' && fileEvents.length === 0) {
          const res = await endpointSecurityApi.getHostFiles(hostId)
          setFileEvents(res.items)
        } else if (activeTab === 'persistence' && persistenceEvents.length === 0) {
          const res = await endpointSecurityApi.getHostPersistence(hostId)
          setPersistenceEvents(res.items)
        } else if (activeTab === 'privileges' && privilegeEvents.length === 0) {
          const res = await endpointSecurityApi.getHostPrivileges(hostId)
          setPrivilegeEvents(res.items)
        }
      } catch (err: any) {
        console.error(`Failed to load data for tab ${activeTab}:`, err)
      }
    }
    fetchTabData()
  }, [activeTab, hostId])

  const handleCreateInvestigation = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!host) return
    try {
      setCreatingInv(true)
      const inv = await endpointSecurityApi.createInvestigation({
        host_id: host.id,
        title: invTitle,
        description: invDesc,
        priority: invPriority,
      })
      setShowCreateInvModal(false)
      navigate(`/endpoint-security/investigations/${inv.id}`)
    } catch (err: any) {
      alert(`Failed to create case: ${err.message}`)
    } finally {
      setCreatingInv(false)
    }
  }

  if (loading) {
    return (
      <div className="endpoint-container">
        <EndpointNav currentHostId={hostId} />
        <div style={{ textAlign: 'center', padding: '4rem', color: '#38bdf8' }}>
          Loading endpoint host workbench...
        </div>
      </div>
    )
  }

  if (error || !host) {
    return (
      <div className="endpoint-container">
        <EndpointNav />
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '8px', padding: '1.5rem', color: '#fca5a5' }}>
          <h3>Host Not Found</h3>
          <p>{error || 'Requested host identifier does not exist in synthetic fleet.'}</p>
        </div>
      </div>
    )
  }

  const platClass = host.platform.toLowerCase()
  const riskClass = host.risk_level.toLowerCase()

  return (
    <div className="endpoint-container">
      {/* Synthetic Warning */}
      <div className="endpoint-synthetic-banner">
        <div className="banner-left">
          <span className="banner-icon">🛡️</span>
          <div>
            <div className="banner-title">
              Synthetic Endpoint Workbench: {host.hostname}
            </div>
            <div className="banner-subtitle">
              All processes, network flows, credentials, and files on this host are safely simulated.
            </div>
          </div>
        </div>
        <span className="banner-badge">ISOLATED SANDBOX</span>
      </div>

      {/* Host Details Header */}
      <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '10px', padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem' }}>
              <span className={`status-dot ${host.status.toLowerCase()}`} />
              <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                {host.hostname}
              </h1>
              <span className={`platform-badge ${platClass}`}>{host.platform}</span>
              <span className={`risk-badge ${riskClass}`}>{host.risk_level}</span>
            </div>
            <div style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
              {host.display_name} • {host.environment} • IP: <span style={{ fontFamily: 'JetBrains Mono', color: '#cbd5e1' }}>{host.ip_address}</span> • MAC: <span style={{ fontFamily: 'JetBrains Mono', color: '#94a3b8' }}>{host.mac_address}</span>
            </div>
          </div>

          <button
            type="button"
            className="btn-cyber-primary"
            onClick={() => setShowCreateInvModal(true)}
          >
            🕵️ Start Host Investigation
          </button>
        </div>
      </div>

      <EndpointNav currentHostId={host.stable_id} />

      {/* Sub-Tabs for Host Telemetry */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #1e293b', marginBottom: '1.5rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
        {[
          { key: 'overview', label: '📊 Overview' },
          { key: 'processes', label: '🌳 Process Tree' },
          { key: 'timeline', label: '⏱️ Unified Timeline' },
          { key: 'authentication', label: '🔑 Authentication' },
          { key: 'network', label: '📡 Network Sockets' },
          { key: 'dns', label: '🔎 DNS Queries' },
          { key: 'files', label: '📁 Files' },
          { key: 'persistence', label: '📌 Persistence' },
          { key: 'privileges', label: '🛡️ Privileges' },
        ].map((tab) => (
          <button
            key={tab.key}
            type="button"
            className={activeTab === tab.key ? 'btn-cyber-primary' : 'btn-cyber-secondary'}
            onClick={() => setActiveTab(tab.key as TabKey)}
            style={{ fontSize: '0.85rem', padding: '0.45rem 0.9rem', whiteSpace: 'nowrap' }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT */}

      {/* 1. Overview */}
      {activeTab === 'overview' && overview && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div className="investigation-section">
            <div className="section-header">
              <span className="section-title">Host Telemetry Inventory</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Active Processes</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', fontFamily: 'JetBrains Mono' }}>
                  {overview.counts.processes}
                </div>
              </div>
              <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Network Connections</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8', fontFamily: 'JetBrains Mono' }}>
                  {overview.counts.network_connections}
                </div>
              </div>
              <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>DNS Queries</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fb923c', fontFamily: 'JetBrains Mono' }}>
                  {overview.counts.dns_queries}
                </div>
              </div>
              <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>File Modifications</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f59e0b', fontFamily: 'JetBrains Mono' }}>
                  {overview.counts.file_modifications}
                </div>
              </div>
              <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Persistence Indicators</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#a855f7', fontFamily: 'JetBrains Mono' }}>
                  {overview.counts.persistence_mechanisms}
                </div>
              </div>
              <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Active Investigations</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#10b981', fontFamily: 'JetBrains Mono' }}>
                  {overview.counts.investigations}
                </div>
              </div>
            </div>
          </div>

          <div className="investigation-section">
            <div className="section-header">
              <span className="section-title">Host Specifications</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div><strong>Operating System:</strong> {host.platform_version} ({host.architecture})</div>
              <div><strong>OS Build:</strong> {host.os_build || 'Standard Synthetic Image'}</div>
              <div><strong>Environment:</strong> {host.environment}</div>
              <div><strong>Description:</strong> {host.description || 'N/A'}</div>
              <div><strong>Stable ID:</strong> {host.stable_id}</div>
              <div><strong>Last Activity Observed:</strong> {host.last_activity_at ? new Date(host.last_activity_at).toLocaleString() : 'N/A'}</div>
            </div>

            <div style={{ marginTop: '1.5rem', background: '#0f172a', padding: '1rem', borderRadius: '6px', fontSize: '0.8rem', color: '#94a3b8' }}>
              💡 <strong>SOC Guidance:</strong> Switch to the <strong>Process Tree</strong> tab to inspect process parent-child relationships and uncover defense evasion or suspicious child processes.
            </div>
          </div>
        </div>
      )}

      {/* 2. Processes */}
      {activeTab === 'processes' && (
        <ProcessTree nodes={processNodes} hostId={host.id} />
      )}

      {/* 3. Timeline */}
      {activeTab === 'timeline' && (
        <EndpointTimeline events={timelineEvents} hostId={host.id} />
      )}

      {/* 4. Authentication */}
      {activeTab === 'authentication' && (
        <div>
          {authData.summary && (
            <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h4 style={{ margin: 0, color: '#f8fafc' }}>Authentication Pattern Evaluation</h4>
                <span className={`risk-badge ${authData.summary.brute_force_indicators ? 'critical' : 'none'}`}>
                  {authData.summary.pattern_status}
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#cbd5e1', margin: '0 0 0.75rem 0' }}>
                {authData.summary.analyst_guidance}
              </p>
              <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: '#94a3b8' }}>
                <span>Total Attempts: <strong>{authData.summary.total_logons}</strong></span>
                <span>Success: <strong style={{ color: '#10b981' }}>{authData.summary.successful_logons}</strong></span>
                <span>Failures: <strong style={{ color: '#ef4444' }}>{authData.summary.failed_logons}</strong></span>
                <span>Distinct Users: <strong>{authData.summary.distinct_users.join(', ')}</strong></span>
              </div>
            </div>
          )}

          <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                  <th style={{ padding: '0.75rem 1rem' }}>User</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Logon Type</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Source IP</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Result</th>
                </tr>
              </thead>
              <tbody>
                {authData.items.map((e) => (
                  <tr key={e.id} style={{ borderBottom: '1px solid #1f2937' }}>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>
                      {new Date(e.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{e.username}</td>
                    <td style={{ padding: '0.75rem 1rem', color: '#94a3b8' }}>{e.logon_type || 'Interactive'}</td>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono' }}>{e.source_ip || '127.0.0.1'}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span className={`risk-badge ${e.result === 'FAILURE' ? 'critical' : 'none'}`}>
                        {e.result || 'SUCCESS'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 5. Network */}
      {activeTab === 'network' && (
        <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem' }}>Process</th>
                <th style={{ padding: '0.75rem 1rem' }}>Protocol</th>
                <th style={{ padding: '0.75rem 1rem' }}>Destination</th>
                <th style={{ padding: '0.75rem 1rem' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {networkEvents.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid #1f2937' }}>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>
                    {new Date(e.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{e.process_name} (PID: {e.process_id})</td>
                  <td style={{ padding: '0.75rem 1rem', color: '#38bdf8' }}>{e.protocol}</td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', color: '#fbbf24' }}>
                    {e.destination_ip}:{e.destination_port}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span className="risk-badge low">{e.action || 'SOCKET_CONNECT'}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 6. DNS */}
      {activeTab === 'dns' && (
        <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem' }}>Domain</th>
                <th style={{ padding: '0.75rem 1rem' }}>Query Type</th>
                <th style={{ padding: '0.75rem 1rem' }}>Process</th>
              </tr>
            </thead>
            <tbody>
              {dnsEvents.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid #1f2937' }}>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>
                    {new Date(e.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', color: '#fbbf24', fontWeight: 600 }}>
                    {e.domain}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', color: '#38bdf8' }}>{e.query_type || 'A'}</td>
                  <td style={{ padding: '0.75rem 1rem' }}>{e.process_name} (PID: {e.process_id})</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 7. Files */}
      {activeTab === 'files' && (
        <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                <th style={{ padding: '0.75rem 1rem' }}>File Path</th>
                <th style={{ padding: '0.75rem 1rem' }}>SHA256 Hash</th>
                <th style={{ padding: '0.75rem 1rem' }}>Process</th>
              </tr>
            </thead>
            <tbody>
              {fileEvents.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid #1f2937' }}>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>
                    {new Date(e.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span className="risk-badge medium">{e.action || 'FILE_CREATE'}</span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', color: '#f1f5f9' }}>
                    {e.file_path}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: '#a855f7' }}>
                    {e.file_hash ? `${e.file_hash.substring(0, 16)}...` : 'N/A'}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>{e.process_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 8. Persistence */}
      {activeTab === 'persistence' && (
        <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem' }}>Mechanism Type</th>
                <th style={{ padding: '0.75rem 1rem' }}>Target Object / Path</th>
                <th style={{ padding: '0.75rem 1rem' }}>Configured Value</th>
              </tr>
            </thead>
            <tbody>
              {persistenceEvents.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid #1f2937' }}>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>
                    {new Date(e.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span className="risk-badge high">{e.persistence_type || 'PERSISTENCE'}</span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', color: '#f1f5f9' }}>
                    {e.target_object || e.service_name || 'N/A'}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', color: '#38bdf8' }}>
                    {e.new_value || e.command_summary || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 9. Privileges */}
      {activeTab === 'privileges' && (
        <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '8px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #1f2937', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem 1rem' }}>User</th>
                <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                <th style={{ padding: '0.75rem 1rem' }}>Command Executed</th>
              </tr>
            </thead>
            <tbody>
              {privilegeEvents.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid #1f2937' }}>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>
                    {new Date(e.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{e.username}</td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span className="risk-badge high">{e.action || 'SUDO_COMMAND'}</span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontFamily: 'JetBrains Mono', color: '#fb923c' }}>
                    {e.command_summary || e.command_line || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Investigation Modal */}
      {showCreateInvModal && (
        <div className="endpoint-modal-overlay" onClick={() => setShowCreateInvModal(false)}>
          <div className="endpoint-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #1f2937', paddingBottom: '0.75rem' }}>
              <h3 style={{ margin: 0, color: '#f8fafc' }}>
                Initialize Endpoint Investigation on {host.hostname}
              </h3>
              <button
                type="button"
                className="btn-cyber-secondary"
                onClick={() => setShowCreateInvModal(false)}
              >
                ✕ Close
              </button>
            </div>

            <form onSubmit={handleCreateInvestigation}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  Case Title
                </label>
                <input
                  type="text"
                  value={invTitle}
                  onChange={(e) => setInvTitle(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    padding: '0.5rem 0.85rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  Initial Case Hypothesis / Description
                </label>
                <textarea
                  value={invDesc}
                  onChange={(e) => setInvDesc(e.target.value)}
                  rows={4}
                  required
                  style={{
                    width: '100%',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    padding: '0.5rem 0.85rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  Priority Tier
                </label>
                <select
                  value={invPriority}
                  onChange={(e) => setInvPriority(e.target.value)}
                  style={{
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    padding: '0.5rem 0.85rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                  }}
                >
                  <option value="P1">P1 - Critical Host Compromise</option>
                  <option value="P2">P2 - Suspicious Execution / Egress</option>
                  <option value="P3">P3 - Routine Investigation</option>
                  <option value="P4">P4 - Low / Educational Practice</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  className="btn-cyber-secondary"
                  onClick={() => setShowCreateInvModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-cyber-primary"
                  disabled={creatingInv}
                >
                  {creatingInv ? 'Creating Case...' : 'Open Investigation Case ➔'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
