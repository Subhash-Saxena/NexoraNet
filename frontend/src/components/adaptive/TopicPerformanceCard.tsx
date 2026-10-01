import React from 'react'
import { Play } from 'lucide-react'
import type { TopicPerformanceItem } from '../../types'

interface TopicPerformanceCardProps {
  topic: TopicPerformanceItem
  onPracticeTopic: (topicId: number) => void
}

export const TopicPerformanceCard: React.FC<TopicPerformanceCardProps> = ({
  topic,
  onPracticeTopic,
}) => {
  const getStatusBadge = () => {
    switch (topic.status) {
      case 'NEEDS_PRACTICE':
        return <span className="ad-status-badge ad-status-needs-practice">Needs Practice</span>
      case 'DEVELOPING':
        return <span className="ad-status-badge ad-status-developing">Developing</span>
      case 'SOLID':
        return <span className="ad-status-badge ad-status-solid">Solid</span>
      case 'STRONG':
        return <span className="ad-status-badge ad-status-strong">Strong</span>
      case 'INSUFFICIENT_DATA':
      default:
        return <span className="ad-status-badge ad-status-insufficient">Initial / No Data</span>
    }
  }

  const getBarColor = () => {
    switch (topic.status) {
      case 'NEEDS_PRACTICE':
        return '#ef4444'
      case 'DEVELOPING':
        return '#3b82f6'
      case 'SOLID':
        return '#818cf8'
      case 'STRONG':
        return '#10b981'
      default:
        return '#475569'
    }
  }

  const hasData = topic.questions_answered > 0

  return (
    <div className="ad-topic-card" data-testid={`topic-card-${topic.topic_slug}`}>
      <div>
        <div className="ad-topic-header">
          <div className="ad-topic-name">{topic.topic_title}</div>
          {getStatusBadge()}
        </div>

        <div className="ad-progress-bar-bg">
          <div
            className="ad-progress-bar-fill"
            style={{
              width: `${hasData ? Math.min(100, Math.max(8, topic.recent_accuracy)) : 0}%`,
              backgroundColor: getBarColor(),
            }}
          />
        </div>

        <div className="ad-topic-stats-row">
          <span>
            {hasData ? `${topic.recent_accuracy.toFixed(0)}% recent accuracy` : '0% accuracy'}
          </span>
          <span>
            {topic.correct_answers}/{topic.questions_answered} answered
          </span>
        </div>

        <div className="ad-topic-action-text">{topic.recommended_action}</div>
      </div>

      <button
        onClick={() => onPracticeTopic(topic.topic_id)}
        className="ad-topic-btn"
        data-testid={`practice-topic-${topic.topic_id}`}
      >
        <Play size={14} /> Practice Topic
      </button>
    </div>
  )
}
