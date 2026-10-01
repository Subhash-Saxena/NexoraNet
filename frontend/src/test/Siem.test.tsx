import '@testing-library/jest-dom'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { SiemDashboardPage } from '../pages/SiemDashboardPage'
import { SiemSearchPage } from '../pages/SiemSearchPage'
import { SiemDatasetsPage } from '../pages/SiemDatasetsPage'
import { SiemRulesPage } from '../pages/SiemRulesPage'
import { SiemLabsPage } from '../pages/SiemLabsPage'
import { siemApi } from '../services/siemApi'
import type {
  CorrelationAlert,
  LogCorrelationRule,
  LogSource,
  SecurityEvent,
  SecurityEventDetail,
  SecurityLogDataset,
  SIEMLabScenario,
  SiemAggregations,
  SiemSearchResponse,
} from '../types/siem'

vi.mock('../services/siemApi', () => ({
  siemApi: {
    listSources: vi.fn(),
    listDatasets: vi.fn(),
    getDataset: vi.fn(),
    importLogs: vi.fn(),
    searchEvents: vi.fn(),
    getAggregations: vi.fn(),
    getEvent: vi.fn(),
    getRelatedEvents: vi.fn(),
    listRules: vi.fn(),
    evaluateRule: vi.fn(),
    listAlerts: vi.fn(),
    updateAlertStatus: vi.fn(),
    listSavedSearches: vi.fn(),
    createSavedSearch: vi.fn(),
    deleteSavedSearch: vi.fn(),
    listSearchHistory: vi.fn(),
    listLabs: vi.fn(),
    getLab: vi.fn(),
    validateLab: vi.fn(),
    investigateInSoc: vi.fn(),
    startThreatHunt: vi.fn(),
    extractIoc: vi.fn(),
  },
}))

describe('Step 15: SIEM & Security Log Analysis Engine Frontend Tests', () => {
  const mockDatasets: SecurityLogDataset[] = [
    {
      id: 1,
      stable_id: 'DS-AUTH-BEG-01',
      name: 'Authentication Anomalies & Brute Force',
      description: 'Windows DC and Linux SSH synthetic telemetry.',
      dataset_type: 'AUTHENTICATION_FOCUS',
      difficulty: 'BEGINNER',
      event_count: 145,
      is_synthetic: true,
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      stable_id: 'DS-NET-INT-01',
      name: 'Network Reconnaissance & Port Scanning',
      description: 'Cisco ASA and Linux iptables firewall logs.',
      dataset_type: 'NETWORK_FOCUS',
      difficulty: 'INTERMEDIATE',
      event_count: 220,
      is_synthetic: true,
      created_at: new Date().toISOString(),
    },
  ]

  const mockSources: LogSource[] = [
    {
      id: 1,
      stable_id: 'SRC-WIN-DC-01',
      name: 'Windows Primary Domain Controller',
      description: 'Active Directory Kerberos & NTLM logon events.',
      source_type: 'WINDOWS_SECURITY',
      platform: 'Windows Server 2022',
      vendor: 'Microsoft',
      status: 'ACTIVE',
      is_synthetic: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ]

  const mockAggregations: SiemAggregations = {
    total_events: 365,
    auth_failures: 42,
    firewall_blocks: 88,
    dns_queries: 50,
    high_severity_count: 18,
    by_severity: { INFO: 200, LOW: 100, MEDIUM: 47, HIGH: 15, CRITICAL: 3 },
    by_source_type: { WINDOWS_SECURITY: 145, FIREWALL: 220 },
    by_category: { AUTHENTICATION: 145, FIREWALL: 220 },
    top_source_ips: [
      { name: '198.51.100.45', count: 35 },
      { name: '192.0.2.10', count: 12 },
    ],
    top_dest_ports: [{ name: '22', count: 40 }],
    top_hosts: [{ name: 'DC01.corp.test', count: 145 }],
    top_users: [{ name: 'alice.smith', count: 15 }],
    top_domains: [{ name: 'corp.test', count: 50 }],
    timeline: [
      {
        bucket: '10:00',
        timestamp: '2026-09-30T10:00:00Z',
        total: 120,
        auth_failures: 15,
        firewall_blocks: 30,
        dns_queries: 10,
      },
    ],
  }

  const mockAlerts: CorrelationAlert[] = [
    {
      id: 1,
      alert_id: 'ALR-CORR-0001',
      rule_id: 1,
      dataset_id: 1,
      timestamp: new Date().toISOString(),
      title: 'High-Volume Failed Logins (Brute Force Anomaly)',
      category: 'AUTHENTICATION',
      severity: 'HIGH',
      confidence: 'HIGH',
      status: 'NEW',
      event_count: 8,
      evidence_summary: 'Observed 8 consecutive LOGIN_FAILURE events for user bad_actor',
      created_at: new Date().toISOString(),
    },
  ]

  const mockEvents: SecurityEvent[] = [
    {
      id: 101,
      event_id: 'EVT-SIEM-001',
      timestamp: new Date().toISOString(),
      event_type: 'linux_ssh_login_failure',
      event_category: 'AUTHENTICATION',
      source_type: 'LINUX_SSH',
      username: 'admin',
      source_ip: '198.51.100.45',
      source_port: 51234,
      destination_ip: '192.0.2.15',
      destination_port: 22,
      action: 'LOGIN_FAILURE',
      severity: 'LOW',
      dataset_id: 1,
    },
  ]

  const mockEventDetail: SecurityEventDetail = {
    ...mockEvents[0],
    raw_message: 'Sep 30 14:00:00 server01 sshd[1234]: Failed password for invalid user admin from 198.51.100.45 port 51234 ssh2',
    metadata_json: '{"attempt": 1}',
  }

  const mockRules: LogCorrelationRule[] = [
    {
      id: 1,
      stable_id: 'AUTH-001',
      name: 'High-Volume Failed Logins (Brute Force Detection)',
      description: 'Detects 5+ consecutive authentication failures for a single target account within 5 minutes.',
      category: 'AUTHENTICATION',
      severity: 'HIGH',
      confidence: 'HIGH',
      status: 'ENABLED',
      version: '1.0',
      logic: 'COUNT(action=LOGIN_FAILURE) >= 5 GROUP BY username',
      time_window_seconds: 300,
      explanation: 'Repeated authentication failures suggest password spraying or brute force attacks.',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ]

  const mockLabs: SIEMLabScenario[] = [
    {
      id: 1,
      slug: 'lab-siem-find-failed-logins',
      title: 'Find All Failed Logins',
      description: 'Investigate synthetic authentication logs to uncover external unauthorized logon attempts.',
      difficulty: 'BEGINNER',
      dataset_id: 1,
      objectives: '1. Formulate a search for action = LOGIN_FAILURE.\n2. Identify the recurring external source IP.',
      expected_event_count: 45,
      hints: 'Use field=action, operator==, value=LOGIN_FAILURE.',
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(siemApi.getAggregations).mockResolvedValue(mockAggregations)
    vi.mocked(siemApi.listAlerts).mockResolvedValue(mockAlerts)
    vi.mocked(siemApi.listDatasets).mockResolvedValue(mockDatasets)
    vi.mocked(siemApi.listSources).mockResolvedValue(mockSources)
    vi.mocked(siemApi.listRules).mockResolvedValue(mockRules)
    vi.mocked(siemApi.listLabs).mockResolvedValue(mockLabs)
    vi.mocked(siemApi.listSavedSearches).mockResolvedValue([])
    vi.mocked(siemApi.searchEvents).mockResolvedValue({
      total: 1,
      limit: 50,
      offset: 0,
      execution_time_ms: 2.5,
      human_readable: 'Found 1 event matching criteria',
      events: mockEvents,
    })
    vi.mocked(siemApi.getEvent).mockResolvedValue(mockEventDetail)
  })

  it('renders SiemDashboardPage with metrics, timeline, and correlation alerts', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SiemDashboardPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('SIEM & Security Log Analysis')).toBeInTheDocument()
    expect(screen.getByText('Total Ingested Events')).toBeInTheDocument()
    expect(screen.getByText('365')).toBeInTheDocument()
    expect(screen.getByText('High-Volume Failed Logins (Brute Force Anomaly)')).toBeInTheDocument()
    expect(screen.getByText('ALR-CORR-0001')).toBeInTheDocument()
  })

  it('renders SiemSearchPage with query builder, quick filters, and log table', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SiemSearchPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('SIEM Log Search & Analytics')).toBeInTheDocument()
    expect(screen.getByText('Failed Logins')).toBeInTheDocument()
    expect(screen.getByText('Firewall Blocks / Drops')).toBeInTheDocument()

    // Table rows - await asynchronous search results
    const eventCell = await screen.findByText('EVT-SIEM-001')
    expect(eventCell).toBeInTheDocument()
    expect(screen.getByText('198.51.100.45:51234')).toBeInTheDocument()
  })

  it('opens event drawer and displays raw log details when clicking an event', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SiemSearchPage />
        </MemoryRouter>
      )
    })

    const row = await screen.findByText('EVT-SIEM-001')
    await act(async () => {
      fireEvent.click(row)
    })

    expect(siemApi.getEvent).toHaveBeenCalledWith('EVT-SIEM-001')
    expect(await screen.findByText('Event Details:')).toBeInTheDocument()
    expect(screen.getByText(/Failed password for invalid user admin/i)).toBeInTheDocument()
    expect(screen.getByText('Investigate in SOC')).toBeInTheDocument()
    expect(screen.getByText('Start Threat Hunt')).toBeInTheDocument()
    expect(screen.getByText('Extract IOC')).toBeInTheDocument()
  })

  it('renders SiemDatasetsPage with educational datasets and ingestion options', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SiemDatasetsPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Datasets & Synthetic Ingestion')).toBeInTheDocument()
    expect(screen.getByText('Authentication Anomalies & Brute Force')).toBeInTheDocument()
    expect(screen.getByText('Windows Primary Domain Controller')).toBeInTheDocument()

    // Click ingest logs button
    const ingestBtn = screen.getByRole('button', { name: /Ingest Synthetic Logs/i })
    await act(async () => {
      fireEvent.click(ingestBtn)
    })

    expect(screen.getByText('Ingest Synthetic Security Logs')).toBeInTheDocument()
  })

  it('renders SiemRulesPage with correlation rules and dry-run tester', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SiemRulesPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Correlation Rules & Behavioral Alerts')).toBeInTheDocument()
    expect(screen.getByText('High-Volume Failed Logins (Brute Force Detection)')).toBeInTheDocument()
    expect(screen.getByText('AUTH-001')).toBeInTheDocument()

    // Click Dry-Run Test button
    const testBtn = screen.getByRole('button', { name: /Dry-Run Test/i })
    await act(async () => {
      fireEvent.click(testBtn)
    })

    expect(screen.getByText(/Dry-Run Rule Tester: AUTH-001/i)).toBeInTheDocument()
  })

  it('renders SiemLabsPage with scenario briefing and validation submission', async () => {
    vi.mocked(siemApi.validateLab).mockResolvedValue({
      success: true,
      score: 85,
      feedback: 'Good work! Identified the brute force IP 198.51.100.45 accurately.',
      criteria: { query_executed: true, entity_identified: true, notes_provided: true },
    })

    await act(async () => {
      render(
        <MemoryRouter>
          <SiemLabsPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('SIEM Log Analysis Practice Labs')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Find All Failed Logins' })).toBeInTheDocument()
    expect(screen.getByText('Investigation Objectives')).toBeInTheDocument()

    // Validate submission
    const valBtn = screen.getByRole('button', { name: /Validate My Findings/i })
    await act(async () => {
      fireEvent.click(valBtn)
    })

    expect(siemApi.validateLab).toHaveBeenCalled()
    expect(screen.getByText('Lab Validation Passed!')).toBeInTheDocument()
    expect(screen.getByText('Score: 85/100')).toBeInTheDocument()
  })
})
