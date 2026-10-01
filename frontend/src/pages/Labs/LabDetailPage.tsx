import React, { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Send,
  CheckCircle2,
  Terminal,
  Layers,
} from 'lucide-react'
import { apiService } from '../../services/api'
import { LabStepList } from '../../components/labs/LabStepList'
import { LabInstructions } from '../../components/labs/LabInstructions'
import { LabObservation } from '../../components/labs/LabObservation'
import { LabHint } from '../../components/labs/LabHint'
import { LabFeedback } from '../../components/labs/LabFeedback'
import { LabCompletion } from '../../components/labs/LabCompletion'
import { LabAnswerInput } from '../../components/labs/inputs/LabAnswerInput'
import type { LabDetail, LabStepDetail, StepSubmitResponse } from '../../types'
import '../../components/labs/labs.css'

export const LabDetailPage: React.FC = () => {
  const { labSlug } = useParams<{ labSlug: string }>()
  const navigate = useNavigate()

  const [lab, setLab] = useState<LabDetail | null>(null)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [currentAnswer, setCurrentAnswer] = useState<unknown>('')
  const [hintRevealed, setHintRevealed] = useState(false)
  const [submissionResult, setSubmissionResult] = useState<StepSubmitResponse | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRetrying, setIsRetrying] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize or fetch active lab attempt
  const loadLab = useCallback(async () => {
    if (!labSlug) return
    try {
      setLoading(true)
      // Call startLab which returns or creates an active attempt for this lab
      const labData = await apiService.startLab(labSlug)
      setLab(labData)

      // Find first incomplete step
      const steps = labData.steps || []
      const firstIncompleteIdx = steps.findIndex((s) => !s.is_completed)
      if (firstIncompleteIdx !== -1) {
        setCurrentStepIndex(firstIncompleteIdx)
      } else {
        setCurrentStepIndex(0)
      }
      setError(null)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to initialize lab session.')
    } finally {
      setLoading(false)
    }
  }, [labSlug])

  useEffect(() => {
    loadLab()
  }, [loadLab])

  const steps = lab?.steps || []
  const currentStep: LabStepDetail | undefined = steps[currentStepIndex]

  // When active step changes, sync current answer and hint state
  useEffect(() => {
    if (currentStep) {
      if (currentStep.latest_submission) {
        setCurrentAnswer(currentStep.latest_submission.submitted_answer)
        setHintRevealed(currentStep.latest_submission.hint_used)
      } else {
        setCurrentAnswer('')
        setHintRevealed(false)
      }
      setSubmissionResult(null)
    }
  }, [currentStepIndex, currentStep?.id])

  // Handle submitting an answer for the current step
  const handleSubmitStep = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!lab || !currentStep || !lab.active_attempt_id) return
    if (currentAnswer === undefined || currentAnswer === null || currentAnswer === '') return

    try {
      setIsSubmitting(true)
      const res = await apiService.submitLabStep(lab.active_attempt_id, currentStep.id, {
        submitted_answer: currentAnswer,
        hint_used: hintRevealed,
      })
      setSubmissionResult(res)

      // Update local state reactively
      setLab((prevLab) => {
        if (!prevLab) return null
        const updatedSteps = prevLab.steps.map((s) => {
          if (s.id === currentStep.id) {
            return {
              ...s,
              is_completed: res.is_correct || s.is_completed,
              points_earned: Math.max(s.points_earned, res.points_earned),
              latest_submission: {
                id: Date.now(),
                step_id: s.id,
                submitted_answer: String(currentAnswer),
                is_correct: res.is_correct,
                points_earned: res.points_earned,
                hint_used: hintRevealed,
                feedback: res.feedback,
                submitted_at: new Date().toISOString(),
              },
            }
          }
          return s
        })

        return {
          ...prevLab,
          active_attempt_score: res.attempt_score,
          active_attempt_percentage: res.attempt_percentage,
          active_attempt_status: res.is_lab_completed ? 'COMPLETED' : prevLab.active_attempt_status,
          steps: updatedSteps,
        }
      })
    } catch (err: unknown) {
      setSubmissionResult({
        step_id: currentStep.id,
        attempt_id: lab.active_attempt_id,
        is_correct: false,
        points_earned: 0,
        max_points: currentStep.points,
        feedback: err instanceof Error ? err.message : 'Error submitting answer. Please try again.',
        attempt_score: lab.active_attempt_score,
        attempt_total_points: lab.total_points,
        attempt_percentage: lab.active_attempt_percentage,
        is_lab_completed: false,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Handle retry
  const handleRetryLab = async () => {
    if (!lab || !lab.active_attempt_id) return
    try {
      setIsRetrying(true)
      const freshLab = await apiService.retryLab(lab.active_attempt_id)
      setLab(freshLab)
      setCurrentStepIndex(0)
      setCurrentAnswer('')
      setHintRevealed(false)
      setSubmissionResult(null)
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to retry lab.')
    } finally {
      setIsRetrying(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0', color: 'var(--text-muted)' }}>
        <Terminal size={40} color="var(--cyan-primary)" style={{ margin: '0 auto 16px auto' }} />
        <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: 8 }}>
          Provisioning Lab Workspace...
        </h2>
        <p>Loading validation schemas, steps, and target network configuration.</p>
      </div>
    )
  }

  if (error || !lab) {
    return (
      <div className="labs-container">
        <div className="lab-feedback-alert incorrect">
          <div className="lab-feedback-head">Unable to Load Lab</div>
          <div className="lab-feedback-msg">{error || 'Lab not found.'}</div>
          <div style={{ marginTop: 12 }}>
            <Link to="/labs" className="btn-lab-action btn-lab-secondary">
              <ArrowLeft size={14} /> Back to Labs Catalog
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const isLastStep = currentStepIndex === steps.length - 1
  const isFirstStep = currentStepIndex === 0
  const allStepsCompleted =
    steps.length > 0 && steps.every((s) => s.is_completed) && lab.active_attempt_status === 'COMPLETED'

  return (
    <div className="labs-container">
      {/* Workspace Grid */}
      <div className="lab-workspace">
        {/* Left Sidebar - Step Navigation */}
        <LabStepList
          lab={lab}
          currentStepIndex={currentStepIndex}
          onSelectStep={(idx) => setCurrentStepIndex(idx)}
        />

        {/* Right Main Pane */}
        <main className="lab-main-pane">
          {allStepsCompleted && submissionResult?.is_lab_completed ? (
            <LabCompletion lab={lab} onRetry={handleRetryLab} isRetrying={isRetrying} />
          ) : currentStep ? (
            <div className="lab-step-card">
              {/* Step Header */}
              <div className="lab-step-header">
                <div className="lab-step-title-wrap">
                  <span className="lab-step-badge">
                    Step {currentStep.step_number} of {steps.length}
                  </span>
                  <h1 className="lab-step-headline">{currentStep.title}</h1>
                </div>

                <div className="lab-step-points-tag">
                  {currentStep.is_completed ? (
                    <span style={{ color: 'var(--emerald-success)' }}>
                      Completed ({currentStep.points_earned} / {currentStep.points} pts)
                    </span>
                  ) : (
                    <span>{currentStep.points} Points</span>
                  )}
                </div>
              </div>

              {/* Step Instructions & OS Command Switcher */}
              <LabInstructions
                step={currentStep}
                environmentType={lab.environment_type}
              />

              {/* Expected Observation */}
              <LabObservation observation={currentStep.expected_observation} />

              {/* Guided Hint */}
              <LabHint
                hint={currentStep.hint}
                isRevealed={hintRevealed}
                onHintRevealed={() => setHintRevealed(true)}
              />

              {/* Answer Input Section */}
              <form onSubmit={handleSubmitStep} className="lab-question-card">
                <div className="lab-question-title">
                  <Terminal size={18} color="var(--cyan-primary)" />
                  <span>
                    {currentStep.questions?.[0]?.question_text ||
                      'Submit your verified observation or value:'}
                  </span>
                </div>

                <LabAnswerInput
                  config={currentStep.safe_input_config}
                  validationType={currentStep.validation_type}
                  value={currentAnswer}
                  onChange={setCurrentAnswer}
                  disabled={isSubmitting}
                />

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
                  <button
                    type="submit"
                    className="btn-lab-action btn-lab-primary"
                    disabled={isSubmitting || currentAnswer === ''}
                  >
                    {isSubmitting ? (
                      'Validating...'
                    ) : (
                      <>
                        <Send size={15} /> Verify & Submit Answer
                      </>
                    )}
                  </button>
                </div>
              </form>

              {/* Real-time Feedback & Explanation */}
              <LabFeedback
                result={submissionResult}
                existingSubmission={currentStep.latest_submission}
              />

              {/* Navigation Action Bar */}
              <div className="lab-action-bar">
                <button
                  type="button"
                  className="btn-lab-action btn-lab-secondary"
                  onClick={() => setCurrentStepIndex((prev) => Math.max(0, prev - 1))}
                  disabled={isFirstStep}
                >
                  <ArrowLeft size={16} /> Previous Step
                </button>

                <div style={{ display: 'flex', gap: 10 }}>
                  {!isLastStep ? (
                    <button
                      type="button"
                      className="btn-lab-action btn-lab-primary"
                      onClick={() =>
                        setCurrentStepIndex((prev) => Math.min(steps.length - 1, prev + 1))
                      }
                    >
                      Next Step <ArrowRight size={16} />
                    </button>
                  ) : allStepsCompleted ? (
                    <button
                      type="button"
                      className="btn-lab-action btn-lab-primary"
                      onClick={() => navigate('/labs')}
                    >
                      Finish Lab <CheckCircle2 size={16} />
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          ) : (
            <div className="lab-step-card" style={{ textAlign: 'center', padding: 40 }}>
              <Layers size={36} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
              <h3>No step selected</h3>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
