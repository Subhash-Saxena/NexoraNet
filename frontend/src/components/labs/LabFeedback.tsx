import React from 'react'
import { CheckCircle2, AlertCircle, Award, BookOpen } from 'lucide-react'
import type { StepSubmitResponse, LabStepSubmissionBrief } from '../../types'

interface LabFeedbackProps {
  result?: StepSubmitResponse | null
  existingSubmission?: LabStepSubmissionBrief | null
}

export const LabFeedback: React.FC<LabFeedbackProps> = ({
  result,
  existingSubmission,
}) => {
  if (!result && !existingSubmission) return null

  const isCorrect = result ? result.is_correct : existingSubmission?.is_correct ?? false
  const pointsEarned = result ? result.points_earned : existingSubmission?.points_earned ?? 0
  const feedbackText = result ? result.feedback : existingSubmission?.feedback
  const explanation = result?.explanation

  return (
    <div className={`lab-feedback-alert ${isCorrect ? 'correct' : 'incorrect'}`}>
      <div className="lab-feedback-head">
        {isCorrect ? (
          <>
            <CheckCircle2 size={20} />
            <span>Correct!</span>
            <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.85rem' }}>
              <Award size={16} /> +{pointsEarned} pts
            </span>
          </>
        ) : (
          <>
            <AlertCircle size={20} />
            <span>Verification Needs Review</span>
          </>
        )}
      </div>

      {feedbackText && <div className="lab-feedback-msg">{feedbackText}</div>}

      {explanation && (
        <div className="lab-feedback-explanation">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700, color: 'var(--text-main)', marginBottom: 4 }}>
            <BookOpen size={14} color="var(--cyan-primary)" />
            <span>Pedagogical Takeaway</span>
          </div>
          <p style={{ margin: 0 }}>{explanation}</p>
        </div>
      )}
    </div>
  )
}
