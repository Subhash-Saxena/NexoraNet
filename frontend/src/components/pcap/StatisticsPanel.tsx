import React from 'react'
import { Activity, HardDrive, Clock, BarChart2, Shield, Network, Zap } from 'lucide-react'
import type { CaptureStatistics, EndpointItem, PortItem, TimelineBucketItem } from '../../types/pcap'

interface StatisticsPanelProps {
  statistics: CaptureStatistics | null
  endpoints: EndpointItem[]
  ports: PortItem[]
  timeline: TimelineBucketItem[]
  isLoading?: boolean
}

export const StatisticsPanel: React.FC<StatisticsPanelProps> = ({
  statistics,
  endpoints,
  ports,
  timeline,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
        Calculating traffic telemetry & endpoint statistics...
      </div>
    )
  }

  if (!statistics) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
        No statistics available for this capture.
      </div>
    )
  }

  // Calculate timeline max height
  const maxBucketPkts = Math.max(...timeline.map((b) => b.packet_count), 1)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Macro Metrics Grid */}
      <div className="pcap-stats-grid">
        <div className="pcap-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#38bdf8' }}>
            <Activity size={18} />
            <span className="pcap-metric-label">Total Packets</span>
          </div>
          <div className="pcap-metric-val">{statistics.total_packets.toLocaleString()}</div>
        </div>

        <div className="pcap-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#10b981' }}>
            <HardDrive size={18} />
            <span className="pcap-metric-label">Total Volume</span>
          </div>
          <div className="pcap-metric-val">
            {(statistics.total_bytes / 1024).toFixed(1)} KB
          </div>
        </div>

        <div className="pcap-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f59e0b' }}>
            <Clock size={18} />
            <span className="pcap-metric-label">Capture Duration</span>
          </div>
          <div className="pcap-metric-val">{statistics.duration_seconds.toFixed(3)}s</div>
        </div>

        <div className="pcap-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#a855f7' }}>
            <Zap size={18} />
            <span className="pcap-metric-label">Avg Packet Rate</span>
          </div>
          <div className="pcap-metric-val">
            {(statistics.packets_per_second || statistics.avg_packet_rate_pps || 0).toFixed(1)} pps
          </div>
        </div>

        <div className="pcap-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#ec4899' }}>
            <Network size={18} />
            <span className="pcap-metric-label">Unique IPs</span>
          </div>
          <div className="pcap-metric-val">{statistics.unique_ips}</div>
        </div>

        <div className="pcap-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#06b6d4' }}>
            <Shield size={18} />
            <span className="pcap-metric-label">Unique Ports</span>
          </div>
          <div className="pcap-metric-val">{statistics.unique_ports}</div>
        </div>
      </div>

      {/* Traffic Density Timeline Burst Visualizer */}
      {timeline.length > 0 && (
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <div>
              <h4 style={{ margin: 0, color: '#fff', fontSize: '0.95rem' }}>Temporal Traffic Density</h4>
              <p style={{ margin: '0.2rem 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
                Histogram of packet volume distribution across {timeline.length} time slices
              </p>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
              Peak: {maxBucketPkts} pkts/slice
            </span>
          </div>

          <div className="pcap-timeline-container">
            {timeline.map((bucket, i) => {
              const heightPct = Math.max((bucket.packet_count / maxBucketPkts) * 100, 4)
              return (
                <div
                  key={i}
                  className="pcap-timeline-bar"
                  style={{ height: `${heightPct}%` }}
                  title={`[${bucket.start_offset_seconds.toFixed(2)}s - ${bucket.end_offset_seconds.toFixed(2)}s]: ${bucket.packet_count} packets (${bucket.byte_count} B)`}
                />
              )
            })}
          </div>
        </div>
      )}

      {/* Protocol Distribution & Top Talkers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.25rem' }}>
        {/* Protocol Distribution */}
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1.25rem' }}>
          <h4 style={{ margin: '0 0 1rem', color: '#fff', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart2 size={16} color="#38bdf8" />
            Protocol Distribution
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {statistics.top_protocols && statistics.top_protocols.length > 0 ? (
              statistics.top_protocols.map((p) => (
                <div key={p.protocol} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem' }}>
                    <span style={{ color: '#fff', fontWeight: 600 }}>{p.protocol}</span>
                    <span style={{ color: '#94a3b8' }}>
                      {p.count} pkts ({p.percentage}%)
                    </span>
                  </div>
                  <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${p.percentage}%`,
                        background: '#0284c7',
                        borderRadius: '3px',
                      }}
                    />
                  </div>
                </div>
              ))
            ) : (
              Object.entries(statistics.protocol_distribution || {}).map(([proto, count]) => {
                const pct = ((count / Math.max(statistics.total_packets, 1)) * 100).toFixed(1)
                return (
                  <div key={proto} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem' }}>
                      <span style={{ color: '#fff', fontWeight: 600 }}>{proto}</span>
                      <span style={{ color: '#94a3b8' }}>{count} pkts ({pct}%)</span>
                    </div>
                    <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${pct}%`,
                          background: '#0284c7',
                          borderRadius: '3px',
                        }}
                      />
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>

        {/* Top Talkers */}
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1.25rem' }}>
          <h4 style={{ margin: '0 0 1rem', color: '#fff', fontSize: '0.95rem' }}>Top Network Talkers</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '240px', overflowY: 'auto' }}>
            {statistics.top_talkers && statistics.top_talkers.length > 0 ? (
              statistics.top_talkers.map((t) => (
                <div
                  key={t.ip}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.5rem 0.75rem',
                    background: '#090d16',
                    border: '1px solid #1e293b',
                    borderRadius: '6px',
                    fontFamily: 'monospace',
                    fontSize: '0.8125rem',
                  }}
                >
                  <span style={{ color: '#38bdf8', fontWeight: 600 }}>{t.ip}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#94a3b8' }}>
                    <span>{t.packet_count} pkts</span>
                    <span>{(t.byte_count / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ color: '#64748b', fontSize: '0.8125rem' }}>No talkers recorded.</div>
            )}
          </div>
        </div>
      </div>

      {/* Endpoints & Ports Tables */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.25rem' }}>
        {/* Endpoints Table */}
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1.25rem' }}>
          <h4 style={{ margin: '0 0 0.75rem', color: '#fff', fontSize: '0.95rem' }}>
            IP Endpoints ({endpoints.length})
          </h4>
          <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
            <table className="pcap-packet-table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Address</th>
                  <th>Packets</th>
                  <th>Bytes</th>
                  <th>Protocols</th>
                </tr>
              </thead>
              <tbody>
                {endpoints.map((ep) => (
                  <tr key={ep.ip}>
                    <td style={{ color: '#38bdf8', fontWeight: 600 }}>{ep.ip}</td>
                    <td>{ep.total_packets}</td>
                    <td>{(ep.total_bytes / 1024).toFixed(1)} KB</td>
                    <td style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{ep.protocols.join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Port Usage Table */}
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1.25rem' }}>
          <h4 style={{ margin: '0 0 0.75rem', color: '#fff', fontSize: '0.95rem' }}>
            Transport Ports ({ports.length})
          </h4>
          <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
            <table className="pcap-packet-table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Port</th>
                  <th>Proto</th>
                  <th>Service Hint</th>
                  <th>Packets</th>
                </tr>
              </thead>
              <tbody>
                {ports.map((p) => (
                  <tr key={`${p.protocol}-${p.port}`}>
                    <td style={{ color: '#fbbf24', fontWeight: 600 }}>{p.port}</td>
                    <td>{p.protocol}</td>
                    <td style={{ color: '#94a3b8' }}>{p.service_hint}</td>
                    <td>{p.packet_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
