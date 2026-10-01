import React from 'react'
import { Award, CheckCircle2, FileQuestion, BarChart2, ShieldCheck } from 'lucide-react'
import type { AdaptiveOverviewResponse } from '../../types'

interface PerformanceOverviewCardProps {
  overview: AdaptiveOverviewResponse
}

export const PerformanceOverviewCard: React.FC<PerformanceOverviewCardProps> = ({ overview }) => {
  const {
    overall_accuracy,
    total_questions_analyzed,
    total_attempts_analyzed,
    recommended_difficulty,
    difficulty_reason,
    difficulty_performance,
  } = overview

  const b = difficulty_performance.BEGINNER
  const i = difficulty_performance.INTERMEDIATE
  const a = difficulty_performance.ADVANCED

  return (
    <div className="ad-overview-section" data-testid="performance-overview-section">
      <div className="ad-metrics-grid">
        <div className="ad-metric-card" data-testid="metric-accuracy">
          <div className="ad-metric-header">
            <span>Recent Accuracy</span>
            <CheckCircle2 size={18} color="#3b82f6" />
          </div>
          <div className="ad-metric-val">{overall_accuracy.toFixed(1)}%</div>
          <div className="ad-metric-sub">Weighted recency average</div>
        </div>

        <div className="ad-metric-card" data-testid="metric-questions">
          <div className="ad-metric-header">
            <span>Questions Analyzed</span>
            <FileQuestion size={18} color="#8b5cf6" />
          </div>
          <div className="ad-metric-val">{total_questions_analyzed}</div>
          <div className="ad-metric-sub">Recent analysis window</div>
        </div>

        <div className="ad-metric-card" data-testid="metric-attempts">
          <div className="ad-metric-header">
            <span>Tests Evaluated</span>
            <BarChart2 size={18} color="#10b981" />
          </div>
          <div className="ad-metric-val">{total_attempts_analyzed}</div>
          <div className="ad-metric-sub">Completed formal sittings</div>
        </div>

        <div className="ad-metric-card" data-testid="metric-difficulty">
          <div className="ad-metric-header">
            <span>Recommended Tier</span>
            <Award size={18} color="#f59e0b" />
          </div>
          <div className="ad-metric-val" style={{ color: '#f59e0b', fontSize: '1.5rem' }}>
            {recommended_difficulty}
          </div>
          <div className="ad-metric-sub">Adaptive calibration tier</div>
        </div>
      </div>

      <div className="ad-diff-breakdown" data-testid="difficulty-breakdown">
        <div className="ad-diff-header">
          <div className="ad-diff-title">
            <ShieldCheck size={18} style={{ display: 'inline', marginRight: 6, color: '#38bdf8' }} />
            Difficulty Progression & Calibrated Recommendations
          </div>
        </div>
        <div className="ad-diff-reason">{difficulty_reason}</div>
        <div className="ad-diff-tiers">
          <div className={`ad-diff-tier-card ${recommended_difficulty === 'BEGINNER' ? 'active' : ''}`}>
            <div className="ad-diff-tier-name">Beginner Tier</div>
            <div className="ad-diff-tier-stat">{b.seen > 0 ? `${b.accuracy.toFixed(0)}%` : 'No data'}</div>
            <div className="ad-metric-sub">{b.seen > 0 ? `${b.correct}/${b.seen} correct` : 'Not attempted yet'}</div>
          </div>

          <div className={`ad-diff-tier-card ${recommended_difficulty === 'INTERMEDIATE' ? 'active' : ''}`}>
            <div className="ad-diff-tier-name">Intermediate Tier</div>
            <div className="ad-diff-tier-stat">{i.seen > 0 ? `${i.accuracy.toFixed(0)}%` : 'No data'}</div>
            <div className="ad-metric-sub">{i.seen > 0 ? `${i.correct}/${i.seen} correct` : 'Not attempted yet'}</div>
          </div>

          <div className={`ad-diff-tier-card ${recommended_difficulty === 'ADVANCED' ? 'active' : ''}`}>
            <div className="ad-diff-tier-name">Advanced Tier</div>
            <div className="ad-diff-tier-stat">{a.seen > 0 ? `${a.accuracy.toFixed(0)}%` : 'No data'}</div>
            <div className="ad-metric-sub">{a.seen > 0 ? `${a.correct}/${a.seen} correct` : 'Not attempted yet'}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
