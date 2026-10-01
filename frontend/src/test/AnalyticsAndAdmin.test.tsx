import '@testing-library/jest-dom';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { SkillCatalogPage } from '../pages/Analytics/SkillCatalogPage';
import { AssessmentReportPage } from '../pages/Analytics/AssessmentReportPage';
import { PortfolioPage } from '../pages/Analytics/PortfolioPage';
import { PublicPortfolioPage } from '../pages/Analytics/PublicPortfolioPage';
import { AdminDashboardPage } from '../pages/Analytics/AdminDashboardPage';
import { AdminContentPage } from '../pages/Analytics/AdminContentPage';
import { AdminAuditPage } from '../pages/Analytics/AdminAuditPage';

import { analyticsApi } from '../services/analyticsApi';
import type {
  AdminAuditLog,
  AdminContentItem,
  AdminDashboardMetrics,
  AssessmentReport,
  PortfolioDetail,
  PublicPortfolioResponse,
  SkillAssessment,
} from '../types/analytics';

vi.mock('../services/analyticsApi', () => ({
  analyticsApi: {
    getOverview: vi.fn(),
    getLearningProgress: vi.fn(),
    getTrends: vi.fn(),
    getSkills: vi.fn(),
    getSkillDetail: vi.fn(),
    getSkillMatrix: vi.fn(),
    getRecommendations: vi.fn(),
    dismissRecommendation: vi.fn(),
    getAchievements: vi.fn(),
    evaluateAchievements: vi.fn(),
    generateAssessmentReport: vi.fn(),
    getReportHistory: vi.fn(),
    getCertificates: vi.fn(),
    verifyCertificate: vi.fn(),
    getMyPortfolio: vi.fn(),
    updatePortfolio: vi.fn(),
    addPortfolioProject: vi.fn(),
    updatePortfolioProject: vi.fn(),
    deletePortfolioProject: vi.fn(),
    getPublicPortfolio: vi.fn(),
    exportPortfolioJson: vi.fn(),
    getAdminDashboard: vi.fn(),
    getAdminContent: vi.fn(),
    updateContentStatus: vi.fn(),
    getAdminAuditLogs: vi.fn(),
  },
}));

const mockSkills: SkillAssessment[] = [
  {
    skill_id: 1,
    skill_code: 'PACKET_ANALYSIS',
    name: 'Packet Analysis & Dissection',
    category: 'PACKET_ANALYSIS',
    description: 'Deconstruct Wireshark frames and reassemble TCP streams.',
    accuracy: 88.5,
    evidence_count: 14,
    confidence: 'HIGH',
    confidence_score: 85.0,
    confidence_rationale: 'Demonstrated consistent accuracy across 14 practical captures.',
    recent_performance: 90.0,
    historical_performance: 85.0,
    practical_performance: 88.0,
    recommended_next_step: 'Explore advanced TLS handshakes.',
  },
  {
    skill_id: 2,
    skill_code: 'SUBNETTING',
    name: 'IP Subnetting & Addressing',
    category: 'NETWORKING',
    description: 'Calculate CIDR prefixes and assign host address ranges.',
    accuracy: 45.0,
    evidence_count: 2,
    confidence: 'LOW',
    confidence_score: 30.0,
    confidence_rationale: 'Recent results suggest additional practice with subnetting may be useful.',
    recent_performance: 40.0,
    historical_performance: 50.0,
    practical_performance: 45.0,
    recommended_next_step: 'Practice in Foundation Labs.',
  },
];

const mockReport: AssessmentReport = {
  report_code: 'REP-A1B2C3D4',
  student_name: 'Cadet Alex Mercer',
  generated_at: '2026-10-01T10:00:00Z',
  executive_summary: 'Student demonstrates solid foundations in defensive analysis.',
  disclaimer: 'This report documents internal learning progress within NexoraNet synthetic environments.',
  knowledge_evidence: {
    lessons_completed: 12,
    tests_attempted: 4,
    average_test_score: 82.5,
  },
  practical_evidence: {
    labs_completed: 8,
    soc_scenarios_completed: 3,
    challenges_solved: 5,
  },
  skills_summary: [
    {
      code: 'PACKET_ANALYSIS',
      name: 'Packet Analysis & Dissection',
      category: 'PACKET_ANALYSIS',
      accuracy: 88.5,
      confidence: 'HIGH',
    },
  ],
  strengths: ['Network traffic analysis and stream inspection'],
  growth_areas: ['CIDR calculation speed under timed conditions'],
  recommendations: ['Complete 2 additional subnetting challenge scenarios'],
};

const mockPortfolio: PortfolioDetail = {
  id: 1,
  user_id: 2,
  public_slug: 'cadet-alex-mercer',
  visibility: 'PRIVATE',
  display_name: 'Cadet Alex Mercer',
  bio: 'Defensive cyber trainee specializing in packet dissection.',
  learning_focus: 'Packet Analysis and Threat Detection',
  social_links: {},
  show_stats: true,
  show_skills: true,
  show_certifications: true,
  no_index: false,
  projects: [
    {
      id: 101,
      title: 'Automated PCAP Stream Forensics',
      description: 'Python parser detecting beaconing patterns.',
      technologies: ['Python', 'Scapy'],
      skills: ['PACKET_ANALYSIS'],
      learning_outcome: 'Identified periodic C2 callbacks.',
      repository_url: 'https://github.com/example/pcap-tool',
      is_featured: true,
    },
  ],
};

const mockAdminMetrics: AdminDashboardMetrics = {
  total_users: 142,
  active_students_7d: 58,
  catalog_counts: {
    courses: 2,
    modules: 6,
    topics: 18,
    lessons: 45,
    labs: 24,
    questions: 120,
    soc_scenarios: 12,
    challenges: 30,
  },
  publication_status: {
    published: 180,
    draft: 15,
    review: 8,
    archived: 4,
  },
  audit_count: 248,
};

const mockContentItems: AdminContentItem[] = [
  {
    type: 'module',
    id: 1,
    title: 'Network Fundamentals',
    slug: 'network-fundamentals',
    category: 'Networking',
    status: 'PUBLISHED',
  },
  {
    type: 'lab',
    id: 5,
    title: 'Subnetting Practical Sandbox',
    slug: 'subnetting-sandbox',
    category: 'Hands-on',
    status: 'DRAFT',
  },
];

const mockAuditLogs: AdminAuditLog[] = [
  {
    id: 1,
    actor_id: 1,
    actor_role: 'ADMIN',
    action: 'PUBLISH_CONTENT',
    target_type: 'module',
    target_id: '1',
    details: 'Module validated and published to live curriculum.',
    created_at: '2026-10-01T09:30:00Z',
  },
];

describe('Step 20: Analytics, Skill Assessment, Portfolio & Admin UI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders SkillCatalogPage with 28-skill matrix, confidence badges and detail modal', async () => {
    vi.mocked(analyticsApi.getSkills).mockResolvedValue(mockSkills);

    await act(async () => {
      render(
        <MemoryRouter>
          <SkillCatalogPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Cybersecurity Skill Assessment Matrix/i)).toBeInTheDocument();
    expect(screen.getByText(/Educational Assessment Philosophy:/i)).toBeInTheDocument();
    expect(screen.getByText('Packet Analysis & Dissection')).toBeInTheDocument();
    expect(screen.getByText('IP Subnetting & Addressing')).toBeInTheDocument();
    expect(screen.getAllByText(/HIGH/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/LOW/i).length).toBeGreaterThan(0);

    // Click on a skill to open detail modal
    await act(async () => {
      fireEvent.click(screen.getByText('Packet Analysis & Dissection'));
    });

    expect(screen.getByText(/Demonstrated consistent accuracy across 14 practical captures/i)).toBeInTheDocument();
    expect(screen.getByText(/Recent \(50%\)/i)).toBeInTheDocument();
  });

  it('renders AssessmentReportPage with formal verification layout and disclaimers', async () => {
    vi.mocked(analyticsApi.getReportHistory).mockResolvedValue([mockReport]);

    await act(async () => {
      render(
        <MemoryRouter>
          <AssessmentReportPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Formal Assessment & Verification Report/i)).toBeInTheDocument();
    expect(screen.getAllByText(/REP-A1B2C3D4/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Cadet Alex Mercer/i)).toBeInTheDocument();
    expect(screen.getByText(/This report documents internal learning progress/i)).toBeInTheDocument();
    expect(screen.getByText(/Executive Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/Demonstrated Strengths/i)).toBeInTheDocument();
    expect(screen.getByText(/Network traffic analysis and stream inspection/i)).toBeInTheDocument();
    expect(screen.getByText(/Recommended Practice Areas/i)).toBeInTheDocument();
  });

  it('renders PortfolioPage, supports visibility toggles and blocks dangerous URLs', async () => {
    vi.mocked(analyticsApi.getMyPortfolio).mockResolvedValue(mockPortfolio);
    vi.mocked(analyticsApi.updatePortfolio).mockResolvedValue({
      ...mockPortfolio,
      visibility: 'PUBLIC',
    });

    await act(async () => {
      render(
        <MemoryRouter>
          <PortfolioPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Cybersecurity Student Portfolio/i)).toBeInTheDocument();
    expect(screen.getByText('Automated PCAP Stream Forensics')).toBeInTheDocument();
    expect(screen.getByText(/cadet-alex-mercer/i)).toBeInTheDocument();

    // Toggle visibility to Public
    const publicBtn = screen.getByRole('button', { name: /Public/i });
    await act(async () => {
      fireEvent.click(publicBtn);
    });
    expect(analyticsApi.updatePortfolio).toHaveBeenCalledWith({ visibility: 'PUBLIC' });

    // Open Add Project modal
    const addBtn = screen.getByRole('button', { name: /Add Project/i });
    await act(async () => {
      fireEvent.click(addBtn);
    });

    expect(screen.getByText(/Add Showcase Project/i)).toBeInTheDocument();

    // Fill in dangerous javascript: URL
    const titleInput = screen.getByPlaceholderText(/e\.g\. PCAP Beaconing Detection Engine/i);
    const descInput = screen.getByPlaceholderText(/Explain what the project simulates/i);
    const repoInput = screen.getByPlaceholderText(/https:\/\/github\.com\/example\/repo/i);

    await act(async () => {
      fireEvent.change(titleInput, { target: { value: 'XSS Probe' } });
      fireEvent.change(descInput, { target: { value: 'Testing validation' } });
      fireEvent.change(repoInput, { target: { value: 'javascript:alert(1)' } });
    });

    const submitBtn = screen.getByRole('button', { name: /Save Project/i });
    await act(async () => {
      fireEvent.click(submitBtn);
    });

    // Client-side URL validation error displayed
    expect(screen.getByText(/Repository URL must be a valid http:\/\/ or https:\/\/ link/i)).toBeInTheDocument();
    expect(analyticsApi.addPortfolioProject).not.toHaveBeenCalled();
  });

  it('renders PublicPortfolioPage safely with zero private student data leakage', async () => {
    const mockPublicView: PublicPortfolioResponse = {
      display_name: 'Cadet Alex Mercer',
      bio: 'Public profile overview without private contact info.',
      learning_focus: 'Threat Detection',
      social_links: {},
      projects: mockPortfolio.projects,
      stats: {
        labs_completed: 8,
        challenges_solved: 5,
        scenarios_completed: 3,
        lessons_completed: 12,
      },
    };

    vi.mocked(analyticsApi.getPublicPortfolio).mockResolvedValue(mockPublicView);

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/portfolio/public/cadet-alex-mercer']}>
          <Routes>
            <Route path="/portfolio/public/:publicSlug" element={<PublicPortfolioPage />} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/NEXORANET VERIFIED CADET PORTFOLIO/i)).toBeInTheDocument();
    expect(screen.getByText('Cadet Alex Mercer')).toBeInTheDocument();
    expect(screen.getByText('Automated PCAP Stream Forensics')).toBeInTheDocument();
    expect(screen.getByText(/Labs Completed/i)).toBeInTheDocument();
    // Verify no sensitive internal strings or email
    expect(screen.queryByText(/password_hash/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/@example\.com/i)).not.toBeInTheDocument();
  });

  it('renders AdminDashboardPage with metrics and shows 403 authorization alert for students', async () => {
    // Default student role produces error
    vi.mocked(analyticsApi.getAdminDashboard).mockRejectedValue(
      new Error('Administrator authorization required')
    );

    await act(async () => {
      render(
        <MemoryRouter>
          <AdminDashboardPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Platform Administration & Content Operations/i)).toBeInTheDocument();
    expect(screen.getByText(/403 Forbidden: Administrator Authorization Required/i)).toBeInTheDocument();

    // Now switch to Admin context and mock success
    vi.mocked(analyticsApi.getAdminDashboard).mockResolvedValue(mockAdminMetrics);

    const adminBtn = screen.getByRole('button', { name: /Admin \(Full Access\)/i });
    await act(async () => {
      fireEvent.click(adminBtn);
    });

    expect(analyticsApi.getAdminDashboard).toHaveBeenCalled();
    expect(screen.getByText('142')).toBeInTheDocument();
    expect(screen.getByText(/Registered Cadets/i)).toBeInTheDocument();
    expect(screen.getByText(/Published Assets/i)).toBeInTheDocument();
  });

  it('renders AdminContentPage with items and status update controls', async () => {
    vi.mocked(analyticsApi.getAdminContent).mockResolvedValue(mockContentItems);
    vi.mocked(analyticsApi.updateContentStatus).mockResolvedValue({
      success: true,
      message: "Content item 'Subnetting Practical Sandbox' transitioned to PUBLISHED.",
      content_id: 5,
      new_status: 'PUBLISHED',
    });

    await act(async () => {
      render(
        <MemoryRouter>
          <AdminContentPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Curriculum & Simulation Content Management/i)).toBeInTheDocument();
    expect(screen.getByText('Network Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Subnetting Practical Sandbox')).toBeInTheDocument();

    // Publish the draft lab using its title attribute
    const publishBtn = screen.getByTitle('Validate and publish live');
    await act(async () => {
      fireEvent.click(publishBtn);
    });

    expect(analyticsApi.updateContentStatus).toHaveBeenCalledWith('lab', 5, 'PUBLISHED');
  });

  it('renders AdminAuditPage displaying immutable administrative ledger', async () => {
    vi.mocked(analyticsApi.getAdminAuditLogs).mockResolvedValue(mockAuditLogs);

    await act(async () => {
      render(
        <MemoryRouter>
          <AdminAuditPage />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Administrative Governance & Audit Ledger/i)).toBeInTheDocument();
    expect(screen.getByText('PUBLISH_CONTENT')).toBeInTheDocument();
    expect(screen.getByText(/Module validated and published to live curriculum/i)).toBeInTheDocument();
  });
});
