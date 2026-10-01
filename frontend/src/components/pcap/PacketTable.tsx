import React from 'react'
import { Bookmark, BookmarkCheck, ChevronLeft, ChevronRight } from 'lucide-react'
import type { ParsedPacketSummary } from '../../types/pcap'

interface PacketTableProps {
  packets: ParsedPacketSummary[]
  selectedPacketNumber?: number | null
  onSelectPacket: (packetNumber: number) => void
  bookmarkedPacketNumbers?: Set<number>
  onToggleBookmark?: (packetNumber: number) => void
  currentPage: number
  totalPages: number
  totalMatched: number
  onPageChange: (newPage: number) => void
  isLoading?: boolean
}

export const PacketTable: React.FC<PacketTableProps> = ({
  packets,
  selectedPacketNumber,
  onSelectPacket,
  bookmarkedPacketNumbers = new Set(),
  onToggleBookmark,
  currentPage,
  totalPages,
  totalMatched,
  onPageChange,
  isLoading = false,
}) => {
  const getProtocolClass = (proto: string): string => {
    const p = proto.toUpperCase()
    if (['TCP', 'HTTP', 'DNS', 'ICMP', 'ARP', 'UDP', 'TLS', 'DHCP'].includes(p)) {
      return p
    }
    return 'OTHER'
  }

  return (
    <div className="pcap-table-wrapper">
      <div className="pcap-table-scroll">
        <table className="pcap-packet-table">
          <thead>
            <tr>
              <th style={{ width: '60px' }}>No.</th>
              <th style={{ width: '90px' }}>Time (s)</th>
              <th style={{ width: '150px' }}>Source</th>
              <th style={{ width: '150px' }}>Destination</th>
              <th style={{ width: '80px' }}>Protocol</th>
              <th style={{ width: '70px' }}>Length</th>
              <th>Info</th>
              {onToggleBookmark && <th style={{ width: '50px', textAlign: 'center' }}>Mark</th>}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={onToggleBookmark ? 8 : 7} style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
                  Loading captured packets...
                </td>
              </tr>
            ) : packets.length === 0 ? (
              <tr>
                <td colSpan={onToggleBookmark ? 8 : 7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  No packets match the current filter criteria.
                </td>
              </tr>
            ) : (
              packets.map((pkt) => {
                const isSelected = selectedPacketNumber === pkt.packet_number
                const isBookmarked = bookmarkedPacketNumbers.has(pkt.packet_number)
                const protoClass = getProtocolClass(pkt.protocol)

                // Format endpoints (prefer IP, fallback to MAC)
                const src = pkt.source_ip
                  ? pkt.source_port
                    ? `${pkt.source_ip}:${pkt.source_port}`
                    : pkt.source_ip
                  : pkt.source_mac || '—'

                const dst = pkt.destination_ip
                  ? pkt.destination_port
                    ? `${pkt.destination_ip}:${pkt.destination_port}`
                    : pkt.destination_ip
                  : pkt.destination_mac || '—'

                return (
                  <tr
                    key={pkt.packet_number}
                    className={`${isSelected ? 'selected' : ''} ${isBookmarked ? 'bookmarked' : ''}`}
                    onClick={() => onSelectPacket(pkt.packet_number)}
                  >
                    <td>{pkt.packet_number}</td>
                    <td>{pkt.relative_time.toFixed(4)}</td>
                    <td title={src}>{src}</td>
                    <td title={dst}>{dst}</td>
                    <td>
                      <span className={`proto-badge ${protoClass}`}>{pkt.protocol}</span>
                    </td>
                    <td>{pkt.captured_length} B</td>
                    <td title={pkt.info} style={{ maxWidth: '450px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {pkt.info}
                    </td>
                    {onToggleBookmark && (
                      <td style={{ textAlign: 'center' }} onClick={(e) => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => onToggleBookmark(pkt.packet_number)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: isBookmarked ? '#eab308' : '#475569' }}
                          title={isBookmarked ? 'Remove bookmark' : 'Bookmark packet'}
                        >
                          {isBookmarked ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
                        </button>
                      </td>
                    )}
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="pcap-pagination-bar">
        <span style={{ color: '#94a3b8' }}>
          Matched: <strong style={{ color: '#fff' }}>{totalMatched}</strong> packets
        </span>
        <div className="pcap-page-btn-group">
          <button
            type="button"
            className="pcap-page-btn"
            disabled={currentPage <= 1 || isLoading}
            onClick={() => onPageChange(currentPage - 1)}
          >
            <ChevronLeft size={14} style={{ verticalAlign: 'middle' }} /> Prev
          </button>
          <span style={{ padding: '0 0.5rem', color: '#cbd5e1' }}>
            Page {currentPage} of {Math.max(totalPages, 1)}
          </span>
          <button
            type="button"
            className="pcap-page-btn"
            disabled={currentPage >= totalPages || isLoading}
            onClick={() => onPageChange(currentPage + 1)}
          >
            Next <ChevronRight size={14} style={{ verticalAlign: 'middle' }} />
          </button>
        </div>
      </div>
    </div>
  )
}
