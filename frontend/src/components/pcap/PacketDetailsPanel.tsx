import React, { useState } from 'react'
import { ChevronDown, ChevronRight, Layers, Cpu, ShieldCheck } from 'lucide-react'
import type { ParsedPacketDetail } from '../../types/pcap'

interface PacketDetailsPanelProps {
  packet: ParsedPacketDetail | null
  isLoading?: boolean
}

export const PacketDetailsPanel: React.FC<PacketDetailsPanelProps> = ({ packet, isLoading }) => {
  const [collapsedLayers, setCollapsedLayers] = useState<Record<string, boolean>>({})

  const toggleLayer = (layerName: string) => {
    setCollapsedLayers((prev) => ({
      ...prev,
      [layerName]: !prev[layerName],
    }))
  }

  if (isLoading) {
    return (
      <div className="pcap-details-card">
        <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
          Loading packet details...
        </div>
      </div>
    )
  }

  if (!packet) {
    return (
      <div className="pcap-details-card">
        <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: '#64748b' }}>
          <Layers size={36} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
          <h4 style={{ color: '#94a3b8', margin: '0 0 0.25rem' }}>No Packet Selected</h4>
          <p style={{ margin: 0, fontSize: '0.8125rem' }}>
            Click on any packet row in the table above to inspect its decoded OSI layer hierarchy.
          </p>
        </div>
      </div>
    )
  }

  const layerKeys = packet.layers || Object.keys(packet.layer_details || {})

  return (
    <div className="pcap-details-card">
      <div className="pcap-details-header">
        <div>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Frame Inspector
          </span>
          <h3 style={{ margin: '0.2rem 0 0', color: '#fff', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            Packet #{packet.packet_number} — <span style={{ color: '#38bdf8' }}>{packet.protocol}</span>
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem' }}>
          <span style={{ color: '#94a3b8' }}>Wire: {packet.original_length} B</span>
          <span style={{ color: '#64748b' }}>|</span>
          <span style={{ color: '#94a3b8' }}>Offset: +{packet.relative_time.toFixed(4)}s</span>
        </div>
      </div>

      {packet.tcp_flags && packet.tcp_flags.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#0b1120', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #1e293b' }}>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600 }}>TCP Flags:</span>
          <div className="pcap-flags-group">
            {packet.tcp_flags.map((flag) => (
              <span key={flag} className={`pcap-flag-tag ${flag}`}>
                {flag}
              </span>
            ))}
          </div>
          {packet.tcp_seq !== undefined && packet.tcp_seq !== null && (
            <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
              Seq={packet.tcp_seq} Ack={packet.tcp_ack ?? '—'}
            </span>
          )}
        </div>
      )}

      <div className="pcap-layer-tree">
        {layerKeys.map((layerName) => {
          const isCollapsed = !!collapsedLayers[layerName]
          const details = packet.layer_details?.[layerName] || {}

          return (
            <div key={layerName} className="pcap-layer-node">
              <div className="pcap-layer-header" onClick={() => toggleLayer(layerName)}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {isCollapsed ? <ChevronRight size={16} /> : <ChevronDown size={16} />}
                  <Cpu size={16} color="#38bdf8" />
                  <span style={{ color: '#fff' }}>Layer: {layerName}</span>
                </div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  {Object.keys(details).length} fields
                </span>
              </div>

              {!isCollapsed && (
                <div className="pcap-layer-body">
                  {Object.entries(details).map(([k, v]) => {
                    let displayVal = ''
                    if (Array.isArray(v)) {
                      displayVal = v.length > 0 ? JSON.stringify(v) : '[]'
                    } else if (typeof v === 'object' && v !== null) {
                      displayVal = JSON.stringify(v)
                    } else {
                      displayVal = String(v ?? '—')
                    }

                    return (
                      <div key={k} className="pcap-layer-prop">
                        <span className="pcap-layer-key">{k}:</span>
                        <span className="pcap-layer-val">{displayVal}</span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 0.85rem', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '6px', fontSize: '0.75rem', color: '#34d399' }}>
        <ShieldCheck size={16} style={{ flexShrink: 0 }} />
        <span>
          Educational Dissection: NexoraNet normalizes L2-L7 protocol headers without executing payload scripts or triggering network transmission.
        </span>
      </div>
    </div>
  )
}
