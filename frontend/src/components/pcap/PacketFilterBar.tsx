import React, { useState, useEffect } from 'react'
import { Filter, X, Check, AlertCircle } from 'lucide-react'

interface PacketFilterBarProps {
  currentFilter: string
  onApplyFilter: (filter: string) => void
  totalMatched?: number
  totalPackets?: number
  filterError?: string | null
}

const PRESET_FILTERS = [
  { label: 'TCP', filter: 'tcp' },
  { label: 'HTTP', filter: 'http' },
  { label: 'DNS', filter: 'dns' },
  { label: 'ICMP', filter: 'icmp' },
  { label: 'ARP', filter: 'arp' },
  { label: 'UDP', filter: 'udp' },
  { label: 'SYN Packets', filter: 'tcp.flags.syn' },
  { label: 'RST Packets', filter: 'tcp.flags.rst' },
  { label: 'Port 80', filter: 'tcp.port == 80' },
  { label: 'Port 53', filter: 'udp.port == 53' },
]

export const PacketFilterBar: React.FC<PacketFilterBarProps> = ({
  currentFilter,
  onApplyFilter,
  totalMatched,
  totalPackets,
  filterError,
}) => {
  const [inputValue, setInputValue] = useState(currentFilter)

  useEffect(() => {
    setInputValue(currentFilter)
  }, [currentFilter])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onApplyFilter(inputValue.trim())
  }

  const handleClear = () => {
    setInputValue('')
    onApplyFilter('')
  }

  const handleChipClick = (filter: string) => {
    setInputValue(filter)
    onApplyFilter(filter)
  }

  return (
    <div className="pcap-filter-bar">
      <form onSubmit={handleSubmit} className="pcap-filter-input-row">
        <div className="pcap-filter-input-wrapper">
          <Filter size={16} className="pcap-filter-input-icon" />
          <input
            type="text"
            className={`pcap-filter-input ${filterError ? 'error' : ''}`}
            placeholder="Apply display filter (e.g. ip.addr == 10.0.0.5 && tcp.flags.syn, or protocol name 'dns')..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          {inputValue && (
            <button
              type="button"
              className="pcap-filter-clear-btn"
              onClick={handleClear}
              title="Clear filter"
            >
              <X size={16} />
            </button>
          )}
        </div>
        <button type="submit" className="pcap-filter-apply-btn">
          Apply Filter
        </button>
      </form>

      {filterError && (
        <div className="pcap-filter-error-msg" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <AlertCircle size={14} />
          <span>{filterError}</span>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div className="pcap-filter-chips">
          <span className="pcap-filter-chip-label">Quick Filters:</span>
          {PRESET_FILTERS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              className="pcap-filter-chip"
              onClick={() => handleChipClick(preset.filter)}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {totalPackets !== undefined && (
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            {currentFilter ? (
              <>
                <Check size={14} color="#10b981" />
                <span>
                  Showing <strong style={{ color: '#fff' }}>{totalMatched ?? 0}</strong> of {totalPackets} packets
                </span>
              </>
            ) : (
              <span>Total packets: <strong style={{ color: '#fff' }}>{totalPackets}</strong></span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
