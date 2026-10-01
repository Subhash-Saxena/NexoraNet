import React, { useEffect, useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ChevronLeft,
  CheckCircle2,
  XCircle,
  HelpCircle,
  BookOpen,
  Flag,
  AlertCircle,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { TestReviewResponse } from '../../types'
import '../../components/mock_tests/mock_tests.css'

export const MockTestReviewPage: React.FC = () => {
  const { attemptId: rawAttemptId } = useParams<{ attemptId: string }>()
  const attemptId = parseInt(rawAttemptId || '0', 10)

  const [reviewData, setReviewData] = useState<TestReviewResponse | null>(null)
  const [activeFilter, setActiveFilter] = useState<'all' | 'incorrect' | 'unanswered' | 'correct' | 'marked'>('all')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!attemptId) return
    setIsLoading(true)
    setError(null)

    apiService
      .getAttemptReview(attemptId)
      .then((data) => setReviewData(data))
      .catch((err) => {
        setError(err.message || 'Failed to retrieve test review.')
      })
      .finally(() => setIsLoading(false))
  }, [attemptId])

  const filteredQuestions = useMemo(() => {
    if (!reviewData) return []
    return reviewData.questions.filter((q) => {
      const isAnswered = q.selected_option_ids.length > 0
      switch (activeFilter) {
        case 'incorrect':
          return isAnswered && !q.is_correct
        case 'unanswered':
          return !isAnswered
        case 'correct':
          return isAnswered && q.is_correct
        case 'marked':
          return q.is_marked_for_review
        default:
          return true
      }
    })
  }, [reviewData, activeFilter])

  if (isLoading) {
    return (
      <div className="mt-container" style={{ textAlign: 'center', padding: '6rem 1rem' }}>
        <div style={{ display: 'inline-block', width: '2rem', height: '2rem', border: '3px solid #334155', borderTopColor: '#38bdf8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <p style={{ marginTop: '1rem', color: '#94a3b8' }}>Unlocking authoritative review and explanations...</p>
      </div>
    )
  }

  if (error || !reviewData) {
    return (
      <div className="mt-container" style={{ maxWidth: '640px', padding: '4rem 1rem', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#f87171', margin: '0 auto 1rem' }} />
        <h2 style={{ color: '#f8fafc', marginBottom: '0.5rem' }}>Review Unavailable</h2>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
          {error?.includes('403')
            ? 'Answer review is protected while the test sitting is in progress. Please submit the examination first.'
            : error || 'Failed to load question explanations.'}
        </p>
        <Link to={`/mock-tests/attempt/${attemptId}`} className="mt-btn mt-btn-primary">
          Return to Test
        </Link>
      </div>
    )
  }

  // Count filter metrics
  let correctCount = 0
  let incorrectCount = 0
  let unansweredCount = 0
  let markedCount = 0

  reviewData.questions.forEach((q) => {
    const isAnswered = q.selected_option_ids.length > 0
    if (!isAnswered) unansweredCount++
    else if (q.is_correct) correctCount++
    else incorrectCount++
    if (q.is_marked_for_review) markedCount++
  })

  return (
    <div className="mt-container" data-testid="mock-test-review-page">
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', marginBottom: '1.5rem' }}>
        <Link
          to={`/mock-tests/attempt/${attemptId}/result`}
          className="mt-btn mt-btn-secondary"
          data-testid="back-to-scorecard-btn"
        >
          <ChevronLeft size={16} /> Back to Scorecard
        </Link>

        <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
          {reviewData.test_title} &bull; Detailed Answer Review
        </h1>
      </div>

      {/* Filter Tabs Bar */}
      <div className="mt-review-filters" data-testid="review-filter-tabs">
        <button
          type="button"
          className={`mt-pill-btn ${activeFilter === 'all' ? 'active' : ''}`}
          onClick={() => setActiveFilter('all')}
          data-testid="filter-all-btn"
        >
          All Questions ({reviewData.questions.length})
        </button>
        <button
          type="button"
          className={`mt-pill-btn ${activeFilter === 'incorrect' ? 'active' : ''}`}
          onClick={() => setActiveFilter('incorrect')}
          data-testid="filter-incorrect-btn"
        >
          <XCircle size={14} style={{ display: 'inline', marginRight: 4, color: '#f87171' }} />
          Incorrect ({incorrectCount})
        </button>
        <button
          type="button"
          className={`mt-pill-btn ${activeFilter === 'unanswered' ? 'active' : ''}`}
          onClick={() => setActiveFilter('unanswered')}
          data-testid="filter-unanswered-btn"
        >
          <HelpCircle size={14} style={{ display: 'inline', marginRight: 4, color: '#94a3b8' }} />
          Unanswered ({unansweredCount})
        </button>
        <button
          type="button"
          className={`mt-pill-btn ${activeFilter === 'correct' ? 'active' : ''}`}
          onClick={() => setActiveFilter('correct')}
          data-testid="filter-correct-btn"
        >
          <CheckCircle2 size={14} style={{ display: 'inline', marginRight: 4, color: '#34d399' }} />
          Correct ({correctCount})
        </button>
        {markedCount > 0 && (
          <button
            type="button"
            className={`mt-pill-btn ${activeFilter === 'marked' ? 'active' : ''}`}
            onClick={() => setActiveFilter('marked')}
            data-testid="filter-marked-btn"
          >
            <Flag size={14} style={{ display: 'inline', marginRight: 4, color: '#fbbf24' }} />
            Marked for Review ({markedCount})
          </button>
        )}
      </div>

      {/* Filter Results Info */}
      <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
        Showing {filteredQuestions.length} of {reviewData.questions.length} questions
      </p>

      {/* Questions Review List */}
      <div>
        {filteredQuestions.map((q) => {
          const isAnswered = q.selected_option_ids.length > 0
          const statusClass = !isAnswered ? 'unanswered' : q.is_correct ? 'correct' : 'incorrect'

          return (
            <div
              key={q.question_id}
              className={`mt-review-card ${statusClass}`}
              data-testid={`review-question-${q.question_id}`}
            >
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span className="mt-q-num">Question {q.question_number}</span>
                  <span className="mt-badge mt-badge-type">{q.topic_title}</span>
                  <span
                    className={`mt-badge ${
                      q.difficulty === 'BEGINNER'
                        ? 'mt-badge-beginner'
                        : q.difficulty === 'INTERMEDIATE'
                        ? 'mt-badge-intermediate'
                        : 'mt-badge-advanced'
                    }`}
                  >
                    {q.difficulty}
                  </span>
                  {q.is_marked_for_review && (
                    <span className="mt-badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                      <Flag size={12} /> Marked
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span
                    style={{
                      fontSize: '0.8125rem',
                      fontWeight: 600,
                      color: !isAnswered ? '#94a3b8' : q.is_correct ? '#34d399' : '#f87171',
                    }}
                  >
                    {!isAnswered ? 'Unanswered (0 pts)' : q.is_correct ? `Correct (+${q.points_earned} pts)` : 'Incorrect (0 pts)'}
                  </span>
                  <span className="mt-q-points">{q.points} max pts</span>
                </div>
              </div>

              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#f8fafc', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                {q.question_text}
              </h3>

              {/* Options Evaluation */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
                {q.options.map((opt) => {
                  const wasSelected = q.selected_option_ids.includes(opt.id)
                  const isTargetCorrect = opt.is_correct

                  let optClass = 'mt-review-opt'
                  if (isTargetCorrect) {
                    optClass += ' is-correct-target'
                  } else if (wasSelected && !isTargetCorrect) {
                    optClass += ' user-incorrect-pick'
                  }

                  return (
                    <div key={opt.id} className={optClass}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                        <span style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
                          {wasSelected ? (
                            isTargetCorrect ? (
                              <CheckCircle2 size={16} style={{ color: '#34d399' }} />
                            ) : (
                              <XCircle size={16} style={{ color: '#f87171' }} />
                            )
                          ) : (
                            <span style={{ display: 'inline-block', width: 16 }} />
                          )}
                        </span>
                        <span>{opt.option_text}</span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', fontWeight: 600 }}>
                        {wasSelected && (
                          <span style={{ color: isTargetCorrect ? '#34d399' : '#f87171', background: 'rgba(0,0,0,0.2)', padding: '0.15rem 0.45rem', borderRadius: '0.25rem' }}>
                            Your Choice
                          </span>
                        )}
                        {isTargetCorrect && (
                          <span style={{ color: '#34d399', background: 'rgba(16, 185, 129, 0.2)', padding: '0.15rem 0.45rem', borderRadius: '0.25rem' }}>
                            Correct Answer
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Pedagogical Explanation Box */}
              <div className="mt-explanation-box">
                <div className="mt-explanation-title">
                  <BookOpen size={16} />
                  Concept Explanation & Networking Rationale:
                </div>
                <div>{q.explanation}</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
