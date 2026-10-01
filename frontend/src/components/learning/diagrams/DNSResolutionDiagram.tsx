import React, { useState } from 'react'
import {
  Globe,
  Server,
  ArrowRight,
  ShieldAlert,
  RotateCcw,
} from 'lucide-react'

interface DNSStep {
  step: number
  title: string
  fromNode: string
  toNode: string
  query: string
  response: string
  recordType: string
  description: string
  cacheImpact: string
}

const DNS_STEPS: DNSStep[] = [
  {
    step: 1,
    title: 'Client Local Cache Check',
    fromNode: 'Web Browser',
    toNode: 'OS Resolver Cache',
    query: 'A? security.nexoranet.com',
    response: 'Cache Miss',
    recordType: 'A Record',
    description: 'The browser first checks its internal DNS cache and OS stub resolver cache. If expired or absent, external resolution begins.',
    cacheImpact: 'TTL expired or record not present.',
  },
  {
    step: 2,
    title: 'Query to Recursive Resolver',
    fromNode: 'OS Stub Resolver',
    toNode: 'Recursive Resolver (1.1.1.1)',
    query: 'Recursive Query: security.nexoranet.com',
    response: 'Pending resolution',
    recordType: 'Standard Query (Port 53 UDP)',
    description: 'Host sends recursive query to ISP or public DNS server (e.g. Cloudflare 1.1.1.1 or Google 8.8.8.8) with recursion desired (RD=1) flag.',
    cacheImpact: 'Recursive resolver begins iterative walk.',
  },
  {
    step: 3,
    title: 'Query Root Nameserver (.)',
    fromNode: 'Recursive Resolver',
    toNode: 'Root Nameserver (198.41.0.4)',
    query: 'Where is security.nexoranet.com?',
    response: 'Referral to .com TLD Servers',
    recordType: 'NS Delegation (.com)',
    description: 'Root server does not know nexoranet.com, but directs the resolver to the Top-Level Domain (TLD) nameservers responsible for the .com zone.',
    cacheImpact: 'Root NS referral cached by resolver.',
  },
  {
    step: 4,
    title: 'Query TLD Nameserver (.com)',
    fromNode: 'Recursive Resolver',
    toNode: '.com TLD Nameserver (192.5.6.30)',
    query: 'Where is security.nexoranet.com?',
    response: 'Referral to ns1.nexoranet.com',
    recordType: 'NS Delegation (nexoranet.com)',
    description: 'TLD server refers the resolver to the authoritative nameservers chosen by the domain registrant at domain registration time.',
    cacheImpact: 'TLD NS referral cached.',
  },
  {
    step: 5,
    title: 'Query Authoritative Nameserver',
    fromNode: 'Recursive Resolver',
    toNode: 'Authoritative NS (ns1.nexoranet.com)',
    query: 'IPv4 address for security.nexoranet.com?',
    response: '192.168.10.50 (TTL: 300s)',
    recordType: 'A Record (Authoritative)',
    description: 'The authoritative nameserver holds the master zone file for nexoranet.com and provides the authoritative answer with Time-To-Live.',
    cacheImpact: 'Direct zone record returned.',
  },
  {
    step: 6,
    title: 'Cached Response Delivered to Client',
    fromNode: 'Recursive Resolver',
    toNode: 'Client Host',
    query: 'Completed Answer',
    response: 'security.nexoranet.com = 192.168.10.50',
    recordType: 'DNS Response (AA flag)',
    description: 'Recursive resolver saves the result in its memory cache for 300 seconds and sends the final A record answer back to the client application.',
    cacheImpact: 'Subsequent queries from any user will hit resolver cache instantly.',
  },
]

export const DNSResolutionDiagram: React.FC = () => {
  const [activeStepIndex, setActiveStepIndex] = useState<number>(0)
  const [showPoisoning, setShowPoisoning] = useState<boolean>(false)

  const step = DNS_STEPS[activeStepIndex]

  return (
    <div className="diagram-container">
      <div className="diagram-header">
        <div className="diagram-title">
          <Globe size={20} color="var(--cyan-primary)" />
          <span>Recursive DNS Resolution & Zone Hierarchy</span>
        </div>

        <div className="diagram-controls">
          <button
            onClick={() => setShowPoisoning(!showPoisoning)}
            className={`diagram-btn ${showPoisoning ? 'primary' : ''}`}
            style={{
              background: showPoisoning ? 'var(--rose-danger)' : undefined,
              borderColor: showPoisoning ? 'var(--rose-danger)' : undefined,
              color: showPoisoning ? '#fff' : undefined,
            }}
          >
            <ShieldAlert size={14} />
            <span>{showPoisoning ? 'Show Standard Flow' : 'DNS Cache Poisoning Exploit'}</span>
          </button>

          <button onClick={() => setActiveStepIndex(0)} className="diagram-btn" title="Reset">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {!showPoisoning ? (
        <div>
          {/* Node Architecture Pipeline */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '12px',
              marginBottom: '20px',
            }}
          >
            {[
              { title: '1. Client', subtitle: 'Stub Resolver', active: activeStepIndex === 0 || activeStepIndex === 5 },
              { title: '2. Recursive DNS', subtitle: '1.1.1.1 Resolver', active: activeStepIndex >= 1 && activeStepIndex <= 5 },
              { title: '3. Root & TLD', subtitle: '. and .com zones', active: activeStepIndex === 2 || activeStepIndex === 3 },
              { title: '4. Authoritative NS', subtitle: 'Master Zone File', active: activeStepIndex === 4 },
            ].map((node, i) => (
              <div
                key={i}
                style={{
                  background: node.active ? 'rgba(6, 182, 212, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${node.active ? 'var(--cyan-primary)' : 'var(--border-color)'}`,
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 14px',
                  textAlign: 'center',
                  transition: 'all 0.2s ease',
                }}
              >
                <Server size={18} color={node.active ? 'var(--cyan-primary)' : 'var(--text-muted)'} style={{ margin: '0 auto 6px' }} />
                <div style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-main)' }}>{node.title}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{node.subtitle}</div>
              </div>
            ))}
          </div>

          {/* Active Step Panel */}
          <div
            style={{
              background: 'rgba(14, 23, 42, 0.85)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '20px',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-ready">Step {step.step} of {DNS_STEPS.length}</span>
                <h5 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                  {step.title}
                </h5>
              </div>
              <span className="badge badge-phase">{step.recordType}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(0, 0, 0, 0.3)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', marginBottom: '14px', fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
              <span style={{ color: 'var(--cyan-primary)', fontWeight: 600 }}>{step.fromNode}</span>
              <ArrowRight size={14} color="var(--text-muted)" />
              <span style={{ color: 'var(--emerald-success)', fontWeight: 600 }}>{step.toNode}</span>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '0.88rem', lineHeight: 1.6, marginBottom: '14px' }}>
              {step.description}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.8rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Query Payload: </span>
                <code style={{ color: '#38bdf8' }}>{step.query}</code>
              </div>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Response: </span>
                <code style={{ color: 'var(--emerald-success)' }}>{step.response}</code>
              </div>
            </div>
          </div>

          {/* Stepper Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '6px' }}>
              {DNS_STEPS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveStepIndex(idx)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-sm)',
                    background: activeStepIndex === idx ? 'var(--cyan-primary)' : 'rgba(255, 255, 255, 0.04)',
                    color: activeStepIndex === idx ? '#020617' : 'var(--text-secondary)',
                    fontWeight: 600,
                    fontSize: '0.78rem',
                    border: '1px solid var(--border-color)',
                    cursor: 'pointer',
                  }}
                >
                  Step {s.step}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setActiveStepIndex(Math.max(0, activeStepIndex - 1))}
                disabled={activeStepIndex === 0}
                className="diagram-btn"
              >
                Previous
              </button>
              <button
                onClick={() => setActiveStepIndex(Math.min(DNS_STEPS.length - 1, activeStepIndex + 1))}
                disabled={activeStepIndex === DNS_STEPS.length - 1}
                className="diagram-btn primary"
              >
                Next Step
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* DNS Cache Poisoning Exploit Panel */
        <div style={{ background: 'rgba(244, 63, 94, 0.05)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-md)', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--rose-danger)', fontWeight: 700, fontSize: '1rem', marginBottom: '12px' }}>
            <ShieldAlert size={20} />
            <span>Kaminsky DNS Cache Poisoning Attack & DNSSEC Mitigation</span>
          </div>

          <p style={{ color: '#e2e8f0', fontSize: '0.88rem', lineHeight: 1.6, marginBottom: '16px' }}>
            DNS relies on UDP without state validation by default. A 16-bit Transaction ID (65,536 possible values) matches requests with responses.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--rose-danger)', marginBottom: '6px' }}>
                Transaction ID Forgery Race
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
                The attacker triggers queries for non-existent subdomains (`random123.nexoranet.com`) and floods the resolver with forged responses. If an attacker packet matches the 16-bit ID before the legitimate authoritative server answers, the attacker injects malicious NS records!
              </p>
            </div>

            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--emerald-success)', marginBottom: '6px' }}>
                DNSSEC Cryptographic Defense
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
                DNS Security Extensions (DNSSEC) add digital signatures to resource records (`RRSIG`). The recursive resolver validates the chain of trust from the Root Key-Signing Key (KSK) down through Delegation Signer (`DS`) records, rendering spoofed replies invalid.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
