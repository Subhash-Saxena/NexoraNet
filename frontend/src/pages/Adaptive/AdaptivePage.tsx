import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Compass, RefreshCw, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'
import type { AdaptiveOverviewResponse } from '../../types'
import { WhatShouldIDoNextCard } from '../../components/adaptive/WhatShouldIDoNextCard'
import { PerformanceOverviewCard } from '../../components/adaptive/PerformanceOverviewCard'
import { TopicPerformanceGrid } from '../../components/adaptive/TopicPerformanceGrid'
import { RecommendationList } from '../../components/adaptive/RecommendationList'
import { BeginnerPathBanner } from '../../components/adaptive/BeginnerPathBanner'
import { AdaptiveLaunchModal } from '../../components/adaptive/AdaptiveLaunchModal'
import '../../components/adaptive/adaptive.css'

export const AdaptivePage: React.FC = () => {
  const navigate = useNavigate()
  const [overview, setOverview] = useState<AdaptiveOverviewResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isStarting, setIsStarting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false)
  const [modalFocusTopicId, setModalFocusTopicId] = useState<number | null>(null)

  const fetchOverview = async () => {
    setIsLoading(true)
    setError(null)
    try {
      if (apiService.getAdaptiveOverview) {
        const data = await apiService.getAdaptiveOverview()
        setOverview(data)
      } else {
        throw new Error('Adaptive service endpoint unavailable')
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load adaptive performance data'
      setError(msg)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOverview()
  }, [])

  const handleStartPractice = async (topicId?: number | null) => {
    setIsStarting(true)
    try {
      const payload = {
        question_count: 20,
        duration_minutes: 20,
        focus_topic_ids: topicId ? [topicId] : undefined,
      }
      const res = await apiService.startAdaptiveTest(payload)
      navigate(`/mock-tests/attempt/${res.attempt_id}`)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to launch adaptive practice session'
      setError(msg)
      setIsStarting(false)
    }
  }

  const handleModalLaunch = async (params: {
    question_count: number
    duration_minutes: number
    focus_topic_ids?: number[]
  }) => {
    setIsStarting(true)
    try {
      const res = await apiService.startAdaptiveTest(params)
      setIsModalOpen(false)
      navigate(`/mock-tests/attempt/${res.attempt_id}`)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to launch custom practice session'
      setError(msg)
      setIsStarting(false)
    }
  }

  const handleOpenCustomize = (topicId?: number | null) => {
    setModalFocusTopicId(topicId || null)
    setIsModalOpen(true)
  }

  if (isLoading) {
    return (
      <div className="ad-container" style={{ textAlign: 'center', padding: '6rem 1rem' }}>
        <div
          style={{
            display: 'inline-block',
            width: '2.5rem',
            height: '2.5rem',
            border: '3px solid #334155',
            borderTopColor: '#38bdf8',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }}
        />
        <p style={{ marginTop: '1rem', color: '#94a3b8' }}>
          Analyzing examination history and computing adaptive recommendations...
        </p>
      </div>
    )
  }

  if (error && !overview) {
    return (
      <div className="ad-container" style={{ maxWidth: '640px', padding: '4rem 1rem', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#f87171', margin: '0 auto 1rem' }} />
        <h2 style={{ color: '#f8fafc', marginBottom: '0.5rem' }}>Adaptive Diagnostics Unavailable</h2>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>{error}</p>
        <button type="button" className="ad-btn-primary" onClick={fetchOverview} style={{ margin: '0 auto' }}>
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    )
  }

  if (!overview) return null

  return (
    <div className="ad-container" data-testid="adaptive-dashboard-page">
      <div className="ad-header">
        <div className="ad-header-title">
          <Compass size={32} color="#38bdf8" />
          Adaptive Testing & Personalized Practice
        </div>
        <p className="ad-header-desc">
          Explainable, rule-based learning guidance for computer networking and cybersecurity.
          The engine analyzes your recent test accuracy, question volume, and topic mastery to
          recommend what you should study, validate, or practice next.
        </p>
      </div>

      {/* Hero: "What should I do next?" Card */}
      <WhatShouldIDoNextCard
        recommendation={overview.next_action}
        onStartPractice={() => handleStartPractice(null)}
        onCustomize={() => handleOpenCustomize(null)}
        isStarting={isStarting}
      />

      {/* Onboarding Pathway if insufficient data */}
      {!overview.has_sufficient_data && <BeginnerPathBanner />}

      {/* Diagnostic Metrics Overview */}
      <PerformanceOverviewCard overview={overview} />

      {/* Categorized Next Step Recommendations */}
      <RecommendationList
        recommendations={overview.recommendations}
        onStartPractice={(topicId) => handleStartPractice(topicId)}
      />

      {/* Granular Networking Topic Performance Grid */}
      <TopicPerformanceGrid
        topics={overview.all_topics}
        onPracticeTopic={(topicId) => handleStartPractice(topicId)}
      />

      {/* Launch Configuration Modal */}
      <AdaptiveLaunchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onLaunch={handleModalLaunch}
        topics={overview.all_topics}
        initialFocusTopicId={modalFocusTopicId}
        isStarting={isStarting}
      />
    </div>
  )
}
