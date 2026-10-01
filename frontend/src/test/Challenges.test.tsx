import { render, screen, act, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { ChallengesPage } from '../pages/Challenges/ChallengesPage';
import { ChallengeDetailPage } from '../pages/Challenges/ChallengeDetailPage';
import { ChallengeWorkspacePage } from '../pages/Challenges/ChallengeWorkspacePage';
import { ChallengeResultPage } from '../pages/Challenges/ChallengeResultPage';
import { challengeApi } from '../services/challengeApi';
import type {
  ChallengeAttempt,
  ChallengeDetail,
  ChallengeMetrics,
  ChallengeSummary,
  ChallengeTrack,
} from '../types/challenge';

vi.mock('../services/challengeApi', () => ({
  challengeApi: {
    getChallenges: vi.fn(),
    getMetrics: vi.fn(),
    getTracks: vi.fn(),
    getTrackDetail: vi.fn(),
    getRecommendations: vi.fn(),
    getChallengeDetail: vi.fn(),
    startAttempt: vi.fn(),
    submitFlag: vi.fn(),
    unlockHint: vi.fn(),
    revealSolution: vi.fn(),
    saveNotes: vi.fn(),
  },
}));

describe('Step 19: CTF Challenges & Advanced Defensive Training Engine', () => {
  const mockChallenges: ChallengeSummary[] = [
    {
      id: 1,
      challenge_id: 'CHAL-BEG-001',
      title: 'Identify the Private IP Address',
      category: 'NETWORKING',
      difficulty: 'BEGINNER',
      challenge_type: 'IP_ADDRESS',
      points: 50,
      estimated_minutes: 10,
      description: 'Analyze network interface configuration and identify RFC 1918 private IPv4 address.',
      is_multi_stage: false,
      flag_format: 'FLAG{...}',
      status: 'NOT_STARTED',
      created_at: '2026-10-01T00:00:00Z',
    },
    {
      id: 2,
      challenge_id: 'CHAL-INT-001',
      title: 'Detect DNS Fast-Flux Cluster',
      category: 'PACKET_ANALYSIS',
      difficulty: 'INTERMEDIATE',
      challenge_type: 'PACKET_INSPECTION',
      points: 100,
      estimated_minutes: 20,
      description: 'Analyze repeated DNS query responses with fluctuating low-TTL A records.',
      is_multi_stage: false,
      flag_format: 'FLAG{...}',
      status: 'SOLVED',
      created_at: '2026-10-01T00:00:00Z',
    },
  ];

  const mockMetrics: ChallengeMetrics = {
    total_challenges: 40,
    difficulty_distribution: { BEGINNER: 10, INTERMEDIATE: 12, ADVANCED: 12, EXPERT: 6 },
    category_distribution: { NETWORKING: 8, SOC_ANALYSIS: 8 },
    user_solved: 5,
    user_in_progress: 2,
    total_points_earned: 450,
    completion_rate_percent: 12.5,
  };

  const mockTracks: ChallengeTrack[] = [
    {
      id: 1,
      track_id: 'TRACK-NET-DEFENDER',
      title: 'Track 1 — Network Defender',
      description: 'Master fundamental network architectures and traffic anomaly identification.',
      target_role: 'Network Security Analyst',
      difficulty: 'BEGINNER',
      badge_name: 'Certified Network Defender',
      challenges_count: 8,
    },
  ];

  const mockDetail: ChallengeDetail = {
    id: 1,
    challenge_id: 'CHAL-BEG-001',
    title: 'Identify the Private IP Address',
    category: 'NETWORKING',
    difficulty: 'BEGINNER',
    challenge_type: 'IP_ADDRESS',
    points: 50,
    estimated_minutes: 10,
    description: 'Analyze network interface configuration and identify RFC 1918 private IPv4 address.',
    scenario: 'A junior workstation on the internal corporate network received an IP configuration via DHCP. Inspect interface eth0 to find the private address.',
    learning_objectives: JSON.stringify(['Distinguish RFC 1918 private ranges from public IP addresses.']),
    prerequisites: JSON.stringify(['IPv4 addressing basics']),
    environment_description: 'Synthetic Linux workstation interface status output.',
    tasks_json: JSON.stringify(['Inspect eth0 details.', 'Identify the RFC 1918 private IPv4 address.', 'Submit flag format: FLAG{...}.']),
    skills_tested_json: JSON.stringify(['IPv4 addressing', 'Interface inspection']),
    flag_format: 'FLAG{...}',
    is_multi_stage: false,
    simulation_only: true,
    stages: [],
    hints: [
      {
        id: 1,
        hint_number: 1,
        penalty_percent: 10.0,
        penalty_points: 5,
        is_unlocked: true,
        hint_text: 'Remember RFC 1918 ranges: 10.x.x.x, 172.16-31.x.x, 192.168.x.x.',
      },
      {
        id: 2,
        hint_number: 2,
        penalty_percent: 25.0,
        penalty_points: 12,
        is_unlocked: false,
        hint_text: null,
      },
    ],
    evidence: [
      {
        id: 1,
        evidence_type: 'CONFIG',
        title: 'workstation_ip_addr.txt',
        description: 'Synthetic network interface dump',
        order_index: 1,
        content_json: 'eth0: inet 10.10.10.25/24 scope global\neth1: inet 203.0.113.5/24 scope public',
      },
    ],
    solution_explanation: '10.10.10.25 belongs to RFC 1918 Class A private block 10.0.0.0/8.',
    common_mistakes: JSON.stringify(['Submitting the public IP 203.0.113.5 instead of private LAN IP.']),
    is_solved: false,
    revealed_solution: false,
  };

  const mockAttempt: ChallengeAttempt = {
    id: 1,
    attempt_id: 'ATT-CHAL-BEG001',
    challenge_id: 1,
    status: 'IN_PROGRESS',
    current_stage_order: 1,
    stage_progress_json: '{}',
    hints_unlocked: 1,
    hints_penalty: 5.0,
    attempts_count: 1,
    score: 0.0,
    max_score: 50.0,
    solved: false,
    revealed_solution: false,
    started_at: '2026-10-01T00:00:00Z',
    last_activity_at: '2026-10-01T00:00:00Z',
    notes: 'Investigating eth0 address...',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders ChallengesPage catalog, metrics, tracks, and challenge cards', async () => {
    vi.mocked(challengeApi.getChallenges).mockResolvedValue(mockChallenges);
    vi.mocked(challengeApi.getMetrics).mockResolvedValue(mockMetrics);
    vi.mocked(challengeApi.getTracks).mockResolvedValue(mockTracks);
    vi.mocked(challengeApi.getRecommendations).mockResolvedValue([]);

    await act(async () => {
      render(
        <MemoryRouter>
          <ChallengesPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/CTF Challenges & Advanced Defensive Training/i)).toBeInTheDocument();
    expect(screen.getByText('40')).toBeInTheDocument(); // total challenges metric
    expect(screen.getByText('450')).toBeInTheDocument(); // points metric
    expect(screen.getByText(/Track 1 — Network Defender/i)).toBeInTheDocument();
    expect(screen.getByText('Identify the Private IP Address')).toBeInTheDocument();
    expect(screen.getByText('Detect DNS Fast-Flux Cluster')).toBeInTheDocument();
  });

  it('filters challenges by difficulty in ChallengesPage', async () => {
    vi.mocked(challengeApi.getChallenges).mockResolvedValue([mockChallenges[0]]);
    vi.mocked(challengeApi.getMetrics).mockResolvedValue(mockMetrics);
    vi.mocked(challengeApi.getTracks).mockResolvedValue([]);
    vi.mocked(challengeApi.getRecommendations).mockResolvedValue([]);

    const user = userEvent.setup();

    await act(async () => {
      render(
        <MemoryRouter>
          <ChallengesPage />
        </MemoryRouter>
      );
    });

    const beginnerBtn = screen.getByRole('button', { name: /^BEGINNER$/i });
    await act(async () => {
      await user.click(beginnerBtn);
    });

    expect(challengeApi.getChallenges).toHaveBeenCalledWith(
      expect.objectContaining({ difficulty: 'BEGINNER' })
    );
  });

  it('renders ChallengeDetailPage with scenario brief, objectives, and start action', async () => {
    vi.mocked(challengeApi.getChallengeDetail).mockResolvedValue(mockDetail);
    vi.mocked(challengeApi.startAttempt).mockResolvedValue(mockAttempt);

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/challenges/CHAL-BEG-001']}>
          <Routes>
            <Route path="/challenges/:challengeId" element={<ChallengeDetailPage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Identify the Private IP Address')).toBeInTheDocument();
    expect(screen.getByText(/Scenario Investigation Brief/i)).toBeInTheDocument();
    expect(screen.getByText(/junior workstation on the internal corporate network/i)).toBeInTheDocument();
    expect(screen.getByText(/Distinguish RFC 1918 private ranges/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Launch Challenge Workspace/i })).toBeInTheDocument();
  });

  it('renders ChallengeWorkspacePage and allows evidence tab switching and flag submission', async () => {
    vi.mocked(challengeApi.getChallengeDetail).mockResolvedValue(mockDetail);
    vi.mocked(challengeApi.startAttempt).mockResolvedValue(mockAttempt);
    vi.mocked(challengeApi.submitFlag).mockResolvedValue({
      is_correct: true,
      solved: true,
      points_awarded: 45.0,
      current_score: 45.0,
      current_stage: 1,
      feedback: 'Congratulations! Flag verified successfully.',
      attempts_used: 1,
      solution_explanation: 'RFC 1918 10.10.10.25 is correct.',
    });

    const user = userEvent.setup();

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/challenges/CHAL-BEG-001/workspace']}>
          <Routes>
            <Route path="/challenges/:challengeId/workspace" element={<ChallengeWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    // Verify task checklist
    expect(screen.getByText(/Inspect eth0 details/i)).toBeInTheDocument();

    // Verify evidence content
    expect(screen.getByText(/workstation_ip_addr\.txt/i)).toBeInTheDocument();
    expect(screen.getByText(/10\.10\.10\.25\/24/i)).toBeInTheDocument();

    // Type and submit flag
    const flagInput = screen.getByPlaceholderText('FLAG{...}');
    act(() => {
      fireEvent.change(flagInput, { target: { value: 'FLAG{10.10.10.25}' } });
    });

    const submitBtn = screen.getByRole('button', { name: /Submit Flag/i });
    await act(async () => {
      await user.click(submitBtn);
    });

    expect(challengeApi.submitFlag).toHaveBeenCalledWith(
      'CHAL-BEG-001',
      'ATT-CHAL-BEG001',
      'FLAG{10.10.10.25}'
    );
    expect(screen.getByText(/Congratulations! Flag verified successfully/i)).toBeInTheDocument();
  });

  it('renders ChallengeResultPage with comprehensive walkthrough and pitfalls', async () => {
    const solvedDetail: ChallengeDetail = {
      ...mockDetail,
      is_solved: true,
      revealed_solution: false,
    };
    vi.mocked(challengeApi.getChallengeDetail).mockResolvedValue(solvedDetail);
    vi.mocked(challengeApi.getRecommendations).mockResolvedValue([]);

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/challenges/CHAL-BEG-001/results']}>
          <Routes>
            <Route path="/challenges/:challengeId/results" element={<ChallengeResultPage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Comprehensive Technical Walkthrough/i)).toBeInTheDocument();
    expect(screen.getByText(/10\.10\.10\.25 belongs to RFC 1918 Class A/i)).toBeInTheDocument();
    expect(screen.getByText(/Common Pitfalls & Mistakes/i)).toBeInTheDocument();
    expect(screen.getByText(/Submitting the public IP 203\.0\.113\.5/i)).toBeInTheDocument();
  });
});
