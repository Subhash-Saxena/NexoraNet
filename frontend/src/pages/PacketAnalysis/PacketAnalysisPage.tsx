import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Binary,
  UploadCloud,
  FileCheck2,
  Clock,
  HardDrive,
  Trash2,
  ShieldCheck,
  AlertCircle,
  Eye,
  RefreshCw,
} from 'lucide-react'
import { pcapApi } from '../../services/pcapApi'
import type { CaptureSummary, CaptureDetail } from '../../types/pcap'
import { CaptureUploader } from '../../components/pcap/CaptureUploader'
import '../../components/pcap/pcap.css'

export const PacketAnalysisPage: React.FC = () => {
  const navigate = useNavigate()
  const [captures, setCaptures] = useState<CaptureSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showUploadModal, setShowUploadModal] = useState(false)

  const loadCaptures = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await pcapApi.listCaptures()
      setCaptures(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load packet captures catalog')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadCaptures()
  }, [])

  const handleUploadSuccess = (newCapture: CaptureDetail) => {
    setShowUploadModal(false)
    navigate(`/packet-analysis/inspect/${newCapture.id}`)
  }

  const handleDeleteCapture = async (captureId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!window.confirm('Are you sure you want to delete this packet capture?')) return

    try {
      await pcapApi.deleteCapture(captureId)
      loadCaptures()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to delete capture')
    }
  }

  const sampleCaptures = captures.filter((c) => c.is_sample)
  const userCaptures = captures.filter((c) => !c.is_sample)

  return (
    <div className="pcap-container">
      {/* Offline Safety Notice */}
      <div className="pcap-notice-banner safety">
        <ShieldCheck size={20} style={{ flexShrink: 0 }} />
        <div>
          <strong>Educational Offline Forensics:</strong> NexoraNet inspects and decapsulates network packets completely offline in a safe virtual environment. Captures are never replayed, transmitted over the wire, or executed.
        </div>
      </div>

      {/* Catalog Header Bar */}
      <div className="pcap-workbench-header">
        <div className="pcap-workbench-title-group">
          <div style={{ background: '#0284c7', padding: '0.5rem', borderRadius: '8px', color: '#fff', display: 'flex' }}>
            <Binary size={24} />
          </div>
          <div>
            <h2 className="pcap-workbench-title">PCAP & Packet Analyzer</h2>
            <p style={{ margin: '0.2rem 0 0', color: '#94a3b8', fontSize: '0.8125rem' }}>
              Inspect packet headers, follow conversation streams, and observe network behavior offline.
            </p>
          </div>
        </div>

        <div className="pcap-workbench-actions">
          <button
            type="button"
            className="pcap-page-btn"
            onClick={loadCaptures}
            title="Refresh Catalog"
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <button
            type="button"
            className="pcap-filter-apply-btn"
            onClick={() => setShowUploadModal(true)}
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <UploadCloud size={16} /> Upload PCAP
          </button>
        </div>
      </div>

      {/* Upload Modal Drawer */}
      {showUploadModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
          onClick={() => setShowUploadModal(false)}
        >
          <div
            style={{ maxWidth: '640px', width: '100%' }}
            onClick={(e) => e.stopPropagation()}
          >
            <CaptureUploader
              onUploadSuccess={handleUploadSuccess}
              onCancel={() => setShowUploadModal(false)}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="pcap-notice-banner danger">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Prebuilt Educational Sample Captures */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem' }}>
              Prebuilt Protocol & Investigation Captures
            </h3>
            <p style={{ margin: '0.2rem 0 0', color: '#94a3b8', fontSize: '0.8125rem' }}>
              Curated packet captures demonstrating core networking protocols and notable security patterns.
            </p>
          </div>
          <span style={{ fontSize: '0.8125rem', color: '#64748b' }}>
            {sampleCaptures.length} samples available
          </span>
        </div>

        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
            Loading capture catalog...
          </div>
        ) : (
          <div className="pcap-library-grid">
            {sampleCaptures.map((cap) => (
              <div key={cap.id} className="pcap-sample-card">
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {cap.sample_category || 'PROTOCOL SAMPLE'}
                    </span>
                    <span className={`pcap-workbench-badge ${cap.status}`}>
                      {cap.status}
                    </span>
                  </div>

                  <h4 style={{ margin: '0 0 0.4rem', color: '#fff', fontSize: '1rem' }}>{cap.name}</h4>
                  <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.8125rem', lineHeight: 1.4 }}>
                    {cap.description || 'Reference capture for offline protocol examination.'}
                  </p>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', paddingBottom: '0.75rem', borderBottom: '1px solid #1e293b', marginBottom: '0.75rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <FileCheck2 size={13} /> {cap.packet_count} packets
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={13} /> {cap.duration.toFixed(2)}s
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <HardDrive size={13} /> {(cap.file_size / 1024).toFixed(1)} KB
                    </span>
                  </div>

                  <Link
                    to={`/packet-analysis/inspect/${cap.id}`}
                    className="pcap-inspect-btn"
                  >
                    <Eye size={16} /> Inspect Packets
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* User Uploads Section */}
      {userCaptures.length > 0 && (
        <section style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.1rem' }}>Your Uploaded Captures</h3>
          <div className="pcap-table-wrapper">
            <table className="pcap-packet-table">
              <thead>
                <tr>
                  <th>Capture Name</th>
                  <th>Format</th>
                  <th>Packets</th>
                  <th>Duration</th>
                  <th>Uploaded</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {userCaptures.map((cap) => (
                  <tr
                    key={cap.id}
                    onClick={() => navigate(`/packet-analysis/inspect/${cap.id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td style={{ color: '#fff', fontWeight: 600 }}>{cap.name}</td>
                    <td style={{ textTransform: 'uppercase' }}>{cap.format}</td>
                    <td>{cap.packet_count}</td>
                    <td>{cap.duration.toFixed(2)}s</td>
                    <td>{new Date(cap.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`pcap-workbench-badge ${cap.status}`}>{cap.status}</span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        type="button"
                        onClick={(e) => handleDeleteCapture(cap.id, e)}
                        style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}
                        title="Delete capture"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
