import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Binary,
  GitCommit,
  ShieldAlert,
  BarChart2,
  FileCheck2,
  RefreshCw,
  AlertCircle,
  FileText,
} from 'lucide-react'
import { pcapApi } from '../../services/pcapApi'
import type {
  CaptureDetail,
  ParsedPacketSummary,
  ParsedPacketDetail,
  ConversationItem,
  CaptureStatistics,
  EndpointItem,
  PortItem,
  TimelineBucketItem,
  ObservationItem,
  BookmarkItem,
  NoteItem,
  FindingItem,
} from '../../types/pcap'
import { PacketFilterBar } from '../../components/pcap/PacketFilterBar'
import { PacketTable } from '../../components/pcap/PacketTable'
import { PacketDetailsPanel } from '../../components/pcap/PacketDetailsPanel'
import { ConversationPanel } from '../../components/pcap/ConversationPanel'
import { StatisticsPanel } from '../../components/pcap/StatisticsPanel'
import { ObservationPanel } from '../../components/pcap/ObservationPanel'
import { InvestigationWorkspace } from '../../components/pcap/InvestigationWorkspace'
import '../../components/pcap/pcap.css'

export const CaptureInspectionPage: React.FC = () => {
  const { captureId } = useParams<{ captureId: string }>()
  const navigate = useNavigate()
  const id = Number(captureId)

  // Master telemetry state
  const [capture, setCapture] = useState<CaptureDetail | null>(null)
  const [activeTab, setActiveTab] = useState<
    'packets' | 'conversations' | 'observations' | 'statistics' | 'workspace'
  >('packets')

  // Packets state
  const [packets, setPackets] = useState<ParsedPacketSummary[]>([])
  const [totalMatched, setTotalMatched] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filterStr, setFilterStr] = useState('')
  const [filterError, setFilterError] = useState<string | null>(null)
  const [isPacketsLoading, setIsPacketsLoading] = useState(false)

  // Selected Packet Details state
  const [selectedPacketNumber, setSelectedPacketNumber] = useState<number | null>(null)
  const [selectedPacketDetail, setSelectedPacketDetail] = useState<ParsedPacketDetail | null>(null)
  const [isDetailLoading, setIsDetailLoading] = useState(false)

  // Conversations state
  const [conversations, setConversations] = useState<ConversationItem[]>([])
  const [isConvLoading, setIsConvLoading] = useState(false)

  // Statistics state
  const [statistics, setStatistics] = useState<CaptureStatistics | null>(null)
  const [endpoints, setEndpoints] = useState<EndpointItem[]>([])
  const [ports, setPorts] = useState<PortItem[]>([])
  const [timeline, setTimeline] = useState<TimelineBucketItem[]>([])
  const [isStatsLoading, setIsStatsLoading] = useState(false)

  // Observations state
  const [observations, setObservations] = useState<ObservationItem[]>([])
  const [isObsLoading, setIsObsLoading] = useState(false)

  // Workspace state
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([])
  const [notes, setNotes] = useState<NoteItem[]>([])
  const [findings, setFindings] = useState<FindingItem[]>([])

  const [generalError, setGeneralError] = useState<string | null>(null)

  // 1. Load capture details
  const loadCaptureMeta = useCallback(async () => {
    if (!id) return
    try {
      const data = await pcapApi.getCapture(id)
      setCapture(data)
    } catch (err: unknown) {
      setGeneralError(err instanceof Error ? err.message : 'Failed to load capture metadata')
    }
  }, [id])

  // 2. Load packets with pagination & display filtering
  const loadPackets = useCallback(
    async (page: number, filter: string) => {
      if (!id) return
      try {
        setIsPacketsLoading(true)
        setFilterError(null)
        const resp = await pcapApi.getPackets(id, { page, pageSize: 50, filter })
        setPackets(resp.packets)
        setTotalMatched(resp.total_matched)
        setCurrentPage(resp.page)
        setTotalPages(resp.total_pages)

        // Auto-select first packet if none selected or previous selection not in view
        if (resp.packets.length > 0 && selectedPacketNumber === null) {
          setSelectedPacketNumber(resp.packets[0].packet_number)
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Filter error'
        setFilterError(msg)
      } finally {
        setIsPacketsLoading(false)
      }
    },
    [id, selectedPacketNumber]
  )

  // 3. Load selected packet layer details
  const loadPacketDetail = useCallback(
    async (packetNum: number) => {
      if (!id) return
      try {
        setIsDetailLoading(true)
        const detail = await pcapApi.getPacketDetail(id, packetNum)
        setSelectedPacketDetail(detail)
      } catch (err: unknown) {
        console.error('Failed to load packet detail:', err)
      } finally {
        setIsDetailLoading(false)
      }
    },
    [id]
  )

  // 4. Load conversations
  const loadConversations = useCallback(async () => {
    if (!id) return
    try {
      setIsConvLoading(true)
      const data = await pcapApi.getConversations(id)
      setConversations(data)
    } catch (err: unknown) {
      console.error('Failed to load conversations:', err)
    } finally {
      setIsConvLoading(false)
    }
  }, [id])

  // 5. Load statistics, endpoints, ports, timeline
  const loadStatistics = useCallback(async () => {
    if (!id) return
    try {
      setIsStatsLoading(true)
      const [stats, eps, pts, tl] = await Promise.all([
        pcapApi.getStatistics(id),
        pcapApi.getEndpoints(id),
        pcapApi.getPorts(id),
        pcapApi.getTimeline(id, 20),
      ])
      setStatistics(stats)
      setEndpoints(eps)
      setPorts(pts)
      setTimeline(tl)
    } catch (err: unknown) {
      console.error('Failed to load statistics:', err)
    } finally {
      setIsStatsLoading(false)
    }
  }, [id])

  // 6. Load observations
  const loadObservations = useCallback(async () => {
    if (!id) return
    try {
      setIsObsLoading(true)
      const obs = await pcapApi.getObservations(id)
      setObservations(obs)
    } catch (err: unknown) {
      console.error('Failed to load observations:', err)
    } finally {
      setIsObsLoading(false)
    }
  }, [id])

  // 7. Load workspace items
  const loadWorkspace = useCallback(async () => {
    if (!id) return
    try {
      const [bm, nt, fd] = await Promise.all([
        pcapApi.listBookmarks(id),
        pcapApi.listNotes(id),
        pcapApi.listFindings(id),
      ])
      setBookmarks(bm)
      setNotes(nt)
      setFindings(fd)
    } catch (err: unknown) {
      console.error('Failed to load workspace items:', err)
    }
  }, [id])

  // Initial load
  useEffect(() => {
    loadCaptureMeta()
    loadPackets(1, '')
    loadConversations()
    loadStatistics()
    loadObservations()
    loadWorkspace()
  }, [loadCaptureMeta, loadPackets, loadConversations, loadStatistics, loadObservations, loadWorkspace])

  // Load packet detail when selected
  useEffect(() => {
    if (selectedPacketNumber !== null) {
      loadPacketDetail(selectedPacketNumber)
    }
  }, [selectedPacketNumber, loadPacketDetail])

  // Handlers
  const handleApplyFilter = (newFilter: string) => {
    setFilterStr(newFilter)
    setCurrentPage(1)
    loadPackets(1, newFilter)
  }

  const handleSelectPacketFromAnywhere = (packetNum: number) => {
    setSelectedPacketNumber(packetNum)
    setActiveTab('packets')
  }

  const handleToggleBookmark = async (packetNumber: number) => {
    const existing = bookmarks.find((b) => b.packet_number === packetNumber)
    try {
      if (existing) {
        await pcapApi.deleteBookmark(id, existing.id)
      } else {
        await pcapApi.createBookmark(id, { packet_number: packetNumber, note: 'Flagged packet' })
      }
      loadWorkspace()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to update bookmark')
    }
  }

  const bookmarkedNumbersSet = new Set(bookmarks.map((b) => b.packet_number))

  if (generalError) {
    return (
      <div className="pcap-container">
        <div className="pcap-notice-banner danger">
          <AlertCircle size={20} />
          <span>{generalError}</span>
        </div>
        <button type="button" className="pcap-page-btn" onClick={() => navigate('/packet-analysis')}>
          Back to Packet Captures
        </button>
      </div>
    )
  }

  return (
    <div className="pcap-container">
      {/* Offline Safety Notice */}
      <div className="pcap-notice-banner safety">
        <ShieldAlert size={18} style={{ flexShrink: 0 }} />
        <span>
          <strong>Offline Analysis Mode:</strong> NexoraNet inspects and dissects packet captures offline. It does not transmit, replay, or execute captured network traffic.
        </span>
      </div>

      {/* Workbench Navigation Header */}
      <div className="pcap-workbench-header">
        <div className="pcap-workbench-title-group">
          <button
            type="button"
            className="pcap-page-btn"
            onClick={() => navigate('/packet-analysis')}
            title="Back to Catalog"
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <ArrowLeft size={14} /> Catalog
          </button>

          <div>
            <h2 className="pcap-workbench-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              {capture?.name || `Capture #${id}`}
              {capture?.status && (
                <span className={`pcap-workbench-badge ${capture.status}`}>{capture.status}</span>
              )}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>
              <span>Packets: {capture?.packet_count ?? 0}</span>
              <span>•</span>
              <span>Duration: {capture?.duration.toFixed(3) ?? '0.000'}s</span>
              <span>•</span>
              <span>File: {capture?.filename}</span>
            </div>
          </div>
        </div>

        <div className="pcap-workbench-actions">
          <button
            type="button"
            className="pcap-page-btn"
            onClick={() => {
              loadCaptureMeta()
              loadPackets(currentPage, filterStr)
              loadConversations()
              loadStatistics()
              loadObservations()
              loadWorkspace()
            }}
            title="Refresh Analysis Telemetry"
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <Link
            to={`/detection/run?captureId=${id}`}
            className="pcap-page-btn"
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8125rem', borderColor: '#0284c7', color: '#38bdf8' }}
            title="Analyze with Detection Engine"
          >
            <ShieldAlert size={16} /> Run Detection
          </Link>
          <Link
            to="/threat-intelligence/indicators"
            className="pcap-page-btn"
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8125rem', borderColor: '#7c3aed', color: '#c084fc' }}
            title="Investigate Threat Indicators"
          >
            🎯 Threat Intel
          </Link>
          <Link
            to={`/packet-analysis/report/${id}`}
            className="pcap-filter-apply-btn"
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8125rem' }}
          >
            <FileText size={16} /> SOC Report
          </Link>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="pcap-tabs">
        <button
          type="button"
          className={`pcap-tab-button ${activeTab === 'packets' ? 'active' : ''}`}
          onClick={() => setActiveTab('packets')}
        >
          <Binary size={16} />
          Packet Dissector
        </button>

        <button
          type="button"
          className={`pcap-tab-button ${activeTab === 'conversations' ? 'active' : ''}`}
          onClick={() => setActiveTab('conversations')}
        >
          <GitCommit size={16} />
          Conversations & Flows ({conversations.length})
        </button>

        <button
          type="button"
          className={`pcap-tab-button ${activeTab === 'observations' ? 'active' : ''}`}
          onClick={() => setActiveTab('observations')}
        >
          <ShieldAlert size={16} />
          Observations ({observations.length})
        </button>

        <button
          type="button"
          className={`pcap-tab-button ${activeTab === 'statistics' ? 'active' : ''}`}
          onClick={() => setActiveTab('statistics')}
        >
          <BarChart2 size={16} />
          Statistics
        </button>

        <button
          type="button"
          className={`pcap-tab-button ${activeTab === 'workspace' ? 'active' : ''}`}
          onClick={() => setActiveTab('workspace')}
        >
          <FileCheck2 size={16} />
          Investigation Workspace ({bookmarks.length + findings.length})
        </button>
      </div>

      {/* Tab 1: Packet Dissector (Filter + Table + Layer Inspector Tree) */}
      {activeTab === 'packets' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <PacketFilterBar
            currentFilter={filterStr}
            onApplyFilter={handleApplyFilter}
            totalMatched={totalMatched}
            totalPackets={capture?.packet_count}
            filterError={filterError}
          />

          <PacketTable
            packets={packets}
            selectedPacketNumber={selectedPacketNumber}
            onSelectPacket={setSelectedPacketNumber}
            bookmarkedPacketNumbers={bookmarkedNumbersSet}
            onToggleBookmark={handleToggleBookmark}
            currentPage={currentPage}
            totalPages={totalPages}
            totalMatched={totalMatched}
            onPageChange={(p) => loadPackets(p, filterStr)}
            isLoading={isPacketsLoading}
          />

          <PacketDetailsPanel
            packet={selectedPacketDetail}
            isLoading={isDetailLoading}
          />
        </div>
      )}

      {/* Tab 2: Conversations & Flow Ladder */}
      {activeTab === 'conversations' && (
        <ConversationPanel
          conversations={conversations}
          onSelectPacket={handleSelectPacketFromAnywhere}
          isLoading={isConvLoading}
        />
      )}

      {/* Tab 3: Observations Engine */}
      {activeTab === 'observations' && (
        <ObservationPanel
          observations={observations}
          onSelectPacket={handleSelectPacketFromAnywhere}
          isLoading={isObsLoading}
        />
      )}

      {/* Tab 4: Traffic Statistics */}
      {activeTab === 'statistics' && (
        <StatisticsPanel
          statistics={statistics}
          endpoints={endpoints}
          ports={ports}
          timeline={timeline}
          isLoading={isStatsLoading}
        />
      )}

      {/* Tab 5: Investigation Workspace */}
      {activeTab === 'workspace' && (
        <InvestigationWorkspace
          captureId={id}
          bookmarks={bookmarks}
          notes={notes}
          findings={findings}
          onRefreshData={loadWorkspace}
          onSelectPacket={handleSelectPacketFromAnywhere}
        />
      )}
    </div>
  )
}
