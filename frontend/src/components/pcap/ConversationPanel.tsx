import React, { useState } from 'react'
import { ArrowRight, ArrowLeft, ArrowLeftRight, GitCommit, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'
import type { ConversationItem, FlowLadderItem } from '../../types/pcap'

interface ConversationPanelProps {
  conversations: ConversationItem[]
  onSelectPacket?: (packetNumber: number) => void
  isLoading?: boolean
}

export const ConversationPanel: React.FC<ConversationPanelProps> = ({
  conversations,
  onSelectPacket,
  isLoading,
}) => {
  const [selectedConvId, setSelectedConvId] = useState<string | null>(
    conversations.length > 0 ? conversations[0].id : null
  )

  const activeConv =
    conversations.find((c) => c.id === selectedConvId) || (conversations.length > 0 ? conversations[0] : null)

  const renderHandshakeIcon = (state: string) => {
    switch (state) {
      case 'COMPLETE':
        return <CheckCircle2 size={14} color="#34d399" />
      case 'INCOMPLETE':
        return <AlertTriangle size={14} color="#fbbf24" />
      case 'RESET':
        return <XCircle size={14} color="#f87171" />
      default:
        return <HelpCircle size={14} color="#94a3b8" />
    }
  }

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
        Analyzing network conversations & flow ladders...
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
        <ArrowLeftRight size={36} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
        <h4 style={{ color: '#94a3b8', margin: '0 0 0.25rem' }}>No Conversations Detected</h4>
        <p style={{ margin: 0, fontSize: '0.8125rem' }}>
          This capture does not contain bidirectional IP traffic streams or transport flows.
        </p>
      </div>
    )
  }

  return (
    <div className="pcap-conv-grid">
      {/* Conversations Stream List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid #1e293b' }}>
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#fff' }}>
            5-Tuple Conversations ({conversations.length})
          </span>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Sorted by packet volume</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '580px', overflowY: 'auto' }}>
          {conversations.map((conv) => {
            const isSelected = activeConv?.id === conv.id
            return (
              <div
                key={conv.id}
                className={`pcap-conv-card ${isSelected ? 'active' : ''}`}
                onClick={() => setSelectedConvId(conv.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <span className="proto-badge TCP">{conv.protocol}</span>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#fff', fontFamily: 'monospace' }}>
                      {conv.client_endpoint}
                    </span>
                  </div>
                  <div className={`pcap-handshake-badge ${conv.handshake_state}`} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    {renderHandshakeIcon(conv.handshake_state)}
                    <span>{conv.handshake_state}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                  <ArrowRight size={12} color="#38bdf8" />
                  <span>{conv.server_endpoint}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                  <span>{conv.packet_count} packets ({conv.total_bytes || conv.byte_count} B)</span>
                  <span>Duration: {conv.duration.toFixed(3)}s</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Sequence Flow Ladder Diagram */}
      <div className="pcap-ladder-container">
        {activeConv ? (
          <>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <h4 style={{ margin: 0, color: '#fff', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <GitCommit size={18} color="#38bdf8" />
                  Flow Sequence Diagram
                </h4>
                <span className={`pcap-handshake-badge ${activeConv.handshake_state}`}>
                  TCP Handshake: {activeConv.handshake_state}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
                Chronological packet exchanges between client and server endpoints.
              </p>
            </div>

            <div className="pcap-ladder-endpoints">
              <span style={{ color: '#38bdf8' }}>Client: {activeConv.client_endpoint}</span>
              <span style={{ color: '#a855f7' }}>Server: {activeConv.server_endpoint}</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '460px', overflowY: 'auto', paddingRight: '0.5rem' }}>
              {activeConv.ladder.map((step: FlowLadderItem, idx: number) => {
                const isReverse = step.source === activeConv.server_endpoint
                return (
                  <div
                    key={idx}
                    className="pcap-ladder-step"
                    onClick={() => onSelectPacket?.(step.step)}
                    title={`Click to view Packet #${step.step}`}
                  >
                    <span style={{ width: '45px', fontSize: '0.72rem', color: '#64748b', fontFamily: 'monospace' }}>
                      #{step.step}
                    </span>
                    <span style={{ width: '65px', fontSize: '0.72rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                      +{step.relative_time.toFixed(3)}s
                    </span>

                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', position: 'relative', height: '28px' }}>
                      <div className={`pcap-ladder-arrow-line ${isReverse ? 'reverse' : ''}`} />
                      <div
                        style={{
                          position: 'absolute',
                          left: isReverse ? '4px' : 'auto',
                          right: isReverse ? 'auto' : '4px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          background: '#090d16',
                          padding: '0 0.4rem',
                          borderRadius: '4px',
                        }}
                      >
                        {isReverse ? <ArrowLeft size={14} color="#a855f7" /> : <ArrowRight size={14} color="#38bdf8" />}
                        <span style={{ fontSize: '0.72rem', color: '#fff', fontFamily: 'monospace', fontWeight: 600 }}>
                          {step.protocol}
                        </span>
                        {step.tcp_flags && step.tcp_flags.length > 0 && (
                          <span style={{ fontSize: '0.68rem', color: '#f59e0b', fontFamily: 'monospace' }}>
                            [{step.tcp_flags.join(', ')}]
                          </span>
                        )}
                      </div>
                    </div>

                    <span
                      className="pcap-ladder-meta"
                      style={{ width: '220px', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                      title={step.info}
                    >
                      {step.info}
                    </span>
                  </div>
                )
              })}
            </div>
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
            Select a conversation on the left to inspect its flow ladder.
          </div>
        )}
      </div>
    </div>
  )
}
