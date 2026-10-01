import React from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, RotateCcw, ArrowRight, History, Clock } from 'lucide-react'
import type { LabDetail } from '../../types'

interface LabCompletionProps {
  lab: LabDetail
  onRetry: () => void
  isRetrying?: boolean
}

export const LabCompletion: React.FC<LabCompletionProps> = ({
  lab,
  onRetry,
  isRetrying = false,
}) => {
  const formatTime = (seconds?: number | null) => {
    if (!seconds) return '—'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    if (mins === 0) return `${secs}s`
    return `${mins}m ${secs}s`
  }

  return (
    <div className="lab-completion-card">
      <div className="lab-completion-icon">
        <CheckCircle2 size={44} />
      </div>

      <div>
        <h2 className="lab-completion-title">Lab Completed!</h2>
        <p className="lab-completion-subtitle">
          Great job! You have verified all steps and completed <strong>{lab.title}</strong>.
        </p>
      </div>

      <div className="lab-completion-stats">
        <div className="lab-completion-stat-box">
          <span className="lab-completion-stat-lbl">Final Score</span>
          <span className="lab-completion-stat-val">
            {lab.active_attempt_score} / {lab.total_points}
          </span>
        </div>

        <div className="lab-completion-stat-box">
          <span className="lab-completion-stat-lbl">Accuracy</span>
          <span className="lab-completion-stat-val">
            {Math.round(lab.active_attempt_percentage)}%
          </span>
        </div>

        <div className="lab-completion-stat-box">
          <span className="lab-completion-stat-lbl">Time Elapsed</span>
          <span className="lab-completion-stat-val" style={{ fontSize: '1.25rem' }}>
            <Clock size={16} style={{ display: 'inline', marginRight: 4 }} />
            {formatTime(lab.active_attempt_time_taken)}
          </span>
        </div>
      </div>

      <div style={{ width: '100%', maxWidth: 600, textAlign: 'left' }}>
        <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>
          Step Performance Summary
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {lab.steps.map((step) => (
            <div
              key={step.id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 14px',
                background: 'var(--bg-input)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <span style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>
                {step.step_number}. {step.title}
              </span>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--emerald-success)' }}>
                {step.points_earned} / {step.points} pts
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="lab-completion-actions">
        <button
          type="button"
          className="btn-lab-action btn-lab-secondary"
          onClick={onRetry}
          disabled={isRetrying}
        >
          <RotateCcw size={16} />
          <span>{isRetrying ? 'Resetting...' : 'Retake Lab'}</span>
        </button>

        <Link to="/labs/history" className="btn-lab-action btn-lab-secondary">
          <History size={16} />
          <span>Attempt History</span>
        </Link>

        <Link to="/labs" className="btn-lab-action btn-lab-primary">
          <span>Explore More Labs</span>
          <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  )
}
