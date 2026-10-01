import React, { useState } from 'react'
import {
  Activity,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  ShieldAlert,
} from 'lucide-react'

interface HandshakeStep {
  step: number
  title: string
  direction: 'client_to_server' | 'server_to_client' | 'none'
  packetName: string
  flags: string[]
  seq: number | string
  ack: number | string
  clientState: string
  serverState: string
  description: string
  securityNote?: string
}

const STEPS: HandshakeStep[] = [
  {
    step: 0,
    title: 'Idle / Passive Open',
    direction: 'none',
    packetName: 'None',
    flags: [],
    seq: '-',
    ack: '-',
    clientState: 'CLOSED',
    serverState: 'LISTEN',
    description: 'The server application binds to port 443 and enters passive LISTEN state awaiting incoming connection requests.',
  },
  {
    step: 1,
    title: 'Step 1: Client Active Open (SYN)',
    direction: 'client_to_server',
    packetName: 'TCP SYN',
    flags: ['SYN'],
    seq: 1000,
    ack: 0,
    clientState: 'SYN_SENT',
    serverState: 'SYN_RCVD',
    description: 'Client chooses random Initial Sequence Number (ISN=1000) and sends SYN packet to initiate connection.',
    securityNote: 'Attacker can spoof Source IP here to cause the server to respond to an innocent victim (reflective SYN flood).',
  },
  {
    step: 2,
    title: 'Step 2: Server Acknowledgment & Sync (SYN-ACK)',
    direction: 'server_to_client',
    packetName: 'TCP SYN-ACK',
    flags: ['SYN', 'ACK'],
    seq: 5000,
    ack: 1001,
    clientState: 'ESTABLISHED',
    serverState: 'SYN_RCVD',
    description: 'Server records client connection in SYN backlog queue, chooses its own ISN (5000), and ACKs client ISN+1 (1001).',
    securityNote: 'In a SYN flood, the server allocates a Transmission Control Block (TCB) in kernel memory and waits for Step 3, which never arrives.',
  },
  {
    step: 3,
    title: 'Step 3: Client Final Acknowledgment (ACK)',
    direction: 'client_to_server',
    packetName: 'TCP ACK',
    flags: ['ACK'],
    seq: 1001,
    ack: 5001,
    clientState: 'ESTABLISHED',
    serverState: 'ESTABLISHED',
    description: 'Client acknowledges server sequence number (5000 + 1 = 5001). Handshake completes; 2-way reliable pipe is established.',
    securityNote: 'Once ESTABLISHED, applications can safely exchange encrypted TLS or plaintext payload without packet loss.',
  },
]

export const TCPHandshakeDiagram: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0)
  const [synFloodMode, setSynFloodMode] = useState<boolean>(false)

  const step = STEPS[currentStepIndex]

  const handleNext = () => {
    if (currentStepIndex < STEPS.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1)
    }
  }

  const handlePrev = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1)
    }
  }

  const handleReset = () => {
    setCurrentStepIndex(0)
  }

  return (
    <div className="diagram-container">
      <div className="diagram-header">
        <div className="diagram-title">
          <Activity size={20} color="var(--cyan-primary)" />
          <span>Interactive TCP 3-Way Handshake & State Machine</span>
        </div>

        <div className="diagram-controls">
          <button
            onClick={() => setSynFloodMode(!synFloodMode)}
            className={`diagram-btn ${synFloodMode ? 'primary' : ''}`}
            style={{
              background: synFloodMode ? 'var(--rose-danger)' : undefined,
              borderColor: synFloodMode ? 'var(--rose-danger)' : undefined,
              color: synFloodMode ? '#fff' : undefined,
            }}
          >
            <ShieldAlert size={14} />
            <span>{synFloodMode ? 'Exit Attack Mode' : 'Simulate SYN Flood Attack'}</span>
          </button>

          <button onClick={handleReset} className="diagram-btn" title="Reset handshake">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {!synFloodMode ? (
        <div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '18px' }}>
            Walk through each exchange of the Transmission Control Protocol (RFC 793) connection establishment.
          </p>

          {/* Handshake Visual Stage */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '180px 1fr 180px',
              gap: '16px',
              alignItems: 'center',
              background: 'rgba(14, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '24px 20px',
              marginBottom: '20px',
            }}
          >
            {/* Client Endpoint */}
            <div
              style={{
                textAlign: 'center',
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
              }}
            >
              <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                Client Host
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                192.168.1.100:54321
              </div>
              <div
                style={{
                  marginTop: '12px',
                  padding: '4px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  background: step.clientState === 'ESTABLISHED' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  color: step.clientState === 'ESTABLISHED' ? 'var(--emerald-success)' : 'var(--cyan-primary)',
                  border: `1px solid ${step.clientState === 'ESTABLISHED' ? 'var(--emerald-success)' : 'var(--border-color)'}`,
                }}
              >
                {step.clientState}
              </div>
            </div>

            {/* In-Flight Packet Visualizer */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              {step.direction === 'none' ? (
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                  No packet in transit. Click "Next Step" below to initiate.
                </div>
              ) : (
                <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div
                    style={{
                      background: 'rgba(6, 182, 212, 0.15)',
                      border: '1px solid var(--cyan-primary)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '8px 16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                    }}
                  >
                    <span style={{ fontWeight: 700, fontSize: '0.86rem', color: 'var(--cyan-primary)' }}>
                      {step.packetName}
                    </span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {step.flags.map((f, i) => (
                        <span key={i} className="badge badge-ready" style={{ fontSize: '0.68rem', padding: '1px 6px' }}>
                          [{f}]
                        </span>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.78rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>
                    <span>Seq: {step.seq}</span>
                    <span>&bull;</span>
                    <span>Ack: {step.ack}</span>
                  </div>

                  <div style={{ width: '80%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cyan-primary)' }}>
                    {step.direction === 'client_to_server' ? (
                      <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <div style={{ flex: 1, height: '2px', background: 'var(--cyan-primary)' }} />
                        <ArrowRight size={20} />
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <ArrowLeft size={20} />
                        <div style={{ flex: 1, height: '2px', background: 'var(--cyan-primary)' }} />
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Server Endpoint */}
            <div
              style={{
                textAlign: 'center',
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
              }}
            >
              <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                Server Host
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                198.51.100.25:443
              </div>
              <div
                style={{
                  marginTop: '12px',
                  padding: '4px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  background: step.serverState === 'ESTABLISHED' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  color: step.serverState === 'ESTABLISHED' ? 'var(--emerald-success)' : 'var(--cyan-primary)',
                  border: `1px solid ${step.serverState === 'ESTABLISHED' ? 'var(--emerald-success)' : 'var(--border-color)'}`,
                }}
              >
                {step.serverState}
              </div>
            </div>
          </div>

          {/* Stepper Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              {STEPS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentStepIndex(idx)}
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: currentStepIndex === idx ? 'var(--cyan-primary)' : 'rgba(255, 255, 255, 0.05)',
                    color: currentStepIndex === idx ? '#020617' : 'var(--text-muted)',
                    fontWeight: 700,
                    fontSize: '0.8rem',
                    border: '1px solid var(--border-color)',
                    cursor: 'pointer',
                  }}
                >
                  {s.step}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={handlePrev}
                disabled={currentStepIndex === 0}
                className="diagram-btn"
              >
                Previous
              </button>
              <button
                onClick={handleNext}
                disabled={currentStepIndex === STEPS.length - 1}
                className="diagram-btn primary"
              >
                Next Step
              </button>
            </div>
          </div>

          {/* Step Detail Explanation */}
          <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <h5 style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
              {step.title}
            </h5>
            <p style={{ color: '#cbd5e1', fontSize: '0.88rem', lineHeight: 1.5, margin: 0 }}>
              {step.description}
            </p>

            {step.securityNote && (
              <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--amber-warning)' }}>
                <ShieldAlert size={14} />
                <span><strong>Security Insight:</strong> {step.securityNote}</span>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* SYN Flood Simulation Mode */
        <div style={{ background: 'rgba(244, 63, 94, 0.05)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-md)', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--rose-danger)', fontWeight: 700, fontSize: '1rem', marginBottom: '12px' }}>
            <ShieldAlert size={20} />
            <span>TCP SYN Flood Attack & Kernel Backlog Queue Exhaustion</span>
          </div>

          <p style={{ color: '#e2e8f0', fontSize: '0.88rem', lineHeight: 1.6, marginBottom: '16px' }}>
            In a SYN flood Denial of Service attack, an adversary transmits millions of spoofed TCP SYN packets without ever completing Step 3 (ACK).
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--rose-danger)', marginBottom: '6px' }}>
                Kernel Queue Overflow
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
                The Linux TCP SYN backlog (`net.ipv4.tcp_max_syn_backlog`) fills completely with half-open connections in `SYN_RCVD` state. Legitimate incoming SYN packets are dropped, rendering the service offline.
              </p>
            </div>

            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--emerald-success)', marginBottom: '6px' }}>
                SYN Cookies Mitigation (RFC 4987)
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
                Instead of allocating TCB memory, the server encodes state into the 32-bit Initial Sequence Number: `ISN = hash(src_ip, src_port, dst_ip, dst_port, secret_key) + timestamp + MSS_index`. Memory is only allocated when valid ACK returns!
              </p>
            </div>
          </div>

          <div style={{ background: 'rgba(0, 0, 0, 0.4)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--cyan-primary)' }}>
            $ sysctl -w net.ipv4.tcp_syncookies=1<br />
            $ sysctl -w net.ipv4.tcp_max_syn_backlog=4096
          </div>
        </div>
      )}
    </div>
  )
}
