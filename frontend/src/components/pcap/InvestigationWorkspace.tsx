import React, { useState } from 'react'
import { Bookmark, FileText, CheckSquare, Download, Plus, Trash2, Eye } from 'lucide-react'
import { Link } from 'react-router-dom'
import { pcapApi } from '../../services/pcapApi'
import type { BookmarkItem, NoteItem, FindingItem, FindingCreateRequest } from '../../types/pcap'

interface InvestigationWorkspaceProps {
  captureId: number
  bookmarks: BookmarkItem[]
  notes: NoteItem[]
  findings: FindingItem[]
  onRefreshData: () => void
  onSelectPacket?: (packetNumber: number) => void
}

export const InvestigationWorkspace: React.FC<InvestigationWorkspaceProps> = ({
  captureId,
  bookmarks,
  notes,
  findings,
  onRefreshData,
  onSelectPacket,
}) => {
  const [activeTab, setActiveTab] = useState<'bookmarks' | 'notes' | 'findings'>('bookmarks')

  // Note creation state
  const [noteTitle, setNoteTitle] = useState('')
  const [noteContent, setNoteContent] = useState('')
  const [isSubmittingNote, setIsSubmittingNote] = useState(false)

  // Finding creation state
  const [findingTitle, setFindingTitle] = useState('')
  const [findingDesc, setFindingDesc] = useState('')
  const [findingSeverity, setFindingSeverity] = useState('INFO')
  const [findingHypothesis, setFindingHypothesis] = useState('')
  const [findingConclusion, setFindingConclusion] = useState('')
  const [evidenceStr, setEvidenceStr] = useState('')
  const [isSubmittingFinding, setIsSubmittingFinding] = useState(false)

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!noteContent.trim()) return

    try {
      setIsSubmittingNote(true)
      await pcapApi.createNote(captureId, {
        title: noteTitle.trim() || undefined,
        content: noteContent.trim(),
      })
      setNoteTitle('')
      setNoteContent('')
      onRefreshData()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to save note')
    } finally {
      setIsSubmittingNote(false)
    }
  }

  const handleCreateFinding = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!findingTitle.trim() || !findingDesc.trim()) return

    const evidencePkts = evidenceStr
      .split(',')
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n))

    try {
      setIsSubmittingFinding(true)
      const payload: FindingCreateRequest = {
        title: findingTitle.trim(),
        description: findingDesc.trim(),
        severity: findingSeverity,
        hypothesis: findingHypothesis.trim() || undefined,
        conclusion: findingConclusion.trim() || undefined,
        evidence_packets: evidencePkts,
      }
      await pcapApi.createFinding(captureId, payload)
      setFindingTitle('')
      setFindingDesc('')
      setFindingHypothesis('')
      setFindingConclusion('')
      setEvidenceStr('')
      onRefreshData()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to save finding')
    } finally {
      setIsSubmittingFinding(false)
    }
  }

  const handleDeleteBookmark = async (bookmarkId: number) => {
    try {
      await pcapApi.deleteBookmark(captureId, bookmarkId)
      onRefreshData()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to delete bookmark')
    }
  }

  const handleDownloadReportJson = async () => {
    try {
      const report = await pcapApi.getReport(captureId)
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(report, null, 2))
      const downloadAnchor = document.createElement('a')
      downloadAnchor.setAttribute('href', dataStr)
      downloadAnchor.setAttribute('download', `nexoranet_investigation_report_${captureId}.json`)
      document.body.appendChild(downloadAnchor)
      downloadAnchor.click()
      downloadAnchor.remove()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to download report')
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Workspace Subtabs & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            className={`pcap-tab-button ${activeTab === 'bookmarks' ? 'active' : ''}`}
            onClick={() => setActiveTab('bookmarks')}
          >
            <Bookmark size={16} />
            Bookmarks ({bookmarks.length})
          </button>
          <button
            type="button"
            className={`pcap-tab-button ${activeTab === 'notes' ? 'active' : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            <FileText size={16} />
            Analyst Notes ({notes.length})
          </button>
          <button
            type="button"
            className={`pcap-tab-button ${activeTab === 'findings' ? 'active' : ''}`}
            onClick={() => setActiveTab('findings')}
          >
            <CheckSquare size={16} />
            Findings ({findings.length})
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            type="button"
            className="pcap-page-btn"
            onClick={handleDownloadReportJson}
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <Download size={14} /> Export JSON
          </button>
          <Link
            to={`/packet-analysis/report/${captureId}`}
            className="pcap-filter-apply-btn"
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8125rem' }}
          >
            <Eye size={14} /> View SOC Report
          </Link>
        </div>
      </div>

      {/* Bookmarks Tab */}
      {activeTab === 'bookmarks' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {bookmarks.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
              <Bookmark size={32} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
              <p style={{ margin: 0, fontSize: '0.875rem' }}>
                No bookmarked packets yet. Click the bookmark icon in the packet table to flag noteworthy packets.
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '0.75rem' }}>
              {bookmarks.map((b) => (
                <div
                  key={b.id}
                  style={{
                    background: '#0f172a',
                    border: '1px solid #1e293b',
                    borderRadius: '8px',
                    padding: '0.875rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <button
                      type="button"
                      className="pcap-evidence-btn"
                      onClick={() => onSelectPacket?.(b.packet_number)}
                      style={{ fontSize: '0.8125rem', padding: '0.2rem 0.5rem' }}
                    >
                      Packet #{b.packet_number}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteBookmark(b.id)}
                      style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}
                      title="Delete bookmark"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  {b.note && <div style={{ fontSize: '0.8125rem', color: '#cbd5e1' }}>{b.note}</div>}
                  {b.tags && b.tags.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                      {b.tags.map((tag) => (
                        <span key={tag} style={{ background: '#1e293b', padding: '0.1rem 0.4rem', borderRadius: '3px', fontSize: '0.7rem', color: '#38bdf8' }}>
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Notes Tab */}
      {activeTab === 'notes' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '1.25rem' }}>
          {/* Note Form */}
          <form onSubmit={handleCreateNote} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <h4 style={{ margin: 0, color: '#fff', fontSize: '0.95rem' }}>Add Analyst Note</h4>
            <input
              type="text"
              className="pcap-filter-input"
              placeholder="Note Title (Optional)"
              value={noteTitle}
              onChange={(e) => setNoteTitle(e.target.value)}
            />
            <textarea
              className="pcap-filter-input"
              rows={4}
              placeholder="Record observations, suspect IP notes, or hypothesis..."
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              required
            />
            <button
              type="submit"
              className="pcap-filter-apply-btn"
              disabled={isSubmittingNote || !noteContent.trim()}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' }}
            >
              <Plus size={14} /> Save Note
            </button>
          </form>

          {/* Notes List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px', overflowY: 'auto' }}>
            {notes.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                No analyst notes recorded yet.
              </div>
            ) : (
              notes.map((n) => (
                <div key={n.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '0.875rem' }}>
                  {n.title && <h5 style={{ margin: '0 0 0.25rem', color: '#fff', fontSize: '0.9rem' }}>{n.title}</h5>}
                  <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.8125rem', whiteSpace: 'pre-wrap' }}>
                    {n.content}
                  </p>
                  <span style={{ display: 'block', marginTop: '0.5rem', fontSize: '0.7rem', color: '#64748b' }}>
                    {new Date(n.created_at).toLocaleString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Findings Tab */}
      {activeTab === 'findings' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.5fr', gap: '1.25rem' }}>
          {/* Finding Form */}
          <form onSubmit={handleCreateFinding} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <h4 style={{ margin: 0, color: '#fff', fontSize: '0.95rem' }}>Log Investigation Finding</h4>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="pcap-filter-input"
                placeholder="Finding Title"
                value={findingTitle}
                onChange={(e) => setFindingTitle(e.target.value)}
                required
                style={{ flex: 1 }}
              />
              <select
                className="pcap-filter-input"
                style={{ width: '110px' }}
                value={findingSeverity}
                onChange={(e) => setFindingSeverity(e.target.value)}
              >
                <option value="INFO">INFO</option>
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
              </select>
            </div>

            <textarea
              className="pcap-filter-input"
              rows={2}
              placeholder="Finding Description..."
              value={findingDesc}
              onChange={(e) => setFindingDesc(e.target.value)}
              required
            />

            <input
              type="text"
              className="pcap-filter-input"
              placeholder="Evidence Packet Numbers (comma-separated, e.g. 5, 8, 12)"
              value={evidenceStr}
              onChange={(e) => setEvidenceStr(e.target.value)}
            />

            <input
              type="text"
              className="pcap-filter-input"
              placeholder="Investigative Hypothesis"
              value={findingHypothesis}
              onChange={(e) => setFindingHypothesis(e.target.value)}
            />

            <textarea
              className="pcap-filter-input"
              rows={2}
              placeholder="Conclusion / Remediation"
              value={findingConclusion}
              onChange={(e) => setFindingConclusion(e.target.value)}
            />

            <button
              type="submit"
              className="pcap-filter-apply-btn"
              disabled={isSubmittingFinding || !findingTitle.trim() || !findingDesc.trim()}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' }}
            >
              <Plus size={14} /> Record Finding
            </button>
          </form>

          {/* Findings List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '480px', overflowY: 'auto' }}>
            {findings.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                No findings recorded yet. Use the form on the left to summarize your investigation.
              </div>
            ) : (
              findings.map((f) => (
                <div key={f.id} className={`pcap-obs-card ${f.severity}`} style={{ padding: '0.875rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <h5 style={{ margin: 0, color: '#fff', fontSize: '0.95rem' }}>{f.title}</h5>
                    <span className={`pcap-obs-severity ${f.severity}`}>{f.severity}</span>
                  </div>
                  <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.8125rem' }}>{f.description}</p>

                  {f.hypothesis && (
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                      <strong style={{ color: '#38bdf8' }}>Hypothesis:</strong> {f.hypothesis}
                    </div>
                  )}

                  {f.conclusion && (
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                      <strong style={{ color: '#10b981' }}>Conclusion:</strong> {f.conclusion}
                    </div>
                  )}

                  {f.evidence_packets && f.evidence_packets.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Evidence:</span>
                      {f.evidence_packets.map((pkt) => (
                        <button
                          key={pkt}
                          type="button"
                          className="pcap-evidence-btn"
                          onClick={() => onSelectPacket?.(pkt)}
                        >
                          #{pkt}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
