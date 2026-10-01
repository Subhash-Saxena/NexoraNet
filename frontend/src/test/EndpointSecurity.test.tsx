import '@testing-library/jest-dom'
import { render, screen, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { EndpointDashboardPage } from '../pages/EndpointDashboardPage'
import { EndpointHostsPage } from '../pages/EndpointHostsPage'
import { EndpointHostDetailPage } from '../pages/EndpointHostDetailPage'
import { EndpointEventsPage } from '../pages/EndpointEventsPage'
import { EndpointInvestigationsPage } from '../pages/EndpointInvestigationsPage'
import { EndpointScenariosPage } from '../pages/EndpointScenariosPage'
import { endpointSecurityApi } from '../services/endpointSecurityApi'
import type {
  EndpointHost,
  EndpointHostOverview,
  EndpointHostSummary,
  EndpointInvestigation,
  EndpointScenario,
  ProcessTreeNode,
} from '../types/endpointSecurity'

vi.mock('../services/endpointSecurityApi', () => ({
  endpointSecurityApi: {
    getOverview: vi.fn(),
    listHosts: vi.fn(),
    getHost: vi.fn(),
    getHostOverview: vi.fn(),
    getHostEvents: vi.fn(),
    getProcessTree: vi.fn(),
    getProcessDetails: vi.fn(),
    getHostAuthentication: vi.fn(),
    getHostNetwork: vi.fn(),
    getHostDns: vi.fn(),
    getHostFiles: vi.fn(),
    getHostServices: vi.fn(),
    getHostPersistence: vi.fn(),
    getHostPrivileges: vi.fn(),
    getHostTimeline: vi.fn(),
    listEvents: vi.fn(),
    getEvent: vi.fn(),
    pivotToIntel: vi.fn(),
    startThreatHunt: vi.fn(),
    investigateInSoc: vi.fn(),
    correlateSiem: vi.fn(),
    correlatePcap: vi.fn(),
    listInvestigations: vi.fn(),
    createInvestigation: vi.fn(),
    getInvestigation: vi.fn(),
    updateInvestigation: vi.fn(),
    addHypothesis: vi.fn(),
    updateHypothesis: vi.fn(),
    addEvidence: vi.fn(),
    addFinding: vi.fn(),
    submitConclusion: vi.fn(),
    listScenarios: vi.fn(),
    getScenario: vi.fn(),
    validateScenario: vi.fn(),
  },
}))

describe('Step 16: Endpoint Security & Host Investigation Engine Frontend Tests', () => {
  const mockSummary: EndpointHostSummary = {
    total_hosts: 4,
    platforms: { WINDOWS: 2, LINUX: 2 },
    risk_levels: { CRITICAL: 1, HIGH: 1, MEDIUM: 1, LOW: 1 },
    environments: { WORKSTATION: 2, SERVER: 2 },
    total_events: 29,
    active_investigations: 2,
  }

  const mockHosts: EndpointHost[] = [
    {
      id: 1,
      stable_id: 'HOST-WIN-001',
      hostname: 'NN-WIN-001',
      display_name: 'Corporate Executive Laptop',
      platform: 'WINDOWS',
      platform_version: 'Windows 11 Pro 23H2',
      architecture: 'X86_64',
      environment: 'WORKSTATION',
      status: 'ONLINE',
      risk_level: 'LOW',
      ip_address: '192.0.2.15',
      mac_address: '00:1A:2B:3C:4D:01',
      os_build: '22631.2861',
      description: 'Standard baseline executive laptop.',
      last_activity_at: '2026-09-30T10:00:00Z',
      is_synthetic: true,
      created_at: '2026-09-30T00:00:00Z',
      updated_at: '2026-09-30T00:00:00Z',
    },
    {
      id: 2,
      stable_id: 'HOST-WIN-002',
      hostname: 'NN-WIN-002',
      display_name: 'Lead Developer Workstation',
      platform: 'WINDOWS',
      platform_version: 'Windows 10 Enterprise 22H2',
      architecture: 'X86_64',
      environment: 'DEVELOPMENT',
      status: 'SUSPICIOUS',
      risk_level: 'HIGH',
      ip_address: '192.0.2.22',
      mac_address: '00:1A:2B:3C:4D:02',
      os_build: '19045.3803',
      description: 'Developer machine with anomalous PowerShell activity.',
      last_activity_at: '2026-09-30T10:05:00Z',
      is_synthetic: true,
      created_at: '2026-09-30T00:00:00Z',
      updated_at: '2026-09-30T00:00:00Z',
    },
  ]

  const mockHostOverview: EndpointHostOverview = {
    host: mockHosts[1],
    counts: {
      processes: 6,
      network_connections: 3,
      dns_queries: 2,
      file_modifications: 3,
      services: 1,
      persistence_mechanisms: 1,
      authentication_events: 2,
      investigations: 1,
    },
  }

  const mockProcessTree: ProcessTreeNode[] = [
    {
      process_id: 1000,
      process_name: 'explorer.exe',
      command_summary: 'C:\\Windows\\explorer.exe',
      command_line: 'C:\\Windows\\explorer.exe',
      user: 'bob.developer',
      integrity_level: 'MEDIUM',
      spawned_at: '2026-09-30T10:00:00Z',
      terminated_at: null,
      file_hash: null,
      children: [
        {
          process_id: 2040,
          process_name: 'powershell.exe',
          command_summary: 'powershell.exe -enc <base64>',
          command_line: 'powershell.exe -nop -w hidden -enc JABjAGw...',
          user: 'bob.developer',
          integrity_level: 'MEDIUM',
          spawned_at: '2026-09-30T10:02:00Z',
          terminated_at: null,
          file_hash: null,
          children: [
            {
              process_id: 3180,
              process_name: 'update.exe',
              command_summary: 'update.exe --beacon-interval 60',
              command_line: 'C:\\Users\\bob\\AppData\\Local\\Temp\\update.exe --beacon-interval 60',
              user: 'bob.developer',
              integrity_level: 'MEDIUM',
              spawned_at: '2026-09-30T10:03:00Z',
              terminated_at: null,
              file_hash: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
              children: [],
            },
          ],
        },
      ],
    },
  ]

  const mockScenarios: EndpointScenario[] = [
    {
      id: 1,
      scenario_id: 'ESCEN-01',
      slug: 'process-tree-investigation',
      title: 'Suspicious PowerShell Process Spawning',
      difficulty: 'BEGINNER',
      category: 'PROCESS_ANOMALY',
      target_host_stable_id: 'HOST-WIN-002',
      description: 'Investigate parent-child process tree anomaly on developer machine.',
      background: 'Security alerts flag hidden PowerShell execution.',
      objectives: ['Identify parent process', 'Locate dropped binary'],
      hints: ['Check explorer.exe children'],
      estimated_minutes: 20,
      is_published: true,
    },
  ]

  const mockInvestigation: EndpointInvestigation = {
    id: 1,
    stable_id: 'EINV-2026-0001',
    host_id: 2,
    user_id: 1,
    title: 'Suspicious Execution on NN-WIN-002',
    description: 'Analyzing update.exe and powershell ingress.',
    status: 'IN_PROGRESS',
    priority: 'P2',
    scenario_slug: 'process-tree-investigation',
    created_at: '2026-09-30T10:15:00Z',
    updated_at: '2026-09-30T10:20:00Z',
    completed_at: null,
    host: mockHosts[1],
    hypotheses: [
      {
        id: 10,
        investigation_id: 1,
        statement: 'Attacker used PowerShell to stage update.exe.',
        status: 'OPEN',
        confidence: 'HIGH',
        analyst_notes: 'Corroborated by process tree',
        created_at: '2026-09-30T10:16:00Z',
        updated_at: '2026-09-30T10:16:00Z',
      },
    ],
    evidence: [
      {
        id: 20,
        investigation_id: 1,
        hypothesis_id: 10,
        event_id: 'EE-WIN2-002',
        observable_type: 'PROCESS',
        observable_value: 'update.exe',
        description: 'Downloaded binary spawned by PowerShell',
        relevance: 'SUPPORTING',
        collected_at: '2026-09-30T10:17:00Z',
      },
    ],
    findings: [
      {
        id: 30,
        investigation_id: 1,
        title: 'Ingress Tool Transfer',
        description: 'Binary downloaded from RFC 5737 IP',
        severity: 'HIGH',
        mitre_technique: 'T1105',
        created_at: '2026-09-30T10:18:00Z',
      },
    ],
    conclusion: null,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(endpointSecurityApi.getOverview).mockResolvedValue(mockSummary)
    vi.mocked(endpointSecurityApi.listHosts).mockResolvedValue({ items: mockHosts, total: 2 })
    vi.mocked(endpointSecurityApi.getHost).mockResolvedValue(mockHosts[1])
    vi.mocked(endpointSecurityApi.getHostOverview).mockResolvedValue(mockHostOverview)
    vi.mocked(endpointSecurityApi.getProcessTree).mockResolvedValue(mockProcessTree)
    vi.mocked(endpointSecurityApi.listScenarios).mockResolvedValue(mockScenarios)
    vi.mocked(endpointSecurityApi.getScenario).mockResolvedValue(mockScenarios[0])
    vi.mocked(endpointSecurityApi.listInvestigations).mockResolvedValue({ items: [mockInvestigation], total: 1 })
    vi.mocked(endpointSecurityApi.getInvestigation).mockResolvedValue(mockInvestigation)
  })

  it('1. EndpointDashboardPage renders synthetic banner, KPI cards, and hosts', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <EndpointDashboardPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/NexoraNet Endpoint Lab — Synthetic Training Environment/i)).toBeInTheDocument()
    expect(screen.getByText('Monitored Hosts')).toBeInTheDocument()
    expect(screen.getByText('Telemetry Events')).toBeInTheDocument()
    expect(screen.getByText('Active Investigations')).toBeInTheDocument()
    expect(screen.getByText('NN-WIN-001')).toBeInTheDocument()
    expect(screen.getByText('NN-WIN-002')).toBeInTheDocument()
    expect(screen.getByText(/Host Investigation Methodology/i)).toBeInTheDocument()
  })

  it('2. EndpointHostsPage renders filterable host inventory', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <EndpointHostsPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Endpoint Host Inventory')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Search hostname, IP, description/i)).toBeInTheDocument()
    expect(screen.getByText('NN-WIN-001')).toBeInTheDocument()
    expect(screen.getByText('NN-WIN-002')).toBeInTheDocument()
    expect(screen.getByText('192.0.2.15')).toBeInTheDocument()
    expect(screen.getByText('192.0.2.22')).toBeInTheDocument()
  })

  it('3. EndpointHostDetailPage renders workbench with tabs and process tree', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/endpoint-security/hosts/HOST-WIN-002']}>
          <Routes>
            <Route path="/endpoint-security/hosts/:hostId" element={<EndpointHostDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText(/Synthetic Endpoint Workbench: NN-WIN-002/i)).toBeInTheDocument()
    expect(screen.getByText('🌳 Process Tree')).toBeInTheDocument()
    expect(screen.getByText('⏱️ Unified Timeline')).toBeInTheDocument()
    expect(screen.getByText('🔑 Authentication')).toBeInTheDocument()
    expect(screen.getByText('Active Processes')).toBeInTheDocument()
  })

  it('4. EndpointEventsPage renders events list and search controls', async () => {
    vi.mocked(endpointSecurityApi.listEvents).mockResolvedValue({
      items: [
        {
          id: 101,
          stable_id: 'EE-101',
          event_id: 'EE-WIN2-002',
          host_id: 2,
          timestamp: '2026-09-30T10:02:00Z',
          event_category: 'PROCESS',
          event_type: 'PROCESS_CREATE',
          severity: 'HIGH',
          action: 'PROCESS_START',
          result: 'SUCCESS',
          process_name: 'powershell.exe',
          process_id: 2040,
          parent_process_name: 'explorer.exe',
          parent_process_id: 1000,
          command_line: 'powershell.exe -enc <base64>',
          command_summary: 'powershell.exe -enc <base64>',
          file_path: 'C:\\Windows\\System32\\powershell.exe',
          file_hash: null,
          username: 'bob.developer',
          user_domain: 'CORP',
          logon_id: null,
          logon_type: null,
          source_ip: null,
          source_port: null,
          destination_ip: null,
          destination_port: null,
          protocol: null,
          domain: null,
          query_type: null,
          target_object: null,
          new_value: null,
          old_value: null,
          service_name: null,
          persistence_type: null,
          integrity_level: 'MEDIUM',
          raw_event_reference: 'Sysmon Event ID 1',
          is_synthetic: true,
          host_hostname: 'NN-WIN-002',
        },
      ],
      total: 1,
    })

    await act(async () => {
      render(
        <MemoryRouter>
          <EndpointEventsPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Endpoint Events Explorer')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Search command, process, user/i)).toBeInTheDocument()
    expect(screen.getAllByText(/powershell\.exe/i).length).toBeGreaterThan(0)
    expect(screen.getByText('PROCESS_CREATE')).toBeInTheDocument()
  })

  it('5. EndpointInvestigationsPage renders case list and workspace', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/endpoint-security/investigations/1']}>
          <Routes>
            <Route path="/endpoint-security/investigations/:investigationId" element={<EndpointInvestigationsPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('EINV-2026-0001')).toBeInTheDocument()
    expect(screen.getByText(/Suspicious Execution on NN-WIN-002/i)).toBeInTheDocument()
    expect(screen.getByText(/Attacker used PowerShell to stage update.exe/i)).toBeInTheDocument()
    expect(screen.getByText('update.exe')).toBeInTheDocument()
    expect(screen.getByText('Ingress Tool Transfer')).toBeInTheDocument()
    expect(screen.getByText(/Final Conclusion & Rubric Scoring/i)).toBeInTheDocument()
  })

  it('6. EndpointScenariosPage renders scenario catalog and active scenario', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/endpoint-security/scenarios/process-tree-investigation']}>
          <Routes>
            <Route path="/endpoint-security/scenarios/:slug" element={<EndpointScenariosPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('ESCEN-01')).toBeInTheDocument()
    expect(screen.getByText('Suspicious PowerShell Process Spawning')).toBeInTheDocument()
    expect(screen.getByText('HOST-WIN-002 ➔ Open in Workbench')).toBeInTheDocument()
    expect(screen.getByText(/Scenario Background/i)).toBeInTheDocument()
    expect(screen.getByText(/Submit Analytical Findings/i)).toBeInTheDocument()
  })
})
