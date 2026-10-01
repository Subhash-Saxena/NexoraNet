import React from 'react'
import { Link } from 'react-router-dom'
import {
  Clock,
  HelpCircle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Play,
  RotateCcw,
  AlertTriangle,
} from 'lucide-react'
import type { MockTestBrief } from '../../types'

interface MockTestCardProps {
  test: MockTestBrief
}

export const MockTestCard: React.FC<MockTestCardProps> = ({ test }) => {
  const getDifficultyBadgeClass = (diff: string) => {
    switch (diff.toUpperCase()) {
      case 'BEGINNER':
        return 'mt-badge-beginner'
      case 'INTERMEDIATE':
        return 'mt-badge-intermediate'
      case 'ADVANCED':
        return 'mt-badge-advanced'
      case 'MIXED':
        return 'mt-badge-advanced'
      default:
        return 'mt-badge-beginner'
    }
  }

  const isReady = test.is_ready !== false && test.status === 'PUBLISHED'
  const hasActiveAttempt = Boolean(test.active_attempt_id)
  const hasPriorAttempt =
    test.latest_attempt_score !== undefined && test.latest_attempt_score !== null

  const renderStatusOrScore = () => {
    if (hasActiveAttempt) {
      return (
        <span
          className="mt-badge mt-badge-inprogress"
          title="You have an active in-progress sitting"
          data-testid={`active-attempt-${test.slug}`}
        >
          Sitting In Progress
        </span>
      )
    }

    if (!isReady) {
      return (
        <span
          className="mt-badge mt-badge-draft"
          title={`Shortfall: ${test.shortfall || 0} questions needed in bank`}
          data-testid={`draft-badge-${test.slug}`}
        >
          <AlertTriangle size={12} style={{ display: 'inline', marginRight: 4 }} />
          Draft (Pool Shortfall: {test.shortfall || 0})
        </span>
      )
    }

    if (hasPriorAttempt) {
      const isPassed =
        test.latest_attempt_status === 'COMPLETED' ||
        test.latest_attempt_score! >= test.passing_percentage
      return (
        <span
          className={`mt-score-indicator ${isPassed ? 'mt-score-passed' : 'mt-score-failed'}`}
          title={`Passing requirement: ${test.passing_percentage}% (${test.attempt_count || 1} attempts)`}
        >
          {isPassed ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
          Score: {Math.round(test.latest_attempt_score!)}% ({isPassed ? 'PASSED' : 'FAILED'})
        </span>
      )
    }

    return <span className="mt-score-indicator mt-score-unattempted">Not Attempted</span>
  }

  return (
    <div className="mt-card" data-testid={`mock-test-card-${test.slug}`}>
      <div>
        <div className="mt-card-header" style={{ marginBottom: '0.35rem' }}>
          {test.code && (
            <span className="mt-code-badge" data-testid={`test-code-${test.code}`}>
              {test.code}
            </span>
          )}
          <h3 className="mt-card-title" style={{ marginTop: '0.35rem' }}>
            {test.title}
          </h3>
        </div>

        <div className="mt-card-badges">
          <span className={`mt-badge ${getDifficultyBadgeClass(test.difficulty)}`}>
            {test.difficulty}
          </span>
          {test.test_type && (
            <span className="mt-badge mt-badge-type">{test.test_type}</span>
          )}
          {test.attempt_count && test.attempt_count > 0 ? (
            <span
              className="mt-badge"
              style={{ background: '#1e293b', color: '#94a3b8', border: '1px solid #334155' }}
            >
              {test.attempt_count} {test.attempt_count === 1 ? 'attempt' : 'attempts'}
            </span>
          ) : null}
        </div>

        <p className="mt-card-desc">
          {test.description || 'Comprehensive networking examination.'}
        </p>

        <div className="mt-card-meta">
          <div className="mt-meta-item">
            <Clock size={14} />
            <span>{test.duration_minutes} mins</span>
          </div>
          <div className="mt-meta-item">
            <HelpCircle size={14} />
            <span>{test.total_questions} questions</span>
          </div>
          <div className="mt-meta-item">
            <span>Pass: {test.passing_percentage}%</span>
          </div>
        </div>

        {test.topics_covered && test.topics_covered.length > 0 && (
          <div className="mt-topics-tags">
            {test.topics_covered.slice(0, 3).map((topic, i) => (
              <span key={i} className="mt-topic-tag">
                {topic}
              </span>
            ))}
            {test.topics_covered.length > 3 && (
              <span className="mt-topic-tag">+{test.topics_covered.length - 3} more</span>
            )}
          </div>
        )}
      </div>

      <div className="mt-card-footer" style={{ gap: '0.5rem', flexWrap: 'wrap' }}>
        <div>{renderStatusOrScore()}</div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          {/* State-aware action button */}
          {hasActiveAttempt ? (
            <Link
              to={`/mock-tests/attempt/${test.active_attempt_id}`}
              className="mt-btn mt-btn-primary"
              style={{
                padding: '0.4rem 0.85rem',
                fontSize: '0.8125rem',
                background: '#059669',
                borderColor: '#10b981',
              }}
              data-testid={`continue-btn-${test.slug}`}
            >
              <Play size={13} /> Continue
            </Link>
          ) : isReady && hasPriorAttempt ? (
            <Link
              to={`/mock-tests/${test.slug}`}
              className="mt-btn mt-btn-secondary"
              style={{ padding: '0.4rem 0.85rem', fontSize: '0.8125rem' }}
              data-testid={`retake-btn-${test.slug}`}
            >
              <RotateCcw size={13} /> Retake
            </Link>
          ) : null}

          <Link
            to={`/mock-tests/${test.slug}`}
            className="mt-btn mt-btn-primary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.8125rem' }}
            data-testid={`view-details-btn-${test.slug}`}
          >
            {isReady ? 'View Test' : 'View Syllabus'} <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  )
}
