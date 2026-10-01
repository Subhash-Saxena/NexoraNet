import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  FileText,
  RotateCcw,
  Sparkles,
  ChevronLeft,
  AlertCircle,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { TestResultResponse } from '../../types'
import { MockTestScoreCard } from '../../components/mock_tests/MockTestScoreCard'
import { MockTestPerformance } from '../../components/mock_tests/MockTestPerformance'
import '../../components/mock_tests/mock_tests.css'

export const MockTestResultPage: React.FC = () => {
  const { attemptId: rawAttemptId } = useParams<{ attemptId: string }>()
  const attemptId = parseInt(rawAttemptId || '0', 10)
  const navigate = useNavigate()

  const [result, setResult] = useState<TestResultResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isPracticing, setIsPracticing] = useState<boolean>(false)
  const [isRetaking, setIsRetaking] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!attemptId) return
    setIsLoading(true)
    setError(null)

    apiService
      .getAttemptResult(attemptId)
      .then((data) => setResult(data))
      .catch((err) => setError(err.message || 'Failed to load test results.'))
      .finally(() => setIsLoading(false))
  }, [attemptId])

  const handleRetake = async () => {
    if (!result) return
    setIsRetaking(true)
    try {
      const newAttempt = await apiService.startAttempt(result.test_id, true)
      navigate(`/mock-tests/attempt/${newAttempt.attempt_id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to launch fresh retake sitting.')
      setIsRetaking(false)
    }
  }

  const handlePracticeMissed = async () => {
    if (!result) return
    setIsPracticing(true)
    try {
      const practiceAttempt = await apiService.createPracticeSession(
        attemptId,
        'incorrect_or_unanswered'
      )
      navigate(`/mock-tests/attempt/${practiceAttempt.attempt_id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create practice session.')
      setIsPracticing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="mt-container" style={{ textAlign: 'center', padding: '6rem 1rem' }}>
        <div style={{ display: 'inline-block', width: '2rem', height: '2rem', border: '3px solid #334155', borderTopColor: '#38bdf8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <p style={{ marginTop: '1rem', color: '#94a3b8' }}>Evaluating examination performance...</p>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="mt-container" style={{ maxWidth: '640px', padding: '4rem 1rem', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#f87171', margin: '0 auto 1rem' }} />
        <h2 style={{ color: '#f8fafc', marginBottom: '0.5rem' }}>Unable to Load Scorecard</h2>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>{error || 'Results are not available for this session.'}</p>
        <Link to="/mock-tests" className="mt-btn mt-btn-secondary">
          <ChevronLeft size={16} /> Back to Catalog
        </Link>
      </div>
    )
  }

  const hasMissedQuestions = result.incorrect_answers > 0 || result.unanswered_questions > 0

  return (
    <div className="mt-container" data-testid="mock-test-result-page">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <Link to="/mock-tests" className="mt-btn mt-btn-secondary" data-testid="back-to-catalog-btn">
          <ChevronLeft size={16} /> Back to Catalog
        </Link>
        <h2 style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
          Exam Session #{attemptId} &bull; {result.test_title}
        </h2>
      </div>

      {/* Main Scorecard Header */}
      <MockTestScoreCard result={result} />

      {/* Action Buttons Row */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <Link
          to={`/mock-tests/attempt/${attemptId}/review`}
          className="mt-btn mt-btn-primary"
          style={{ padding: '0.75rem 1.5rem', fontSize: '0.9375rem' }}
          data-testid="review-answers-btn"
        >
          <FileText size={16} />
          Review Answers & Explanations
        </Link>

        {hasMissedQuestions && (
          <button
            type="button"
            className="mt-btn mt-btn-outline"
            style={{ padding: '0.75rem 1.25rem', fontSize: '0.9375rem' }}
            onClick={handlePracticeMissed}
            disabled={isPracticing}
            data-testid="practice-missed-btn"
          >
            <Sparkles size={16} />
            {isPracticing ? 'Preparing Practice...' : 'Practice Missed Questions'}
          </button>
        )}

        <button
          type="button"
          className="mt-btn mt-btn-secondary"
          style={{ padding: '0.75rem 1.25rem', fontSize: '0.9375rem' }}
          onClick={handleRetake}
          disabled={isRetaking}
          data-testid="retake-test-btn"
        >
          <RotateCcw size={16} />
          {isRetaking ? 'Launching Retake...' : 'Retake Full Exam'}
        </button>

        <Link
          to="/adaptive-test"
          className="mt-btn mt-btn-primary"
          style={{ padding: '0.75rem 1.25rem', fontSize: '0.9375rem', background: '#2563eb' }}
          data-testid="view-adaptive-recs-btn"
        >
          <Sparkles size={16} />
          View Updated Adaptive Practice
        </Link>
      </div>

      {/* Topic and Difficulty Performance Breakdowns */}
      <MockTestPerformance
        topicBreakdown={result.topic_breakdown}
        difficultyBreakdown={result.difficulty_breakdown}
      />
    </div>
  )
}
