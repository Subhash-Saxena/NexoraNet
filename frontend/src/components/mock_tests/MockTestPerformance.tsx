import React from 'react'
import type { DifficultyPerformanceResponse, TopicPerformanceResponse } from '../../types'

interface MockTestPerformanceProps {
  topicBreakdown: TopicPerformanceResponse[]
  difficultyBreakdown: DifficultyPerformanceResponse[]
}

export const MockTestPerformance: React.FC<MockTestPerformanceProps> = ({
  topicBreakdown,
  difficultyBreakdown,
}) => {
  const getFillClass = (pct: number) => {
    if (pct >= 75) return 'mt-fill-emerald'
    if (pct >= 50) return 'mt-fill-amber'
    return 'mt-fill-rose'
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
      {/* Topic Performance */}
      <div className="mt-breakdown-card" data-testid="topic-performance-breakdown">
        <h3 className="mt-breakdown-header">Topic Mastery Breakdown</h3>
        {topicBreakdown.length === 0 ? (
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>No topic distribution data recorded.</p>
        ) : (
          topicBreakdown.map((t) => (
            <div key={t.topic_id} className="mt-breakdown-item">
              <div className="mt-breakdown-label-row">
                <span style={{ fontWeight: 500 }}>{t.topic_title}</span>
                <span style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                  {t.correct_questions} / {t.total_questions} ({Math.round(t.percentage)}%)
                </span>
              </div>
              <div className="mt-progress-track">
                <div
                  className={`mt-progress-fill ${getFillClass(t.percentage)}`}
                  style={{ width: `${Math.max(0, Math.min(100, t.percentage))}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Difficulty Performance */}
      <div className="mt-breakdown-card" data-testid="difficulty-performance-breakdown">
        <h3 className="mt-breakdown-header">Difficulty Performance</h3>
        {difficultyBreakdown.length === 0 ? (
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>No difficulty breakdown data recorded.</p>
        ) : (
          difficultyBreakdown.map((d) => (
            <div key={d.difficulty} className="mt-breakdown-item">
              <div className="mt-breakdown-label-row">
                <span style={{ fontWeight: 500 }}>{d.difficulty}</span>
                <span style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                  {d.correct_questions} / {d.total_questions} ({Math.round(d.percentage)}%)
                </span>
              </div>
              <div className="mt-progress-track">
                <div
                  className={`mt-progress-fill ${getFillClass(d.percentage)}`}
                  style={{ width: `${Math.max(0, Math.min(100, d.percentage))}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
