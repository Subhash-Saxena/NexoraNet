import React, { useState } from 'react'
import { Search, Layers } from 'lucide-react'
import { TopicPerformanceCard } from './TopicPerformanceCard'
import type { TopicPerformanceItem } from '../../types'

interface TopicPerformanceGridProps {
  topics: TopicPerformanceItem[]
  onPracticeTopic: (topicId: number) => void
}

type FilterMode = 'ALL' | 'ACTIVE' | 'NEEDS_PRACTICE'

export const TopicPerformanceGrid: React.FC<TopicPerformanceGridProps> = ({
  topics,
  onPracticeTopic,
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterMode, setFilterMode] = useState<FilterMode>('ALL')

  const filteredTopics = topics.filter((t) => {
    // Search query matching
    const matchesSearch =
      t.topic_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.topic_slug.toLowerCase().includes(searchQuery.toLowerCase())
    if (!matchesSearch) return false

    // Filter mode matching
    if (filterMode === 'ACTIVE') {
      return t.questions_answered > 0
    }
    if (filterMode === 'NEEDS_PRACTICE') {
      return t.status === 'NEEDS_PRACTICE'
    }
    return true
  })

  return (
    <div className="ad-topic-section" data-testid="topic-performance-section">
      <div className="ad-section-header">
        <div className="ad-section-title">
          <Layers size={20} color="#38bdf8" />
          Networking Topic Performance
        </div>
      </div>

      <div className="mt-filters-bar" style={{ marginBottom: '1.5rem' }}>
        <div className="mt-search-box">
          <Search size={16} className="mt-search-icon" />
          <input
            type="text"
            className="mt-search-input"
            placeholder="Search networking topics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            data-testid="topic-search-input"
          />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setFilterMode('ALL')}
            className={`mt-filter-btn ${filterMode === 'ALL' ? 'active' : ''}`}
            data-testid="filter-all-topics"
          >
            All Topics ({topics.length})
          </button>
          <button
            onClick={() => setFilterMode('ACTIVE')}
            className={`mt-filter-btn ${filterMode === 'ACTIVE' ? 'active' : ''}`}
            data-testid="filter-active-topics"
          >
            Attempted ({topics.filter((t) => t.questions_answered > 0).length})
          </button>
          <button
            onClick={() => setFilterMode('NEEDS_PRACTICE')}
            className={`mt-filter-btn ${filterMode === 'NEEDS_PRACTICE' ? 'active' : ''}`}
            data-testid="filter-needs-practice-topics"
          >
            Needs Practice ({topics.filter((t) => t.status === 'NEEDS_PRACTICE').length})
          </button>
        </div>
      </div>

      {filteredTopics.length === 0 ? (
        <div
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '0.75rem',
            padding: '2.5rem',
            textAlign: 'center',
            color: '#94a3b8',
          }}
          data-testid="no-topics-found"
        >
          No topics matched your search criteria.
        </div>
      ) : (
        <div className="ad-topic-grid" data-testid="topics-grid">
          {filteredTopics.map((topic) => (
            <TopicPerformanceCard
              key={topic.topic_id}
              topic={topic}
              onPracticeTopic={onPracticeTopic}
            />
          ))}
        </div>
      )}
    </div>
  )
}
