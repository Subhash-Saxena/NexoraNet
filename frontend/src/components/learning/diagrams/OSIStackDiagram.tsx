import React, { useState } from 'react'
import {
  Layers,
  ShieldAlert,
  ShieldCheck,
  ArrowDown,
  ArrowUp,
} from 'lucide-react'

interface LayerDetail {
  number: number
  name: string
  pdu: string
  protocols: string[]
  primaryFunction: string
  headers: string[]
  attackVector: string
  defenseTechnique: string
  color: string
}

const OSI_LAYERS: LayerDetail[] = [
  {
    number: 7,
    name: 'Application Layer',
    pdu: 'Data / Messages',
    protocols: ['HTTP/HTTPS', 'DNS', 'DHCP', 'SSH', 'FTP', 'SMTP'],
    primaryFunction: 'Provides human-computer interaction and direct access to network applications.',
    headers: ['HTTP Headers (Host, User-Agent, Authorization)', 'DNS RR Query/Answers'],
    attackVector: 'SQL Injection, Cross-Site Scripting (XSS), Layer 7 HTTP flood DDoS, DNS Spoofing.',
    defenseTechnique: 'Web Application Firewalls (WAF), input sanitization, strict TLS, DNSSEC.',
    color: '#8b5cf6', // purple
  },
  {
    number: 6,
    name: 'Presentation Layer',
    pdu: 'Formatted / Encrypted Data',
    protocols: ['TLS/SSL', 'JPEG/PNG', 'ASCII/Unicode', 'MIME', 'Gzip'],
    primaryFunction: 'Translates, compresses, and encrypts/decrypts syntax and semantic data between network and application.',
    headers: ['TLS Record Header', 'Compression dictionary headers'],
    attackVector: 'SSL Stripping, TLS Downgrade (POODLE, BEAST), malformed decompression bombs (zip bombs).',
    defenseTechnique: 'HSTS (HTTP Strict Transport Security), enforcing modern TLS 1.3 ciphers, disabling fallback.',
    color: '#a855f7',
  },
  {
    number: 5,
    name: 'Session Layer',
    pdu: 'Session Controls & Tokens',
    protocols: ['NetBIOS', 'RPC', 'PPTP', 'NFS', 'SOCKS'],
    primaryFunction: 'Establishes, manages, and terminates multi-turn dialogues and duplex connections between communicating hosts.',
    headers: ['Session IDs', 'Sync checkpoints', 'Token state descriptors'],
    attackVector: 'Session Hijacking, RPC endpoint authentication bypass, token prediction attacks.',
    defenseTechnique: 'Cryptographically random 128-bit session tokens, short session TTLs, mutual TLS auth.',
    color: '#3b82f6',
  },
  {
    number: 4,
    name: 'Transport Layer',
    pdu: 'Segments (TCP) / Datagrams (UDP)',
    protocols: ['TCP', 'UDP', 'QUIC', 'SCTP'],
    primaryFunction: 'End-to-end host-to-host process delivery, port multiplexing, sequencing, flow control, and reliability.',
    headers: ['Source Port (16-bit)', 'Destination Port (16-bit)', 'Sequence Number (32-bit)', 'ACK Number', 'Flags (SYN, ACK, FIN, RST)'],
    attackVector: 'TCP SYN Flood, Port Scanning (Nmap SYN scan), TCP RST injection, UDP amplification reflection.',
    defenseTechnique: 'TCP SYN Cookies (`syncookies=1`), stateful inspection firewalls, egress rate-limiting, strict TCP state tracking.',
    color: '#06b6d4',
  },
  {
    number: 3,
    name: 'Network Layer',
    pdu: 'Packets',
    protocols: ['IPv4', 'IPv6', 'ICMP', 'IPsec', 'OSPF', 'BGP'],
    primaryFunction: 'Logical addressing, path selection, dynamic routing between subnets, and fragmentation control.',
    headers: ['Source IP (32/128-bit)', 'Destination IP', 'Time-to-Live (TTL / Hop Limit)', 'Protocol ID (6=TCP, 17=UDP, 1=ICMP)'],
    attackVector: 'IP Address Spoofing, ICMP Ping of Death, ICMP Smurf attacks, BGP route hijacking, Ping sweeps.',
    defenseTechnique: 'uRPF (Unicast Reverse Path Forwarding), BCP 38 egress filtering, RPKI for BGP, ICMP rate limiting.',
    color: '#10b981',
  },
  {
    number: 2,
    name: 'Data Link Layer',
    pdu: 'Frames',
    protocols: ['Ethernet (802.3)', 'Wi-Fi (802.11)', 'ARP', 'VLAN (802.1Q)', 'PPP'],
    primaryFunction: 'Node-to-node hop delivery on the same physical link, hardware MAC addressing, and frame error checking.',
    headers: ['Source MAC (48-bit)', 'Destination MAC', 'EtherType (0x0800 IPv4, 0x0806 ARP)', 'CRC / FCS Trailer (32-bit)'],
    attackVector: 'ARP Poisoning / Spoofing, MAC Address Flooding (CAM table overflow), VLAN Hopping (Double Tagging).',
    defenseTechnique: 'Dynamic ARP Inspection (DAI), Port Security (sticky MAC limit), 802.1X authentication, strict native VLAN tagging.',
    color: '#eab308',
  },
  {
    number: 1,
    name: 'Physical Layer',
    pdu: 'Bits (0s and 1s)',
    protocols: ['RJ45 / Cat6 Copper', 'Fiber Optic (Single/Multi-mode)', 'RF Radio Signals', 'Hubs', 'Repeaters'],
    primaryFunction: 'Transmission and reception of raw unstructured bitstreams over a physical transmission medium.',
    headers: ['Preamble & Start Frame Delimiter (SFD) sync pulses', 'Optical carrier modulations'],
    attackVector: 'Physical wiretapping, rogue hardware implants (e.g. keyloggers/packet sniffers), RF jamming, physical fiber cuts.',
    defenseTechnique: 'Locked server racks, conduit-protected fiber runs, MACsec (802.1AE link-layer encryption), Faraday shielding.',
    color: '#f97316',
  },
]

export const OSIStackDiagram: React.FC = () => {
  const [selectedLayerNum, setSelectedLayerNum] = useState<number>(4)
  const [flowDirection, setFlowDirection] = useState<'encapsulate' | 'decapsulate'>('encapsulate')

  const selectedLayer = OSI_LAYERS.find((l) => l.number === selectedLayerNum) || OSI_LAYERS[3]

  return (
    <div className="diagram-container">
      <div className="diagram-header">
        <div className="diagram-title">
          <Layers size={20} color="var(--cyan-primary)" />
          <span>Interactive OSI 7-Layer Architecture Model</span>
        </div>

        <div className="diagram-controls">
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Data Flow:</span>
          <button
            onClick={() => setFlowDirection('encapsulate')}
            className={`diagram-btn ${flowDirection === 'encapsulate' ? 'primary' : ''}`}
          >
            <ArrowDown size={14} />
            <span>Encapsulation (L7 &rarr; L1)</span>
          </button>
          <button
            onClick={() => setFlowDirection('decapsulate')}
            className={`diagram-btn ${flowDirection === 'decapsulate' ? 'primary' : ''}`}
          >
            <ArrowUp size={14} />
            <span>Decapsulation (L1 &rarr; L7)</span>
          </button>
        </div>
      </div>

      <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '18px' }}>
        Click any layer to inspect its PDU format, header fields, common protocols, and layer-specific cybersecurity attack vectors.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 340px) 1fr', gap: '24px', alignItems: 'start' }}>
        {/* Layer Stack */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {OSI_LAYERS.map((layer) => {
            const isSelected = selectedLayer.number === layer.number
            return (
              <div
                key={layer.number}
                onClick={() => setSelectedLayerNum(layer.number)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  background: isSelected ? 'rgba(6, 182, 212, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                  borderTop: `1px solid ${isSelected ? 'var(--cyan-primary)' : 'var(--border-color)'}`,
                  borderRight: `1px solid ${isSelected ? 'var(--cyan-primary)' : 'var(--border-color)'}`,
                  borderBottom: `1px solid ${isSelected ? 'var(--cyan-primary)' : 'var(--border-color)'}`,
                  borderLeft: `5px solid ${layer.color}`,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span
                    style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      background: isSelected ? layer.color : 'rgba(255, 255, 255, 0.08)',
                      color: isSelected ? '#000' : 'var(--text-main)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.78rem',
                      fontWeight: 700,
                    }}
                  >
                    {layer.number}
                  </span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.88rem', color: isSelected ? 'var(--text-main)' : '#cbd5e1' }}>
                      {layer.name}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      PDU: {layer.pdu}
                    </div>
                  </div>
                </div>

                <span
                  style={{
                    fontSize: '0.7rem',
                    color: layer.color,
                    fontWeight: 600,
                    background: 'rgba(0, 0, 0, 0.3)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                  }}
                >
                  {layer.protocols[0]}
                </span>
              </div>
            )
          })}
        </div>

        {/* Selected Layer Deep-Dive Pane */}
        <div
          style={{
            background: 'rgba(14, 23, 42, 0.8)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '20px 24px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span
                style={{
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-sm)',
                  background: selectedLayer.color,
                  color: '#020617',
                  fontWeight: 800,
                  fontSize: '0.8rem',
                }}
              >
                Layer {selectedLayer.number}
              </span>
              <h4 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {selectedLayer.name}
              </h4>
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--cyan-primary)', fontWeight: 600 }}>
              PDU: {selectedLayer.pdu}
            </div>
          </div>

          <p style={{ color: '#cbd5e1', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '18px' }}>
            {selectedLayer.primaryFunction}
          </p>

          {/* Protocols and Headers */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '18px' }}>
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px 16px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '6px' }}>
                Key Protocols
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {selectedLayer.protocols.map((p, idx) => (
                  <code key={idx} style={{ background: 'rgba(255, 255, 255, 0.06)', padding: '2px 6px', fontSize: '0.78rem' }}>
                    {p}
                  </code>
                ))}
              </div>
            </div>

            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px 16px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '6px' }}>
                Header / Metadata Fields
              </div>
              <div style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                {selectedLayer.headers.join(', ')}
              </div>
            </div>
          </div>

          {/* Attack & Defense Perspectives */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div
              style={{
                background: 'rgba(244, 63, 94, 0.08)',
                borderLeft: '4px solid var(--rose-danger)',
                padding: '10px 14px',
                borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--rose-danger)', fontWeight: 700, fontSize: '0.8rem', marginBottom: '4px' }}>
                <ShieldAlert size={14} />
                <span>Offensive Threat Vectors at Layer {selectedLayer.number}</span>
              </div>
              <p style={{ fontSize: '0.82rem', color: '#f1f5f9', margin: 0, lineHeight: 1.5 }}>
                {selectedLayer.attackVector}
              </p>
            </div>

            <div
              style={{
                background: 'rgba(16, 185, 129, 0.08)',
                borderLeft: '4px solid var(--emerald-success)',
                padding: '10px 14px',
                borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--emerald-success)', fontWeight: 700, fontSize: '0.8rem', marginBottom: '4px' }}>
                <ShieldCheck size={14} />
                <span>Defensive Hardening & Mitigation</span>
              </div>
              <p style={{ fontSize: '0.82rem', color: '#f1f5f9', margin: 0, lineHeight: 1.5 }}>
                {selectedLayer.defenseTechnique}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
