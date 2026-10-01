import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { DetectionDashboardPage } from '../pages/Detection/DetectionDashboardPage'
import { DetectionRunPage } from '../pages/Detection/DetectionRunPage'
import { AlertDetailsPage } from '../pages/Detection/AlertDetailsPage'
import { DetectionRulesPage } from '../pages/Detection/DetectionRulesPage'
import { detectionApi } from '../services/detectionApi'
import { pcapApi } from '../services/pcapApi'
import type {
  DetectionStats,
  DetectionAlertListItem,
  DetectionAlertDetail,
  DetectionRunResponse,
  DetectionRule,
  DetectionRuleTestResponse,
} from '../types/detection'
import type { CaptureSummary } from '../types/pcap'

vi.mock('../services/detectionApi', () => ({
  detectionApi: {
    getStats: vi.fn(),
    listRules: vi.fn(),
    getRule: vi.fn(),
    testRule: vi.fn(),
    createRun: vi.fn(),
    listRuns: vi.fn(),
    getRun: vi.fn(),
    listAlerts: vi.fn(),
    getAlert: vi.fn(),
    updateAlertStatus: vi.fn(),
    addAlertNote: vi.fn(),
  },
}))

vi.mock('../services/pcapApi', () => ({
  pcapApi: {
    listCaptures: vi.fn(),
  },
}))

const mockStats: DetectionStats = {
  total_runs: 3,
  total_alerts: 8,
  active_alerts: 5,
  alerts_by_severity: {
    CRITICAL: 1,
    HIGH: 3,
    MEDIUM: 2,
    LOW: 1,
    INFO: 1,
  },
  alerts_by_category: {
    TCP: 4,
    DNS: 2,
    ARP: 2,
  },
  alerts_by_status: {
    NEW: 4,
    ACKNOWLEDGED: 1,
    INVESTIGATING: 2,
    CLOSED: 1,
    FALSE_POSITIVE: 0,
  },
  total_rules: 15,
  active_rules: 15,
}

const mockAlerts: DetectionAlertListItem[] = [
  {
    id: 1,
    run_id: 10,
    rule_id: 1,
    rule_code: 'NET-TCP-001',
    capture_id: 5,
    title: 'Repeated TCP SYN Connection Attempts Without Completion',
    category: 'TCP',
    severity: 'HIGH',
    confidence: 'HIGH',
    status: 'NEW',
    source_ip: '192.168.1.100',
    source_port: 45000,
    destination_ip: '192.168.1.50',
    destination_port: 80,
    protocol: 'TCP',
    first_seen_timestamp: 1700000000.0,
    last_seen_timestamp: 1700000005.0,
    packet_count: 8,
    created_at: '2026-09-30T10:00:00Z',
  },
]

const mockAlertDetail: DetectionAlertDetail = {
  ...mockAlerts[0],
  explanation: 'Educational explanation: Rapid sequence of SYN packets indicates potential scan.',
  mitre_attack_id: 'T1046',
  mitre_technique: 'Network Service Discovery',
  investigation_steps: [
    'Inspect TCP flag distribution',
    'Verify if target host answered with RST or SYN-ACK',
    'Correlate with destination service logs',
  ],
  evidence: [
    {
      id: 101,
      alert_id: 1,
      evidence_type: 'PACKET',
      packet_number: 14,
      timestamp: 1.25,
      protocol: 'TCP',
      source_ip: '192.168.1.100',
      destination_ip: '192.168.1.50',
      source_port: 45000,
      destination_port: 80,
      evidence_payload: { flags: ['SYN'], seq: 1000 },
      summary: 'TCP SYN packet transmitted without completing three-way handshake.',
      created_at: '2026-09-30T10:00:00Z',
    },
  ],
  notes: [
    {
      id: 201,
      alert_id: 1,
      user_id: 2,
      author_name: 'Lead SOC Analyst',
      note: 'Source host verified as internal test scanner.',
      created_at: '2026-09-30T10:15:00Z',
    },
  ],
  status_history: [
    {
      id: 301,
      alert_id: 1,
      old_status: 'NEW',
      new_status: 'INVESTIGATING',
      reason: 'Triage started by analyst.',
      created_at: '2026-09-30T10:10:00Z',
    },
  ],
}

const mockRules: DetectionRule[] = [
  {
    id: 1,
    rule_id: 'NET-TCP-001',
    name: 'Repeated TCP SYN Connection Attempts',
    description: 'Detects a high volume of TCP SYN packets without completed three-way handshakes.',
    category: 'TCP',
    severity: 'HIGH',
    status: 'ENABLED',
    logic_type: 'SYN_BURST_DETECTION',
    threshold_config: { min_syn_count: 5, window_seconds: 10.0 },
    mitre_attack_id: 'T1046',
    mitre_technique: 'Network Service Discovery',
    explanation_template: 'Identified repeated TCP SYN packets.',
    investigation_steps: ['Check SYN response flags'],
    is_builtin: true,
  },
]

const mockCaptures: CaptureSummary[] = [
  {
    id: 5,
    name: 'Lab Reconnaissance Trace',
    filename: 'recon_trace.pcap',
    file_size: 15420,
    format: 'pcap',
    packet_count: 142,
    start_time: '2026-09-30T09:00:00Z',
    end_time: '2026-09-30T09:05:00Z',
    duration: 300.0,
    status: 'READY',
    error_message: null,
    is_sample: true,
    sample_category: 'Reconnaissance',
    description: 'Educational PCAP for port scan detection',
    created_at: '2026-09-30T09:00:00Z',
  },
]

describe('Step 11 — Detection Engine Frontend Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(detectionApi.getStats).mockResolvedValue(mockStats)
    vi.mocked(detectionApi.listAlerts).mockResolvedValue(mockAlerts)
    vi.mocked(detectionApi.listRuns).mockResolvedValue([])
    vi.mocked(detectionApi.listRules).mockResolvedValue(mockRules)
    vi.mocked(detectionApi.getAlert).mockResolvedValue(mockAlertDetail)
    vi.mocked(pcapApi.listCaptures).mockResolvedValue(mockCaptures)
  })

  it('renders DetectionDashboardPage with statistics and alerts table', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <DetectionDashboardPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Network Detection & SOC Triage')).toBeInTheDocument()
    expect(screen.getByText('Defensive Educational Detection:')).toBeInTheDocument()
    expect(screen.getByText('Active Triage Alerts')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument() // active alerts
    expect(screen.getByText('Repeated TCP SYN Connection Attempts Without Completion')).toBeInTheDocument()
    expect(screen.getByText('NET-TCP-001')).toBeInTheDocument()
  })

  it('renders DetectionRunPage, selects capture, and executes detection run', async () => {
    const mockRunResult: DetectionRunResponse = {
      id: 12,
      source_type: 'PCAP',
      capture_id: 5,
      status: 'COMPLETED',
      packets_analyzed: 142,
      alerts_generated: 2,
      execution_time_ms: 18.5,
      created_at: '2026-09-30T10:30:00Z',
    }
    vi.mocked(detectionApi.createRun).mockResolvedValue(mockRunResult)

    await act(async () => {
      render(
        <MemoryRouter>
          <DetectionRunPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Execute Offline Detection Run')).toBeInTheDocument()
    expect(screen.getByText('1. Select Target PCAP Capture')).toBeInTheDocument()

    const launchButton = screen.getByRole('button', { name: /launch detection run/i })
    await act(async () => {
      fireEvent.click(launchButton)
    })

    expect(detectionApi.createRun).toHaveBeenCalledWith({
      source_type: 'PCAP',
      capture_id: 5,
      rule_ids: undefined,
    })

    expect(await screen.findByText('Detection Run #12 Completed!')).toBeInTheDocument()
    expect(screen.getByText('142')).toBeInTheDocument() // packets analyzed
  })

  it('renders AlertDetailsPage, toggles checklist step, updates status, and adds note', async () => {
    const updatedAlert: DetectionAlertDetail = {
      ...mockAlertDetail,
      status: 'INVESTIGATING',
    }
    vi.mocked(detectionApi.updateAlertStatus).mockResolvedValue(updatedAlert)
    vi.mocked(detectionApi.addAlertNote).mockResolvedValue({
      id: 202,
      alert_id: 1,
      user_id: 2,
      author_name: 'Student Analyst',
      note: 'Verified syn flags in wireshark.',
      created_at: '2026-09-30T11:00:00Z',
    })

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/detection/alerts/1']}>
          <Routes>
            <Route path="/detection/alerts/:alertId" element={<AlertDetailsPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    // Header & Flow Box
    expect(screen.getByText('Repeated TCP SYN Connection Attempts Without Completion')).toBeInTheDocument()
    expect(screen.getByText('192.168.1.100:45000')).toBeInTheDocument()
    expect(screen.getByText('192.168.1.50:80')).toBeInTheDocument()
    expect(screen.getByText('MITRE T1046')).toBeInTheDocument()

    // Interactive Checklist
    const step1 = screen.getByText(/Inspect TCP flag distribution/i)
    expect(step1).toBeInTheDocument()
    await act(async () => {
      fireEvent.click(step1)
    })
    expect(screen.getByText('1 / 3 Completed')).toBeInTheDocument()

    // Evidence Table
    expect(screen.getByText('TCP SYN packet transmitted without completing three-way handshake.')).toBeInTheDocument()

    // Update Status
    const updateButton = screen.getByRole('button', { name: /apply status change/i })
    await act(async () => {
      fireEvent.click(updateButton)
    })
    expect(detectionApi.updateAlertStatus).toHaveBeenCalled()

    // Add Note
    const noteTextarea = screen.getByPlaceholderText(/Add observations, Wireshark filter syntax/i)
    fireEvent.change(noteTextarea, { target: { value: 'Verified syn flags in wireshark.' } })
    const noteSubmitBtn = screen.getByRole('button', { name: /add note/i })
    await act(async () => {
      fireEvent.click(noteSubmitBtn)
    })
    expect(detectionApi.addAlertNote).toHaveBeenCalledWith(1, 'Verified syn flags in wireshark.')
  })

  it('renders DetectionRulesPage and executes dry-run simulation in Sandbox', async () => {
    const mockTestRes: DetectionRuleTestResponse = {
      rule_id: 'NET-TCP-001',
      matches_found: 1,
      simulated_alerts: [
        {
          title: 'Simulated Repeated SYN Burst',
          category: 'TCP',
          severity: 'HIGH',
          confidence: 'HIGH',
          explanation: 'Simulated alert for testing',
          source_ip: '10.0.0.1',
          destination_ip: '10.0.0.2',
          packet_count: 5,
          evidence_count: 5,
          investigation_steps: ['Step 1'],
        },
      ],
      execution_time_ms: 4.2,
    }
    vi.mocked(detectionApi.testRule).mockResolvedValue(mockTestRes)

    await act(async () => {
      render(
        <MemoryRouter>
          <DetectionRulesPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Detection Rule Catalog & Sandbox')).toBeInTheDocument()
    expect(screen.getByText('NET-TCP-001')).toBeInTheDocument()

    // Open Test Sandbox Modal
    const testBtn = screen.getByRole('button', { name: 'Test' })
    await act(async () => {
      fireEvent.click(testBtn)
    })

    expect(screen.getByText('Simulate Rule Test: NET-TCP-001')).toBeInTheDocument()

    // Run simulation
    const runSimBtn = screen.getByRole('button', { name: 'Run Simulation' })
    await act(async () => {
      fireEvent.click(runSimBtn)
    })

    expect(detectionApi.testRule).toHaveBeenCalledWith({
      rule_id: 'NET-TCP-001',
      capture_id: 5,
    })

    expect(await screen.findByText('Simulated Repeated SYN Burst')).toBeInTheDocument()
    expect(screen.getByText('4.2 ms')).toBeInTheDocument()
  })
})
