import React from 'react'
import { CheckCircle2, XCircle } from 'lucide-react'
import type { TestResultResponse } from '../../types'

interface MockTestScoreCardProps {
  result: TestResultResponse
}

export const MockTestScoreCard: React.FC<MockTestScoreCardProps> = ({ result }) => {
  const formatDuration = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60)
    const secs = totalSeconds % 60
    if (mins === 0) return `${secs}s`
    return `${mins}m ${secs}s`
  }

  const isPassed = result.passed

  return (
    <div>
      <div
        className={`mt-result-banner ${isPassed ? 'mt-result-banner-passed' : 'mt-result-banner-failed'}`}
        data-testid="mock-test-scorecard"
      >
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          {isPassed ? (
            <CheckCircle2 size={32} style={{ color: '#34d399' }} />
          ) : (
            <XCircle size={32} style={{ color: '#f87171' }} />
          )}
          <span
            className={`mt-result-status-title ${isPassed ? 'mt-result-status-passed' : 'mt-result-status-failed'}`}
          >
            {isPassed ? 'EXAMINATION PASSED' : 'EXAMINATION FAILED'}
          </span>
        </div>

        <p style={{ color: '#94a3b8', fontSize: '1rem', maxWidth: '36rem', margin: '0 auto' }}>
          {isPassed
            ? 'Outstanding work! You demonstrated mastery above the required threshold for this examination.'
            : `You scored ${Math.round(result.percentage)}%, which is below the ${result.passing_percentage}% passing standard. Review weak topics below and practice again.`}
        </p>

        <div className="mt-result-score-circle" data-testid="score-percentage-display">
          {Math.round(result.percentage)}%
        </div>

        <div style={{ color: '#cbd5e1', fontSize: '0.875rem' }}>
          Passing Threshold: <strong>{result.passing_percentage}%</strong>
        </div>
      </div>

      <div className="mt-metrics-grid">
        <div className="mt-metric-card">
          <div className="mt-metric-val" style={{ color: '#38bdf8' }}>
            {result.earned_points} / {result.total_points}
          </div>
          <div className="mt-metric-label">Points Earned</div>
        </div>

        <div className="mt-metric-card">
          <div className="mt-metric-val" style={{ color: '#34d399' }}>
            {result.correct_answers}
          </div>
          <div className="mt-metric-label">Correct Answers</div>
        </div>

        <div className="mt-metric-card">
          <div className="mt-metric-val" style={{ color: '#f87171' }}>
            {result.incorrect_answers}
          </div>
          <div className="mt-metric-label">Incorrect Answers</div>
        </div>

        <div className="mt-metric-card">
          <div className="mt-metric-val" style={{ color: '#94a3b8' }}>
            {result.unanswered_questions}
          </div>
          <div className="mt-metric-label">Unanswered</div>
        </div>

        <div className="mt-metric-card">
          <div className="mt-metric-val" style={{ color: '#cbd5e1' }}>
            {formatDuration(result.time_taken_seconds)}
          </div>
          <div className="mt-metric-label">Time Taken</div>
        </div>
      </div>
    </div>
  )
}
