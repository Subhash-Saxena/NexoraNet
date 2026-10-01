import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

// Components
import { MockTestCard } from '../components/mock_tests/MockTestCard'
import { MockTestFilters } from '../components/mock_tests/MockTestFilters'
import { MockTestTimer } from '../components/mock_tests/MockTestTimer'
import { MockTestNavigator } from '../components/mock_tests/MockTestNavigator'
import { MockTestQuestion } from '../components/mock_tests/MockTestQuestion'
import { MockTestSubmitModal } from '../components/mock_tests/MockTestSubmitModal'
import { MockTestScoreCard } from '../components/mock_tests/MockTestScoreCard'
import { MockTestPerformance } from '../components/mock_tests/MockTestPerformance'

// Pages
import { MockTestsPage } from '../pages/MockTests/MockTestsPage'
import { MockTestDetailPage } from '../pages/MockTests/MockTestDetailPage'
import { MockTestWorkspacePage } from '../pages/MockTests/MockTestWorkspacePage'
import { MockTestResultPage } from '../pages/MockTests/MockTestResultPage'
import { MockTestReviewPage } from '../pages/MockTests/MockTestReviewPage'
import { MockTestHistoryPage } from '../pages/MockTests/MockTestHistoryPage'

import type {
  MockTestBrief,
  MockTestDetail,
  StudentQuestionPayload,
  TestResultResponse,
  TestReviewResponse,
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
    getCatalogCategories: vi.fn().mockResolvedValue([]),
    getCatalogTopics: vi.fn().mockResolvedValue([]),
    getCatalogDifficulties: vi.fn().mockResolvedValue([]),
    getCatalogTypes: vi.fn().mockResolvedValue([]),
    getCatalogFilterOptions: vi.fn().mockResolvedValue({
      categories: [],
      topics: [],
      difficulties: [],
      types: [],
      duration_ranges: [],
    }),
    getCatalogStatistics: vi.fn().mockResolvedValue(null),
    getMockTestPreview: vi.fn().mockResolvedValue(null),
    getMockTestAttemptHistory: vi.fn().mockResolvedValue([]),
    getMockTestBlueprint: vi.fn().mockResolvedValue(null),
  },
}))

import { apiService } from '../services/api'

const sampleTestBrief: MockTestBrief = {
  id: 1,
  title: 'Beginner Networking Fundamentals Test',
  slug: 'beginner-networking-fundamentals-test',
  description: 'Comprehensive 30-question diagnostic exam.',
  difficulty: 'BEGINNER',
  test_type: 'COMPREHENSIVE',
  duration_minutes: 30,
  total_questions: 30,
  passing_percentage: 70.0,
  status: 'PUBLISHED',
  topics_covered: ['Seven OSI Layers', 'IPv4 Addressing', 'Subnetting'],
  latest_attempt_score: 85.0,
  latest_attempt_status: 'COMPLETED',
}

const sampleQuestions: StudentQuestionPayload[] = [
  {
    id: 101,
    question_number: 1,
    question_text: 'Which OSI layer is responsible for port addressing?',
    question_type: 'SINGLE_CHOICE',
    points: 1,
    topic_title: 'Seven OSI Layers',
    difficulty: 'BEGINNER',
    options: [
      { id: 1, option_text: 'Layer 3 Network', order_index: 1 },
      { id: 2, option_text: 'Layer 4 Transport', order_index: 2 },
    ],
  },
  {
    id: 102,
    question_number: 2,
    question_text: 'Select all RFC 1918 private IPv4 subnets:',
    question_type: 'MULTIPLE_CHOICE',
    points: 2,
    topic_title: 'IPv4 Addressing',
    difficulty: 'BEGINNER',
    options: [
      { id: 3, option_text: '10.0.0.0/8', order_index: 1 },
      { id: 4, option_text: '172.16.0.0/12', order_index: 2 },
      { id: 5, option_text: '8.8.8.8/32', order_index: 3 },
    ],
  },
]

const sampleResult: TestResultResponse = {
  attempt_id: 42,
  test_id: 1,
  test_title: 'Beginner Networking Fundamentals Test',
  test_slug: 'beginner-networking-fundamentals-test',
  status: 'SUBMITTED',
  score: 25,
  percentage: 83.3,
  total_points: 30,
  earned_points: 25,
  passing_percentage: 70.0,
  passed: true,
  total_questions: 30,
  attempted_questions: 30,
  unanswered_questions: 0,
  correct_answers: 25,
  incorrect_answers: 5,
  time_taken_seconds: 1200,
  started_at: '2026-09-29T20:00:00Z',
  submitted_at: '2026-09-29T20:20:00Z',
  topic_breakdown: [
    {
      topic_id: 1,
      topic_title: 'Seven OSI Layers',
      total_questions: 10,
      correct_questions: 9,
      points_earned: 9,
      total_points: 10,
      percentage: 90.0,
    },
    {
      topic_id: 2,
      topic_title: 'Subnetting',
      total_questions: 10,
      correct_questions: 7,
      points_earned: 7,
      total_points: 10,
      percentage: 70.0,
    },
  ],
  difficulty_breakdown: [
    {
      difficulty: 'BEGINNER',
      total_questions: 20,
      correct_questions: 18,
      percentage: 90.0,
    },
    {
      difficulty: 'INTERMEDIATE',
      total_questions: 10,
      correct_questions: 7,
      percentage: 70.0,
    },
  ],
}

describe('MockTestEngine Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders MockTestCard with metadata, badges, and score indicator', () => {
    render(
      <MemoryRouter>
        <MockTestCard test={sampleTestBrief} />
      </MemoryRouter>
    )

    expect(screen.getByText('Beginner Networking Fundamentals Test')).toBeInTheDocument()
    expect(screen.getByText('BEGINNER')).toBeInTheDocument()
    expect(screen.getByText('COMPREHENSIVE')).toBeInTheDocument()
    expect(screen.getByText('30 mins')).toBeInTheDocument()
    expect(screen.getByText('30 questions')).toBeInTheDocument()
    expect(screen.getByText(/85% \(PASSED\)/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /view test/i })).toHaveAttribute(
      'href',
      '/mock-tests/beginner-networking-fundamentals-test'
    )
  })

  it('renders MockTestFilters and fires change handlers', () => {
    const onSearchChange = vi.fn()
    const onDifficultyChange = vi.fn()
    const onTestTypeChange = vi.fn()

    render(
      <MockTestFilters
        searchQuery=""
        onSearchChange={onSearchChange}
        difficulty=""
        onDifficultyChange={onDifficultyChange}
        testType=""
        onTestTypeChange={onTestTypeChange}
      />
    )

    const searchInput = screen.getByTestId('mock-test-search-input')
    fireEvent.change(searchInput, { target: { value: 'osi' } })
    expect(onSearchChange).toHaveBeenCalledWith('osi')

    const beginnerPill = screen.getByTestId('filter-diff-BEGINNER')
    fireEvent.click(beginnerPill)
    expect(onDifficultyChange).toHaveBeenCalledWith('BEGINNER')

    const select = screen.getByTestId('filter-test-type')
    fireEvent.change(select, { target: { value: 'COMPREHENSIVE' } })
    expect(onTestTypeChange).toHaveBeenCalledWith('COMPREHENSIVE')
  })

  it('renders MockTestTimer with formatted MM:SS and calls onExpire at 0', () => {
    const onExpire = vi.fn()
    render(<MockTestTimer remainingSeconds={125} onExpire={onExpire} />)

    expect(screen.getByText('02:05')).toBeInTheDocument()
    const timerEl = screen.getByTestId('mock-test-countdown-timer')
    expect(timerEl).toHaveClass('mt-timer-warning')

    render(<MockTestTimer remainingSeconds={0} onExpire={onExpire} />)
    expect(onExpire).toHaveBeenCalled()
  })

  it('renders MockTestNavigator with question grid and fires selection and submit', () => {
    const onSelect = vi.fn()
    const onSubmit = vi.fn()

    render(
      <MockTestNavigator
        questions={sampleQuestions}
        currentIndex={0}
        onSelectQuestion={onSelect}
        answers={{ 101: [2] }}
        markedQuestions={new Set([102])}
        onSubmitClick={onSubmit}
      />
    )

    expect(screen.getByText('Question Navigator')).toBeInTheDocument()
    expect(screen.getByTestId('nav-btn-1')).toHaveClass('current')
    expect(screen.getByTestId('nav-btn-2')).toHaveClass('marked')

    fireEvent.click(screen.getByTestId('nav-btn-2'))
    expect(onSelect).toHaveBeenCalledWith(1)

    fireEvent.click(screen.getByTestId('navigator-submit-btn'))
    expect(onSubmit).toHaveBeenCalled()
  })

  it('renders MockTestQuestion with single and multiple choice options and actions', () => {
    const onToggle = vi.fn()
    const onMark = vi.fn()
    const onClear = vi.fn()
    const onPrev = vi.fn()
    const onNext = vi.fn()

    const { rerender } = render(
      <MockTestQuestion
        question={sampleQuestions[0]}
        selectedOptionIds={[2]}
        onOptionToggle={onToggle}
        isMarkedForReview={false}
        onToggleMarkForReview={onMark}
        onClearAnswer={onClear}
        onPrevQuestion={onPrev}
        onNextQuestion={onNext}
        hasPrev={false}
        hasNext={true}
      />
    )

    expect(screen.getByText('Which OSI layer is responsible for port addressing?')).toBeInTheDocument()
    expect(screen.getByTestId('option-input-2')).toBeChecked()

    fireEvent.click(screen.getByTestId('option-input-1'))
    expect(onToggle).toHaveBeenCalledWith(1)

    fireEvent.click(screen.getByTestId('mark-review-toggle-btn'))
    expect(onMark).toHaveBeenCalled()

    fireEvent.click(screen.getByTestId('clear-answer-btn'))
    expect(onClear).toHaveBeenCalled()

    // Test multiple choice note
    rerender(
      <MockTestQuestion
        question={sampleQuestions[1]}
        selectedOptionIds={[3, 4]}
        onOptionToggle={onToggle}
        isMarkedForReview={true}
        onToggleMarkForReview={onMark}
        onClearAnswer={onClear}
        onPrevQuestion={onPrev}
        onNextQuestion={onNext}
        hasPrev={true}
        hasNext={false}
      />
    )
    expect(screen.getByText('* Select all options that apply')).toBeInTheDocument()
    expect(screen.getByTestId('option-input-3')).toHaveAttribute('type', 'checkbox')
  })

  it('renders MockTestSubmitModal with warning on unanswered questions', () => {
    const onConfirm = vi.fn()
    const onClose = vi.fn()

    render(
      <MockTestSubmitModal
        isOpen={true}
        onClose={onClose}
        onConfirmSubmit={onConfirm}
        totalQuestions={10}
        answeredCount={7}
        unansweredCount={3}
        markedCount={1}
        isSubmitting={false}
      />
    )

    expect(screen.getByText(/Warning: You have answered 7 of 10 questions/)).toBeInTheDocument()
    expect(screen.getByTestId('modal-confirm-submit-btn')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('modal-confirm-submit-btn'))
    expect(onConfirm).toHaveBeenCalled()

    fireEvent.click(screen.getByTestId('modal-cancel-btn'))
    expect(onClose).toHaveBeenCalled()
  })

  it('renders MockTestScoreCard and MockTestPerformance accurately', () => {
    render(
      <>
        <MockTestScoreCard result={sampleResult} />
        <MockTestPerformance
          topicBreakdown={sampleResult.topic_breakdown}
          difficultyBreakdown={sampleResult.difficulty_breakdown}
        />
      </>
    )

    expect(screen.getByText('EXAMINATION PASSED')).toBeInTheDocument()
    expect(screen.getByTestId('score-percentage-display')).toHaveTextContent('83%')
    expect(screen.getByText('25 / 30')).toBeInTheDocument()
    expect(screen.getByText('Seven OSI Layers')).toBeInTheDocument()
    expect(screen.getByText('9 / 10 (90%)')).toBeInTheDocument()
    expect(screen.getByText('18 / 20 (90%)')).toBeInTheDocument()
  })
})

describe('MockTestEngine Page Flow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('MockTestsPage loads and renders tests and blueprints', async () => {
    vi.mocked(apiService.getMockTests).mockResolvedValue([sampleTestBrief])
    vi.mocked(apiService.getTestBlueprints).mockResolvedValue([])

    await act(async () => {
      render(
        <MemoryRouter>
          <MockTestsPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Beginner Networking Fundamentals Test')).toBeInTheDocument()
    expect(screen.getByTestId('mock-test-search-input')).toBeInTheDocument()
  })

  it('MockTestDetailPage loads and starts exam session', async () => {
    const detail: MockTestDetail = {
      ...sampleTestBrief,
      instructions: 'Time starts immediately upon entry.',
      topics_breakdown: [{ topic: 'Seven OSI Layers', question_count: 30 }],
      questions: [],
    }
    vi.mocked(apiService.getMockTest).mockResolvedValue(detail)
    vi.mocked(apiService.startAttempt).mockResolvedValue({
      attempt_id: 77,
      test_id: 1,
      test_title: 'Beginner Networking Fundamentals Test',
      test_slug: 'beginner-networking-fundamentals-test',
      duration_minutes: 30,
      passing_percentage: 70.0,
      started_at: '2026-09-29T20:00:00Z',
      expires_at: '2026-09-29T20:30:00Z',
      remaining_seconds: 1800,
      status: 'IN_PROGRESS',
      questions: sampleQuestions,
      saved_answers: [],
    })

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/mock-tests/beginner-networking-fundamentals-test']}>
          <Routes>
            <Route path="/mock-tests/:slug" element={<MockTestDetailPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Beginner Networking Fundamentals Test')).toBeInTheDocument()
    expect(screen.getByText('Time starts immediately upon entry.')).toBeInTheDocument()

    const startBtn = screen.getByTestId('start-exam-btn')
    await act(async () => {
      fireEvent.click(startBtn)
    })

    expect(apiService.startAttempt).toHaveBeenCalledWith(1, false)
  })

  it('MockTestWorkspacePage synchronizes and allows answer saving', async () => {
    vi.mocked(apiService.getAttemptStatus).mockResolvedValue({
      attempt_id: 77,
      status: 'IN_PROGRESS',
      started_at: '2026-09-29T20:00:00Z',
      expires_at: '2026-09-29T20:30:00Z',
      remaining_seconds: 1750,
      is_expired: false,
      answered_count: 0,
      marked_count: 0,
      total_questions: 2,
    })

    vi.mocked(apiService.startAttempt).mockResolvedValue({
      attempt_id: 77,
      test_id: 1,
      test_title: 'Beginner Networking Fundamentals Test',
      test_slug: 'beginner-networking-fundamentals-test',
      duration_minutes: 30,
      passing_percentage: 70.0,
      started_at: '2026-09-29T20:00:00Z',
      expires_at: '2026-09-29T20:30:00Z',
      remaining_seconds: 1750,
      status: 'IN_PROGRESS',
      questions: sampleQuestions,
      saved_answers: [],
    })

    vi.mocked(apiService.saveAnswer).mockResolvedValue({
      success: true,
      question_id: 101,
      selected_option_ids: [2],
      is_marked_for_review: false,
      message: 'Saved',
    })

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/mock-tests/attempt/77']}>
          <Routes>
            <Route path="/mock-tests/attempt/:attemptId" element={<MockTestWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByTestId('mock-test-workspace')).toBeInTheDocument()
    expect(screen.getByText('Which OSI layer is responsible for port addressing?')).toBeInTheDocument()

    // Select option 2
    const opt2 = screen.getByTestId('option-input-2')
    await act(async () => {
      fireEvent.click(opt2)
    })

    expect(apiService.saveAnswer).toHaveBeenCalledWith(77, {
      question_id: 101,
      selected_option_ids: [2],
    })
  })

  it('MockTestReviewPage filters questions and displays explanations', async () => {
    const reviewData: TestReviewResponse = {
      attempt_id: 77,
      test_id: 1,
      test_title: 'Beginner Networking Fundamentals Test',
      test_slug: 'beginner-networking-fundamentals-test',
      status: 'SUBMITTED',
      result: sampleResult,
      questions: [
        {
          question_id: 101,
          question_number: 1,
          question_text: 'Which OSI layer is responsible for port addressing?',
          question_type: 'SINGLE_CHOICE',
          points: 1,
          topic_title: 'Seven OSI Layers',
          difficulty: 'BEGINNER',
          options: [
            { id: 1, option_text: 'Layer 3 Network', is_correct: false },
            { id: 2, option_text: 'Layer 4 Transport', is_correct: true },
          ],
          selected_option_ids: [2],
          is_correct: true,
          points_earned: 1,
          is_marked_for_review: false,
          explanation: 'Layer 4 Transport handles port numbers and end-to-end flow control.',
        },
      ],
    }

    vi.mocked(apiService.getAttemptReview).mockResolvedValue(reviewData)

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/mock-tests/attempt/77/review']}>
          <Routes>
            <Route path="/mock-tests/attempt/:attemptId/review" element={<MockTestReviewPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(screen.getByTestId('mock-test-review-page')).toBeInTheDocument()
    expect(screen.getByText('Layer 4 Transport handles port numbers and end-to-end flow control.')).toBeInTheDocument()
    expect(screen.getByText('Correct Answer')).toBeInTheDocument()
  })

  it('MockTestHistoryPage renders list of historical exam sittings', async () => {
    const historyItem: AttemptHistoryItem = {
      attempt_id: 77,
      test_id: 1,
      test_title: 'Beginner Networking Fundamentals Test',
      test_slug: 'beginner-networking-fundamentals-test',
      difficulty: 'BEGINNER',
      test_type: 'COMPREHENSIVE',
      status: 'SUBMITTED',
      score: 25,
      total_points: 30,
      percentage: 83.3,
      passed: true,
      started_at: '2026-09-29T20:00:00Z',
      submitted_at: '2026-09-29T20:20:00Z',
      time_taken_seconds: 1200,
    }

    vi.mocked(apiService.getAttemptHistory).mockResolvedValue([historyItem])

    await act(async () => {
      render(
        <MemoryRouter>
          <MockTestHistoryPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByTestId('history-item-77')).toBeInTheDocument()
    expect(screen.getByText('Examination Sitting History')).toBeInTheDocument()
    expect(screen.getByText('83%')).toBeInTheDocument()
  })
})
