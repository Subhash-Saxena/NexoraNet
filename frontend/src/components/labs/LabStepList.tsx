import React from 'react'
import { Check, Award, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { LabDetail } from '../../types'

interface LabStepListProps {
  lab: LabDetail
  currentStepIndex: number
  onSelectStep: (index: number) => void
}

export const LabStepList: React.FC<LabStepListProps> = ({
  lab,
  currentStepIndex,
  onSelectStep,
}) => {
  const steps = lab.steps || []
  const completedCount = steps.filter((s) => s.is_completed).length
  const totalSteps = steps.length
  const progressPercent = totalSteps > 0 ? (completedCount / totalSteps) * 100 : 0

  return (
    <aside className="lab-sidebar">
      <Link to="/labs" className="lab-card-topic" style={{ marginBottom: 4 }}>
        <ArrowLeft size={14} /> Back to Labs
      </Link>

      <div className="lab-sidebar-header">
        <h2 className="lab-sidebar-title">{lab.title}</h2>
        <div className="lab-sidebar-score">
          <span>Current Score:</span>
          <span className="lab-sidebar-score-val">
            {lab.active_attempt_score} / {lab.total_points} pts ({Math.round(lab.active_attempt_percentage)}%)
          </span>
        </div>
        <div className="lab-progress-track">
          <div
            className="lab-progress-bar"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      <div className="lab-steps-nav">
        {steps.map((step, idx) => {
          const isActive = idx === currentStepIndex
          const isDone = step.is_completed

          return (
            <button
              key={step.id}
              type="button"
              className={`lab-step-item ${isActive ? 'active' : ''} ${isDone ? 'completed' : ''}`}
              onClick={() => onSelectStep(idx)}
            >
              <div className="lab-step-indicator">
                {isDone ? <Check size={14} /> : idx + 1}
              </div>

              <div className="lab-step-info">
                <span className="lab-step-name">
                  {step.step_number}. {step.title}
                </span>
                <div className="lab-step-meta">
                  <span>
                    {isDone ? (
                      <span style={{ color: 'var(--emerald-success)' }}>
                        Earned: {step.points_earned} pts
                      </span>
                    ) : (
                      `${step.points} pts`
                    )}
                  </span>
                  {step.is_required && (
                    <span style={{ color: 'var(--text-muted)' }}>Required</span>
                  )}
                </div>
              </div>
            </button>
          )
        })}
      </div>

      <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border-subtle)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <Award size={14} color="var(--cyan-primary)" />
          <span>Attempt #{lab.attempt_number || 1}</span>
        </div>
        <div>All submissions are verified securely with instant feedback.</div>
      </div>
    </aside>
  )
}
