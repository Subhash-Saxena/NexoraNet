import React, { useState } from 'react'
import {
  Binary,
  ArrowDown,
  ArrowUp,
} from 'lucide-react'

interface HeaderSegment {
  id: string
  name: string
  layer: string
  pdu: string
  sizeBytes: string
  color: string
  fields: { name: string; size: string; value: string }[]
  securitySignificance: string
}

const SEGMENTS: HeaderSegment[] = [
  {
    id: 'eth_hdr',
    name: 'Ethernet II Header',
    layer: 'Layer 2 (Data Link)',
    pdu: 'Frame Header',
    sizeBytes: '14 Bytes',
    color: '#eab308',
    fields: [
      { name: 'Destination MAC', size: '6 Bytes', value: '00:1A:2B:3C:4D:5E' },
      { name: 'Source MAC', size: '6 Bytes', value: 'AA:BB:CC:11:22:33' },
      { name: 'EtherType', size: '2 Bytes', value: '0x0800 (IPv4)' },
    ],
    securitySignificance: 'Vulnerable to MAC spoofing and ARP poisoning. Switches use this to populate CAM tables.',
  },
  {
    id: 'ip_hdr',
    name: 'IPv4 Header',
    layer: 'Layer 3 (Network)',
    pdu: 'Packet Header',
    sizeBytes: '20 Bytes (Min)',
    color: '#10b981',
    fields: [
      { name: 'Version & IHL', size: '1 Byte', value: '0x45 (v4, 20B)' },
      { name: 'DSCP & ECN', size: '1 Byte', value: '0x00' },
      { name: 'Total Length', size: '2 Bytes', value: '1500 Bytes' },
      { name: 'Identification', size: '2 Bytes', value: '0x4F2A' },
      { name: 'Flags & Offset', size: '2 Bytes', value: '0x4000 (DF=1)' },
      { name: 'TTL', size: '1 Byte', value: '64' },
      { name: 'Protocol', size: '1 Byte', value: '6 (TCP)' },
      { name: 'Header Checksum', size: '2 Bytes', value: '0xB71E' },
      { name: 'Source IP', size: '4 Bytes', value: '192.168.1.50' },
      { name: 'Destination IP', size: '4 Bytes', value: '93.184.216.34' },
    ],
    securitySignificance: 'TTL decrementing is inspected for traceroute mapping and OS fingerprinting (Linux=64, Windows=128). IP spoofing alters Source IP.',
  },
  {
    id: 'tcp_hdr',
    name: 'TCP Header',
    layer: 'Layer 4 (Transport)',
    pdu: 'Segment Header',
    sizeBytes: '20 Bytes (Min)',
    color: '#06b6d4',
    fields: [
      { name: 'Source Port', size: '2 Bytes', value: '54123' },
      { name: 'Destination Port', size: '2 Bytes', value: '443 (HTTPS)' },
      { name: 'Sequence Number', size: '4 Bytes', value: '0x3A2190B4' },
      { name: 'Acknowledgment No.', size: '4 Bytes', value: '0x00000000' },
      { name: 'Data Offset & Flags', size: '2 Bytes', value: '0x8002 (SYN)' },
      { name: 'Window Size', size: '2 Bytes', value: '64240' },
      { name: 'Checksum', size: '2 Bytes', value: '0xA93B' },
      { name: 'Urgent Pointer', size: '2 Bytes', value: '0' },
    ],
    securitySignificance: 'Flags dictate state transitions. Port scanning inspects RST vs SYN-ACK responses. Predictable ISNs enable TCP session hijacking.',
  },
  {
    id: 'payload',
    name: 'Application Payload Data',
    layer: 'Layer 7 (Application)',
    pdu: 'Data',
    sizeBytes: 'Variable (e.g. 512B)',
    color: '#8b5cf6',
    fields: [
      { name: 'Application Data', size: '512 Bytes', value: 'GET /api/v1/auth HTTP/1.1\\r\\nHost: api.nexoranet.internal' },
    ],
    securitySignificance: 'Carries user data, credentials, and API requests. TLS encryption prevents plaintext packet eavesdropping by Wireshark/sniffers.',
  },
  {
    id: 'eth_trailer',
    name: 'Ethernet FCS Trailer',
    layer: 'Layer 2 (Data Link)',
    pdu: 'Frame Trailer',
    sizeBytes: '4 Bytes',
    color: '#f59e0b',
    fields: [
      { name: 'CRC-32 Checksum', size: '4 Bytes', value: '0x9E4B12C8' },
    ],
    securitySignificance: 'Hardware NIC checks FCS; corrupted frames caused by electromagnetic interference or bad cabling are discarded silently.',
  },
]

export const EncapsulationDiagram: React.FC = () => {
  const [selectedSegmentId, setSelectedSegmentId] = useState<string>('ip_hdr')
  const [direction, setDirection] = useState<'encapsulate' | 'decapsulate'>('encapsulate')

  const segment = SEGMENTS.find((s) => s.id === selectedSegmentId) || SEGMENTS[1]

  return (
    <div className="diagram-container">
      <div className="diagram-header">
        <div className="diagram-title">
          <Binary size={20} color="var(--cyan-primary)" />
          <span>Interactive Packet Encapsulation & Protocol Header Deconstruction</span>
        </div>

        <div className="diagram-controls">
          <button
            onClick={() => setDirection('encapsulate')}
            className={`diagram-btn ${direction === 'encapsulate' ? 'primary' : ''}`}
          >
            <ArrowDown size={14} />
            <span>Encapsulation (TX)</span>
          </button>
          <button
            onClick={() => setDirection('decapsulate')}
            className={`diagram-btn ${direction === 'decapsulate' ? 'primary' : ''}`}
          >
            <ArrowUp size={14} />
            <span>Decapsulation (RX)</span>
          </button>
        </div>
      </div>

      <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '18px' }}>
        {direction === 'encapsulate'
          ? 'Outgoing transmission: Each lower networking layer wraps the upper layer data with its own control header.'
          : 'Incoming reception: Each layer inspects its header, validates checksums, strips the header, and passes payload upward.'}
      </p>

      {/* Frame Visual Strip */}
      <div
        style={{
          display: 'flex',
          alignItems: 'stretch',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid var(--border-color)',
          marginBottom: '20px',
        }}
      >
        {SEGMENTS.map((s) => {
          const isSelected = s.id === segment.id
          return (
            <div
              key={s.id}
              onClick={() => setSelectedSegmentId(s.id)}
              style={{
                flex: s.id === 'payload' ? 2 : 1,
                padding: '16px 12px',
                background: isSelected ? s.color : 'rgba(255, 255, 255, 0.02)',
                color: isSelected ? '#020617' : 'var(--text-main)',
                cursor: 'pointer',
                textAlign: 'center',
                borderRight: '1px solid var(--border-subtle)',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', fontWeight: 700, opacity: isSelected ? 0.9 : 0.6 }}>
                {s.pdu}
              </div>
              <div style={{ fontWeight: 800, fontSize: '0.86rem', marginTop: '4px' }}>
                {s.name}
              </div>
              <div style={{ fontSize: '0.7rem', marginTop: '2px', opacity: isSelected ? 0.9 : 0.5 }}>
                {s.sizeBytes}
              </div>
            </div>
          )
        })}
      </div>

      {/* Detailed Field Inspector */}
      <div
        style={{
          background: 'rgba(14, 23, 42, 0.85)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <span
              style={{
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                background: segment.color,
                color: '#020617',
                fontWeight: 700,
                fontSize: '0.75rem',
              }}
            >
              {segment.layer}
            </span>
            <h4 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '6px' }}>
              {segment.name} ({segment.sizeBytes})
            </h4>
          </div>
        </div>

        {/* Field Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '10px', marginBottom: '16px' }}>
          {segment.fields.map((field, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(0, 0, 0, 0.35)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                <span>{field.name}</span>
                <span>{field.size}</span>
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.84rem', color: 'var(--cyan-primary)', marginTop: '4px', fontWeight: 600 }}>
                {field.value}
              </div>
            </div>
          ))}
        </div>

        {/* Security Significance Callout */}
        <div
          style={{
            background: 'rgba(244, 63, 94, 0.08)',
            borderLeft: '4px solid var(--rose-danger)',
            padding: '10px 14px',
            borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
          }}
        >
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--rose-danger)', marginBottom: '4px' }}>
            Packet Analysis & Threat Relevance
          </div>
          <p style={{ fontSize: '0.84rem', color: '#cbd5e1', margin: 0, lineHeight: 1.5 }}>
            {segment.securitySignificance}
          </p>
        </div>
      </div>
    </div>
  )
}
