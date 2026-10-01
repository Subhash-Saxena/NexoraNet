import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ThreatIntelNav } from '../../components/threat_intel/ThreatIntelNav'
import { threatIntelApi } from '../../services/threatIntelApi'
import type { IndicatorBrief, ThreatIntelGraph } from '../../types/threat_intel'
import '../../components/threat_intel/threat_intel.css'

export const IndicatorGraphPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const rootParam = searchParams.get('root')

  const [indicators, setIndicators] = useState<IndicatorBrief[]>([])
  const [selectedId, setSelectedId] = useState<number>(rootParam ? parseInt(rootParam, 10) : 0)
  const [graphData, setGraphData] = useState<ThreatIntelGraph | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadIndicatorOptions()
  }, [])

  useEffect(() => {
    if (selectedId) {
      loadGraph(selectedId)
    }
  }, [selectedId])

  const loadIndicatorOptions = async () => {
    try {
      const list = await threatIntelApi.listIndicators({ limit: 50 })
      setIndicators(list)
      if (!selectedId && list.length > 0) {
        setSelectedId(list[0].id)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load indicators for graph.')
    }
  }

  const loadGraph = async (id: number) => {
    try {
      setLoading(true)
      const data = await threatIntelApi.getGraph(id)
      setGraphData(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load graph.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectChange = (id: number) => {
    setSelectedId(id)
    setSearchParams({ root: String(id) })
  }

  return (
    <div className="threat-intel-container">
      <div className="threat-intel-header">
        <div className="threat-intel-title-group">
          <h1>🕸️ Indicator Correlation Graph</h1>
          <p className="threat-intel-subtitle">
            Interactive multi-entity correlation connecting IOCs, domain resolutions, alerts, and investigations.
          </p>
        </div>
        <div className="threat-intel-actions">
          <label style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Focus Indicator:</label>
          <select
            value={selectedId}
            onChange={(e) => handleSelectChange(parseInt(e.target.value, 10))}
            style={{
              padding: '0.5rem 0.75rem',
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '0.375rem',
              color: '#f8fafc',
              fontSize: '0.875rem',
            }}
          >
            {indicators.map((ind) => (
              <option key={ind.id} value={ind.id}>
                {ind.display_value} ({ind.indicator_type})
              </option>
            ))}
          </select>
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
        <p style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Compiling correlation graph...</p>
      ) : !graphData || graphData.nodes.length === 0 ? (
        <div className="ioc-panel" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#94a3b8' }}>No correlation links found for this indicator.</p>
        </div>
      ) : (
        <div>
          {/* Graph Visualization Container */}
          <div
            className="threat-graph-wrapper"
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              padding: '2rem',
              position: 'relative',
              background: '#0a0f1d',
            }}
          >
            <div
              style={{
                position: 'absolute',
                top: '1rem',
                left: '1rem',
                fontSize: '0.8rem',
                color: '#64748b',
                background: 'rgba(15, 23, 42, 0.8)',
                padding: '0.4rem 0.8rem',
                borderRadius: '0.25rem',
                border: '1px solid #334155',
              }}
            >
              Nodes: {graphData.nodes.length} | Relationships: {graphData.links.length}
            </div>

            {/* SVG Visualizer rendering central root and satellite nodes */}
            <svg width="100%" height="100%" viewBox="0 0 800 450" style={{ maxHeight: '450px' }}>
              <defs>
                <marker
                  id="arrow"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
                </marker>
              </defs>

              {/* Render links */}
              {graphData.links.map((link, idx) => {
                const total = graphData.nodes.length - 1
                const nodeIdx = graphData.nodes.findIndex((n) => n.id === link.target || n.id === link.source)
                const angle = (nodeIdx / Math.max(total, 1)) * 2 * Math.PI
                const x2 = 400 + Math.cos(angle) * 180
                const y2 = 225 + Math.sin(angle) * 140

                return (
                  <g key={idx}>
                    <line
                      x1={400}
                      y1={225}
                      x2={x2}
                      y2={y2}
                      stroke="#475569"
                      strokeWidth="2"
                      strokeDasharray="4 2"
                      markerEnd="url(#arrow)"
                    />
                    <text
                      x={(400 + x2) / 2}
                      y={(225 + y2) / 2 - 6}
                      fill="#94a3b8"
                      fontSize="10"
                      textAnchor="middle"
                      fontFamily="monospace"
                    >
                      {link.label}
                    </text>
                  </g>
                )
              })}

              {/* Center Root Node */}
              <circle cx={400} cy={225} r={32} fill="#0284c7" stroke="#38bdf8" strokeWidth="3" />
              <text x={400} y={229} fill="#ffffff" fontSize="12" fontWeight="700" textAnchor="middle">
                ROOT IOC
              </text>
              <text x={400} y={268} fill="#f8fafc" fontSize="11" fontWeight="600" textAnchor="middle">
                {graphData.nodes[0]?.label}
              </text>

              {/* Satellite Connected Nodes */}
              {graphData.nodes.slice(1).map((node, idx) => {
                const total = graphData.nodes.length - 1
                const angle = (idx / Math.max(total, 1)) * 2 * Math.PI
                const cx = 400 + Math.cos(angle) * 180
                const cy = 225 + Math.sin(angle) * 140

                let nodeColor = '#334155'
                if (node.type === 'ALERT') nodeColor = '#dc2626'
                else if (node.type === 'INVESTIGATION' || node.type === 'CASE') nodeColor = '#7c3aed'
                else if (node.type === 'IP_ADDRESS') nodeColor = '#d97706'
                else if (node.type === 'DOMAIN') nodeColor = '#2563eb'

                return (
                  <g key={node.id}>
                    <circle cx={cx} cy={cy} r={22} fill={nodeColor} stroke="#cbd5e1" strokeWidth="2" />
                    <text x={cx} y={cy + 4} fill="#ffffff" fontSize="10" fontWeight="600" textAnchor="middle">
                      {node.type.slice(0, 4)}
                    </text>
                    <text
                      x={cx}
                      y={cy + 34}
                      fill="#cbd5e1"
                      fontSize="10"
                      textAnchor="middle"
                      style={{ maxWidth: '120px' }}
                    >
                      {node.label.length > 24 ? `${node.label.slice(0, 22)}...` : node.label}
                    </text>
                  </g>
                )
              })}
            </svg>
          </div>

          {/* Node Summary List */}
          <div className="ioc-panel" style={{ marginTop: '1.5rem' }}>
            <h3 className="ioc-panel-title">Connected Entities in Scope</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              {graphData.nodes.map((node) => (
                <div
                  key={node.id}
                  style={{
                    background: '#0f172a',
                    padding: '0.85rem',
                    borderRadius: '0.5rem',
                    border: '1px solid #334155',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                    <span className="ioc-badge ioc-badge-type">{node.type}</span>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{node.severity}</span>
                  </div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: '0.9rem' }}>{node.label}</div>
                  {node.id.startsWith('ioc-') && (
                    <Link
                      to={`/threat-intelligence/indicators/${node.id.replace('ioc-', '')}`}
                      style={{ color: '#38bdf8', fontSize: '0.8rem', display: 'inline-block', marginTop: '0.5rem' }}
                    >
                      Investigate IOC →
                    </Link>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
