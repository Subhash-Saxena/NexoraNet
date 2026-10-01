import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Printer, Download, ShieldAlert, Activity } from 'lucide-react'
import { pcapApi } from '../../services/pcapApi'
import type { InvestigationReport } from '../../types/pcap'
import '../../components/pcap/pcap.css'

export const InvestigationReportPage: React.FC = () => {
  const { captureId } = useParams<{ captureId: string }>()
  const navigate = useNavigate()
  const id = Number(captureId)

  const [report, setReport] = useState<InvestigationReport | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchReport = async () => {
      if (!id) return
      try {
        setIsLoading(true)
        setError(null)
        const data = await pcapApi.getReport(id)
        setReport(data)
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to generate investigation report')
      } finally {
        setIsLoading(false)
      }
    }
    fetchReport()
  }, [id])

  const handlePrint = () => {
    window.print()
  }

  const handleDownloadJson = () => {
    if (!report) return
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(report, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', dataStr)
    downloadAnchor.setAttribute('download', `nexoranet_report_capture_${id}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  if (isLoading) {
    return (
      <div className="pcap-container" style={{ textAlign: 'center', padding: '4rem' }}>
        <Activity size={36} color="#38bdf8" style={{ margin: '0 auto 1rem', animation: 'spin 2s linear infinite' }} />
        <h3>Compiling SOC Incident & Packet Forensic Report...</h3>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="pcap-container">
        <div className="pcap-notice-banner danger">
          <ShieldAlert size={20} />
          <span>{error || 'Unable to compile report'}</span>
        </div>
        <button type="button" className="pcap-page-btn" onClick={() => navigate(`/packet-analysis/inspect/${id}`)}>
          Back to Inspection Workbench
        </button>
      </div>
    )
  }

  const { capture, statistics, observations, findings, bookmarks, notes, top_endpoints } = report

  return (
    <div className="pcap-container" style={{ maxWidth: '1100px' }}>
      {/* Action Header */}
      <div className="pcap-workbench-header" style={{ printColorAdjust: 'exact' }}>
        <button
          type="button"
          className="pcap-page-btn"
          onClick={() => navigate(`/packet-analysis/inspect/${id}`)}
          style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
        >
          <ArrowLeft size={14} /> Back to Workbench
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            type="button"
            className="pcap-page-btn"
            onClick={handlePrint}
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <Printer size={14} /> Print Report
          </button>
          <button
            type="button"
            className="pcap-filter-apply-btn"
            onClick={handleDownloadJson}
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <Download size={14} /> Export JSON
          </button>
        </div>
      </div>

      {/* Official Forensic Report Document */}
      <div
        style={{
          background: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '10px',
          padding: '2.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '2rem',
        }}
      >
        {/* Document Header */}
        <div style={{ borderBottom: '2px solid #38bdf8', paddingBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.8125rem', color: '#38bdf8', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              NexoraNet Security Operations Center — Forensic Analysis
            </span>
            <span style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
              Generated: {new Date().toLocaleString()}
            </span>
          </div>
          <h1 style={{ margin: '0.5rem 0 0.25rem', color: '#fff', fontSize: '1.75rem' }}>
            Incident Traffic Inspection Report: {capture.name}
          </h1>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.875rem' }}>
            Target Capture: <span style={{ fontFamily: 'monospace', color: '#cbd5e1' }}>{capture.filename}</span> (ID #{capture.id})
          </p>
        </div>

        {/* Disclaimer Banner */}
        <div className="pcap-notice-banner safety">
          <ShieldAlert size={18} style={{ flexShrink: 0 }} />
          <span>{report.disclaimer}</span>
        </div>

        {/* 1. Executive Summary Telemetry */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.4rem' }}>
            1. Executive Traffic Telemetry
          </h3>
          <div className="pcap-stats-grid">
            <div className="pcap-metric-card">
              <span className="pcap-metric-label">Packets Captured</span>
              <div className="pcap-metric-val">{statistics.total_packets.toLocaleString()}</div>
            </div>
            <div className="pcap-metric-card">
              <span className="pcap-metric-label">Total Volume</span>
              <div className="pcap-metric-val">{(statistics.total_bytes / 1024).toFixed(1)} KB</div>
            </div>
            <div className="pcap-metric-card">
              <span className="pcap-metric-label">Duration</span>
              <div className="pcap-metric-val">{statistics.duration_seconds.toFixed(3)}s</div>
            </div>
            <div className="pcap-metric-card">
              <span className="pcap-metric-label">Unique Endpoints</span>
              <div className="pcap-metric-val">{statistics.unique_ips} IPs</div>
            </div>
          </div>
        </section>

        {/* 2. Top Communicating Endpoints */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.4rem' }}>
            2. Significant Traffic Endpoints
          </h3>
          <table className="pcap-packet-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>IP Address</th>
                <th>Packets Sent</th>
                <th>Packets Received</th>
                <th>Total Volume</th>
                <th>Protocols</th>
              </tr>
            </thead>
            <tbody>
              {top_endpoints.slice(0, 8).map((ep) => (
                <tr key={ep.ip}>
                  <td style={{ color: '#38bdf8', fontWeight: 600 }}>{ep.ip}</td>
                  <td>{ep.packets_sent}</td>
                  <td>{ep.packets_received}</td>
                  <td>{(ep.total_bytes / 1024).toFixed(1)} KB</td>
                  <td style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{ep.protocols.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* 3. Rule-Based Pattern Observations */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.4rem' }}>
            3. Automated Pattern Observations ({observations.length})
          </h3>
          {observations.length === 0 ? (
            <p style={{ color: '#64748b', fontSize: '0.875rem' }}>No anomalous patterns detected.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {observations.map((obs) => (
                <div key={obs.id} className={`pcap-obs-card ${obs.severity}`} style={{ padding: '0.875rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <h4 style={{ margin: 0, color: '#fff', fontSize: '0.95rem' }}>{obs.title}</h4>
                    <span className={`pcap-obs-severity ${obs.severity}`}>{obs.severity}</span>
                  </div>
                  <p style={{ margin: '0.25rem 0', color: '#cbd5e1', fontSize: '0.8125rem' }}>{obs.description}</p>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    <strong style={{ color: '#38bdf8' }}>SOC Relevance:</strong> {obs.cyber_relevance}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* 4. Student Analyst Findings */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.4rem' }}>
            4. Recorded Investigation Findings ({findings.length})
          </h3>
          {findings.length === 0 ? (
            <p style={{ color: '#64748b', fontSize: '0.875rem' }}>No student findings recorded for this session.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {findings.map((f) => (
                <div key={f.id} style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <h4 style={{ margin: 0, color: '#fff', fontSize: '1rem' }}>{f.title}</h4>
                    <span className={`pcap-obs-severity ${f.severity}`}>{f.severity}</span>
                  </div>
                  <p style={{ margin: '0.35rem 0', color: '#cbd5e1', fontSize: '0.875rem' }}>{f.description}</p>
                  {f.hypothesis && (
                    <div style={{ fontSize: '0.8125rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                      <strong style={{ color: '#38bdf8' }}>Hypothesis:</strong> {f.hypothesis}
                    </div>
                  )}
                  {f.conclusion && (
                    <div style={{ fontSize: '0.8125rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                      <strong style={{ color: '#10b981' }}>Conclusion:</strong> {f.conclusion}
                    </div>
                  )}
                  {f.evidence_packets && f.evidence_packets.length > 0 && (
                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.35rem' }}>
                      Evidence Packets: #{f.evidence_packets.join(', #')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* 5. Bookmarked Packets & Notes */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.4rem' }}>
            5. Forensic Evidence Bookmarks & Notes ({bookmarks.length})
          </h3>
          {bookmarks.length === 0 ? (
            <p style={{ color: '#64748b', fontSize: '0.875rem' }}>No individual packets bookmarked.</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.75rem' }}>
              {bookmarks.map((b) => (
                <div key={b.id} style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.75rem' }}>
                  <div style={{ color: '#38bdf8', fontWeight: 600, fontSize: '0.8125rem' }}>
                    Packet #{b.packet_number}
                  </div>
                  {b.note && <div style={{ fontSize: '0.8125rem', color: '#cbd5e1', marginTop: '0.2rem' }}>{b.note}</div>}
                  {b.tags && b.tags.length > 0 && (
                    <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>
                      Tags: {b.tags.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {notes.length > 0 && (
            <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h4 style={{ margin: 0, color: '#94a3b8', fontSize: '0.875rem' }}>Analyst Notes</h4>
              {notes.map((n) => (
                <div key={n.id} style={{ background: '#090d16', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.75rem' }}>
                  {n.title && <h5 style={{ margin: '0 0 0.2rem', color: '#fff', fontSize: '0.875rem' }}>{n.title}</h5>}
                  <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.8125rem' }}>{n.content}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
