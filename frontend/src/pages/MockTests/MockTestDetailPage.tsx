import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  Clock,
  HelpCircle,
  Award,
  ChevronLeft,
  Play,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Flag,
  RotateCcw,
  AlertTriangle,
  BookOpen,
  Target,
  ExternalLink,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { AttemptHistoryItem, MockTestDetail } from '../../types'
import '../../components/mock_tests/mock_tests.css'

export const MockTestDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()

  const [testDetail, setTestDetail] = useState<MockTestDetail | null>(null)
  const [attemptHistory, setAttemptHistory] = useState<AttemptHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isStarting, setIsStarting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    setIsLoading(true)
    setError(null)

    apiService
      .getMockTest(slug)
      .then((data) => {
        setTestDetail(data)
        return apiService.getMockTestAttemptHistory
          ? apiService.getMockTestAttemptHistory(data.id).catch(() => [])
          : Promise.resolve([])
      })
      .then((history) => {
        setAttemptHistory(history)
      })
      .catch((err) => setError(err.message || 'Failed to load test details.'))
      .finally(() => setIsLoading(false))
  }, [slug])

  const handleStartExam = async (retake = false) => {
    if (!testDetail) return
    setIsStarting(true)
    setError(null)

    try {
      const attempt = await apiService.startAttempt(testDetail.id, retake)
      navigate(`/mock-tests/attempt/${attempt.attempt_id}`)
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Failed to launch examination sitting.'
      setError(message)
      setIsStarting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="mt-container" style={{ textAlign: 'center', padding: '6rem 1rem' }}>
        <div
          style={{
            display: 'inline-block',
            width: '2rem',
            height: '2rem',
            border: '3px solid #334155',
            borderTopColor: '#38bdf8',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }}
        />
        <p style={{ marginTop: '1rem', color: '#94a3b8' }}>Loading examination details...</p>
      </div>
    )
  }

  if (error && !testDetail) {
    return (
      <div
        className="mt-container"
        style={{ maxWidth: '640px', padding: '4rem 1rem', textAlign: 'center' }}
      >
        <AlertCircle size={48} style={{ color: '#f87171', margin: '0 auto 1rem' }} />
        <h2 style={{ color: '#f8fafc', marginBottom: '0.5rem' }}>Examination Not Found</h2>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
          {error || 'The requested test could not be located.'}
        </p>
        <Link to="/mock-tests" className="mt-btn mt-btn-secondary">
          <ChevronLeft size={16} /> Back to Catalog
        </Link>
      </div>
    )
  }

  if (!testDetail) return null

  const isReady = testDetail.is_ready !== false && testDetail.status === 'PUBLISHED'
  const hasActiveAttempt = Boolean(testDetail.active_attempt_id)
  const hasPriorAttempt =
    testDetail.latest_attempt_score !== undefined && testDetail.latest_attempt_score !== null
  const isPriorPassed =
    hasPriorAttempt && testDetail.latest_attempt_score! >= testDetail.passing_percentage

  return (
    <div className="mt-container" data-testid="mock-test-detail-page">
      <Link
        to="/mock-tests"
        className="mt-btn mt-btn-secondary"
        style={{ marginBottom: '1.5rem', display: 'inline-flex' }}
        data-testid="back-to-catalog-link"
      >
        <ChevronLeft size={16} /> Back to Catalog
      </Link>

      {/* Main Overview Card */}
      <div
        style={{
          background: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '0.75rem',
          padding: '2rem',
          marginBottom: '2rem',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '0.75rem',
            marginBottom: '0.75rem',
          }}
        >
          {testDetail.code && <span className="mt-code-badge">{testDetail.code}</span>}
          <span
            className={`mt-badge ${
              testDetail.difficulty === 'BEGINNER'
                ? 'mt-badge-beginner'
                : testDetail.difficulty === 'INTERMEDIATE'
                ? 'mt-badge-intermediate'
                : 'mt-badge-advanced'
            }`}
          >
            {testDetail.difficulty}
          </span>
          {testDetail.test_type && (
            <span className="mt-badge mt-badge-type">{testDetail.test_type}</span>
          )}
          {isReady ? (
            <span className="mt-badge mt-badge-ready">Ready to Attempt</span>
          ) : (
            <span className="mt-badge mt-badge-draft">
              Draft (Shortfall: {testDetail.shortfall || 0} Qs)
            </span>
          )}
        </div>

        <h1
          style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: '#f8fafc',
            marginBottom: '0.75rem',
            lineHeight: 1.3,
          }}
        >
          {testDetail.title}
        </h1>

        <p
          style={{
            fontSize: '1rem',
            color: '#94a3b8',
            maxWidth: '52rem',
            lineHeight: 1.6,
            marginBottom: '1.5rem',
          }}
        >
          {testDetail.description}
        </p>

        {/* Metrics Grid */}
        <div className="mt-metrics-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="mt-metric-card">
            <Clock size={20} style={{ color: '#38bdf8', margin: '0 auto 0.5rem' }} />
            <div className="mt-metric-val">{testDetail.duration_minutes} Minutes</div>
            <div className="mt-metric-label">Time Limit</div>
          </div>
          <div className="mt-metric-card">
            <HelpCircle size={20} style={{ color: '#a855f7', margin: '0 auto 0.5rem' }} />
            <div className="mt-metric-val">{testDetail.total_questions} Questions</div>
            <div className="mt-metric-label">Total Questions</div>
          </div>
          <div className="mt-metric-card">
            <Award size={20} style={{ color: '#34d399', margin: '0 auto 0.5rem' }} />
            <div className="mt-metric-val">{testDetail.passing_percentage}%</div>
            <div className="mt-metric-label">Passing Standard</div>
          </div>
          {hasPriorAttempt && (
            <div className="mt-metric-card">
              <CheckCircle2
                size={20}
                style={{
                  color: isPriorPassed ? '#34d399' : '#f87171',
                  margin: '0 auto 0.5rem',
                }}
              />
              <div
                className="mt-metric-val"
                style={{ color: isPriorPassed ? '#34d399' : '#f87171' }}
              >
                {Math.round(testDetail.latest_attempt_score!)}%
              </div>
              <div className="mt-metric-label">
                Last Score ({isPriorPassed ? 'PASSED' : 'FAILED'})
              </div>
            </div>
          )}
        </div>

        {/* Shortfall Alert if Draft */}
        {!isReady && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '0.5rem',
              padding: '1rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              color: '#f87171',
            }}
          >
            <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              <strong style={{ display: 'block', marginBottom: '0.25rem', color: '#fca5a5' }}>
                Question Pool Staging (Draft Status)
              </strong>
              This test blueprint requires {testDetail.total_questions} questions, but the published
              question pool currently has a shortfall of {testDetail.shortfall || 0} questions for this
              specific domain. Examination attempts will unlock automatically when authors stage
              additional questions.
            </div>
          </div>
        )}

        {/* Start / Resume Action Bar */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '1rem',
            paddingTop: '1.25rem',
            borderTop: '1px solid #1e293b',
          }}
        >
          {hasActiveAttempt ? (
            <button
              type="button"
              className="mt-btn mt-btn-primary"
              style={{
                padding: '0.75rem 1.75rem',
                fontSize: '1rem',
                background: '#059669',
                borderColor: '#10b981',
              }}
              onClick={() => navigate(`/mock-tests/attempt/${testDetail.active_attempt_id}`)}
              data-testid="continue-exam-btn"
            >
              <Play size={18} />
              Continue Active Sitting
            </button>
          ) : (
            <button
              type="button"
              className="mt-btn mt-btn-primary"
              style={{
                padding: '0.75rem 1.75rem',
                fontSize: '1rem',
                opacity: isReady ? 1 : 0.5,
                cursor: isReady ? 'pointer' : 'not-allowed',
              }}
              onClick={() => handleStartExam(false)}
              disabled={isStarting || !isReady}
              data-testid="start-exam-btn"
            >
              <Play size={18} />
              {isStarting
                ? 'Launching Session...'
                : hasPriorAttempt
                ? 'Resume / Start Sitting'
                : 'Start Examination'}
            </button>
          )}

          {hasPriorAttempt && isReady && (
            <button
              type="button"
              className="mt-btn mt-btn-secondary"
              style={{ padding: '0.75rem 1.25rem', fontSize: '1rem' }}
              onClick={() => handleStartExam(true)}
              disabled={isStarting}
              data-testid="retake-exam-btn"
            >
              <RotateCcw size={16} />
              Start Fresh Retake
            </button>
          )}
        </div>
      </div>

      {/* Prerequisites & What You Will Practice */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        {/* What You Will Practice */}
        {testDetail.what_you_will_practice && testDetail.what_you_will_practice.length > 0 && (
          <div
            style={{
              background: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: '0.75rem',
              padding: '1.5rem',
            }}
          >
            <h3
              style={{
                fontSize: '1.125rem',
                fontWeight: 600,
                color: '#f8fafc',
                marginBottom: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <Target size={18} style={{ color: '#38bdf8' }} />
              What You Will Practice
            </h3>
            <ul
              style={{
                paddingLeft: '1.25rem',
                margin: 0,
                color: '#cbd5e1',
                fontSize: '0.875rem',
                lineHeight: 1.7,
              }}
            >
              {testDetail.what_you_will_practice.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Prerequisites & Instructions */}
        <div
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '0.75rem',
            padding: '1.5rem',
          }}
        >
          <h3
            style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: '#f8fafc',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <BookOpen size={18} style={{ color: '#a855f7' }} />
            Prerequisites & Knowledge
          </h3>
          <p style={{ color: '#cbd5e1', fontSize: '0.875rem', lineHeight: 1.6, margin: 0 }}>
            {testDetail.prerequisites ||
              'Foundational networking concepts matching the specified difficulty level.'}
          </p>

          {testDetail.instructions && (
            <div
              style={{
                marginTop: '1rem',
                padding: '0.75rem',
                background: '#1e293b',
                borderRadius: '0.375rem',
                color: '#94a3b8',
                fontSize: '0.8125rem',
                lineHeight: 1.5,
              }}
            >
              <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '0.25rem' }}>
                Instructions:
              </strong>
              {testDetail.instructions}
            </div>
          )}
        </div>
      </div>

      {/* Dedicated Pre-Test Guidelines */}
      <div
        style={{
          background: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '0.75rem',
          padding: '1.75rem',
          marginBottom: '2rem',
        }}
      >
        <h3
          style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            color: '#f8fafc',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <ShieldCheck size={20} style={{ color: '#38bdf8' }} />
          Authoritative Exam Engine Guarantees
        </h3>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '1rem',
            color: '#94a3b8',
            fontSize: '0.875rem',
            lineHeight: 1.5,
          }}
        >
          <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
            <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '0.25rem' }}>
              1. Authoritative Server Clock
            </strong>
            The timer begins the moment you enter the workspace and is enforced on the server. If the
            clock expires, answers auto-submit.
          </div>
          <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
            <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '0.25rem' }}>
              2. Zero-Knowledge Shielding
            </strong>
            Correct answer keys and explanations are protected until final submission. You cannot view
            scoring keys while active.
          </div>
          <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
            <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '0.25rem' }}>
              3. Free Navigation & Palette
            </strong>
            Navigate between questions at will, skip difficult items, and track completion via the
            Question Palette.
          </div>
          <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
            <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '0.25rem' }}>
              4. Mark for Review
            </strong>
            Flag questions with the{' '}
            <Flag size={12} style={{ display: 'inline', color: '#fbbf24' }} /> icon to revisit
            before finalizing your submission.
          </div>
        </div>
      </div>

      {/* Syllabus / Topic Distribution */}
      {testDetail.topics_breakdown && testDetail.topics_breakdown.length > 0 && (
        <div
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '0.75rem',
            padding: '1.75rem',
            marginBottom: '2rem',
          }}
        >
          <h3
            style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: '#f8fafc',
              marginBottom: '1rem',
            }}
          >
            Syllabus Topic Coverage & Breakdown
          </h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
              gap: '0.75rem',
            }}
          >
            {testDetail.topics_breakdown.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '0.375rem',
                  padding: '0.75rem 1rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ color: '#f8fafc', fontSize: '0.875rem', fontWeight: 500 }}>
                  {item.topic}
                </span>
                <span style={{ color: '#38bdf8', fontSize: '0.8125rem', fontWeight: 600 }}>
                  {item.question_count} {item.question_count === 1 ? 'question' : 'questions'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Previous Attempts History Table */}
      {attemptHistory.length > 0 && (
        <div
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '0.75rem',
            padding: '1.75rem',
          }}
          data-testid="test-attempt-history-section"
        >
          <h3
            style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: '#f8fafc',
              marginBottom: '1rem',
            }}
          >
            Your Previous Attempts ({attemptHistory.length})
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                textAlign: 'left',
                fontSize: '0.875rem',
              }}
            >
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Attempt</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Date</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Score</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Result</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {attemptHistory.map((att, idx) => (
                  <tr
                    key={att.attempt_id}
                    style={{ borderBottom: '1px solid #1e293b', color: '#cbd5e1' }}
                  >
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>
                      Sitting #{attemptHistory.length - idx}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      {new Date(att.started_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span
                        className={`mt-badge ${
                          att.status === 'IN_PROGRESS' ? 'mt-badge-inprogress' : ''
                        }`}
                      >
                        {att.status}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      {att.status === 'IN_PROGRESS' ? '—' : `${Math.round(att.percentage)}%`}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      {att.status === 'IN_PROGRESS' ? (
                        '—'
                      ) : att.passed ? (
                        <span style={{ color: '#34d399', fontWeight: 600 }}>PASSED</span>
                      ) : (
                        <span style={{ color: '#f87171', fontWeight: 600 }}>FAILED</span>
                      )}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      {att.status === 'IN_PROGRESS' ? (
                        <Link
                          to={`/mock-tests/attempt/${att.attempt_id}`}
                          className="mt-btn mt-btn-primary"
                          style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem' }}
                        >
                          Resume
                        </Link>
                      ) : (
                        <Link
                          to={`/mock-tests/result/${att.attempt_id}`}
                          className="mt-btn mt-btn-secondary"
                          style={{
                            padding: '0.3rem 0.75rem',
                            fontSize: '0.75rem',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          Review <ExternalLink size={12} />
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
