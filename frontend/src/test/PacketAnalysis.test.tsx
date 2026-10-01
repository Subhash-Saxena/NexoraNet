import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { PacketFilterBar } from '../components/pcap/PacketFilterBar'
import { PacketTable } from '../components/pcap/PacketTable'
import { PacketDetailsPanel } from '../components/pcap/PacketDetailsPanel'
import { ConversationPanel } from '../components/pcap/ConversationPanel'
import { StatisticsPanel } from '../components/pcap/StatisticsPanel'
import { ObservationPanel } from '../components/pcap/ObservationPanel'
import { InvestigationWorkspace } from '../components/pcap/InvestigationWorkspace'
import { PacketAnalysisPage } from '../pages/PacketAnalysis/PacketAnalysisPage'
import { pcapApi } from '../services/pcapApi'
import type {
  CaptureSummary,
  ParsedPacketSummary,
  ParsedPacketDetail,
  ConversationItem,
  CaptureStatistics,
  ObservationItem,
  BookmarkItem,
  NoteItem,
  FindingItem,
} from '../types/pcap'

vi.mock('../services/pcapApi', () => ({
  pcapApi: {
    listCaptures: vi.fn(),
    getCapture: vi.fn(),
    uploadCapture: vi.fn(),
    deleteCapture: vi.fn(),
    getPackets: vi.fn(),
    getPacketDetail: vi.fn(),
    getStatistics: vi.fn(),
    getConversations: vi.fn(),
    getEndpoints: vi.fn(),
    getPorts: vi.fn(),
    getTimeline: vi.fn(),
    getObservations: vi.fn(),
    listBookmarks: vi.fn(),
    createBookmark: vi.fn(),
    deleteBookmark: vi.fn(),
    listNotes: vi.fn(),
    createNote: vi.fn(),
    listFindings: vi.fn(),
    createFinding: vi.fn(),
    getReport: vi.fn(),
  },
}))

describe('PacketFilterBar Component', () => {
  it('renders presets and invokes onApplyFilter on chip click', () => {
    const handleApply = vi.fn()
    render(
      <PacketFilterBar
        currentFilter=""
        onApplyFilter={handleApply}
        totalMatched={10}
        totalPackets={10}
      />
    )

    expect(screen.getByText('Quick Filters:')).toBeInTheDocument()
    const tcpChip = screen.getByRole('button', { name: 'TCP' })
    fireEvent.click(tcpChip)
    expect(handleApply).toHaveBeenCalledWith('tcp')
  })

  it('submits typed filter expression on form submit', () => {
    const handleApply = vi.fn()
    render(
      <PacketFilterBar
        currentFilter=""
        onApplyFilter={handleApply}
      />
    )

    const input = screen.getByPlaceholderText(/apply display filter/i)
    fireEvent.change(input, { target: { value: 'ip.addr == 192.168.1.1' } })
    const applyBtn = screen.getByRole('button', { name: /apply filter/i })
    fireEvent.click(applyBtn)

    expect(handleApply).toHaveBeenCalledWith('ip.addr == 192.168.1.1')
  })
})

describe('PacketTable Component', () => {
  const samplePackets: ParsedPacketSummary[] = [
    {
      packet_number: 1,
      timestamp: 1700000000.1,
      relative_time: 0.1,
      captured_length: 74,
      protocol: 'TCP',
      source_ip: '10.0.0.5',
      destination_ip: '10.0.0.80',
      source_port: 50000,
      destination_port: 80,
      info: '50000 -> 80 [SYN] Seq=0',
    },
    {
      packet_number: 2,
      timestamp: 1700000000.12,
      relative_time: 0.12,
      captured_length: 74,
      protocol: 'TCP',
      source_ip: '10.0.0.80',
      destination_ip: '10.0.0.5',
      source_port: 80,
      destination_port: 50000,
      info: '80 -> 50000 [SYN, ACK] Seq=0 Ack=1',
    },
  ]

  it('renders packet rows and triggers onSelectPacket', () => {
    const handleSelect = vi.fn()
    render(
      <PacketTable
        packets={samplePackets}
        selectedPacketNumber={1}
        onSelectPacket={handleSelect}
        currentPage={1}
        totalPages={1}
        totalMatched={2}
        onPageChange={vi.fn()}
      />
    )

    expect(screen.getByText('50000 -> 80 [SYN] Seq=0')).toBeInTheDocument()
    expect(screen.getByText('80 -> 50000 [SYN, ACK] Seq=0 Ack=1')).toBeInTheDocument()

    // Click second row
    fireEvent.click(screen.getByText('80 -> 50000 [SYN, ACK] Seq=0 Ack=1'))
    expect(handleSelect).toHaveBeenCalledWith(2)
  })
})

describe('PacketDetailsPanel Component', () => {
  const sampleDetail: ParsedPacketDetail = {
    packet_number: 5,
    timestamp: 1700000000.5,
    relative_time: 0.5,
    captured_length: 120,
    original_length: 120,
    protocol: 'HTTP',
    source_ip: '10.0.0.5',
    destination_ip: '10.0.0.80',
    tcp_flags: ['ACK', 'PSH'],
    layers: ['Frame', 'Ethernet', 'IPv4', 'TCP', 'HTTP'],
    layer_details: {
      IPv4: {
        src: '10.0.0.5',
        dst: '10.0.0.80',
        ttl: 64,
        proto: 6,
      },
      TCP: {
        sport: 50000,
        dport: 80,
        seq: 101,
        ack: 201,
      },
    },
    info: 'GET /index.html HTTP/1.1',
  }

  it('renders empty state when no packet is selected', () => {
    render(<PacketDetailsPanel packet={null} />)
    expect(screen.getByText('No Packet Selected')).toBeInTheDocument()
  })

  it('renders decoded layers and fields when packet is selected', () => {
    render(<PacketDetailsPanel packet={sampleDetail} />)
    expect(screen.getByText(/Packet #5/)).toBeInTheDocument()
    expect(screen.getByText('Layer: IPv4')).toBeInTheDocument()
    expect(screen.getByText('Layer: TCP')).toBeInTheDocument()
    expect(screen.getByText('ttl:')).toBeInTheDocument()
    expect(screen.getByText('64')).toBeInTheDocument()
  })
})

describe('ConversationPanel Component', () => {
  const sampleConvs: ConversationItem[] = [
    {
      id: 'TCP_10.0.0.5:50000_10.0.0.80:80',
      client_endpoint: '10.0.0.5:50000',
      server_endpoint: '10.0.0.80:80',
      protocol: 'TCP',
      packet_count: 4,
      byte_count: 320,
      total_bytes: 320,
      start_time: 0.1,
      duration: 0.15,
      handshake_state: 'COMPLETE',
      ladder: [
        {
          step: 1,
          relative_time: 0.1,
          source: '10.0.0.5:50000',
          destination: '10.0.0.80:80',
          protocol: 'TCP',
          info: '[SYN] Seq=0',
          tcp_flags: ['SYN'],
        },
      ],
    },
  ]

  it('renders conversation list and sequence ladder', () => {
    render(<ConversationPanel conversations={sampleConvs} />)
    expect(screen.getByText('10.0.0.5:50000')).toBeInTheDocument()
    expect(screen.getByText('Flow Sequence Diagram')).toBeInTheDocument()
    expect(screen.getByText('[SYN] Seq=0')).toBeInTheDocument()
  })
})

describe('StatisticsPanel Component', () => {
  const sampleStats: CaptureStatistics = {
    capture_id: 1,
    total_packets: 150,
    total_bytes: 45000,
    duration_seconds: 5.2,
    packets_per_second: 28.8,
    bytes_per_second: 8653.8,
    unique_ips: 4,
    unique_macs: 3,
    unique_ports: 5,
    protocol_distribution: { TCP: 100, HTTP: 30, DNS: 20 },
    top_protocols: [
      { protocol: 'TCP', count: 100, percentage: 66.7 },
      { protocol: 'HTTP', count: 30, percentage: 20.0 },
    ],
    top_talkers: [
      { ip: '10.0.0.5', packet_count: 80, byte_count: 24000, destinations: ['10.0.0.80'] },
    ],
  }

  it('renders KPI metrics and protocol distribution', () => {
    render(
      <StatisticsPanel
        statistics={sampleStats}
        endpoints={[]}
        ports={[]}
        timeline={[]}
      />
    )

    expect(screen.getByText('150')).toBeInTheDocument()
    expect(screen.getByText('Protocol Distribution')).toBeInTheDocument()
    expect(screen.getByText('TCP')).toBeInTheDocument()
  })
})

describe('ObservationPanel Component', () => {
  const sampleObservations: ObservationItem[] = [
    {
      id: 'obs-syn-1',
      type: 'HIGH_SYN_RATE',
      severity: 'LOW',
      title: 'Elevated TCP SYN Attempt Frequency',
      description: 'Host 10.0.0.99 generated 7 SYN packets in 0.35s.',
      why_it_matters: 'Indicates connection scanning or rapid session initialization.',
      cyber_relevance: 'Common pattern in port scans.',
      evidence_packets: [1, 2, 3, 4, 5],
    },
  ]

  it('renders observation title and evidence packet buttons', () => {
    const handleSelect = vi.fn()
    render(
      <ObservationPanel
        observations={sampleObservations}
        onSelectPacket={handleSelect}
      />
    )

    expect(screen.getByText('Elevated TCP SYN Attempt Frequency')).toBeInTheDocument()
    const pktBtn = screen.getByRole('button', { name: '#1' })
    fireEvent.click(pktBtn)
    expect(handleSelect).toHaveBeenCalledWith(1)
  })
})

describe('InvestigationWorkspace Component', () => {
  const sampleBookmarks: BookmarkItem[] = [
    {
      id: 1,
      capture_id: 10,
      packet_number: 4,
      note: 'HTTP GET request containing query parameter',
      tags: ['web', 'http'],
      created_at: new Date().toISOString(),
    },
  ]

  const sampleNotes: NoteItem[] = [
    {
      id: 1,
      capture_id: 10,
      target_type: 'general',
      target_id: null,
      title: 'Initial Recon',
      content: 'Examining outbound DNS query sequences.',
      created_at: new Date().toISOString(),
    },
  ]

  const sampleFindings: FindingItem[] = [
    {
      id: 1,
      capture_id: 10,
      title: 'Unauthenticated API access pattern',
      description: 'Multiple queries sent without auth header.',
      severity: 'LOW',
      evidence_packets: [4, 5],
      hypothesis: 'Service misconfiguration',
      conclusion: 'Implement Bearer token requirement',
      created_at: new Date().toISOString(),
    },
  ]

  it('renders bookmarks and supports tab switching to notes and findings', () => {
    render(
      <MemoryRouter>
        <InvestigationWorkspace
          captureId={10}
          bookmarks={sampleBookmarks}
          notes={sampleNotes}
          findings={sampleFindings}
          onRefreshData={vi.fn()}
        />
      </MemoryRouter>
    )

    expect(screen.getByText(/HTTP GET request containing query parameter/)).toBeInTheDocument()

    // Switch to Notes tab
    fireEvent.click(screen.getByRole('button', { name: /Analyst Notes/i }))
    expect(screen.getByText('Initial Recon')).toBeInTheDocument()

    // Switch to Findings tab
    fireEvent.click(screen.getByRole('button', { name: /Findings/i }))
    expect(screen.getByText('Unauthenticated API access pattern')).toBeInTheDocument()
  })
})

describe('PacketAnalysisPage Component', () => {
  const mockCaptures: CaptureSummary[] = [
    {
      id: 1,
      name: 'Sample DNS Lookup',
      filename: 'dns_lookup.pcap',
      file_size: 1540,
      format: 'pcap',
      packet_count: 4,
      start_time: '2023-11-14T22:13:20Z',
      end_time: '2023-11-14T22:13:21Z',
      duration: 0.15,
      status: 'READY',
      error_message: null,
      is_sample: true,
      sample_category: 'DNS & NAME RESOLUTION',
      description: 'Recursive A record query for example.com',
      created_at: '2026-09-30T10:00:00Z',
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(pcapApi.listCaptures).mockResolvedValue(mockCaptures)
  })

  it('renders prebuilt sample captures and opens upload modal', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <PacketAnalysisPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('PCAP & Packet Analyzer')).toBeInTheDocument()
    expect(screen.getByText('Sample DNS Lookup')).toBeInTheDocument()

    // Open upload modal
    const uploadBtn = screen.getByRole('button', { name: /Upload PCAP/i })
    fireEvent.click(uploadBtn)
    expect(screen.getByText(/Click to browse/i)).toBeInTheDocument()
  })
})
