import React, { useState } from 'react'
import {
  Wifi,
  ShieldAlert,
  RotateCcw,
} from 'lucide-react'

interface DORAStep {
  letter: string
  name: string
  from: string
  to: string
  srcIp: string
  dstIp: string
  ports: string
  details: string
  flags: string
}

const DORA_STEPS: DORAStep[] = [
  {
    letter: 'D',
    name: 'DHCP Discover',
    from: 'Client (No IP)',
    to: 'Broadcast (All)',
    srcIp: '0.0.0.0',
    dstIp: '255.255.255.255',
    ports: 'UDP 68 &rarr; 67',
    details: 'Client powers on with no IP address. It broadcasts a DHCPDISCOVER message containing its MAC address seeking an available DHCP server on the local LAN broadcast domain.',
    flags: 'Broadcast Flag = 1',
  },
  {
    letter: 'O',
    name: 'DHCP Offer',
    from: 'DHCP Server',
    to: 'Client Host',
    srcIp: '192.168.1.1',
    dstIp: '255.255.255.255 / Unicast',
    ports: 'UDP 67 &rarr; 68',
    details: 'Server reserves an unassigned IP (192.168.1.105) from its scope pool and offers it along with Subnet Mask (255.255.255.0), Gateway (192.168.1.1), DNS servers, and Lease Duration.',
    flags: 'Offered IP: 192.168.1.105',
  },
  {
    letter: 'R',
    name: 'DHCP Request',
    from: 'Client Host',
    to: 'Broadcast (All)',
    srcIp: '0.0.0.0',
    dstIp: '255.255.255.255',
    ports: 'UDP 68 &rarr; 67',
    details: 'Client formally requests the offered IP by broadcasting DHCPREQUEST. Broadcasting informs all DHCP servers which offer was accepted and which can return their reserved IPs to the pool.',
    flags: 'Server Identifier = 192.168.1.1',
  },
  {
    letter: 'A',
    name: 'DHCP Acknowledgment (ACK)',
    from: 'DHCP Server',
    to: 'Client Host',
    srcIp: '192.168.1.1',
    dstIp: '255.255.255.255 / Unicast',
    ports: 'UDP 67 &rarr; 68',
    details: 'Server registers the MAC-to-IP binding in its lease database and transmits DHCPACK. Client completes TCP/IP stack configuration, performs gratuitous ARP check, and enters network.',
    flags: 'Lease Time: 86400 seconds (24h)',
  },
]

export const DHCPSequenceDiagram: React.FC = () => {
  const [currentDoraIndex, setCurrentDoraIndex] = useState<number>(0)
  const [rogueMode, setRogueMode] = useState<boolean>(false)

  const step = DORA_STEPS[currentDoraIndex]

  return (
    <div className="diagram-container">
      <div className="diagram-header">
        <div className="diagram-title">
          <Wifi size={20} color="var(--cyan-primary)" />
          <span>Interactive DHCP DORA Process (RFC 2131)</span>
        </div>

        <div className="diagram-controls">
          <button
            onClick={() => setRogueMode(!rogueMode)}
            className={`diagram-btn ${rogueMode ? 'primary' : ''}`}
            style={{
              background: rogueMode ? 'var(--rose-danger)' : undefined,
              borderColor: rogueMode ? 'var(--rose-danger)' : undefined,
              color: rogueMode ? '#fff' : undefined,
            }}
          >
            <ShieldAlert size={14} />
            <span>{rogueMode ? 'Exit Rogue Mode' : 'Rogue DHCP & Snooping Defense'}</span>
          </button>

          <button onClick={() => setCurrentDoraIndex(0)} className="diagram-btn" title="Reset">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {!rogueMode ? (
        <div>
          {/* DORA 4-stage Pills */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px' }}>
            {DORA_STEPS.map((s, idx) => (
              <div
                key={idx}
                onClick={() => setCurrentDoraIndex(idx)}
                style={{
                  padding: '12px',
                  borderRadius: 'var(--radius-md)',
                  background: currentDoraIndex === idx ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${currentDoraIndex === idx ? 'var(--cyan-primary)' : 'var(--border-color)'}`,
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: currentDoraIndex === idx ? 'var(--cyan-primary)' : 'var(--text-muted)' }}>
                  {s.letter}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 600, color: currentDoraIndex === idx ? 'var(--text-main)' : 'var(--text-secondary)' }}>
                  {s.name}
                </div>
              </div>
            ))}
          </div>

          {/* Active Flow Box */}
          <div
            style={{
              background: 'rgba(14, 23, 42, 0.85)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '24px',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: 'var(--cyan-primary)',
                    color: '#020617',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 800,
                  }}
                >
                  {step.letter}
                </span>
                <h4 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {step.name}
                </h4>
              </div>
              <span className="badge badge-ready">{step.flags}</span>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '18px' }}>
              {step.details}
            </p>

            {/* Protocol Packet Spec */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', background: 'rgba(0, 0, 0, 0.3)', padding: '12px 16px', borderRadius: 'var(--radius-sm)' }}>
              <div>
                <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>Source IP</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.84rem', color: 'var(--cyan-primary)', marginTop: '2px' }}>
                  {step.srcIp}
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>Destination IP</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.84rem', color: 'var(--emerald-success)', marginTop: '2px' }}>
                  {step.dstIp}
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>UDP Ports</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.84rem', color: '#cbd5e1', marginTop: '2px' }} dangerouslySetInnerHTML={{ __html: step.ports }} />
              </div>
            </div>
          </div>

          {/* Stepper Controls */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <button
              onClick={() => setCurrentDoraIndex(Math.max(0, currentDoraIndex - 1))}
              disabled={currentDoraIndex === 0}
              className="diagram-btn"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentDoraIndex(Math.min(DORA_STEPS.length - 1, currentDoraIndex + 1))}
              disabled={currentDoraIndex === DORA_STEPS.length - 1}
              className="diagram-btn primary"
            >
              Next Step
            </button>
          </div>
        </div>
      ) : (
        /* Rogue DHCP & Snooping Defense */
        <div style={{ background: 'rgba(244, 63, 94, 0.05)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-md)', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--rose-danger)', fontWeight: 700, fontSize: '1rem', marginBottom: '12px' }}>
            <ShieldAlert size={20} />
            <span>Rogue DHCP Server Attack & Cisco DHCP Snooping Mitigation</span>
          </div>

          <p style={{ color: '#e2e8f0', fontSize: '0.88rem', lineHeight: 1.6, marginBottom: '16px' }}>
            Since DHCP Discover is broadcast to all hosts on the VLAN, an attacker plugged into any access port can respond with a malicious DHCP Offer faster than the legitimate server.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--rose-danger)', marginBottom: '6px' }}>
                Default Gateway Hijack (MITM)
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
                The rogue server sets the default gateway IP to the attacker's machine. All outbound student/corporate web traffic routes through the attacker's proxy for credential harvesting and TLS interception.
              </p>
            </div>

            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--emerald-success)', marginBottom: '6px' }}>
                DHCP Snooping Defense
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
                Switch ports are classified as <strong>Trusted</strong> (uplink to real DHCP server) or <strong>Untrusted</strong> (end-user access ports). The switch automatically drops DHCP Offer and ACK frames arriving on untrusted ports!
              </p>
            </div>
          </div>

          <div style={{ background: 'rgba(0, 0, 0, 0.4)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--cyan-primary)' }}>
            Switch(config)# ip dhcp snooping<br />
            Switch(config)# ip dhcp snooping vlan 10<br />
            Switch(config-if)# ip dhcp snooping trust  # only on legitimate server uplink
          </div>
        </div>
      )}
    </div>
  )
}
