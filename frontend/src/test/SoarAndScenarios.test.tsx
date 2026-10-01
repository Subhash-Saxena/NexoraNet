import '@testing-library/jest-dom';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { SoarDashboardPage } from '../pages/Soc/SoarDashboardPage';
import { SoarPlaybooksPage } from '../pages/Soc/SoarPlaybooksPage';
import { SoarPlaybookDetailPage } from '../pages/Soc/SoarPlaybookDetailPage';
import { SoarExecutionsPage } from '../pages/Soc/SoarExecutionsPage';
import { SoarExecutionDetailPage } from '../pages/Soc/SoarExecutionDetailPage';
import { SocScenariosPage } from '../pages/Soc/SocScenariosPage';
import { SocScenarioWorkspacePage } from '../pages/Soc/SocScenarioWorkspacePage';
import { SocScenarioResultPage } from '../pages/Soc/SocScenarioResultPage';

import { soarApi } from '../services/soarApi';
import { socScenarioApi } from '../services/socScenarioApi';
import type {
  AutomationPlaybook,
  PlaybookExecution,
  SoarMetrics,
  DryRunResponse,
} from '../types/soar';
import type {
  SocScenarioSummary,
  SocScenarioDetail,
  ScenarioAttempt,
  ScenarioEvaluationResponse,
  ScenarioMetrics,
} from '../types/socScenario';

vi.mock('../services/soarApi', () => ({
  soarApi: {
    getPlaybooks: vi.fn(),
    getPlaybookDetail: vi.fn(),
    createPlaybook: vi.fn(),
    updatePlaybookStatus: vi.fn(),
    dryRunPlaybook: vi.fn(),
    getExecutions: vi.fn(),
    getExecutionDetail: vi.fn(),
    triggerPlaybook: vi.fn(),
    approveExecution: vi.fn(),
    rejectExecution: vi.fn(),
    cancelExecution: vi.fn(),
    getSoarMetrics: vi.fn(),
    getAuditLogs: vi.fn(),
  },
}));

vi.mock('../services/socScenarioApi', () => ({
  socScenarioApi: {
    getScenarios: vi.fn(),
    getScenarioMetrics: vi.fn(),
    getScenarioDetail: vi.fn(),
    startAttempt: vi.fn(),
    getAttempt: vi.fn(),
    updateStage: vi.fn(),
    unlockHint: vi.fn(),
    submitAttempt: vi.fn(),
  },
}));

const mockMetrics: SoarMetrics = {
  total_playbooks: 8,
  enabled_playbooks: 8,
  total_executions: 12,
  completed_executions: 10,
  waiting_approval: 1,
  failed_executions: 1,
  success_rate_percent: 91.7,
  analyst_hours_saved: 24.5,
  top_playbooks: [
    { name: 'Phishing Triage', playbook_id: 'SOAR-PB-001', executions: 5 },
  ],
};

const mockPlaybooks: AutomationPlaybook[] = [
  {
    id: 1,
    playbook_id: 'SOAR-PB-001',
    name: 'Phishing Email Triage & Safe Quarantine',
    description: 'Enriches headers and extracts suspicious URLs safely.',
    category: 'PHISHING',
    version: '1.0.0',
    status: 'ENABLED',
    trigger_type: 'ALERT_CREATED',
    risk_level: 'MEDIUM',
    requires_approval: false,
    is_system: true,
    simulation_only: true,
    created_by: 'system',
    created_at: '2026-03-30T10:00:00Z',
    updated_at: '2026-03-30T10:00:00Z',
    steps: [
      {
        id: 101,
        playbook_id: 1,
        step_order: 1,
        name: 'Enrich Email IOCs',
        action_type: 'ENRICH_IOC',
        requires_approval: false,
        timeout_seconds: 30,
        enabled: true,
        on_failure: 'CONTINUE',
        retry_count: 0,
        created_at: '2026-03-30T10:00:00Z',
        updated_at: '2026-03-30T10:00:00Z',
      },
      {
        id: 102,
        playbook_id: 1,
        step_order: 2,
        name: 'Quarantine Email Message',
        action_type: 'SIMULATED_QUARANTINE_EMAIL',
        requires_approval: false,
        timeout_seconds: 30,
        enabled: true,
        on_failure: 'STOP',
        retry_count: 0,
        created_at: '2026-03-30T10:00:00Z',
        updated_at: '2026-03-30T10:00:00Z',
      },
    ],
  },
];

const mockExecutions: PlaybookExecution[] = [
  {
    id: 201,
    execution_id: 'EXEC-TEST-001',
    playbook_id: 1,
    playbook_identifier: 'SOAR-PB-001',
    playbook_name: 'Phishing Email Triage & Safe Quarantine',
    trigger_source: 'ALERT_QUEUE',
    source_id: 'ALT-1001',
    status: 'WAITING_APPROVAL',
    current_step_order: 2,
    total_steps: 4,
    requested_by: 'soc_analyst',
    started_at: '2026-03-30T10:15:00Z',
    simulation_only: true,
    step_logs: [
      {
        id: 301,
        execution_id: 201,
        step_order: 1,
        step_name: 'Enrich Email IOCs',
        action_type: 'ENRICH_IOC',
        status: 'COMPLETED',
        started_at: '2026-03-30T10:15:01Z',
        completed_at: '2026-03-30T10:15:02Z',
        retry_attempt: 0,
        simulation_only: true,
      },
      {
        id: 302,
        execution_id: 201,
        step_order: 2,
        step_name: 'Quarantine Email Message',
        action_type: 'SIMULATED_QUARANTINE_EMAIL',
        status: 'WAITING_APPROVAL',
        started_at: '2026-03-30T10:15:03Z',
        retry_attempt: 0,
        simulation_only: true,
      },
    ],
  },
];

const mockScenarioList: SocScenarioSummary[] = [
  {
    id: 1,
    scenario_id: 'SCEN-001',
    title: 'Phishing to Suspicious PowerShell Execution',
    description: 'Investigate malicious macro attachment spawning encoded PowerShell.',
    difficulty: 'BEGINNER',
    category: 'MALWARE_INFECTION',
    estimated_duration_minutes: 20,
    is_active: true,
    created_at: '2026-03-30T10:00:00Z',
    updated_at: '2026-03-30T10:00:00Z',
  },
];

const mockScenarioDetail: SocScenarioDetail = {
  ...mockScenarioList[0],
  learning_objectives: 'Identify spearphishing attachments and investigate child process spawning.',
  initial_signal_json: JSON.stringify({
    alert_name: 'Encoded PowerShell Invocation',
    target_host: 'FIN-WKSTN-04',
    severity: 'HIGH',
    summary: 'Word document spawned powershell.exe with -EncodedCommand flag.',
  }),
  available_evidence_json: JSON.stringify([
    { id: 'ev1', type: 'PROCESS', title: 'powershell.exe -enc', details: 'Spawned by WINWORD.EXE' },
    { id: 'ev2', type: 'NETWORK', title: 'TCP Outbound 185.220.101.5:443', details: 'C2 beacon connection' },
  ]),
  correlation_targets_json: JSON.stringify([
    { label: 'Parent-Child Process Link', prompt: 'Connect WINWORD.EXE to PowerShell' },
  ]),
  hypotheses_options_json: JSON.stringify([
    { id: 'hyp1', title: 'Macro Execution Dropper', details: 'Malicious Office document executed VBA macro.' },
  ]),
  mitre_techniques_json: JSON.stringify([
    { technique_id: 'T1059.001', name: 'PowerShell', tactic: 'Execution' },
  ]),
  response_options_json: JSON.stringify([
    { id: 'resp1', action_title: 'Isolate Host FIN-WKSTN-04', description: 'Simulated endpoint isolation' },
  ]),
  scoring_rubric_json: JSON.stringify({
    signal: 15,
    evidence: 20,
    correlation: 15,
    hypothesis: 20,
    mitre: 15,
    response: 15,
  }),
  hints_json: JSON.stringify(['Look at the parent process of powershell.exe']),
  solution_explanation: 'The user opened a spearphishing invoice containing malicious VBA macros.',
};

const mockAttempt: ScenarioAttempt = {
  id: 501,
  attempt_id: 'ATT-TEST-001',
  scenario_id: 1,
  scenario_identifier: 'SCEN-001',
  scenario_title: 'Phishing to Suspicious PowerShell Execution',
  status: 'IN_PROGRESS',
  current_stage: 'INITIAL_SIGNAL',
  stage_data_json: JSON.stringify({}),
  hints_used: 0,
  score: 0,
  started_at: '2026-03-30T10:00:00Z',
};

const mockEvaluation: ScenarioEvaluationResponse = {
  attempt_id: 'ATT-TEST-001',
  scenario_id: 'SCEN-001',
  scenario_title: 'Phishing to Suspicious PowerShell Execution',
  status: 'COMPLETED',
  score: 92.5,
  max_score: 100,
  passed: true,
  breakdown: {
    signal_analysis: 15,
    evidence_selection: 20,
    correlation: 15,
    hypothesis: 20,
    mitre_mapping: 12.5,
    response_actions: 15,
    hint_penalty: -5.0,
  },
  feedback: [
    'Excellent evidence isolation; noise artifacts were correctly rejected.',
    'Identified the correct root cause hypothesis.',
  ],
  solution_explanation: 'The user opened a spearphishing invoice containing malicious VBA macros.',
  completed_at: '2026-03-30T10:25:00Z',
};

describe('Step 18 SOAR Security Automation Engine Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(soarApi.getSoarMetrics).mockResolvedValue(mockMetrics);
    vi.mocked(soarApi.getPlaybooks).mockResolvedValue(mockPlaybooks);
    vi.mocked(soarApi.getPlaybookDetail).mockResolvedValue(mockPlaybooks[0]);
    vi.mocked(soarApi.getExecutions).mockResolvedValue(mockExecutions);
    vi.mocked(soarApi.getExecutionDetail).mockResolvedValue(mockExecutions[0]);
  });

  it('renders SOAR Dashboard with KPI metrics and approval alert banner', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SoarDashboardPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Security Orchestration, Automation & Response/i)).toBeInTheDocument();
    expect(screen.getByText(/Simulation Mode Only/i)).toBeInTheDocument();
    expect(screen.getByText(/Action Required: 1 Playbook Execution\(s\) Awaiting Analyst Approval/i)).toBeInTheDocument();
    expect(screen.getByText('91.7%')).toBeInTheDocument();
    expect(screen.getByText('24.5h')).toBeInTheDocument();
  });

  it('renders Playbooks Catalog with filters and cards', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SoarPlaybooksPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Automation Playbooks Catalog/i)).toBeInTheDocument();
    expect(screen.getByText('Phishing Email Triage & Safe Quarantine')).toBeInTheDocument();
    expect(screen.getByText('SOAR-PB-001')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
  });

  it('renders Playbook Detail Page and step sequences', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/automation/playbooks/SOAR-PB-001']}>
          <Routes>
            <Route path="/soc/automation/playbooks/:playbookId" element={<SoarPlaybookDetailPage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Phishing Email Triage & Safe Quarantine')).toBeInTheDocument();
    expect(screen.getByText('Enrich Email IOCs')).toBeInTheDocument();
    expect(screen.getByText('Quarantine Email Message')).toBeInTheDocument();
  });

  it('renders Execution Traces and human approval gate action', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/automation/executions/EXEC-TEST-001']}>
          <Routes>
            <Route path="/soc/automation/executions/:executionId" element={<SoarExecutionDetailPage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Human-in-the-Loop Analyst Approval Required/i)).toBeInTheDocument();
    expect(screen.getByText(/Approve & Resume Playbook/i)).toBeInTheDocument();
    expect(screen.getByText(/Reject Action/i)).toBeInTheDocument();
  });
});

describe('Step 18 Advanced SOC Scenario Engine Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(socScenarioApi.getScenarios).mockResolvedValue(mockScenarioList);
    vi.mocked(socScenarioApi.getScenarioMetrics).mockResolvedValue({
      total_scenarios: 28,
      total_attempts: 14,
      completed_attempts: 10,
      avg_score: 86.4,
      user_completed: 4,
      difficulty_distribution: { BEGINNER: 5, INTERMEDIATE: 8, ADVANCED: 10, EXPERT: 5 },
      category_distribution: { MALWARE_INFECTION: 8 },
    });
    vi.mocked(socScenarioApi.getScenarioDetail).mockResolvedValue(mockScenarioDetail);
    vi.mocked(socScenarioApi.getAttempt).mockResolvedValue(mockAttempt);
    vi.mocked(socScenarioApi.submitAttempt).mockResolvedValue(mockEvaluation);
  });

  it('renders SOC Scenarios catalog with difficulty badges and start button', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <SocScenariosPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Advanced SOC Investigation Scenarios/i)).toBeInTheDocument();
    expect(screen.getByText('Phishing to Suspicious PowerShell Execution')).toBeInTheDocument();
    expect(screen.getByText('BEGINNER')).toBeInTheDocument();
    expect(screen.getByText(/Start Investigation/i)).toBeInTheDocument();
  });

  it('renders Scenario Workspace with 9-stage stepper navigation', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/scenarios/workspace/ATT-TEST-001']}>
          <Routes>
            <Route path="/soc/scenarios/workspace/:attemptId" element={<SocScenarioWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Phishing to Suspicious PowerShell Execution')).toBeInTheDocument();
    expect(screen.getByText('Stage 1: Initial Security Signal & Alert Triage')).toBeInTheDocument();
    expect(screen.getByText(/Get Hint \(-5% penalty\)/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Initial Signal/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Evidence Selection/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Correlation/i).length).toBeGreaterThanOrEqual(1);
  });

  it('renders Scenario Evaluation Results with 7-factor rubric breakdown', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/soc/scenarios/results/ATT-TEST-001']}>
          <Routes>
            <Route path="/soc/scenarios/results/:attemptId" element={<SocScenarioResultPage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('93%')).toBeInTheDocument();
    expect(screen.getByText('INVESTIGATION MASTERED')).toBeInTheDocument();
    expect(screen.getByText(/7-Factor Rubric Score Breakdown/i)).toBeInTheDocument();
    expect(screen.getByText(/Solution & Root-Cause Walkthrough/i)).toBeInTheDocument();
    expect(screen.getByText(/Excellent evidence isolation/i)).toBeInTheDocument();
  });
});
