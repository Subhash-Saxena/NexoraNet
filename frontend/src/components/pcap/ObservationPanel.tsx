import React from 'react'
import { Info, ShieldAlert, CheckCircle2, Eye } from 'lucide-react'
import type { ObservationItem } from '../../types/pcap'

interface ObservationPanelProps {
  observations: ObservationItem[]
  onSelectPacket?: (packetNumber: number) => void
  isLoading?: boolean
}

export const ObservationPanel: React.FC<ObservationPanelProps> = ({
  observations,
  onSelectPacket,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
        Scanning traffic patterns for pedagogical observations...
      </div>
    )
  }

  if (observations.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
        <CheckCircle2 size={36} style={{ margin: '0 auto 0.75rem', opacity: 0.5, color: '#10b981' }} />
        <h4 style={{ color: '#94a3b8', margin: '0 0 0.25rem' }}>No Noteworthy Anomalies Detected</h4>
        <p style={{ margin: 0, fontSize: '0.8125rem' }}>
          The rule-based observation engine found standard traffic behavior with no unusual SYN ratios, reset spikes, or DNS lookup anomalies.
        </p>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Educational SOC Disclaimer */}
      <div className="pcap-notice-banner warning">
        <Info size={18} style={{ flexShrink: 0 }} />
        <div>
          <strong>Pedagogical Pattern Engine:</strong> Observations highlight noteworthy traffic behaviors (such as high SYN ratios or unmapped ARP updates). In defensive SOC analysis, these indicate patterns warranting investigation rather than definitive proof of malice.
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {observations.map((obs) => (
          <div key={obs.id} className={`pcap-obs-card ${obs.severity}`}>
            <div className="pcap-obs-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <ShieldAlert size={18} color="#38bdf8" />
                <h4 style={{ margin: 0, color: '#fff', fontSize: '1rem' }}>{obs.title}</h4>
              </div>
              <span className={`pcap-obs-severity ${obs.severity}`}>
                {obs.severity} Priority
              </span>
            </div>

            <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.875rem', lineHeight: 1.5 }}>
              {obs.description}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem', marginTop: '0.25rem' }}>
              <div style={{ padding: '0.6rem 0.85rem', background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px' }}>
                <span style={{ display: 'block', fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  Why It Matters
                </span>
                <span style={{ fontSize: '0.8125rem', color: '#cbd5e1' }}>{obs.why_it_matters}</span>
              </div>

              <div style={{ padding: '0.6rem 0.85rem', background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px' }}>
                <span style={{ display: 'block', fontSize: '0.7rem', color: '#38bdf8', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  Cybersecurity Relevance
                </span>
                <span style={{ fontSize: '0.8125rem', color: '#cbd5e1' }}>{obs.cyber_relevance}</span>
              </div>
            </div>

            {obs.evidence_packets && obs.evidence_packets.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Eye size={14} /> Evidence Packets:
                </span>
                <div className="pcap-evidence-chips">
                  {obs.evidence_packets.slice(0, 15).map((pktNum) => (
                    <button
                      key={pktNum}
                      type="button"
                      className="pcap-evidence-btn"
                      onClick={() => onSelectPacket?.(pktNum)}
                      title={`Jump to Packet #${pktNum}`}
                    >
                      #{pktNum}
                    </button>
                  ))}
                  {obs.evidence_packets.length > 15 && (
                    <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                      +{obs.evidence_packets.length - 15} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
