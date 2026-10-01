import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { ThreatIntelDashboardPage } from '../pages/ThreatIntel/ThreatIntelDashboardPage'
import { IndicatorListPage } from '../pages/ThreatIntel/IndicatorListPage'
import { IndicatorDetailPage } from '../pages/ThreatIntel/IndicatorDetailPage'
import { IndicatorGraphPage } from '../pages/ThreatIntel/IndicatorGraphPage'
import { ThreatIntelSearchPage } from '../pages/ThreatIntel/ThreatIntelSearchPage'
import { WatchlistPage } from '../pages/ThreatIntel/WatchlistPage'
import { ThreatIntelChallengesPage } from '../pages/ThreatIntel/ThreatIntelChallengesPage'
import { ThreatIntelChallengeDetailPage } from '../pages/ThreatIntel/ThreatIntelChallengeDetailPage'
import { threatIntelApi } from '../services/threatIntelApi'
import type {
  ChallengeAttempt,
  IndicatorBrief,
  IndicatorDetail,
  ThreatIntelChallengeBrief,
  ThreatIntelChallengeDetail,
  ThreatIntelGraph,
  ThreatIntelOverview,
  ThreatIntelSource,
  WatchlistItem,
} from '../types/threat_intel'

vi.mock('../services/threatIntelApi', () => ({
  threatIntelApi: {
    getOverview: vi.fn(),
    listIndicators: vi.fn(),
    getIndicator: vi.fn(),
    createIndicator: vi.fn(),
    enrichIndicator: vi.fn(),
    updateClassification: vi.fn(),
    getEvidence: vi.fn(),
    getCorrelatedAlerts: vi.fn(),
    getCorrelatedInvestigations: vi.fn(),
    getCorrelatedCases: vi.fn(),
    getRelationships: vi.fn(),
    createRelationship: vi.fn(),
    getTimeline: vi.fn(),
    getNotes: vi.fn(),
    createNote: vi.fn(),
    getGraph: vi.fn(),
    search: vi.fn(),
    getSources: vi.fn(),
    getWatchlist: vi.fn(),
    addToWatchlist: vi.fn(),
    removeFromWatchlist: vi.fn(),
    importIndicators: vi.fn(),
    exportIndicators: vi.fn(),
    listChallenges: vi.fn(),
    getChallenge: vi.fn(),
    submitChallengeAttempt: vi.fn(),
    getChallengeAttempts: vi.fn(),
  },
}))

describe('Step 13: Threat Intelligence & IOC Investigation UI Tests', () => {
  const mockOverview: ThreatIntelOverview = {
    total_indicators: 12,
    by_classification: { MALICIOUS: 5, SUSPICIOUS: 3, BENIGN: 2, UNKNOWN: 2 },
    by_type: { IP_ADDRESS: 4, DOMAIN: 3, URL: 2, FILE_HASH: 2, EMAIL_ADDRESS: 1 },
    by_severity: { CRITICAL: 2, HIGH: 4, MEDIUM: 3, LOW: 1, INFO: 2 },
    active_watchlists: 3,
    total_challenges: 5,
    recent_indicators: [
      {
        id: 1,
        indicator_id: 'IOC-2026-0001',
        indicator_type: 'IP_ADDRESS',
        value: '198.51.100.25',
        normalized_value: '198.51.100.25',
        display_value: '198.51.100.25',
        source_name: 'NexoraNet Synthetic Feed',
        classification: 'MALICIOUS',
        confidence: 'HIGH',
        severity: 'CRITICAL',
        status: 'ACTIVE',
        is_synthetic: true,
        created_at: '2026-09-30T10:00:00Z',
      },
    ],
  }

  const mockSources: ThreatIntelSource[] = [
    {
      id: 1,
      name: 'NexoraNet Synthetic Threat Intelligence',
      source_type: 'SYNTHETIC',
      reliability: 'HIGH',
      enabled: true,
      is_synthetic: true,
      created_at: '2026-09-30T10:00:00Z',
    },
  ]

  const mockIndicators: IndicatorBrief[] = [
    {
      id: 1,
      indicator_id: 'IOC-2026-0001',
      indicator_type: 'IP_ADDRESS',
      value: '198.51.100.25',
      normalized_value: '198.51.100.25',
      display_value: '198.51.100.25',
      source_name: 'NexoraNet Synthetic Feed',
      classification: 'MALICIOUS',
      confidence: 'HIGH',
      severity: 'CRITICAL',
      status: 'ACTIVE',
      is_synthetic: true,
      created_at: '2026-09-30T10:00:00Z',
    },
  ]

  const mockIndicatorDetail: IndicatorDetail = {
    ...mockIndicators[0],
    description: 'Known C2 server communicating with beacon handlers.',
    is_watched: false,
    mitre_attack_id: 'T1071.001',
    mitre_technique: 'Application Layer Protocol',
    observations: [],
    outgoing_relationships: [],
    incoming_relationships: [],
    timeline_events: [
      {
        id: 1,
        indicator_id: 1,
        event_type: 'ENRICHED',
        title: 'Indicator Cataloged',
        actor_name: 'Synthetic Feed',
        event_timestamp: '2026-09-30T10:00:00Z',
        created_at: '2026-09-30T10:00:00Z',
      },
    ],
    notes: [
      {
        id: 1,
        indicator_id: 1,
        author_name: 'Alex Rivera (Cadet)',
        note: 'Observed during initial perimeter triage.',
        created_at: '2026-09-30T10:05:00Z',
        updated_at: '2026-09-30T10:05:00Z',
      },
    ],
  }

  const mockGraph: ThreatIntelGraph = {
    root_indicator_id: 1,
    nodes: [
      { id: 'ioc-1', label: '198.51.100.25', type: 'IP_ADDRESS', severity: 'CRITICAL' },
      { id: 'ioc-2', label: 'c2-controller.training.test', type: 'DOMAIN', severity: 'HIGH' },
    ],
    links: [
      { source: 'ioc-1', target: 'ioc-2', label: 'RESOLVES_TO' },
    ],
  }

  const mockChallenges: ThreatIntelChallengeBrief[] = [
    {
      id: 1,
      slug: 'c2-ip-attribution',
      title: 'Command & Control IP Attribution & Correlation',
      difficulty: 'BEGINNER',
      category: 'C2_INVESTIGATION',
      objective: 'Investigate external IP 198.51.100.25 and formulate defensive SOC response.',
      target_indicator_value: '198.51.100.25',
      expected_classification: 'MALICIOUS',
      created_at: '2026-09-30T10:00:00Z',
    },
  ]

  const mockChallengeDetail: ThreatIntelChallengeDetail = {
    ...mockChallenges[0],
    scenario_description: 'Workstation 10.0.0.45 makes repeated outbound connections to 198.51.100.25.',
  }

  const mockAttempt: ChallengeAttempt = {
    id: 1,
    challenge_id: 1,
    user_id: 2,
    selected_classification: 'MALICIOUS',
    hypothesis_text: 'Reputation shows high confidence C2 node.',
    evidence_notes: 'Packet inspection reveals 60-second beacon intervals.',
    conclusion: 'Block at perimeter and isolate infected host.',
    score: 92.0,
    passed: true,
    feedback: JSON.stringify({
      total_score: 92.0,
      max_score: 100.0,
      passed: true,
      passing_threshold: 70.0,
      breakdown: {
        ioc_classification: { score: 20.0, max: 20.0, feedback: 'Correctly classified as MALICIOUS.' },
        evidence_review: { score: 20.0, max: 20.0, feedback: 'Comprehensive evidence review.' },
        threat_intel_interpretation: { score: 18.0, max: 20.0, feedback: 'Strong analytical hypothesis.' },
        correlation_context: { score: 18.0, max: 20.0, feedback: 'Multi-entity correlation demonstrated.' },
        soc_conclusion: { score: 16.0, max: 20.0, feedback: 'Actionable SOC disposition.' },
      },
      educational_takeaway: 'An IOC is evidence, not absolute proof of compromise.',
    }),
    created_at: '2026-09-30T10:15:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(threatIntelApi.getOverview).mockResolvedValue(mockOverview)
    vi.mocked(threatIntelApi.getSources).mockResolvedValue(mockSources)
    vi.mocked(threatIntelApi.listIndicators).mockResolvedValue(mockIndicators)
    vi.mocked(threatIntelApi.getIndicator).mockResolvedValue(mockIndicatorDetail)
    vi.mocked(threatIntelApi.getCorrelatedAlerts).mockResolvedValue({ indicator_id: 1, total_alerts: 0, alerts: [] })
    vi.mocked(threatIntelApi.getCorrelatedInvestigations).mockResolvedValue({ indicator_id: 1, total_investigations: 0, investigations: [] })
    vi.mocked(threatIntelApi.getCorrelatedCases).mockResolvedValue({ indicator_id: 1, total_cases: 0, cases: [] })
    vi.mocked(threatIntelApi.getGraph).mockResolvedValue(mockGraph)
    vi.mocked(threatIntelApi.search).mockResolvedValue(mockIndicators)
    vi.mocked(threatIntelApi.getWatchlist).mockResolvedValue([
      {
        id: 1,
        indicator_id: 1,
        user_id: 2,
        reason: 'Under active C2 observation.',
        added_by: 'Alex Rivera',
        created_at: '2026-09-30T10:00:00Z',
        indicator: mockIndicators[0],
      },
    ])
    vi.mocked(threatIntelApi.listChallenges).mockResolvedValue(mockChallenges)
    vi.mocked(threatIntelApi.getChallenge).mockResolvedValue(mockChallengeDetail)
    vi.mocked(threatIntelApi.getChallengeAttempts).mockResolvedValue([mockAttempt])
  })

  // 1. Dashboard Page Test
  it('renders Threat Intelligence Dashboard with metrics and educational directive', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <ThreatIntelDashboardPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Threat Intelligence & IOC Investigation/i)).toBeInTheDocument()
    expect(screen.getByText(/Unknown ≠ Benign/i)).toBeInTheDocument()
    expect(screen.getByText('Total Cataloged IOCs')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('Confirmed Malicious')).toBeInTheDocument()
    expect(screen.getAllByText('5')[0]).toBeInTheDocument()
  })

  // 2. Indicators List Page Test
  it('renders Indicator Repository and opens Ingest IOC modal', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <IndicatorListPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Indicators of Compromise \(IOCs\)/i)).toBeInTheDocument()
    expect(screen.getByText('198.51.100.25')).toBeInTheDocument()
    expect(screen.getByText('MALICIOUS')).toBeInTheDocument()

    // Click Ingest New IOC button
    const addBtn = screen.getByText(/\+ Ingest New IOC/i)
    fireEvent.click(addBtn)

    expect(screen.getByText('Ingest Threat Indicator')).toBeInTheDocument()
  })

  // 3. Indicator Detail Page Test
  it('renders Indicator Detail page with MITRE ATT&CK, notes, and classification modal', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/threat-intelligence/indicators/1']}>
          <Routes>
            <Route path="/threat-intelligence/indicators/:indicatorId" element={<IndicatorDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getAllByText('198.51.100.25')[0]).toBeInTheDocument()
    expect(screen.getByText('T1071.001')).toBeInTheDocument()
    expect(screen.getByText('Observed during initial perimeter triage.')).toBeInTheDocument()

    // Click Classify button
    const classifyBtn = screen.getByText(/🏷️ Classify/i)
    fireEvent.click(classifyBtn)
    expect(screen.getByText('Update Analyst Classification')).toBeInTheDocument()
  })

  // 4. Correlation Graph Page Test
  it('renders Indicator Correlation Graph and connected nodes', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/threat-intelligence/graph?root=1']}>
          <Routes>
            <Route path="/threat-intelligence/graph" element={<IndicatorGraphPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Indicator Correlation Graph/i)).toBeInTheDocument()
    expect(screen.getByText(/ROOT IOC/i)).toBeInTheDocument()
    expect(screen.getByText('c2-controller.training.test')).toBeInTheDocument()
  })

  // 5. Threat Intel Search Page Test
  it('performs intelligence search and displays query results', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <ThreatIntelSearchPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Threat Intelligence Search & OSINT/i)).toBeInTheDocument()

    const searchInput = screen.getByPlaceholderText(/Enter IP, domain, hash/i)
    fireEvent.change(searchInput, { target: { value: '198.51.100.25' } })

    const searchBtn = screen.getByRole('button', { name: /Search Intelligence/i })
    await act(async () => {
      fireEvent.click(searchBtn)
    })

    expect(threatIntelApi.search).toHaveBeenCalledWith('198.51.100.25', undefined, undefined)
    expect(screen.getByText(/Search Results \(1 found\)/i)).toBeInTheDocument()
  })

  // 6. Watchlist Page Test
  it('renders Analyst Watchlist with active monitored indicators', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <WatchlistPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Analyst Indicator Watchlist/i)).toBeInTheDocument()
    expect(screen.getByText('Under active C2 observation.')).toBeInTheDocument()
    expect(screen.getByText('198.51.100.25')).toBeInTheDocument()
  })

  // 7. Challenges List Page Test
  it('renders hands-on investigation challenges list', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <ThreatIntelChallengesPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Threat Intelligence Investigation Challenges/i)).toBeInTheDocument()
    expect(screen.getByText('Command & Control IP Attribution & Correlation')).toBeInTheDocument()
    expect(screen.getByText(/Start Investigation →/i)).toBeInTheDocument()
  })

  // 8. Challenge Detail Page & Rubric Submission Test
  it('renders Challenge Detail page and displays rubric breakdown evaluation', async () => {
    vi.mocked(threatIntelApi.submitChallengeAttempt).mockResolvedValue(mockAttempt)

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/threat-intelligence/challenges/c2-ip-attribution']}>
          <Routes>
            <Route path="/threat-intelligence/challenges/:slug" element={<ThreatIntelChallengeDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Command & Control IP Attribution & Correlation')).toBeInTheDocument()
    expect(screen.getByText(/Challenge Passed/i)).toBeInTheDocument()
    expect(screen.getAllByText(/92%/i)[0]).toBeInTheDocument()
    expect(screen.getByText('Correctly classified as MALICIOUS.')).toBeInTheDocument()
  })
})
