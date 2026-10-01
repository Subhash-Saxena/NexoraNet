import React from 'react'
import { AlertTriangle, Send, X } from 'lucide-react'

interface MockTestSubmitModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirmSubmit: () => void
  totalQuestions: number
  answeredCount: number
  unansweredCount: number
  markedCount: number
  isSubmitting: boolean
}

export const MockTestSubmitModal: React.FC<MockTestSubmitModalProps> = ({
  isOpen,
  onClose,
  onConfirmSubmit,
  totalQuestions,
  answeredCount,
  unansweredCount,
  markedCount,
  isSubmitting,
}) => {
  if (!isOpen) return null

  return (
    <div className="mt-modal-overlay" data-testid="mock-test-submit-dialog">
      <div className="mt-modal">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 className="mt-modal-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
            {unansweredCount > 0 ? (
              <AlertTriangle size={20} style={{ color: '#fbbf24' }} />
            ) : (
              <Send size={20} style={{ color: '#38bdf8' }} />
            )}
            Confirm Test Submission
          </h3>
          <button
            type="button"
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <p className="mt-modal-text">
          {unansweredCount > 0 ? (
            <span style={{ color: '#f87171' }}>
              Warning: You have answered {answeredCount} of {totalQuestions} questions (<strong>{unansweredCount}</strong> unanswered).
            </span>
          ) : (
            `You have answered all ${totalQuestions} questions in this examination.`
          )}
          {markedCount > 0 && (
            <span> You still have <strong>{markedCount}</strong> questions marked for review.</span>
          )}
          {' '}Once submitted, your responses will be evaluated authoritatively by the backend server.
        </p>

        <div className="mt-modal-stats">
          <div>
            <div className="mt-modal-stat-val" style={{ color: '#34d399' }}>
              {answeredCount}
            </div>
            <div className="mt-modal-stat-label">Answered</div>
          </div>
          <div>
            <div className="mt-modal-stat-val" style={{ color: unansweredCount > 0 ? '#f87171' : '#94a3b8' }}>
              {unansweredCount}
            </div>
            <div className="mt-modal-stat-label">Unanswered</div>
          </div>
          <div>
            <div className="mt-modal-stat-val" style={{ color: markedCount > 0 ? '#fbbf24' : '#94a3b8' }}>
              {markedCount}
            </div>
            <div className="mt-modal-stat-label">Marked</div>
          </div>
        </div>

        <div className="mt-modal-actions">
          <button
            type="button"
            className="mt-btn mt-btn-secondary"
            onClick={onClose}
            disabled={isSubmitting}
            data-testid="modal-cancel-btn"
          >
            Return to Exam
          </button>
          <button
            type="button"
            className="mt-btn mt-btn-danger"
            onClick={onConfirmSubmit}
            disabled={isSubmitting}
            data-testid="modal-confirm-submit-btn"
          >
            {isSubmitting ? 'Evaluating...' : 'Confirm & Submit'}
          </button>
        </div>
      </div>
    </div>
  )
}
