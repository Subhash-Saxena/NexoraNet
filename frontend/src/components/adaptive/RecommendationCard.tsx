import React from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Terminal, FileCheck2, Zap, ArrowRight, RotateCcw } from 'lucide-react'
import type { RecommendationItem } from '../../types'
import { apiService } from '../../services/api'

interface RecommendationCardProps {
  recommendation: RecommendationItem
  onStartPractice?: (topicId?: number | null) => void
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onStartPractice,
}) => {
  const getTypeBadge = () => {
    switch (recommendation.type) {
      case 'LESSON':
        return (
          <span className="ad-rec-type-badge ad-type-lesson">
            <BookOpen size={12} style={{ display: 'inline', marginRight: 4 }} />
            Curriculum Lesson
          </span>
        )
      case 'LAB':
        return (
          <span className="ad-rec-type-badge ad-type-lab">
            <Terminal size={12} style={{ display: 'inline', marginRight: 4 }} />
            Hands-on Lab
          </span>
        )
      case 'MOCK_TEST':
        return (
          <span className="ad-rec-type-badge ad-type-test">
            <FileCheck2 size={12} style={{ display: 'inline', marginRight: 4 }} />
            Mock Test
          </span>
        )
      case 'REVIEW':
        return (
          <span className="ad-rec-type-badge ad-type-practice">
            <RotateCcw size={12} style={{ display: 'inline', marginRight: 4 }} />
            Refresher
          </span>
        )
      case 'TOPIC_PRACTICE':
      case 'ADAPTIVE_TEST':
      default:
        return (
          <span className="ad-rec-type-badge ad-type-practice">
            <Zap size={12} style={{ display: 'inline', marginRight: 4 }} />
            Targeted Practice
          </span>
        )
    }
  }

  const handleActionClick = () => {
    // Fire-and-forget telemetry logging
    if (apiService.trackAdaptiveEvent) {
      apiService.trackAdaptiveEvent({
        recommendation_type: recommendation.type,
        title: recommendation.title,
        reason: recommendation.reason,
        action_url: recommendation.action_url,
        event_type: 'CLICKED',
      })
    }

    if (
      (recommendation.type === 'TOPIC_PRACTICE' || recommendation.type === 'ADAPTIVE_TEST') &&
      onStartPractice
    ) {
      onStartPractice(recommendation.topic_id)
    }
  }

  const isInternal = recommendation.action_url.startsWith('/')
  const isPracticeFlow =
    recommendation.type === 'TOPIC_PRACTICE' || recommendation.type === 'ADAPTIVE_TEST'

  return (
    <div className="ad-rec-card" data-testid={`rec-card-${recommendation.id}`}>
      <div>
        <div className="ad-rec-header">
          {getTypeBadge()}
          {recommendation.priority === 'HIGH' && (
            <span className="ad-priority-high">High Priority</span>
          )}
        </div>

        <div className="ad-rec-title">{recommendation.title}</div>
        <div className="ad-rec-reason">{recommendation.reason}</div>
      </div>

      {isPracticeFlow && onStartPractice ? (
        <button
          onClick={handleActionClick}
          className="ad-btn-secondary"
          style={{ width: '100%', justifyContent: 'center' }}
          data-testid={`rec-action-${recommendation.id}`}
        >
          <span>{recommendation.action_label}</span>
          <ArrowRight size={16} />
        </button>
      ) : isInternal ? (
        <Link
          to={recommendation.action_url}
          onClick={handleActionClick}
          className="ad-btn-secondary"
          style={{ width: '100%', justifyContent: 'center' }}
          data-testid={`rec-action-${recommendation.id}`}
        >
          <span>{recommendation.action_label}</span>
          <ArrowRight size={16} />
        </Link>
      ) : (
        <a
          href={recommendation.action_url}
          onClick={handleActionClick}
          className="ad-btn-secondary"
          style={{ width: '100%', justifyContent: 'center' }}
          data-testid={`rec-action-${recommendation.id}`}
        >
          <span>{recommendation.action_label}</span>
          <ArrowRight size={16} />
        </a>
      )}
    </div>
  )
}
