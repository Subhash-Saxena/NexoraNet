import React, { useState } from 'react'
import { Layers, Shield, HelpCircle } from 'lucide-react'
import type { HopRecord } from '../../types/simulator'

interface PacketInspectorProps {
  activeHop: HopRecord | null
}

export const PacketInspector: React.FC<PacketInspectorProps> = ({ activeHop }) => {
  const [activeProtoTab, setActiveProtoTab] = useState<'l2' | 'l3' | 'l4' | 'l7'>('l3')

  if (!activeHop) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: '#64748b',
          fontSize: '0.8rem',
        }}
      >
        Run a simulation (e.g. Ping or TCP Handshake) to inspect packet headers and Layer 2/3/4 traversal.
      </div>
    )
  }

  const pkt = activeHop.packet_snapshot
  const layers = pkt.osi_layers || [1, 2, 3]

  const osiLayers = [
    { level: 7, name: 'Application', desc: 'DNS, DHCP, HTTP payloads' },
    { level: 4, name: 'Transport', desc: 'TCP Ports & Flags, UDP' },
    { level: 3, name: 'Network', desc: 'IPv4 / IPv6, TTL, Routing' },
    { level: 2, name: 'Data Link', desc: 'Ethernet MAC Addresses, Switching' },
    { level: 1, name: 'Physical', desc: 'Bit signaling, Twisted pair, Fiber' },
  ]

  return (
    <div className="osi-container" aria-label="Packet Inspector and OSI Visualizer">
      {/* 5-Layer OSI Stack */}
      <div className="osi-layers-stack">
        {osiLayers.map((l) => {
          const isActive = layers.includes(l.level)
          return (
            <div
              key={l.level}
              className={`osi-layer-box ${isActive ? 'active' : ''}`}
              title={l.desc}
            >
              <span>
                L{l.level}: {l.name}
              </span>
              {isActive && (
                <span
                  style={{
                    fontSize: '0.62rem',
                    padding: '0.1rem 0.3rem',
                    borderRadius: '0.2rem',
                    background: '#0284c7',
                    color: '#fff',
                  }}
                >
                  ACTIVE
                </span>
              )}
            </div>
          )
        })}
      </div>

      {/* Packet Inspection Details */}
      <div className="osi-detail-panel">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '0.6rem',
            borderBottom: '1px solid #1e293b',
            paddingBottom: '0.4rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600 }}>
            <Layers size={16} color="#38bdf8" />
            <span>
              Hop #{activeHop.hop_number}: {activeHop.device_name} ({activeHop.device_type})
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.35rem' }}>
            <button
              className={`sim-btn ${activeProtoTab === 'l2' ? 'sim-btn-primary' : 'sim-btn-secondary'}`}
              style={{ padding: '0.15rem 0.5rem', fontSize: '0.7rem' }}
              onClick={() => setActiveProtoTab('l2')}
            >
              Layer 2 (Ethernet)
            </button>
            <button
              className={`sim-btn ${activeProtoTab === 'l3' ? 'sim-btn-primary' : 'sim-btn-secondary'}`}
              style={{ padding: '0.15rem 0.5rem', fontSize: '0.7rem' }}
              onClick={() => setActiveProtoTab('l3')}
            >
              Layer 3 (IP)
            </button>
            {layers.includes(4) && (
              <button
                className={`sim-btn ${activeProtoTab === 'l4' ? 'sim-btn-primary' : 'sim-btn-secondary'}`}
                style={{ padding: '0.15rem 0.5rem', fontSize: '0.7rem' }}
                onClick={() => setActiveProtoTab('l4')}
              >
                Layer 4 ({pkt.protocol})
              </button>
            )}
            {layers.includes(7) && (
              <button
                className={`sim-btn ${activeProtoTab === 'l7' ? 'sim-btn-primary' : 'sim-btn-secondary'}`}
                style={{ padding: '0.15rem 0.5rem', fontSize: '0.7rem' }}
                onClick={() => setActiveProtoTab('l7')}
              >
                Layer 7 (Payload)
              </button>
            )}
          </div>
        </div>

        {/* Tab: Layer 2 */}
        {activeProtoTab === 'l2' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', fontSize: '0.75rem' }}>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>SOURCE MAC</div>
              <div style={{ color: '#38bdf8', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.source_mac}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>DESTINATION MAC</div>
              <div style={{ color: '#38bdf8', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.destination_mac}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>ETHERTYPE</div>
              <div style={{ color: '#34d399', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.ethernet_type} (IPv4)
              </div>
            </div>
          </div>
        )}

        {/* Tab: Layer 3 */}
        {activeProtoTab === 'l3' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem', fontSize: '0.75rem' }}>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>SOURCE IP</div>
              <div style={{ color: '#38bdf8', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.source_ip}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>DESTINATION IP</div>
              <div style={{ color: '#38bdf8', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.destination_ip}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>TIME-TO-LIVE (TTL)</div>
              <div style={{ color: '#f59e0b', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.ttl} hops
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>PROTOCOL</div>
              <div style={{ color: '#c084fc', fontFamily: 'monospace', fontWeight: 600 }}>
                {pkt.protocol}
              </div>
            </div>
          </div>
        )}

        {/* Tab: Layer 4 */}
        {activeProtoTab === 'l4' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', fontSize: '0.75rem' }}>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>SOURCE PORT</div>
              <div style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
                {pkt.l3_payload.src_port || 'N/A'}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>DESTINATION PORT</div>
              <div style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
                {pkt.l3_payload.dst_port || 'N/A'}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
              <div style={{ color: '#64748b' }}>FLAGS / TYPE</div>
              <div style={{ color: '#34d399', fontFamily: 'monospace' }}>
                {pkt.l3_payload.flags?.join(', ') || pkt.l3_payload.type || 'N/A'}
              </div>
            </div>
          </div>
        )}

        {/* Tab: Layer 7 */}
        {activeProtoTab === 'l7' && (
          <div style={{ background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem' }}>
            <div style={{ color: '#64748b', marginBottom: '0.25rem' }}>APPLICATION DATA</div>
            <pre style={{ margin: 0, fontFamily: 'monospace', color: '#e2e8f0' }}>
              {JSON.stringify(pkt.l3_payload, null, 2)}
            </pre>
          </div>
        )}

        {/* Educational Takeaway & Why Did This Happen */}
        <div className="edu-explanation-box">
          <div className="edu-header">
            <HelpCircle size={15} /> Educational Analysis
          </div>
          <div className="edu-text">{activeHop.explanation}</div>
          <div className="edu-cyber">
            <Shield size={12} style={{ display: 'inline', marginRight: '0.3rem' }} />
            {activeHop.cyber_relevance}
          </div>
        </div>
      </div>
    </div>
  )
}
