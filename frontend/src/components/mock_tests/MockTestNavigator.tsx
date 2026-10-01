import React from 'react'
import { Flag, Send } from 'lucide-react'
import type { StudentQuestionPayload } from '../../types'

interface MockTestNavigatorProps {
  questions: StudentQuestionPayload[]
  currentIndex: number
  onSelectQuestion: (index: number) => void
  answers: Record<number, number[]>
  markedQuestions: Set<number>
  onSubmitClick: () => void
}

export const MockTestNavigator: React.FC<MockTestNavigatorProps> = ({
  questions,
  currentIndex,
  onSelectQuestion,
  answers,
  markedQuestions,
  onSubmitClick,
}) => {
  const total = questions.length
  let answeredCount = 0
  let markedCount = 0

  questions.forEach((q) => {
    const selected = answers[q.id]
    if (selected && selected.length > 0) {
      answeredCount++
    }
    if (markedQuestions.has(q.id)) {
      markedCount++
    }
  })

  const unansweredCount = total - answeredCount

  const getQuestionButtonClass = (q: StudentQuestionPayload, idx: number) => {
    const isCurrent = idx === currentIndex
    const isAnswered = answers[q.id] && answers[q.id].length > 0
    const isMarked = markedQuestions.has(q.id)

    const classes = ['mt-palette-btn']
    if (isCurrent) classes.push('current')
    else if (isAnswered) classes.push('answered')
    if (isMarked) classes.push('marked')

    return classes.join(' ')
  }

  return (
    <aside className="mt-navigator" data-testid="mock-test-question-navigator">
      <h3 className="mt-navigator-title">Question Navigator</h3>

      <div className="mt-palette-legend">
        <div className="mt-legend-item">
          <span className="mt-legend-indicator mt-legend-current" />
          <span>Current</span>
        </div>
        <div className="mt-legend-item">
          <span className="mt-legend-indicator mt-legend-answered" />
          <span>Answered</span>
        </div>
        <div className="mt-legend-item">
          <span className="mt-legend-indicator mt-legend-marked" />
          <span>Marked</span>
        </div>
        <div className="mt-legend-item">
          <span className="mt-legend-indicator mt-legend-unanswered" />
          <span>Unanswered</span>
        </div>
      </div>

      <div className="mt-palette-grid">
        {questions.map((q, idx) => (
          <button
            key={q.id}
            type="button"
            className={getQuestionButtonClass(q, idx)}
            onClick={() => onSelectQuestion(idx)}
            data-testid={`nav-btn-${idx + 1}`}
            title={`Question ${idx + 1}${markedQuestions.has(q.id) ? ' (Marked for review)' : ''}`}
          >
            {idx + 1}
          </button>
        ))}
      </div>

      <div className="mt-navigator-stats">
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Answered:</span>
          <strong style={{ color: '#34d399' }}>{answeredCount} / {total}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Unanswered:</span>
          <strong style={{ color: '#94a3b8' }}>{unansweredCount}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Marked for Review:</span>
          <strong style={{ color: '#fbbf24' }}>
            <Flag size={12} style={{ display: 'inline', marginRight: 4 }} />
            {markedCount}
          </strong>
        </div>
      </div>

      <button
        type="button"
        className="mt-btn mt-btn-danger"
        style={{ width: '100%', marginTop: 'auto' }}
        onClick={onSubmitClick}
        data-testid="navigator-submit-btn"
      >
        <Send size={16} />
        Submit Test
      </button>
    </aside>
  )
}
