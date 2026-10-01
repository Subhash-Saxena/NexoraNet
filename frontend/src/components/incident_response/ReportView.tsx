import React, { useState } from 'react'
import type { IncidentReport } from '../../types/incidentResponse'

interface ReportViewProps {
  report: IncidentReport | null
  loading: boolean
}

export const ReportView: React.FC<ReportViewProps> = ({ report, loading }) => {
  const [copied, setCopied] = useState(false)

  if (loading) {
    return <div style={{ padding: '32px', color: '#9ca3af' }}>Compiling NIST SP 800-61 Post-Incident Report...</div>
  }

  if (!report) {
    return <div style={{ padding: '32px', color: '#6b7280' }}>No report available for this incident.</div>
  }

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(report.markdown_report)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([report.markdown_report], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `incident_report_${report.incident_id}.md`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      {/* Report Header Bar */}
      <div className="ir-filter-bar">
        <div>
          <span className="ir-pill badge-cyan">{report.incident_id}</span>
          <strong style={{ marginLeft: '10px', color: '#fff', fontSize: '1rem' }}>
            NIST SP 800-61 Post-Incident Executive Report
          </strong>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
          <button className="ir-btn-secondary" onClick={handleCopyMarkdown}>
            {copied ? '✓ Copied!' : '📋 Copy Markdown'}
          </button>
          <button className="ir-btn-primary" onClick={handleDownload}>
            ⬇ Download .MD
          </button>
        </div>
      </div>

      {/* KPI Overview Grid */}
      <div className="ir-kpi-grid">
        <div className="ir-kpi-card">
          <div className="ir-kpi-label">Classification</div>
          <div className="ir-kpi-val" style={{ fontSize: '1.2rem', color: '#38bdf8' }}>
            {report.classification}
          </div>
        </div>

        <div className="ir-kpi-card">
          <div className="ir-kpi-label">Current Phase</div>
          <div className="ir-kpi-val" style={{ fontSize: '1.05rem', color: '#a78bfa' }}>
            {report.phase}
          </div>
        </div>

        <div className="ir-kpi-card">
          <div className="ir-kpi-label">Evidence Artifacts</div>
          <div className="ir-kpi-val">{report.evidence_count}</div>
        </div>

        <div className="ir-kpi-card">
          <div className="ir-kpi-label">MITRE Tactics Observed</div>
          <div className="ir-kpi-val" style={{ fontSize: '1.1rem', color: '#4ade80' }}>
            {report.tactics_observed.length} Tactics
          </div>
        </div>
      </div>

      {/* Rendered Document View */}
      <div
        style={{
          background: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '8px',
          padding: '28px',
          color: '#e2e8f0',
          lineHeight: '1.6',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          whiteSpace: 'pre-wrap',
          fontSize: '0.92rem',
        }}
      >
        {report.markdown_report}
      </div>
    </div>
  )
}
