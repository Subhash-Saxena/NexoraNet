import React, { useState } from 'react'
import { X, Zap, Sliders } from 'lucide-react'
import type { TopicPerformanceItem } from '../../types'

interface AdaptiveLaunchModalProps {
  isOpen: boolean
  onClose: () => void
  onLaunch: (params: {
    question_count: number
    duration_minutes: number
    focus_topic_ids?: number[]
  }) => void
  topics: TopicPerformanceItem[]
  initialFocusTopicId?: number | null
  isStarting?: boolean
}

export const AdaptiveLaunchModal: React.FC<AdaptiveLaunchModalProps> = ({
  isOpen,
  onClose,
  onLaunch,
  topics,
  initialFocusTopicId = null,
  isStarting = false,
}) => {
  const [questionCount, setQuestionCount] = useState<number>(20)
  const [durationMinutes, setDurationMinutes] = useState<number>(20)
  const [selectedTopicId, setSelectedTopicId] = useState<string>(
    initialFocusTopicId ? String(initialFocusTopicId) : 'all'
  )

  if (!isOpen) return null

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onLaunch({
      question_count: questionCount,
      duration_minutes: durationMinutes,
      focus_topic_ids: selectedTopicId !== 'all' ? [parseInt(selectedTopicId, 10)] : undefined,
    })
  }

  return (
    <div className="ad-modal-backdrop" data-testid="adaptive-launch-modal">
      <div className="ad-modal-box">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="ad-modal-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
            <Sliders size={20} color="#38bdf8" />
            Customize Adaptive Session
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <div className="ad-modal-desc">
          Configure session duration and focus topics. Questions will be dynamically calibrated
          to your recent diagnostic profile.
        </div>

        <form onSubmit={handleFormSubmit}>
          <div className="ad-form-group">
            <label className="ad-form-label">Question Count</label>
            <select
              className="ad-select"
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              data-testid="modal-question-count-select"
            >
              <option value={10}>10 Questions (Quick Review)</option>
              <option value={15}>15 Questions (Focused Drill)</option>
              <option value={20}>20 Questions (Standard Calibration)</option>
              <option value={30}>30 Questions (In-Depth Assessment)</option>
            </select>
          </div>

          <div className="ad-form-group">
            <label className="ad-form-label">Time Limit (Minutes)</label>
            <select
              className="ad-select"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(Number(e.target.value))}
              data-testid="modal-duration-select"
            >
              <option value={10}>10 Minutes</option>
              <option value={15}>15 Minutes</option>
              <option value={20}>20 Minutes (Default)</option>
              <option value={30}>30 Minutes</option>
              <option value={45}>45 Minutes</option>
            </select>
          </div>

          <div className="ad-form-group">
            <label className="ad-form-label">Focus Area (Optional)</label>
            <select
              className="ad-select"
              value={selectedTopicId}
              onChange={(e) => setSelectedTopicId(e.target.value)}
              data-testid="modal-topic-select"
            >
              <option value="all">Automatic Multi-Topic Balance (Recommended)</option>
              {topics.map((t) => (
                <option key={t.topic_id} value={t.topic_id}>
                  {t.topic_title} ({t.status.replace('_', ' ')})
                </option>
              ))}
            </select>
          </div>

          <div className="ad-modal-actions">
            <button type="button" onClick={onClose} className="ad-btn-secondary" disabled={isStarting}>
              Cancel
            </button>
            <button
              type="submit"
              className="ad-btn-primary"
              disabled={isStarting}
              data-testid="modal-launch-submit-btn"
            >
              <Zap size={16} />
              {isStarting ? 'Calibrating...' : 'Launch Practice'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
