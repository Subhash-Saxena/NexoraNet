import React, { useEffect, useState } from 'react'
import {
  Calendar,
  Database,
  HardDrive,
  Info,
  Layers,
  Radio,
  Server,
  ShieldCheck,
  Upload,
  X,
} from 'lucide-react'
import { SiemNav } from '../components/siem/SiemNav'
import { siemApi } from '../services/siemApi'
import type { LogSource, SecurityLogDataset } from '../types/siem'
import '../components/siem/siem.css'

export const SiemDatasetsPage: React.FC = () => {
  const [datasets, setDatasets] = useState<SecurityLogDataset[]>([])
  const [sources, setSources] = useState<LogSource[]>([])
  const [error, setError] = useState<string | null>(null)

  // Ingestion Modal
  const [showImportModal, setShowImportModal] = useState<boolean>(false)
  const [targetDatasetId, setTargetDatasetId] = useState<number | undefined>(undefined)
  const [importFormat, setImportFormat] = useState<string>('JSON')
  const [importContent, setImportContent] = useState<string>('')
  const [importing, setImporting] = useState<boolean>(false)
  const [importSuccess, setImportSuccess] = useState<string | null>(null)

  const loadData = async () => {
    try {
      setError(null)
      const [dsList, srcList] = await Promise.all([
        siemApi.listDatasets(),
        siemApi.listSources(),
      ])
      setDatasets(dsList)
      setSources(srcList)
      if (dsList.length > 0 && !targetDatasetId) {
        setTargetDatasetId(dsList[0].id)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load telemetry datasets')
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Sample templates for learners
  const handleLoadTemplate = (format: string) => {
    setImportFormat(format)
    if (format === 'JSON') {
      setImportContent(
        JSON.stringify(
          [
            {
              timestamp: new Date().toISOString(),
              event_type: 'windows_logon_failure',
              host: 'WORKSTATION-08.corp.test',
              username: 'contractor_temp',
              source_ip: '198.51.100.77',
              destination_ip: '192.0.2.10',
              action: 'LOGIN_FAILURE',
              severity: 'LOW',
              message: 'Failed login attempt via NTLM',
            },
            {
              timestamp: new Date().toISOString(),
              event_type: 'windows_logon_failure',
              host: 'WORKSTATION-08.corp.test',
              username: 'contractor_temp',
              source_ip: '198.51.100.77',
              destination_ip: '192.0.2.10',
              action: 'LOGIN_FAILURE',
              severity: 'LOW',
              message: 'Failed login attempt via NTLM - Bad Password',
            },
          ],
          null,
          2
        )
      )
    } else if (format === 'SYSLOG') {
      setImportContent(
        `Sep 30 18:30:15 gateway01 sshd[9182]: Failed password for invalid user admin from 198.51.100.44 port 51234 ssh2\n` +
        `Sep 30 18:30:18 gateway01 sshd[9184]: Failed password for invalid user root from 198.51.100.44 port 51235 ssh2\n` +
        `Sep 30 18:30:22 gateway01 sshd[9189]: Failed password for invalid user test from 198.51.100.44 port 51236 ssh2`
      )
    } else if (format === 'CEF') {
      setImportContent(
        `CEF:0|Cisco|ASA|9.2|106023|Deny Inbound TCP|7|src=198.51.100.88 dst=192.0.2.5 spt=60123 dpt=3389 proto=TCP act=DROP\n` +
        `CEF:0|Cisco|ASA|9.2|106023|Deny Inbound TCP|7|src=198.51.100.88 dst=192.0.2.5 spt=60124 dpt=445 proto=TCP act=DROP`
      )
    } else if (format === 'CSV') {
      setImportContent(
        `timestamp,host,username,source_ip,destination_ip,dst_port,protocol,action,message\n` +
        `${new Date().toISOString()},DC01,alice.smith,192.0.2.50,192.0.2.10,88,TCP,LOGIN,Kerberos ticket granted\n` +
        `${new Date().toISOString()},DC01,alice.smith,192.0.2.50,192.0.2.10,445,TCP,CONNECTION,SMB share access`
      )
    }
  }

  const handleExecuteImport = async () => {
    if (!targetDatasetId || !importContent.trim()) {
      window.alert('Please select a dataset and provide log content.')
      return
    }

    try {
      setImporting(true)
      setImportSuccess(null)
      const res = await siemApi.importLogs({
        dataset_id: targetDatasetId,
        content: importContent.trim(),
        format: importFormat,
      })
      setImportSuccess(`Successfully ingested ${res.imported_events} event(s)! Dataset now contains ${res.dataset_total} total records.`)
      setImportContent('')
      loadData()
    } catch (err: unknown) {
      window.alert(`Ingestion failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="siem-container">
      {/* Header */}
      <div className="siem-header">
        <div className="siem-header-left">
          <div className="siem-title-row">
            <h1>
              <Database className="text-cyan-400" size={26} />
              Datasets & Synthetic Ingestion
            </h1>
            <span className="siem-tag">OFFLINE ARCHITECTURE</span>
          </div>
          <p className="siem-subtitle">
            Manage multi-source educational log datasets, inspect collector sources, and safely ingest synthetic log events.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            className="siem-btn-primary"
            onClick={() => {
              handleLoadTemplate('JSON')
              setShowImportModal(true)
            }}
          >
            <Upload size={14} /> Ingest Synthetic Logs
          </button>
        </div>
      </div>

      <SiemNav />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239,68,68,0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', color: '#f87171' }}>
          {error}
        </div>
      )}

      {/* Safety Notice */}
      <div style={{ background: '#131b2e', border: '1px solid #1e293b', borderRadius: '0.5rem', padding: '1rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <ShieldCheck size={20} color="#10b981" />
        <div style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
          <strong style={{ color: '#f8fafc' }}>Safe Educational Environment:</strong> All telemetry is strictly offline and synthetic. All IP addresses adhere to RFC 5737 documentation ranges (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24). Ingestion includes spreadsheet formula injection neutralization and payload limits.
        </div>
      </div>

      {/* Section 1: Pre-loaded Datasets */}
      <div>
        <h2 style={{ fontSize: '1.125rem', color: '#f8fafc', margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={18} color="#38bdf8" />
          Educational Security Datasets ({datasets.length})
        </h2>

        <div className="datasets-grid">
          {datasets.map((ds) => (
            <div key={ds.id} className="dataset-card">
              <div>
                <div className="dataset-card-header">
                  <h3 className="dataset-name">{ds.name}</h3>
                  <span className={`sev-badge sev-${ds.difficulty === 'ADVANCED' ? 'HIGH' : ds.difficulty === 'INTERMEDIATE' ? 'MEDIUM' : 'LOW'}`}>
                    {ds.difficulty}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontFamily: 'monospace', marginTop: '0.25rem' }}>
                  {ds.stable_id} &bull; <span className="cat-badge">{ds.dataset_type}</span>
                </div>
                <p className="dataset-desc">{ds.description}</p>
              </div>

              <div className="dataset-meta">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  <HardDrive size={14} />
                  <span><strong>{ds.event_count.toLocaleString()}</strong> events</span>
                </div>
                {ds.start_time && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                    <Calendar size={14} />
                    <span>{new Date(ds.start_time).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: Configured Log Sources */}
      <div className="siem-table-container">
        <div className="siem-table-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Server size={16} color="#38bdf8" />
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>Configured Synthetic Log Sources ({sources.length})</span>
          </div>
          <span>Status & Platform Coverage</span>
        </div>

        <table className="siem-events-table">
          <thead>
            <tr>
              <th>Stable ID</th>
              <th>Source Name</th>
              <th>Source Type</th>
              <th>Platform / Vendor</th>
              <th>Status</th>
              <th>Classification</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((src) => (
              <tr key={src.id}>
                <td className="mono-cell" style={{ color: '#38bdf8' }}>{src.stable_id}</td>
                <td style={{ fontWeight: 500, color: '#f1f5f9' }}>{src.name}</td>
                <td><span className="cat-badge">{src.source_type}</span></td>
                <td>{src.platform} ({src.vendor})</td>
                <td>
                  <span style={{ color: src.status === 'ACTIVE' ? '#34d399' : '#f87171', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Radio size={12} /> {src.status}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    {src.is_synthetic ? 'Synthetic Generator' : 'Standard Ingestion'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Safe Ingestion Modal */}
      {showImportModal && (
        <div className="siem-modal-backdrop">
          <div className="siem-modal-box" style={{ width: '700px' }}>
            <div className="siem-modal-header">
              <h3 style={{ margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Upload size={18} color="#38bdf8" />
                Ingest Synthetic Security Logs
              </h3>
              <button className="drawer-close" onClick={() => setShowImportModal(false)}>
                <X size={18} />
              </button>
            </div>

            <div className="siem-modal-body">
              {importSuccess && (
                <div style={{ padding: '0.75rem', background: 'rgba(16,185,129,0.15)', border: '1px solid #10b981', borderRadius: '0.375rem', color: '#34d399', fontSize: '0.8125rem' }}>
                  {importSuccess}
                </div>
              )}

              <div>
                <label style={{ fontSize: '0.8125rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>
                  Target Dataset:
                </label>
                <select
                  className="condition-select"
                  style={{ width: '100%' }}
                  value={targetDatasetId ?? ''}
                  onChange={(e) => setTargetDatasetId(Number(e.target.value))}
                >
                  {datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.stable_id} - {d.name} ({d.event_count} events)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                  <label style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>Log Format & Sample Template:</label>
                  <div style={{ display: 'flex', gap: '0.375rem' }}>
                    {['JSON', 'SYSLOG', 'CEF', 'CSV'].map((fmt) => (
                      <button
                        key={fmt}
                        type="button"
                        className={`quick-filter-chip ${importFormat === fmt ? 'active' : ''}`}
                        onClick={() => handleLoadTemplate(fmt)}
                      >
                        {fmt}
                      </button>
                    ))}
                  </div>
                </div>

                <textarea
                  className="siem-input-main"
                  style={{ width: '100%', height: '180px', resize: 'vertical', fontSize: '0.75rem' }}
                  placeholder="Paste raw log lines or JSON array here..."
                  value={importContent}
                  onChange={(e) => setImportContent(e.target.value)}
                />
              </div>

              <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Info size={14} />
                <span>
                  Max 5MB payload limit, 2,000 events per submission. Spreadsheet formulas (=, +, -, @) are auto-neutralized.
                </span>
              </div>
            </div>

            <div className="siem-modal-footer">
              <button className="siem-btn-secondary" onClick={() => setShowImportModal(false)}>
                Cancel
              </button>
              <button
                className="siem-btn-primary"
                onClick={handleExecuteImport}
                disabled={importing}
              >
                {importing ? 'Normalizing & Ingesting...' : 'Submit & Ingest Logs'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
