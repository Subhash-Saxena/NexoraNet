import '@testing-library/jest-dom'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { ThreatHuntingDashboardPage } from '../pages/ThreatHuntingDashboardPage'
import { HuntScenariosPage } from '../pages/HuntScenariosPage'
import { HuntWorkspacePage } from '../pages/HuntWorkspacePage'
import { threatHuntingApi } from '../services/threatHuntingApi'
import type {
  HuntDataset,
  HuntOverviewResponse,
  HuntScenario,
  ThreatHunt,
  ThreatHuntDetail,
} from '../types/threat_hunting'

vi.mock('../services/threatHuntingApi', () => ({
  threatHuntingApi: {
    getOverview: vi.fn(),
    listDatasets: vi.fn(),
    getDatasetAnalytics: vi.fn(),
    createDataset: vi.fn(),
    listScenarios: vi.fn(),
    getScenario: vi.fn(),
    launchScenario: vi.fn(),
    listHunts: vi.fn(),
    getHuntDetail: vi.fn(),
    createHunt: vi.fn(),
    launchFromAlert: vi.fn(),
    launchFromIOC: vi.fn(),
    startHunt: vi.fn(),
    pauseHunt: vi.fn(),
    completeHunt: vi.fn(),
    queryTelemetry: vi.fn(),
    getTimeline: vi.fn(),
    getEntityGraph: vi.fn(),
    pivotEntity: vi.fn(),
    listHypotheses: vi.fn(),
    createHypothesis: vi.fn(),
    updateHypothesis: vi.fn(),
    deleteHypothesis: vi.fn(),
    listEvidence: vi.fn(),
    addEvidence: vi.fn(),
    updateEvidence: vi.fn(),
    deleteEvidence: vi.fn(),
    listFindings: vi.fn(),
    createFinding: vi.fn(),
    deleteFinding: vi.fn(),
    listNotes: vi.fn(),
    addNote: vi.fn(),
    deleteNote: vi.fn(),
    submitConclusion: vi.fn(),
    getHuntScore: vi.fn(),
  },
}))

describe('Step 14: Threat Hunting & Investigation Workspace UI Tests', () => {
  const mockOverview: HuntOverviewResponse = {
    total_hunts: 5,
    active_hunts: 2,
    completed_hunts: 3,
    total_datasets: 9,
    total_events: 1250,
    total_scenarios: 8,
    recent_hunts: [
      {
        id: 1,
        hunt_id: 'HUNT-2026-0001',
        title: 'Hunt: DNS Exfiltration via Tunneling',
        description: 'Investigation into TXT records',
        objective: 'Identify exfiltrating host',
        status: 'RUNNING',
        difficulty: 'BEGINNER',
        user_id: 1,
        created_at: '2026-09-30T10:00:00Z',
        updated_at: '2026-09-30T10:00:00Z',
      },
    ],
  }

  const mockDatasets: HuntDataset[] = [
    {
      id: 1,
      dataset_id: 'DS-HUNT-DNS-TUNNEL',
      name: 'DNS Exfiltration & High-Entropy Query Dataset',
      description: '500+ normalized queries',
      dataset_type: 'PCAP',
      source: 'PCAP Replay',
      event_count: 520,
      status: 'READY',
      created_at: '2026-09-30T10:00:00Z',
    },
  ]

  const mockScenarios: HuntScenario[] = [
    {
      slug: 'dns-exfiltration-tunneling',
      title: 'DNS Exfiltration via Tunneling',
      difficulty: 'BEGINNER',
      category: 'Exfiltration',
      estimated_minutes: 25,
      mitre_tactics: ['Exfiltration (TA0010)'],
      mitre_techniques: ['T1071.004 (DNS)'],
      brief: 'Detect sensitive data encoding in high-entropy DNS queries.',
      objective: 'Identify compromised host.',
      background: 'Anomalous outbound UDP/53 traffic flagged.',
      dataset_code: 'DS-HUNT-DNS-TUNNEL',
      initial_pivot_type: 'DOMAIN',
      initial_pivot_value: 'corp-sync.test',
      guided_questions: ['What unusual record types are being requested?'],
      suggested_hypotheses: [{ title: 'DNS Tunneling Active', description: 'Data staged over TXT' }],
      expected_findings: [{ title: 'Base64 in TXT', description: 'Data encoded', finding_type: 'ANOMALY' }],
    },
    {
      slug: 'c2-beaconing-investigation',
      title: 'Suspicious C2 Beaconing Activity',
      difficulty: 'INTERMEDIATE',
      category: 'Command and Control',
      estimated_minutes: 35,
      mitre_tactics: ['Command and Control (TA0011)'],
      mitre_techniques: ['T1071.001 (Web Protocols)'],
      brief: 'Hunt for periodic TLS beaconing.',
      objective: 'Isolate beacon interval.',
      background: 'Domain cdn-telemetry-cache.test reported by threat intel.',
      dataset_code: 'DS-HUNT-C2-BEACON',
      initial_pivot_type: 'DOMAIN',
      initial_pivot_value: 'cdn-telemetry-cache.test',
      guided_questions: ['What is the connection interval?'],
      suggested_hypotheses: [{ title: 'Host 192.168.1.142 active C2', description: 'Beaconing detected' }],
      expected_findings: [{ title: 'Periodic HTTPS Beacon', description: '60s delta', finding_type: 'NETWORK_BEHAVIOR' }],
    },
  ]

  const mockHuntDetail: ThreatHuntDetail = {
    id: 1,
    hunt_id: 'HUNT-2026-0001',
    title: 'Hunt: DNS Exfiltration via Tunneling',
    description: 'Investigation into TXT records',
    objective: 'Identify exfiltrating host',
    status: 'RUNNING',
    difficulty: 'BEGINNER',
    user_id: 1,
    dataset_id: 1,
    initial_pivot_type: 'DOMAIN',
    initial_pivot_value: 'corp-sync.test',
    created_at: '2026-09-30T10:00:00Z',
    updated_at: '2026-09-30T10:00:00Z',
    hypotheses: [
      {
        id: 1,
        hunt_id: 1,
        title: 'Active DNS Tunneling Exfiltration',
        description: 'Base64 encoded subdomains represent data transfer',
        status: 'OPEN',
        confidence: 'HIGH',
        analyst_reasoning: 'Observed 7 base64 queries',
        created_at: '2026-09-30T10:00:00Z',
        updated_at: '2026-09-30T10:00:00Z',
      },
    ],
    evidence: [
      {
        id: 1,
        hunt_id: 1,
        hypothesis_id: 1,
        evidence_type: 'DNS_EVENT',
        source_id: 'EVT-TUNNEL-0001',
        description: 'TXT query resolving to 198.51.100.53',
        relevance: 'SUPPORTING',
        analyst_note: 'Decodes to secret payload chunk',
        created_at: '2026-09-30T10:00:00Z',
      },
    ],
    findings: [
      {
        id: 1,
        hunt_id: 1,
        title: 'DNS Tunneling Egress',
        description: 'Covert channel detected',
        finding_type: 'ANOMALY',
        confidence: 'HIGH',
        evidence_count: 1,
        mitigation_recommendation: 'Block outbound UDP 53',
        created_at: '2026-09-30T10:00:00Z',
      },
    ],
    notes: [
      {
        id: 1,
        hunt_id: 1,
        user_id: 1,
        author_name: 'cadet_student',
        content: 'Domain pivot reveals 7 unique base64 subdomains',
        created_at: '2026-09-30T10:00:00Z',
      },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(threatHuntingApi.getOverview).mockResolvedValue(mockOverview)
    vi.mocked(threatHuntingApi.listDatasets).mockResolvedValue(mockDatasets)
    vi.mocked(threatHuntingApi.listScenarios).mockResolvedValue(mockScenarios)
    vi.mocked(threatHuntingApi.listHunts).mockResolvedValue(mockOverview.recent_hunts)
    vi.mocked(threatHuntingApi.getHuntDetail).mockResolvedValue(mockHuntDetail)
    vi.mocked(threatHuntingApi.queryTelemetry).mockResolvedValue({
      total: 1,
      limit: 50,
      offset: 0,
      events: [
        {
          id: 1,
          event_id: 'EVT-TUNNEL-0001',
          dataset_id: 1,
          event_type: 'DNS_QUERY',
          timestamp: '2026-09-30T10:00:00Z',
          source_ip: '192.168.1.105',
          destination_ip: '198.51.100.53',
          protocol: 'DNS',
          domain: 'corp-sync.test',
          severity: 'HIGH',
          summary: 'High entropy DNS query',
        },
      ],
      took_ms: 1.25,
      conditions_used: [],
      explanation: 'Retrieved 1 of 1 events in 1.25ms',
    })
  })

  // 1. Dashboard Page Tests
  it('renders ThreatHuntingDashboardPage with metrics and datasets', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <ThreatHuntingDashboardPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Threat Hunting & Investigation Workspace/i)).toBeInTheDocument()
    expect(screen.getByText('Active Hunts')).toBeInTheDocument()
    expect(screen.getByText('Completed Hunts')).toBeInTheDocument()
    expect(screen.getByText('Telemetry Datasets')).toBeInTheDocument()
    expect(screen.getByText('DNS Exfiltration & High-Entropy Query Dataset')).toBeInTheDocument()
    expect(screen.getByText('HUNT-2026-0001')).toBeInTheDocument()
  })

  // 2. Scenarios Page Tests
  it('renders HuntScenariosPage with scenario cards and filters', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <HuntScenariosPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Threat Hunting Scenarios Catalog/i)).toBeInTheDocument()
    expect(screen.getByText('DNS Exfiltration via Tunneling')).toBeInTheDocument()
    expect(screen.getByText('Suspicious C2 Beaconing Activity')).toBeInTheDocument()
    expect(screen.getByText('T1071.004 (DNS)')).toBeInTheDocument()
  })

  // 3. Workspace Page Tests
  it('renders HuntWorkspacePage with tabs, telemetry table, and hypotheses', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/threat-hunting/hunts/1']}>
          <Routes>
            <Route path="/threat-hunting/hunts/:huntId" element={<HuntWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('HUNT-2026-0001')).toBeInTheDocument()
    expect(screen.getByText('Hunt: DNS Exfiltration via Tunneling')).toBeInTheDocument()
    expect(screen.getByText('Query & Telemetry')).toBeInTheDocument()
    expect(screen.getByText('Timeline')).toBeInTheDocument()
    expect(screen.getByText('Entity Graph')).toBeInTheDocument()
    expect(screen.getByText('Pivot Correlator')).toBeInTheDocument()
    expect(screen.getByText(/Hypotheses \(1\)/i)).toBeInTheDocument()

    // Telemetry event rendered
    expect(screen.getByText('EVT-TUNNEL-0001')).toBeInTheDocument()
    expect(screen.getByText('corp-sync.test')).toBeInTheDocument()
  })

  it('switches to Hypotheses tab in HuntWorkspacePage', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/threat-hunting/hunts/1']}>
          <Routes>
            <Route path="/threat-hunting/hunts/:huntId" element={<HuntWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    const hypTab = screen.getByText(/Hypotheses \(1\)/i)
    await act(async () => {
      fireEvent.click(hypTab)
    })

    expect(screen.getByText(/Formulate Analytical Hypothesis/i)).toBeInTheDocument()
    expect(screen.getByText('Active DNS Tunneling Exfiltration')).toBeInTheDocument()
  })

  it('switches to Evidence & Findings tab in HuntWorkspacePage', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/threat-hunting/hunts/1']}>
          <Routes>
            <Route path="/threat-hunting/hunts/:huntId" element={<HuntWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    const evTab = screen.getByText(/Evidence & Findings \(1\)/i)
    await act(async () => {
      fireEvent.click(evTab)
    })

    expect(screen.getByText(/Evidence Vault/i)).toBeInTheDocument()
    expect(screen.getByText('TXT query resolving to 198.51.100.53')).toBeInTheDocument()
    expect(screen.getByText('DNS Tunneling Egress')).toBeInTheDocument()
  })
})
