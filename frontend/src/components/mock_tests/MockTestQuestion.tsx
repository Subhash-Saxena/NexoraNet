import React from 'react'
import { Flag, RotateCcw, ChevronLeft, ChevronRight } from 'lucide-react'
import type { StudentQuestionPayload } from '../../types'

interface MockTestQuestionProps {
  question: StudentQuestionPayload
  selectedOptionIds: number[]
  onOptionToggle: (optionId: number) => void
  isMarkedForReview: boolean
  onToggleMarkForReview: () => void
  onClearAnswer: () => void
  onPrevQuestion: () => void
  onNextQuestion: () => void
  hasPrev: boolean
  hasNext: boolean
  isSaving?: boolean
}

export const MockTestQuestion: React.FC<MockTestQuestionProps> = ({
  question,
  selectedOptionIds,
  onOptionToggle,
  isMarkedForReview,
  onToggleMarkForReview,
  onClearAnswer,
  onPrevQuestion,
  onNextQuestion,
  hasPrev,
  hasNext,
  isSaving = false,
}) => {
  const isMultiple = question.question_type === 'MULTIPLE_CHOICE'

  return (
    <div className="mt-question-area" data-testid="mock-test-question-area">
      <div className="mt-question-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className="mt-q-num">Question {question.question_number}</span>
          <span className="mt-badge mt-badge-type">{question.topic_title}</span>
          <span
            className={`mt-badge ${
              question.difficulty === 'BEGINNER'
                ? 'mt-badge-beginner'
                : question.difficulty === 'INTERMEDIATE'
                ? 'mt-badge-intermediate'
                : 'mt-badge-advanced'
            }`}
          >
            {question.difficulty}
          </span>
        </div>
        <span className="mt-q-points">{question.points} {question.points === 1 ? 'Point' : 'Points'}</span>
      </div>

      <h2 className="mt-question-text">{question.question_text}</h2>

      {isMultiple && (
        <p style={{ color: '#38bdf8', fontSize: '0.8125rem', marginBottom: '1rem', fontWeight: 500 }}>
          * Select all options that apply
        </p>
      )}

      <div className="mt-options-list" role="group" aria-label="Question options">
        {question.options.map((opt) => {
          const isSelected = selectedOptionIds.includes(opt.id)
          return (
            <label
              key={opt.id}
              className={`mt-option-item ${isSelected ? 'selected' : ''}`}
              data-testid={`option-item-${opt.id}`}
            >
              <input
                type={isMultiple ? 'checkbox' : 'radio'}
                name={`question-${question.id}`}
                value={opt.id}
                checked={isSelected}
                onChange={() => onOptionToggle(opt.id)}
                className="mt-option-input"
                data-testid={`option-input-${opt.id}`}
              />
              <span className="mt-option-text">{opt.option_text}</span>
            </label>
          )
        })}
      </div>

      <div className="mt-question-actions">
        <div className="mt-actions-left">
          <button
            type="button"
            className={`mt-btn ${isMarkedForReview ? 'mt-btn-primary' : 'mt-btn-secondary'}`}
            onClick={onToggleMarkForReview}
            data-testid="mark-review-toggle-btn"
            title="Mark this question to review later"
          >
            <Flag size={15} style={{ color: isMarkedForReview ? '#fbbf24' : 'currentColor' }} />
            {isMarkedForReview ? 'Marked for Review' : 'Mark for Review'}
          </button>

          <button
            type="button"
            className="mt-btn mt-btn-secondary"
            onClick={onClearAnswer}
            disabled={selectedOptionIds.length === 0 || isSaving}
            data-testid="clear-answer-btn"
            title="Clear chosen options for this question"
          >
            <RotateCcw size={15} />
            Clear Choice
          </button>
        </div>

        <div className="mt-actions-right">
          <button
            type="button"
            className="mt-btn mt-btn-secondary"
            onClick={onPrevQuestion}
            disabled={!hasPrev}
            data-testid="prev-question-btn"
          >
            <ChevronLeft size={16} />
            Previous
          </button>

          <button
            type="button"
            className="mt-btn mt-btn-primary"
            onClick={onNextQuestion}
            disabled={!hasNext}
            data-testid="next-question-btn"
          >
            Next
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
