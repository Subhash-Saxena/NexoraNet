import React, { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'
import type {
  StartAttemptResponse,
  StudentQuestionPayload,
} from '../../types'
import { MockTestTimer } from '../../components/mock_tests/MockTestTimer'
import { MockTestNavigator } from '../../components/mock_tests/MockTestNavigator'
import { MockTestQuestion } from '../../components/mock_tests/MockTestQuestion'
import { MockTestSubmitModal } from '../../components/mock_tests/MockTestSubmitModal'
import '../../components/mock_tests/mock_tests.css'

export const MockTestWorkspacePage: React.FC = () => {
  const { attemptId: rawAttemptId } = useParams<{ attemptId: string }>()
  const attemptId = parseInt(rawAttemptId || '0', 10)
  const navigate = useNavigate()

  const [attemptData, setAttemptData] = useState<StartAttemptResponse | null>(null)
  const [currentIndex, setCurrentIndex] = useState<number>(0)
  const [answers, setAnswers] = useState<Record<number, number[]>>({})
  const [markedQuestions, setMarkedQuestions] = useState<Set<number>>(new Set())
  const [remainingSeconds, setRemainingSeconds] = useState<number>(1800)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isSaving, setIsSaving] = useState<boolean>(false)
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const syncIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const timerTickRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // 1. Initial attempt fetch & status hydration
  useEffect(() => {
    if (!attemptId) return
    setIsLoading(true)
    setError(null)

    // Check status first to see if expired/submitted
    apiService
      .getAttemptStatus(attemptId)
      .then((statusRes) => {
        if (statusRes.status === 'SUBMITTED' || statusRes.status === 'EXPIRED') {
          navigate(`/mock-tests/attempt/${attemptId}/result`, { replace: true })
          return null
        }
        setRemainingSeconds(statusRes.remaining_seconds)
        // Resume attempt details
        return apiService.startAttempt(attemptId.toString())
      })
      .then((res) => {
        if (!res) return
        setAttemptData(res)
        setRemainingSeconds(res.remaining_seconds)

        // Populate saved answers map & marked set
        const ansMap: Record<number, number[]> = {}
        const markedSet = new Set<number>()
        res.saved_answers.forEach((sa) => {
          if (sa.selected_option_ids && sa.selected_option_ids.length > 0) {
            ansMap[sa.question_id] = sa.selected_option_ids
          }
          if (sa.is_marked_for_review) {
            markedSet.add(sa.question_id)
          }
        })
        setAnswers(ansMap)
        setMarkedQuestions(markedSet)
      })
      .catch((err) => {
        setError(err.message || 'Failed to initialize exam workspace.')
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [attemptId, navigate])

  // 2. Second-by-second local countdown ticker
  useEffect(() => {
    if (isLoading || !attemptData) return

    timerTickRef.current = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(timerTickRef.current!)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => {
      if (timerTickRef.current) clearInterval(timerTickRef.current)
    }
  }, [isLoading, attemptData])

  // 3. Periodic server-side timer sync (every 30s)
  useEffect(() => {
    if (!attemptId || isLoading) return

    syncIntervalRef.current = setInterval(() => {
      apiService
        .getAttemptStatus(attemptId)
        .then((stat) => {
          if (stat.is_expired || stat.status === 'SUBMITTED' || stat.status === 'EXPIRED') {
            navigate(`/mock-tests/attempt/${attemptId}/result`, { replace: true })
          } else {
            setRemainingSeconds(stat.remaining_seconds)
          }
        })
        .catch(() => {
          // Silent catch for intermittent background polling
        })
    }, 30000)

    return () => {
      if (syncIntervalRef.current) clearInterval(syncIntervalRef.current)
    }
  }, [attemptId, isLoading, navigate])

  // Auto-submit when time expires
  const handleTimeExpire = useCallback(() => {
    if (isSubmitting) return
    setIsSubmitting(true)
    apiService
      .submitAttempt(attemptId)
      .then(() => {
        navigate(`/mock-tests/attempt/${attemptId}/result`, { replace: true })
      })
      .catch(() => {
        navigate(`/mock-tests/attempt/${attemptId}/result`, { replace: true })
      })
  }, [attemptId, navigate, isSubmitting])

  // Toggle option selection (Single Choice or Multiple Choice)
  const handleOptionToggle = async (optionId: number) => {
    if (!attemptData || isSaving) return
    const currentQ = attemptData.questions[currentIndex]
    if (!currentQ) return

    const isMultiple = currentQ.question_type === 'MULTIPLE_CHOICE'
    const prevSelected = answers[currentQ.id] || []

    let nextSelected: number[]
    if (isMultiple) {
      if (prevSelected.includes(optionId)) {
        nextSelected = prevSelected.filter((id) => id !== optionId)
      } else {
        nextSelected = [...prevSelected, optionId]
      }
    } else {
      nextSelected = [optionId]
    }

    // Optimistic local state update
    setAnswers((prev) => ({
      ...prev,
      [currentQ.id]: nextSelected,
    }))

    setIsSaving(true)
    try {
      await apiService.saveAnswer(attemptId, {
        question_id: currentQ.id,
        selected_option_ids: nextSelected,
      })
    } catch (err: unknown) {
      // Revert on error
      setAnswers((prev) => ({
        ...prev,
        [currentQ.id]: prevSelected,
      }))
      const msg = err instanceof Error ? err.message : 'Failed to record answer.'
      setError(msg)
    } finally {
      setIsSaving(false)
    }
  }

  // Clear answer choice for current question
  const handleClearAnswer = async () => {
    if (!attemptData || isSaving) return
    const currentQ = attemptData.questions[currentIndex]
    if (!currentQ) return

    const prevSelected = answers[currentQ.id] || []
    setAnswers((prev) => {
      const next = { ...prev }
      delete next[currentQ.id]
      return next
    })

    setIsSaving(true)
    try {
      await apiService.clearAnswer(attemptId, currentQ.id)
    } catch (err: unknown) {
      setAnswers((prev) => ({ ...prev, [currentQ.id]: prevSelected }))
      const msg = err instanceof Error ? err.message : 'Failed to clear choice.'
      setError(msg)
    } finally {
      setIsSaving(false)
    }
  }

  // Toggle Mark for Review
  const handleToggleMarkForReview = async () => {
    if (!attemptData) return
    const currentQ = attemptData.questions[currentIndex]
    if (!currentQ) return

    const isCurrentlyMarked = markedQuestions.has(currentQ.id)
    const nextMarked = !isCurrentlyMarked

    // Optimistic update
    setMarkedQuestions((prev) => {
      const copy = new Set(prev)
      if (nextMarked) copy.add(currentQ.id)
      else copy.delete(currentQ.id)
      return copy
    })

    try {
      await apiService.markQuestion(attemptId, currentQ.id, nextMarked)
    } catch (err: unknown) {
      // Revert on error
      setMarkedQuestions((prev) => {
        const copy = new Set(prev)
        if (isCurrentlyMarked) copy.add(currentQ.id)
        else copy.delete(currentQ.id)
        return copy
      })
      const msg = err instanceof Error ? err.message : 'Failed to toggle review marker.'
      setError(msg)
    }
  }

  // Final examination submission
  const handleConfirmSubmit = async () => {
    setIsSubmitting(true)
    setError(null)

    try {
      await apiService.submitAttempt(attemptId)
      navigate(`/mock-tests/attempt/${attemptId}/result`, { replace: true })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit examination.'
      setError(msg)
      setIsSubmitting(false)
      setIsSubmitModalOpen(false)
    }
  }

  if (isLoading) {
    return (
      <div className="mt-container" style={{ textAlign: 'center', padding: '6rem 1rem' }}>
        <div style={{ display: 'inline-block', width: '2rem', height: '2rem', border: '3px solid #334155', borderTopColor: '#38bdf8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <p style={{ marginTop: '1rem', color: '#94a3b8' }}>Synchronizing exam sitting and starting timer...</p>
      </div>
    )
  }

  if (error && !attemptData) {
    return (
      <div className="mt-container" style={{ maxWidth: '640px', padding: '4rem 1rem', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#f87171', margin: '0 auto 1rem' }} />
        <h2 style={{ color: '#f8fafc', marginBottom: '0.5rem' }}>Unable to Open Session</h2>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>{error}</p>
        <button type="button" className="mt-btn mt-btn-secondary" onClick={() => navigate('/mock-tests')}>
          Return to Catalog
        </button>
      </div>
    )
  }

  if (!attemptData || attemptData.questions.length === 0) {
    return null
  }

  const currentQuestion: StudentQuestionPayload = attemptData.questions[currentIndex]
  const currentSelected = answers[currentQuestion.id] || []
  const isMarked = markedQuestions.has(currentQuestion.id)

  const answeredCount = Object.values(answers).filter((arr) => arr.length > 0).length
  const unansweredCount = attemptData.questions.length - answeredCount
  const markedCount = markedQuestions.size

  return (
    <div className="mt-workspace" data-testid="mock-test-workspace">
      {/* Sticky Top Bar */}
      <header className="mt-sticky-topbar">
        <div className="mt-topbar-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <h2 className="mt-topbar-title">{attemptData.test_title}</h2>
            {(attemptData.test_slug.startsWith('adaptive') ||
              attemptData.test_title.toLowerCase().includes('adaptive')) && (
              <span
                className="mt-badge"
                style={{
                  background: '#2563eb',
                  color: '#ffffff',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '0.25rem',
                }}
                data-testid="adaptive-session-badge"
              >
                Adaptive Practice
              </span>
            )}
          </div>
          <span className="mt-topbar-progress">
            Question {currentIndex + 1} of {attemptData.questions.length}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MockTestTimer
            remainingSeconds={remainingSeconds}
            onExpire={handleTimeExpire}
          />
          <button
            type="button"
            className="mt-btn mt-btn-danger"
            onClick={() => setIsSubmitModalOpen(true)}
            data-testid="topbar-submit-btn"
          >
            <Send size={15} />
            Submit Exam
          </button>
        </div>
      </header>

      {/* Workspace Body: 2 Columns */}
      <div className="mt-workspace-body">
        {/* Left Column: Question Area */}
        <main>
          {error && (
            <div style={{ margin: '1rem 2rem 0', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', padding: '0.75rem 1rem', color: '#f87171', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <MockTestQuestion
            question={currentQuestion}
            selectedOptionIds={currentSelected}
            onOptionToggle={handleOptionToggle}
            isMarkedForReview={isMarked}
            onToggleMarkForReview={handleToggleMarkForReview}
            onClearAnswer={handleClearAnswer}
            onPrevQuestion={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
            onNextQuestion={() => setCurrentIndex((prev) => Math.min(attemptData.questions.length - 1, prev + 1))}
            hasPrev={currentIndex > 0}
            hasNext={currentIndex < attemptData.questions.length - 1}
            isSaving={isSaving}
          />
        </main>

        {/* Right Column: Question Navigator */}
        <MockTestNavigator
          questions={attemptData.questions}
          currentIndex={currentIndex}
          onSelectQuestion={(idx) => setCurrentIndex(idx)}
          answers={answers}
          markedQuestions={markedQuestions}
          onSubmitClick={() => setIsSubmitModalOpen(true)}
        />
      </div>

      {/* Confirmation Modal */}
      <MockTestSubmitModal
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        onConfirmSubmit={handleConfirmSubmit}
        totalQuestions={attemptData.questions.length}
        answeredCount={answeredCount}
        unansweredCount={unansweredCount}
        markedCount={markedCount}
        isSubmitting={isSubmitting}
      />
    </div>
  )
}
