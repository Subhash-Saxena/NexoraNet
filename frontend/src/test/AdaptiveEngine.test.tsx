import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { AdaptivePage } from '../pages/Adaptive/AdaptivePage'
import { WhatShouldIDoNextCard } from '../components/adaptive/WhatShouldIDoNextCard'
import { PerformanceOverviewCard } from '../components/adaptive/PerformanceOverviewCard'
import { TopicPerformanceCard } from '../components/adaptive/TopicPerformanceCard'
import { TopicPerformanceGrid } from '../components/adaptive/TopicPerformanceGrid'
import { RecommendationCard } from '../components/adaptive/RecommendationCard'
import { BeginnerPathBanner } from '../components/adaptive/BeginnerPathBanner'
import { AdaptiveLaunchModal } from '../components/adaptive/AdaptiveLaunchModal'
import type { AdaptiveOverviewResponse, RecommendationItem, TopicPerformanceItem } from '../types'

// Mock API service
vi.mock('../services/api', () => ({
  apiService: {
    getAdaptiveOverview: vi.fn(),
    getTopicPerformance: vi.fn(),
    getRecommendations: vi.fn(),
    getNextRecommendation: vi.fn(),
    startAdaptiveTest: vi.fn(),
    getAdaptiveTestSession: vi.fn(),
    getAdaptiveTestStatus: vi.fn(),
    trackAdaptiveEvent: vi.fn(),
  },
}))

import { apiService } from '../services/api'

const sampleOverview: AdaptiveOverviewResponse = {
  user_id: 1,
  has_sufficient_data: true,
  data_message: 'Diagnostic profile active based on 25 recent questions.',
  overall_accuracy: 74.2,
  total_questions_analyzed: 25,
  total_attempts_analyzed: 2,
  recommended_difficulty: 'INTERMEDIATE',
  difficulty_reason: 'Your Intermediate accuracy is steady at 75%; continued Intermediate practice is recommended.',
  difficulty_performance: {
    BEGINNER: { seen: 15, correct: 13, accuracy: 86.7 },
    INTERMEDIATE: { seen: 10, correct: 7, accuracy: 70.0 },
    ADVANCED: { seen: 0, correct: 0, accuracy: 0.0 },
  },
  top_topics_needing_practice: [
    {
      topic_id: 4,
      topic_title: 'IPv4 Subnetting',
      topic_slug: 'ipv4-subnetting',
      status: 'NEEDS_PRACTICE',
      questions_seen: 10,
      questions_answered: 10,
      correct_answers: 5,
      incorrect_answers: 5,
      unanswered: 0,
      accuracy: 50.0,
      recent_accuracy: 52.0,
      confidence_level: 'DEVELOPING',
      recommended_action: 'Targeted practice recommended to reinforce subnet masks.',
      last_attempt_at: '2026-09-30T09:00:00Z',
      difficulty_distribution: {
        BEGINNER: { seen: 4, correct: 3, accuracy: 75.0 },
        INTERMEDIATE: { seen: 6, correct: 2, accuracy: 33.3 },
        ADVANCED: { seen: 0, correct: 0, accuracy: 0.0 },
      },
    },
  ],
  developing_topics: [],
  strongest_topics: [
    {
      topic_id: 2,
      topic_title: 'OSI Reference Model',
      topic_slug: 'osi-model',
      status: 'STRONG',
      questions_seen: 15,
      questions_answered: 15,
      correct_answers: 14,
      incorrect_answers: 1,
      unanswered: 0,
      accuracy: 93.3,
      recent_accuracy: 93.3,
      confidence_level: 'DEVELOPING',
      recommended_action: 'Strong mastery demonstrated. Maintain proficiency with advanced drills.',
      last_attempt_at: '2026-09-30T09:00:00Z',
      difficulty_distribution: {
        BEGINNER: { seen: 15, correct: 14, accuracy: 93.3 },
        INTERMEDIATE: { seen: 0, correct: 0, accuracy: 0.0 },
        ADVANCED: { seen: 0, correct: 0, accuracy: 0.0 },
      },
    },
  ],
  all_topics: [
    {
      topic_id: 4,
      topic_title: 'IPv4 Subnetting',
      topic_slug: 'ipv4-subnetting',
      status: 'NEEDS_PRACTICE',
      questions_seen: 10,
      questions_answered: 10,
      correct_answers: 5,
      incorrect_answers: 5,
      unanswered: 0,
      accuracy: 50.0,
      recent_accuracy: 52.0,
      confidence_level: 'DEVELOPING',
      recommended_action: 'Targeted practice recommended to reinforce subnet masks.',
      last_attempt_at: '2026-09-30T09:00:00Z',
      difficulty_distribution: {
        BEGINNER: { seen: 4, correct: 3, accuracy: 75.0 },
        INTERMEDIATE: { seen: 6, correct: 2, accuracy: 33.3 },
        ADVANCED: { seen: 0, correct: 0, accuracy: 0.0 },
      },
    },
    {
      topic_id: 2,
      topic_title: 'OSI Reference Model',
      topic_slug: 'osi-model',
      status: 'STRONG',
      questions_seen: 15,
      questions_answered: 15,
      correct_answers: 14,
      incorrect_answers: 1,
      unanswered: 0,
      accuracy: 93.3,
      recent_accuracy: 93.3,
      confidence_level: 'DEVELOPING',
      recommended_action: 'Strong mastery demonstrated.',
      last_attempt_at: '2026-09-30T09:00:00Z',
      difficulty_distribution: {
        BEGINNER: { seen: 15, correct: 14, accuracy: 93.3 },
        INTERMEDIATE: { seen: 0, correct: 0, accuracy: 0.0 },
        ADVANCED: { seen: 0, correct: 0, accuracy: 0.0 },
      },
    },
  ],
  next_action: {
    id: 'rec-next-1',
    type: 'TOPIC_PRACTICE',
    title: 'Practice IPv4 Subnetting',
    reason: 'Your recent subnetting accuracy is 52% across 10 questions.',
    priority: 'HIGH',
    topic_id: 4,
    topic_slug: 'ipv4-subnetting',
    recommended_difficulty: 'INTERMEDIATE',
    action_label: 'Start Practice',
    action_url: '/adaptive-test',
  },
  recommendations: [
    {
      id: 'rec-1',
      type: 'TOPIC_PRACTICE',
      title: 'Practice IPv4 Subnetting',
      reason: 'Your recent subnetting accuracy is 52% across 10 questions.',
      priority: 'HIGH',
      topic_id: 4,
      topic_slug: 'ipv4-subnetting',
      recommended_difficulty: 'INTERMEDIATE',
      action_label: 'Start Practice',
      action_url: '/adaptive-test',
    },
    {
      id: 'rec-2',
      type: 'LAB',
      title: 'Hands-On Lab: Subnetting Workshop',
      reason: 'Reinforce calculation mechanics via terminal validation.',
      priority: 'HIGH',
      topic_id: 4,
      action_label: 'Launch Lab',
      action_url: '/labs/subnet-calculation',
    },
  ],
}

describe('Adaptive Testing & Personalized Practice Engine Frontend', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders AdaptivePage with diagnostics and recommendations', async () => {
    vi.mocked(apiService.getAdaptiveOverview).mockResolvedValue(sampleOverview)

    await act(async () => {
      render(
        <MemoryRouter>
          <AdaptivePage />
        </MemoryRouter>
      )
    })

    expect(screen.getByTestId('adaptive-dashboard-page')).toBeInTheDocument()
    expect(screen.getByText('Adaptive Testing & Personalized Practice')).toBeInTheDocument()
    expect(screen.getByTestId('what-should-i-do-next-card')).toBeInTheDocument()
    expect(screen.getAllByText('Practice IPv4 Subnetting').length).toBeGreaterThan(0)
    expect(screen.getByText('74.2%')).toBeInTheDocument()
    expect(screen.getByText('INTERMEDIATE')).toBeInTheDocument()
    expect(screen.getByTestId('topic-card-ipv4-subnetting')).toBeInTheDocument()
  })

  it('renders WhatShouldIDoNextCard with explicit explainable rationale', () => {
    const startSpy = vi.fn()
    const customizeSpy = vi.fn()

    render(
      <MemoryRouter>
        <WhatShouldIDoNextCard
          recommendation={sampleOverview.next_action}
          onStartPractice={startSpy}
          onCustomize={customizeSpy}
        />
      </MemoryRouter>
    )

    expect(screen.getByText('Practice IPv4 Subnetting')).toBeInTheDocument()
    expect(screen.getByText(/Your recent subnetting accuracy is 52%/)).toBeInTheDocument()

    const startBtn = screen.getByTestId('start-adaptive-btn')
    fireEvent.click(startBtn)
    expect(startSpy).toHaveBeenCalledTimes(1)

    const configBtn = screen.getByText('Configure')
    fireEvent.click(configBtn)
    expect(customizeSpy).toHaveBeenCalledTimes(1)
  })

  it('renders PerformanceOverviewCard difficulty breakdown accurately', () => {
    render(
      <MemoryRouter>
        <PerformanceOverviewCard overview={sampleOverview} />
      </MemoryRouter>
    )

    expect(screen.getByTestId('performance-overview-section')).toBeInTheDocument()
    expect(screen.getByText('74.2%')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
    expect(screen.getByText('Beginner Tier')).toBeInTheDocument()
    expect(screen.getByText('Intermediate Tier')).toBeInTheDocument()
    expect(screen.getByText('87%')).toBeInTheDocument()
    expect(screen.getByText('70%')).toBeInTheDocument()
  })

  it('filters topics by search query and category buttons in TopicPerformanceGrid', () => {
    const practiceSpy = vi.fn()

    render(
      <MemoryRouter>
        <TopicPerformanceGrid
          topics={sampleOverview.all_topics}
          onPracticeTopic={practiceSpy}
        />
      </MemoryRouter>
    )

    expect(screen.getByText('IPv4 Subnetting')).toBeInTheDocument()
    expect(screen.getByText('OSI Reference Model')).toBeInTheDocument()

    // Search filter
    const searchInput = screen.getByTestId('topic-search-input')
    fireEvent.change(searchInput, { target: { value: 'Subnet' } })

    expect(screen.getByText('IPv4 Subnetting')).toBeInTheDocument()
    expect(screen.queryByText('OSI Reference Model')).not.toBeInTheDocument()

    // Clear search
    fireEvent.change(searchInput, { target: { value: '' } })

    // Filter by Needs Practice
    const needsPracticeBtn = screen.getByTestId('filter-needs-practice-topics')
    fireEvent.click(needsPracticeBtn)

    expect(screen.getByText('IPv4 Subnetting')).toBeInTheDocument()
    expect(screen.queryByText('OSI Reference Model')).not.toBeInTheDocument()
  })

  it('renders BeginnerPathBanner when student has insufficient diagnostic data', () => {
    render(
      <MemoryRouter>
        <BeginnerPathBanner />
      </MemoryRouter>
    )

    expect(screen.getByTestId('beginner-path-banner')).toBeInTheDocument()
    expect(screen.getByText('Recommended Foundational Sequence')).toBeInTheDocument()
    expect(screen.getByText('Step 01')).toBeInTheDocument()
    expect(screen.getByText('Networking Fundamentals')).toBeInTheDocument()
    expect(screen.getByTestId('start-learning-path-btn')).toBeInTheDocument()
  })

  it('configures session and calls onLaunch in AdaptiveLaunchModal', () => {
    const launchSpy = vi.fn()
    const closeSpy = vi.fn()

    render(
      <AdaptiveLaunchModal
        isOpen={true}
        onClose={closeSpy}
        onLaunch={launchSpy}
        topics={sampleOverview.all_topics}
      />
    )

    expect(screen.getByTestId('adaptive-launch-modal')).toBeInTheDocument()

    // Select 15 questions
    const countSelect = screen.getByTestId('modal-question-count-select')
    fireEvent.change(countSelect, { target: { value: '15' } })

    // Select 30 minutes
    const durSelect = screen.getByTestId('modal-duration-select')
    fireEvent.change(durSelect, { target: { value: '30' } })

    // Submit
    const submitBtn = screen.getByTestId('modal-launch-submit-btn')
    fireEvent.click(submitBtn)

    expect(launchSpy).toHaveBeenCalledWith({
      question_count: 15,
      duration_minutes: 30,
      focus_topic_ids: undefined,
    })
  })

  it('tracks telemetry and executes action in RecommendationCard', () => {
    const practiceSpy = vi.fn()

    render(
      <MemoryRouter>
        <RecommendationCard
          recommendation={sampleOverview.recommendations[0]}
          onStartPractice={practiceSpy}
        />
      </MemoryRouter>
    )

    expect(screen.getByText('Practice IPv4 Subnetting')).toBeInTheDocument()
    expect(screen.getByText('High Priority')).toBeInTheDocument()

    const actionBtn = screen.getByTestId('rec-action-rec-1')
    fireEvent.click(actionBtn)

    expect(practiceSpy).toHaveBeenCalledWith(4)
    expect(apiService.trackAdaptiveEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        recommendation_type: 'TOPIC_PRACTICE',
        title: 'Practice IPv4 Subnetting',
      })
    )
  })
})
