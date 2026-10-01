import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { MockTestCard } from '../components/mock_tests/MockTestCard'
import { MockTestCategoryTabs } from '../components/mock_tests/MockTestCategoryTabs'
import { MockTestFilters } from '../components/mock_tests/MockTestFilters'
import { MockTestsPage } from '../pages/MockTests/MockTestsPage'
import { MockTestDetailPage } from '../pages/MockTests/MockTestDetailPage'
import type {
  CatalogCategoryItem,
  CatalogStatisticsResponse,
  CatalogTopicItem,
  MockTestBrief,
  MockTestDetail,
  AttemptHistoryItem,
} from '../types'

// Mock API service
vi.mock('../services/api', () => ({
  apiService: {
    getMockTests: vi.fn(),
    getMockTest: vi.fn(),
    startAttempt: vi.fn(),
    getAttemptStatus: vi.fn(),
    saveAnswer: vi.fn(),
    clearAnswer: vi.fn(),
    markQuestion: vi.fn(),
    submitAttempt: vi.fn(),
    getAttemptResult: vi.fn(),
    getAttemptReview: vi.fn(),
    getAttemptHistory: vi.fn(),
    createPracticeSession: vi.fn(),
    getTestBlueprints: vi.fn(),
    getCatalogCategories: vi.fn(),
    getCatalogTopics: vi.fn(),
    getCatalogDifficulties: vi.fn(),
    getCatalogTypes: vi.fn(),
    getCatalogFilterOptions: vi.fn(),
    getCatalogStatistics: vi.fn(),
    getMockTestPreview: vi.fn(),
    getMockTestAttemptHistory: vi.fn(),
    getMockTestBlueprint: vi.fn(),
  },
}))

import { apiService } from '../services/api'

const sampleReadyTest: MockTestBrief = {
  id: 101,
  code: 'BEGINNER-NETWORKING-001',
  title: 'Networking Fundamentals',
  slug: 'networking-fundamentals',
  description: 'Foundational 20-question networking examination.',
  difficulty: 'BEGINNER',
  test_type: 'TOPIC',
  duration_minutes: 20,
  total_questions: 20,
  passing_percentage: 70.0,
  status: 'PUBLISHED',
  is_ready: true,
  shortfall: 0,
  topics_covered: ['What is Computer Networking', 'Network Topologies', 'LAN & WAN'],
  latest_attempt_score: null,
  latest_attempt_status: null,
  active_attempt_id: null,
  attempt_count: 0,
}

const sampleDraftTest: MockTestBrief = {
  id: 102,
  code: 'BEGINNER-DNS-001',
  title: 'DNS Fundamentals & Name Resolution',
  slug: 'dns-basics',
  description: 'Domain name resolution quiz.',
  difficulty: 'BEGINNER',
  test_type: 'TOPIC',
  duration_minutes: 20,
  total_questions: 20,
  passing_percentage: 70.0,
  status: 'DRAFT',
  is_ready: false,
  shortfall: 13,
  topics_covered: ['DNS'],
  latest_attempt_score: null,
  latest_attempt_status: null,
  active_attempt_id: null,
  attempt_count: 0,
}

const sampleActiveSittingTest: MockTestBrief = {
  id: 103,
  code: 'FULL-MOCK-001',
  title: 'Full Networking Mock Exam',
  slug: 'full-networking-mock-exam',
  description: 'Full-length 50-question mock exam.',
  difficulty: 'MIXED',
  test_type: 'FULL_MOCK',
  duration_minutes: 60,
  total_questions: 50,
  passing_percentage: 70.0,
  status: 'PUBLISHED',
  is_ready: true,
  shortfall: 0,
  topics_covered: ['Subnetting', 'Routing', 'Switching'],
  latest_attempt_score: 80.0,
  latest_attempt_status: 'IN_PROGRESS',
  active_attempt_id: 999,
  attempt_count: 1,
}

const sampleCategories: CatalogCategoryItem[] = [
  { key: 'all', title: 'All Tests', description: 'Complete library', test_count: 46, icon: 'Layers' },
  { key: 'recommended', title: 'Recommended Practice', description: 'Foundational track', test_count: 12, icon: 'Star' },
  { key: 'beginner', title: 'Beginner', description: 'Beginner fundamentals', test_count: 14, icon: 'ShieldCheck' },
  { key: 'intermediate', title: 'Intermediate', description: 'Routing and subnetting', test_count: 16, icon: 'Sliders' },
  { key: 'advanced', title: 'Advanced', description: 'Deep packet analysis', test_count: 13, icon: 'Cpu' },
  { key: 'full_mocks', title: 'Full Mocks', description: 'Certification exams', test_count: 3, icon: 'Award' },
]

const sampleTopics: CatalogTopicItem[] = [
  { topic_id: 1, topic_title: 'OSI Reference Model', topic_slug: 'seven-osi-layers', test_count: 4 },
  { topic_id: 2, topic_title: 'IPv4 Subnetting', topic_slug: 'subnetting', test_count: 5 },
]

const sampleStats: CatalogStatisticsResponse = {
  total_tests: 46,
  ready_tests: 40,
  draft_tests: 6,
  beginner_tests: 14,
  intermediate_tests: 16,
  advanced_tests: 13,
  full_mock_tests: 3,
  total_questions_represented: 826,
}

describe('Mock Test Catalog & Test Library Components', () => {
  it('renders MockTestCategoryTabs and fires active category click', () => {
    const onCategoryChange = vi.fn()
    render(
      <MockTestCategoryTabs
        categories={sampleCategories}
        activeCategory="all"
        onCategoryChange={onCategoryChange}
      />
    )

    expect(screen.getByText('All Tests')).toBeInTheDocument()
    expect(screen.getByText('Recommended Practice')).toBeInTheDocument()
    expect(screen.getByText('Full Mocks')).toBeInTheDocument()

    // Click category
    fireEvent.click(screen.getByTestId('category-tab-recommended'))
    expect(onCategoryChange).toHaveBeenCalledWith('recommended')
  })

  it('renders MockTestCard with code badge, readiness badge, and state-aware buttons', () => {
    // 1. Ready test
    const { rerender } = render(
      <MemoryRouter>
        <MockTestCard test={sampleReadyTest} />
      </MemoryRouter>
    )

    expect(screen.getByTestId('test-code-BEGINNER-NETWORKING-001')).toBeInTheDocument()
    expect(screen.getByText('Networking Fundamentals')).toBeInTheDocument()
    expect(screen.getByTestId('view-details-btn-networking-fundamentals')).toHaveTextContent('View Test')

    // 2. Draft test with shortfall badge
    rerender(
      <MemoryRouter>
        <MockTestCard test={sampleDraftTest} />
      </MemoryRouter>
    )
    expect(screen.getByTestId('draft-badge-dns-basics')).toHaveTextContent('Draft (Pool Shortfall: 13)')
    expect(screen.getByTestId('view-details-btn-dns-basics')).toHaveTextContent('View Syllabus')

    // 3. Active sitting test with Continue button
    rerender(
      <MemoryRouter>
        <MockTestCard test={sampleActiveSittingTest} />
      </MemoryRouter>
    )
    expect(screen.getByTestId('active-attempt-full-networking-mock-exam')).toBeInTheDocument()
    expect(screen.getByTestId('continue-btn-full-networking-mock-exam')).toHaveTextContent('Continue')
  })

  it('renders MockTestFilters with topic, duration, and status selects', () => {
    const onSearchChange = vi.fn()
    const onDifficultyChange = vi.fn()
    const onTestTypeChange = vi.fn()
    const onTopicChange = vi.fn()
    const onDurationFilterChange = vi.fn()
    const onStatusFilterChange = vi.fn()

    render(
      <MockTestFilters
        searchQuery=""
        onSearchChange={onSearchChange}
        difficulty=""
        onDifficultyChange={onDifficultyChange}
        testType=""
        onTestTypeChange={onTestTypeChange}
        topic=""
        onTopicChange={onTopicChange}
        availableTopics={sampleTopics}
        durationFilter=""
        onDurationFilterChange={onDurationFilterChange}
        statusFilter=""
        onStatusFilterChange={onStatusFilterChange}
      />
    )

    expect(screen.getByTestId('mock-test-search-input')).toBeInTheDocument()
    expect(screen.getByTestId('filter-topic')).toBeInTheDocument()
    expect(screen.getByTestId('filter-duration')).toBeInTheDocument()
    expect(screen.getByTestId('filter-status')).toBeInTheDocument()

    // Select topic
    fireEvent.change(screen.getByTestId('filter-topic'), { target: { value: 'subnetting' } })
    expect(onTopicChange).toHaveBeenCalledWith('subnetting')

    // Select duration
    fireEvent.change(screen.getByTestId('filter-duration'), { target: { value: 'quick' } })
    expect(onDurationFilterChange).toHaveBeenCalledWith('quick')

    // Select status
    fireEvent.change(screen.getByTestId('filter-status'), { target: { value: 'READY' } })
    expect(onStatusFilterChange).toHaveBeenCalledWith('READY')
  })
})

describe('Mock Test Catalog Pages Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('MockTestsPage renders catalog metrics, category tabs, and tests', async () => {
    vi.mocked(apiService.getMockTests).mockResolvedValue([sampleReadyTest, sampleDraftTest])
    vi.mocked(apiService.getCatalogCategories).mockResolvedValue(sampleCategories)
    vi.mocked(apiService.getCatalogTopics).mockResolvedValue(sampleTopics)
    vi.mocked(apiService.getCatalogStatistics).mockResolvedValue(sampleStats)
    vi.mocked(apiService.getTestBlueprints).mockResolvedValue([])

    await act(async () => {
      render(
        <MemoryRouter>
          <MockTestsPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Mock Test Library & Examination Catalog')).toBeInTheDocument()
    expect(screen.getByTestId('catalog-statistics')).toBeInTheDocument()
    expect(screen.getByText('Total Examinations')).toBeInTheDocument()
    expect(screen.getByTestId('mock-test-category-tabs')).toBeInTheDocument()
    expect(screen.getByText('Networking Fundamentals')).toBeInTheDocument()
    expect(screen.getByText('DNS Fundamentals & Name Resolution')).toBeInTheDocument()
  })

  it('MockTestDetailPage displays code, readiness, objectives, and attempt history table', async () => {
    const detailData: MockTestDetail = {
      ...sampleReadyTest,
      instructions: 'Answer 20 questions in 20 minutes.',
      what_you_will_practice: [
        'Mastering core principles of Network Topologies',
        'Distinguish between LAN and WAN scales',
      ],
      blueprint_id: 1,
      topics_breakdown: [
        { topic: 'Network Topologies', question_count: 5 },
        { topic: 'LAN', question_count: 5 },
      ],
      questions: [],
    }

    const sampleHistory: AttemptHistoryItem[] = [
      {
        attempt_id: 501,
        test_id: 101,
        test_title: 'Networking Fundamentals',
        test_slug: 'networking-fundamentals',
        difficulty: 'BEGINNER',
        test_type: 'TOPIC',
        status: 'COMPLETED',
        score: 85.0,
        total_points: 100.0,
        percentage: 85.0,
        passed: true,
        started_at: '2026-09-30T00:00:00Z',
        submitted_at: '2026-09-30T00:15:00Z',
        time_taken_seconds: 900,
      },
    ]

    vi.mocked(apiService.getMockTest).mockResolvedValue(detailData)
    vi.mocked(apiService.getMockTestAttemptHistory).mockResolvedValue(sampleHistory)

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/mock-tests/networking-fundamentals']}>
          <Routes>
            <Route path="/mock-tests/:slug" element={<MockTestDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Networking Fundamentals')).toBeInTheDocument()
    expect(screen.getByText('What You Will Practice')).toBeInTheDocument()
    expect(screen.getByText('Mastering core principles of Network Topologies')).toBeInTheDocument()
    expect(screen.getByTestId('test-attempt-history-section')).toBeInTheDocument()
    expect(screen.getByText('Sitting #1')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('PASSED')).toBeInTheDocument()
  })
})
