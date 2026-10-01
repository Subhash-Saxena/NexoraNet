import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { SocDashboardPage } from '../pages/Soc/SocDashboardPage'
import { AlertQueuePage } from '../pages/Soc/AlertQueuePage'
import { AlertDetailPage } from '../pages/Soc/AlertDetailPage'
import { AlertTriagePage } from '../pages/Soc/AlertTriagePage'
import { InvestigationWorkspacePage } from '../pages/Soc/InvestigationWorkspacePage'
import { SocChallengeDetailPage } from '../pages/Soc/SocChallengeDetailPage'
import { socApi } from '../services/socApi'
import type {
  SocOverviewResponse,
  SocStatisticsResponse,
  SocAlertItem,
  SocAlertDetailResponse,
  InvestigationDetailResponse,
  SocChallengeDetailResponse,
  SocChallengeEvaluation,
} from '../types/soc'

vi.mock('../services/socApi', () => ({
  socApi: {
    getOverview: vi.fn(),
    getStatistics: vi.fn(),
    getActivityStream: vi.fn(),
    listAlerts: vi.fn(),
    getAlertDetail: vi.fn(),
    acknowledgeAlert: vi.fn(),
    updateClassification: vi.fn(),
    bulkAlertAction: vi.fn(),
    addAlertNote: vi.fn(),
    listInvestigations: vi.fn(),
    createInvestigation: vi.fn(),
    getInvestigation: vi.fn(),
    updateInvestigation: vi.fn(),
    addHypothesis: vi.fn(),
    updateHypothesis: vi.fn(),
    addInvestigationEvidence: vi.fn(),
    addInvestigationFinding: vi.fn(),
    addInvestigationNote: vi.fn(),
    linkAlertToInvestigation: vi.fn(),
    exportInvestigationReport: vi.fn(),
    listCases: vi.fn(),
    createCase: vi.fn(),
    getCase: vi.fn(),
    updateCase: vi.fn(),
    addCaseNote: vi.fn(),
    getDetectionCoverage: vi.fn(),
    listChallenges: vi.fn(),
    getChallenge: vi.fn(),
    submitChallenge: vi.fn(),
    listDatasets: vi.fn(),
    resetTrainingDataset: vi.fn(),
    listAuditLogs: vi.fn(),
    listNotifications: vi.fn(),
    markNotificationRead: vi.fn(),
  },
}))

const mockOverview: SocOverviewResponse = {
  platform: 'NexoraNet SOC Lab',
  environment_status: 'Offline Training Environment',
  metrics: {
    total_alerts: 15,
    open_alerts: 6,
    investigating_alerts: 4,
    closed_alerts: 5,
    p1_alerts: 3,
    p2_alerts: 4,
    active_rules_count: 9,
    open_investigations_count: 2,
    open_cases_count: 1,
  },
  learning_recommendations: [
    {
      title: 'Practice TCP SYN Triage',
      reason: 'Multiple P1 SYN burst anomalies observed.',
      action_link: '/soc/challenges/investigate-tcp-activity',
      category: 'TCP',
    },
  ],
}

const mockStats: SocStatisticsResponse = {
  alerts_by_severity: { CRITICAL: 3, HIGH: 4, MEDIUM: 5, LOW: 3 },
  alerts_by_priority: { P1: 3, P2: 4, P3: 5, P4: 3 },
  alerts_by_status: { NEW: 6, ACKNOWLEDGED: 4, CLOSED: 5 },
  alerts_by_classification: { UNREVIEWED: 6, BENIGN: 2, SUSPICIOUS: 7 },
  alerts_by_category: { TCP: 8, DNS: 4, ARP: 3 },
  top_sources: [{ ip: '192.168.1.100', count: 8 }],
  top_destinations: [{ ip: '10.0.0.1', count: 8 }],
  recent_alert_volume: [{ hour: '12:00', count: 8 }],
}

const mockAlerts: SocAlertItem[] = [
  {
    id: 101,
    title: 'Suspicious TCP SYN Scan Detected',
    severity: 'HIGH',
    priority: 'P1',
    priority_reason: 'High volume probe pattern without ACK handshakes',
    confidence: 'HIGH',
    status: 'NEW',
    classification: 'UNREVIEWED',
    source_ip: '192.168.1.100',
    source_port: 44521,
    destination_ip: '10.0.0.1',
    destination_port: 80,
    protocol: 'TCP',
    packet_count: 24,
    evidence_count: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

const mockAlertDetail: SocAlertDetailResponse = {
  ...mockAlerts[0],
  explanation: 'Rapid burst of TCP SYN packets without completed handshakes indicates port scanning.',
  mitre_attack_id: 'T1046',
  mitre_technique: 'Network Service Discovery',
  investigation_steps: [
    'Inspect TCP flag distribution',
    'Verify if SYN-ACK responses were sent',
    'Correlate with source IP history',
  ],
  evidence: [
    {
      id: 1,
      evidence_type: 'PACKET',
      packet_number: 14,
      summary: 'TCP SYN without ACK on destination port 80',
      created_at: new Date().toISOString(),
    },
  ],
  notes: [
    {
      id: 1,
      author: 'Senior SOC Analyst',
      note: 'Initial alert inspection confirms reconnaissance flags.',
      created_at: new Date().toISOString(),
    },
  ],
  status_history: [
    {
      id: 1,
      new_status: 'NEW',
      actor: 'Detection Engine',
      created_at: new Date().toISOString(),
    },
  ],
  timeline: [
    {
      timestamp: new Date().toISOString(),
      time_display: '12:00:01 UTC',
      event_type: 'PACKET_ACTIVITY',
      title: 'Packet Activity Observed',
      description: 'First TCP SYN observed',
      actor_name: 'Sensor',
    },
  ],
  related_alerts: [],
  network_context: {
    source: {
      ip: '192.168.1.100',
      packet_count: 24,
      byte_count: 1440,
      protocols: ['TCP'],
      ports: [44521, 44522],
    },
    destination: {
      ip: '10.0.0.1',
      packet_count: 24,
      byte_count: 1440,
      protocols: ['TCP'],
      ports: [80, 443],
    },
    conversation_summary: 'Asymmetric SYN traffic pattern between 192.168.1.100 and 10.0.0.1.',
  },
  investigations: [],
}

const mockInvestigation: InvestigationDetailResponse = {
  id: 1,
  investigation_id: 'INV-2026-0001',
  title: 'Investigation: Reconnaissance Burst on DMZ',
  description: 'Probing analysis targeting web ports.',
  status: 'INVESTIGATING',
  priority: 'P1',
  classification: 'SUSPICIOUS',
  started_at: new Date().toISOString(),
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  alerts: [mockAlerts[0]],
  evidence: [
    {
      id: 1,
      investigation_id: 1,
      evidence_type: 'PACKET',
      packet_number: 14,
      description: 'TCP SYN flag confirmed',
      created_at: new Date().toISOString(),
    },
  ],
  hypotheses: [
    {
      id: 1,
      investigation_id: 1,
      hypothesis_text: 'External scanner is sweeping DMZ web ports.',
      status: 'SUPPORTED',
      reasoning: 'Consistent port incrementation observed in packet evidence.',
      supporting_evidence_ids: ['1'],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  findings: [
    {
      id: 1,
      investigation_id: 1,
      title: 'Port Scan Verified',
      description: 'Host scanned ports 80, 443, and 8080.',
      confidence: 'HIGH',
      created_at: new Date().toISOString(),
    },
  ],
  notes: [
    {
      id: 1,
      investigation_id: 1,
      author_name: 'SOC Analyst',
      note: 'Evidence confirms scan behavior.',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  cases: [],
}

const mockChallenge: SocChallengeDetailResponse = {
  id: 1,
  slug: 'investigate-tcp-activity',
  title: 'Investigate TCP Port Scan Activity',
  difficulty: 'Beginner',
  category: 'TCP',
  objective: 'Inspect TCP flags and determine if traffic is a port sweep.',
  scenario_description: 'Multiple internal servers reported SYN packets on unusual ports.',
  expected_observations: ['SYN packets without ACK', 'Incremental target port sequence'],
  sample_alerts: [mockAlerts[0]],
}

const mockEvaluation: SocChallengeEvaluation = {
  alert_triaged_score: 20,
  classification_accuracy_score: 20,
  hypothesis_validity_score: 20,
  evidence_linking_score: 15,
  conclusion_depth_score: 18,
  total_score: 93,
  percentage: 93,
  passed: true,
  feedback_summary: 'Excellent forensic methodology and evidence correlation.',
  specific_tips: ['Include specific byte counts to further strengthen evidence.'],
}

describe('Step 12 SOC Dashboard, Alert Queue, Triage & Investigations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(socApi.getOverview).mockResolvedValue(mockOverview)
    vi.mocked(socApi.getStatistics).mockResolvedValue(mockStats)
    vi.mocked(socApi.getActivityStream).mockResolvedValue([])
    vi.mocked(socApi.listAlerts).mockResolvedValue(mockAlerts)
    vi.mocked(socApi.listDatasets).mockResolvedValue([
      {
        dataset_id: 'tcp_investigation',
        name: 'TCP Investigation Lab',
        category: 'TCP',
        description: 'SYN patterns',
        target_capture_name: 'test.pcap',
      },
    ])
    vi.mocked(socApi.getAlertDetail).mockResolvedValue(mockAlertDetail)
    vi.mocked(socApi.getInvestigation).mockResolvedValue(mockInvestigation)
    vi.mocked(socApi.getChallenge).mockResolvedValue(mockChallenge)
    vi.mocked(socApi.submitChallenge).mockResolvedValue(mockEvaluation)
  })

  it('renders SOC Overview dashboard with key metrics and banner', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc']}>
          <Routes>
            <Route path="/soc" element={<SocDashboardPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    // Check Offline Training Banner
    expect(screen.getByText(/NexoraNet Defensive SOC — Offline Training Environment/i)).toBeInTheDocument()
    expect(screen.getByText(/ALERT ≠ INCIDENT/i)).toBeInTheDocument()

    // Check key metrics
    expect(screen.getByText('Total Alerts')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument()
    expect(screen.getByText('P1 Critical Alerts')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()

    // Check alert preview table
    expect(screen.getByText('Suspicious TCP SYN Scan Detected')).toBeInTheDocument()
    expect(screen.getByText('Practice TCP SYN Triage')).toBeInTheDocument()
  })

  it('renders Alert Queue and supports filtering and selection', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/alerts']}>
          <Routes>
            <Route path="/soc/alerts" element={<AlertQueuePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Alert Queue & Triage Workbench')).toBeInTheDocument()
    expect(screen.getByText('Suspicious TCP SYN Scan Detected')).toBeInTheDocument()
    expect(screen.getByText('P1 CRITICAL')).toBeInTheDocument()

    // Select alert checkbox
    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes.length).toBeGreaterThan(0)
    await act(async () => {
      fireEvent.click(checkboxes[1])
    })

    expect(screen.getByText(/1 alert selected/i)).toBeInTheDocument()
  })

  it('renders Alert Detail with network context, packet evidence, and timeline', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/alerts/101']}>
          <Routes>
            <Route path="/soc/alerts/:alertId" element={<AlertDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Alert #101: Suspicious TCP SYN Scan Detected')).toBeInTheDocument()
    expect(screen.getByText(/MITRE ATT&CK: /i)).toBeInTheDocument()
    expect(screen.getByText('T1046')).toBeInTheDocument()
    expect(screen.getByText('Endpoint Context & Telemetry')).toBeInTheDocument()
    expect(screen.getByText('192.168.1.100')).toBeInTheDocument()
    expect(screen.getByText('10.0.0.1')).toBeInTheDocument()
    expect(screen.getByText(/Supporting Packet Evidence/i)).toBeInTheDocument()
    expect(screen.getByText(/Chronological Timeline/i)).toBeInTheDocument()
  })

  it('renders Alert Triage 12-step guided checklist and allows classification', async () => {
    vi.mocked(socApi.updateClassification).mockResolvedValue(mockAlerts[0])

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/alerts/101/triage']}>
          <Routes>
            <Route path="/soc/alerts/:alertId/triage" element={<AlertTriagePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Guided Alert Triage: Alert #101')).toBeInTheDocument()
    expect(screen.getByText(/12-Step Triage Checklist/i)).toBeInTheDocument()
    expect(screen.getByText(/Step 1: Check Alert Metadata/i)).toBeInTheDocument()
    expect(screen.getByText(/Step 12: Record Justification & Audit Trail/i)).toBeInTheDocument()

    // Fill in justification
    const textarea = screen.getByPlaceholderText(/Document your evidence/i)
    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'Confirmed SYN scan targeting web ports.' } })
    })

    // Submit triage decision
    const submitBtn = screen.getByText('Commit Triage Classification')
    await act(async () => {
      fireEvent.click(submitBtn)
    })

    expect(socApi.updateClassification).toHaveBeenCalledWith(
      101,
      'SUSPICIOUS',
      'Confirmed SYN scan targeting web ports.',
      'NEW'
    )
  })

  it('renders Investigation Workspace with hypotheses, findings, and JSON report export', async () => {
    vi.mocked(socApi.exportInvestigationReport).mockResolvedValue({
      platform: 'NexoraNet SOC Forensic Lab',
      investigation_id: 'INV-2026-0001',
      title: 'Investigation: Reconnaissance Burst on DMZ',
      findings: mockInvestigation.findings,
    })

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/investigations/1']}>
          <Routes>
            <Route path="/soc/investigations/:investigationId" element={<InvestigationWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/INV-2026-0001: Investigation: Reconnaissance Burst on DMZ/i)).toBeInTheDocument()
    expect(screen.getByText('Overview & Conclusion')).toBeInTheDocument()
    expect(screen.getByText(/Linked Alerts \(1\)/i)).toBeInTheDocument()
    expect(screen.getByText(/Hypotheses \(1\)/i)).toBeInTheDocument()
    expect(screen.getByText(/Findings \(1\)/i)).toBeInTheDocument()

    // Switch to Hypotheses tab
    const hypTab = screen.getByText(/Hypotheses \(1\)/i)
    await act(async () => {
      fireEvent.click(hypTab)
    })

    expect(screen.getByText('External scanner is sweeping DMZ web ports.')).toBeInTheDocument()
    expect(screen.getByText('✓ Supported')).toBeInTheDocument()

    // Export report
    const exportBtn = screen.getByText(/Export JSON Report 📄/i)
    await act(async () => {
      fireEvent.click(exportBtn)
    })

    expect(socApi.exportInvestigationReport).toHaveBeenCalledWith(1)
  })

  it('renders SOC Challenge Detail, submits findings, and displays scorecard', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/challenges/investigate-tcp-activity']}>
          <Routes>
            <Route path="/soc/challenges/:challengeSlug" element={<SocChallengeDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Investigate TCP Port Scan Activity')).toBeInTheDocument()
    expect(screen.getByText(/Scenario Briefing & Objective/i)).toBeInTheDocument()
    expect(screen.getByText(/Key Telemetry Indicators to Investigate/i)).toBeInTheDocument()

    // Fill in submission form
    const hypInput = screen.getByPlaceholderText(/Endpoint 192.168.1.100 is executing/i)
    const conclusionInput = screen.getByPlaceholderText(/Summarize your conclusive proof/i)

    await act(async () => {
      fireEvent.change(hypInput, { target: { value: 'Port scan probing web ports.' } })
      fireEvent.change(conclusionInput, { target: { value: 'Recommend firewall rate limiting.' } })
    })

    const gradeBtn = screen.getByText(/Grade My Investigation 🎓/i)
    await act(async () => {
      fireEvent.click(gradeBtn)
    })

    expect(socApi.submitChallenge).toHaveBeenCalledWith('investigate-tcp-activity', {
      selected_classification: 'SUSPICIOUS',
      hypothesis_text: 'Port scan probing web ports.',
      evidence_packet_numbers: [],
      conclusion: 'Recommend firewall rate limiting.',
    })

    // Verify Scorecard
    expect(screen.getByText(/Investigation Rubric Scorecard/i)).toBeInTheDocument()
    expect(screen.getByText(/93% — PASSED/i)).toBeInTheDocument()
    expect(screen.getByText('Alert Triage & Inspection (20%)')).toBeInTheDocument()
  })
})
