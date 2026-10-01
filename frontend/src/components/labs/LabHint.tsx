import React, { useState } from 'react'
import { HelpCircle, ChevronDown, ChevronUp, Lightbulb } from 'lucide-react'

interface LabHintProps {
  hint?: string | null
  onHintRevealed?: () => void
  isRevealed?: boolean
}

export const LabHint: React.FC<LabHintProps> = ({
  hint,
  onHintRevealed,
  isRevealed = false,
}) => {
  const [isOpen, setIsOpen] = useState(isRevealed)

  if (!hint) return null

  const handleToggle = () => {
    const nextState = !isOpen
    setIsOpen(nextState)
    if (nextState && onHintRevealed) {
      onHintRevealed()
    }
  }

  return (
    <div className="lab-hint-wrapper">
      <button
        type="button"
        className="lab-hint-toggle"
        onClick={handleToggle}
        aria-expanded={isOpen}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <HelpCircle size={16} />
          <span>{isOpen ? 'Hide Guidance Hint' : 'Need a Hint?'}</span>
        </span>
        {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isOpen && (
        <div className="lab-hint-content">
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            <Lightbulb size={18} color="var(--amber-warning)" style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              <p style={{ margin: 0 }}>{hint}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
