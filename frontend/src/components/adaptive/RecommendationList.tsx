import React from 'react'
import { Sparkles } from 'lucide-react'
import { RecommendationCard } from './RecommendationCard'
import type { RecommendationItem } from '../../types'

interface RecommendationListProps {
  recommendations: RecommendationItem[]
  onStartPractice?: (topicId?: number | null) => void
}

export const RecommendationList: React.FC<RecommendationListProps> = ({
  recommendations,
  onStartPractice,
}) => {
  if (!recommendations || recommendations.length === 0) {
    return null
  }

  return (
    <div className="ad-recommendations-section" data-testid="recommendations-section">
      <div className="ad-section-header">
        <div className="ad-section-title">
          <Sparkles size={20} color="#a855f7" />
          Recommended Next Activities
        </div>
      </div>

      <div className="ad-rec-grid" data-testid="recommendations-grid">
        {recommendations.map((rec) => (
          <RecommendationCard
            key={rec.id}
            recommendation={rec}
            onStartPractice={onStartPractice}
          />
        ))}
      </div>
    </div>
  )
}
