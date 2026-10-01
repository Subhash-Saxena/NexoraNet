import React, { useState } from 'react'
import type { ProcessDetails, ProcessTreeNode } from '../../types/endpointSecurity'
import { endpointSecurityApi } from '../../services/endpointSecurityApi'
import './endpointSecurity.css'

interface ProcessTreeProps {
  nodes: ProcessTreeNode[]
  hostId: string | number
  onSelectProcess?: (processId: number) => void
}

interface TreeNodeItemProps {
  node: ProcessTreeNode
  hostId: string | number
  onInspect: (node: ProcessTreeNode) => void
  selectedPid: number | null
}

const TreeNodeItem: React.FC<TreeNodeItemProps> = ({
  node,
  hostId,
  onInspect,
  selectedPid,
}) => {
  const [collapsed, setCollapsed] = useState(false)
  const hasChildren = node.children && node.children.length > 0

  const integrityClass = (node.integrity_level || '').toLowerCase()

  return (
    <div className="process-node">
      <div
        className={`process-node-card ${selectedPid === node.process_id ? 'selected' : ''}`}
        onClick={() => onInspect(node)}
      >
        <div className="process-node-info">
          {hasChildren && (
            <button
              type="button"
              className="btn-cyber-secondary"
              style={{ padding: '0.15rem 0.4rem', fontSize: '0.75rem' }}
              onClick={(e) => {
                e.stopPropagation()
                setCollapsed(!collapsed)
              }}
              title={collapsed ? 'Expand children' : 'Collapse children'}
            >
              {collapsed ? '+' : '−'}
            </button>
          )}
          <span className="process-pid">PID {node.process_id}</span>
          <span className="process-name">{node.process_name}</span>
          {node.integrity_level && (
            <span className={`integrity-badge ${integrityClass}`}>
              {node.integrity_level}
            </span>
          )}
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            [{node.user || 'SYSTEM'}]
          </span>
          {node.command_summary && (
            <span className="process-cmd" title={node.command_line || node.command_summary}>
              {node.command_summary}
            </span>
          )}
        </div>

        <button
          type="button"
          className="btn-cyber-secondary"
          style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
          onClick={(e) => {
            e.stopPropagation()
            onInspect(node)
          }}
        >
          Details ➔
        </button>
      </div>

      {!collapsed && hasChildren && (
        <div className="process-children">
          {node.children.map((child) => (
            <TreeNodeItem
              key={child.process_id}
              node={child}
              hostId={hostId}
              onInspect={onInspect}
              selectedPid={selectedPid}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export const ProcessTree: React.FC<ProcessTreeProps> = ({ nodes, hostId, onSelectProcess }) => {
  const [selectedNode, setSelectedNode] = useState<ProcessTreeNode | null>(null)
  const [details, setDetails] = useState<ProcessDetails | null>(null)
  const [loadingDetails, setLoadingDetails] = useState(false)
  const [pivotMessage, setPivotMessage] = useState<string | null>(null)
  const [filterQuery, setFilterQuery] = useState('')

  const handleInspect = async (node: ProcessTreeNode) => {
    setSelectedNode(node)
    if (onSelectProcess) onSelectProcess(node.process_id)
    setLoadingDetails(true)
    setPivotMessage(null)
    try {
      const data = await endpointSecurityApi.getProcessDetails(hostId, node.process_id)
      setDetails(data)
    } catch (err: any) {
      console.error('Error fetching process details:', err)
      setDetails(null)
    } finally {
      setLoadingDetails(false)
    }
  }

  // Filter helper
  const matchesFilter = (node: ProcessTreeNode, q: string): boolean => {
    if (!q) return true
    const term = q.toLowerCase()
    const matchThis =
      node.process_name.toLowerCase().includes(term) ||
      String(node.process_id).includes(term) ||
      (node.command_summary && node.command_summary.toLowerCase().includes(term))
    if (matchThis) return true
    return (node.children || []).some((c) => matchesFilter(c, term))
  }

  const filteredNodes = nodes.filter((n) => matchesFilter(n, filterQuery))

  return (
    <div className="process-tree-wrapper">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🌳</span> Hierarchical Process Tree
        </h3>
        <input
          type="text"
          placeholder="Filter processes (name, PID, cmd)..."
          value={filterQuery}
          onChange={(e) => setFilterQuery(e.target.value)}
          style={{
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '0.4rem 0.8rem',
            color: '#f8fafc',
            fontSize: '0.825rem',
            width: '280px',
          }}
        />
      </div>

      <div className="process-tree-container">
        {filteredNodes.length === 0 ? (
          <p style={{ color: '#64748b', textAlign: 'center', margin: '2rem 0' }}>
            No process telemetry records match current query.
          </p>
        ) : (
          filteredNodes.map((root) => (
            <TreeNodeItem
              key={root.process_id}
              node={root}
              hostId={hostId}
              onInspect={handleInspect}
              selectedPid={selectedNode?.process_id || null}
            />
          ))
        )}
      </div>

      {/* Process Details Modal / Drawer */}
      {selectedNode && (
        <div className="endpoint-modal-overlay" onClick={() => setSelectedNode(null)}>
          <div className="endpoint-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #1f2937', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ margin: 0, color: '#f8fafc' }}>
                  {selectedNode.process_name} (PID: {selectedNode.process_id})
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  User: {selectedNode.user || 'SYSTEM'} | Integrity: {selectedNode.integrity_level || 'MEDIUM'}
                </span>
              </div>
              <button
                type="button"
                className="btn-cyber-secondary"
                onClick={() => setSelectedNode(null)}
              >
                ✕ Close
              </button>
            </div>

            {loadingDetails ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#38bdf8' }}>
                Analyzing process execution context...
              </div>
            ) : details ? (
              <div>
                {/* Security Context Banners */}
                {details.security_context.flags.length > 0 && (
                  <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{ fontWeight: 600, color: '#f87171', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                      Security Flags Identified:
                    </div>
                    <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8rem', color: '#fca5a5' }}>
                      {details.security_context.flags.map((flag, idx) => (
                        <li key={idx}>{flag}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Command Line */}
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem' }}>
                    Command Line Execution:
                  </label>
                  <div className="code-block">
                    {details.command_line || selectedNode.command_line || 'N/A'}
                  </div>
                </div>

                {/* Parent Process */}
                <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                    Parent Process:
                  </div>
                  {details.parent.process_id ? (
                    <div style={{ fontSize: '0.825rem', color: '#e2e8f0' }}>
                      <strong>{details.parent.process_name}</strong> (PID {details.parent.process_id})
                      <div className="code-block" style={{ marginTop: '0.3rem', fontSize: '0.75rem' }}>
                        {details.parent.command_line || 'N/A'}
                      </div>
                    </div>
                  ) : (
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>No parent process found (Root / System init)</span>
                  )}
                </div>

                {/* Child Processes */}
                {details.children.length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                      Child Processes ({details.children.length}):
                    </div>
                    {details.children.map((c) => (
                      <div key={c.process_id} style={{ background: '#1e293b', padding: '0.5rem 0.75rem', borderRadius: '4px', marginBottom: '0.35rem', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between' }}>
                        <span><strong>{c.process_name}</strong> (PID: {c.process_id})</span>
                        <span style={{ color: '#64748b' }}>{c.spawned_at}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Correlated Activity Tabs/Lists */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '6px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.35rem' }}>
                      🌐 Network Sockets ({details.network_connections.length})
                    </div>
                    {details.network_connections.length === 0 ? (
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>No network connections observed</span>
                    ) : (
                      details.network_connections.map((net, i) => (
                        <div key={i} style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.2rem' }}>
                          ➜ {net.destination_ip}:{net.destination_port} ({net.protocol})
                        </div>
                      ))
                    )}
                  </div>

                  <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '6px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fb923c', marginBottom: '0.35rem' }}>
                      🔎 DNS Queries ({details.dns_queries.length})
                    </div>
                    {details.dns_queries.length === 0 ? (
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>No DNS queries recorded</span>
                    ) : (
                      details.dns_queries.map((dns, i) => (
                        <div key={i} style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.2rem' }}>
                          ➜ {dns.domain} ({dns.query_type})
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* File Modifications */}
                {details.file_modifications.length > 0 && (
                  <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f59e0b', marginBottom: '0.35rem' }}>
                      📁 File System Activity ({details.file_modifications.length})
                    </div>
                    {details.file_modifications.map((f, i) => (
                      <div key={i} style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.25rem' }}>
                        <strong>[{f.action}]</strong> {f.file_path} {f.file_hash && `(Hash: ${f.file_hash})`}
                      </div>
                    ))}
                  </div>
                )}

                {/* Pivot Actions Feedback */}
                {pivotMessage && (
                  <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', borderRadius: '6px', padding: '0.65rem', marginBottom: '1rem', color: '#6ee7b7', fontSize: '0.825rem' }}>
                    {pivotMessage}
                  </div>
                )}

                {/* Analytical Guidance Note */}
                <div style={{ fontSize: '0.775rem', color: '#64748b', fontStyle: 'italic', borderTop: '1px solid #1f2937', paddingTop: '0.75rem' }}>
                  Educational SOC Principle: Review parent-child lineage to spot defense evasion or ingress tool transfer (e.g. browser spawning command shell, or shell downloading secondary executables).
                </div>
              </div>
            ) : (
              <p style={{ color: '#ef4444' }}>Failed to load process details.</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
