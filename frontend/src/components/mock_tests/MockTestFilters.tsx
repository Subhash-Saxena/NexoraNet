import React from 'react'
import { Search } from 'lucide-react'
import type { CatalogTopicItem } from '../../types'

interface MockTestFiltersProps {
  searchQuery: string
  onSearchChange: (q: string) => void
  difficulty: string
  onDifficultyChange: (d: string) => void
  testType: string
  onTestTypeChange: (t: string) => void
  topic?: string
  onTopicChange?: (t: string) => void
  availableTopics?: CatalogTopicItem[]
  durationFilter?: string
  onDurationFilterChange?: (d: string) => void
  statusFilter?: string
  onStatusFilterChange?: (s: string) => void
}

export const MockTestFilters: React.FC<MockTestFiltersProps> = ({
  searchQuery,
  onSearchChange,
  difficulty,
  onDifficultyChange,
  testType,
  onTestTypeChange,
  topic = '',
  onTopicChange,
  availableTopics = [],
  durationFilter = '',
  onDurationFilterChange,
  statusFilter = '',
  onStatusFilterChange,
}) => {
  const difficulties = [
    { label: 'All Levels', value: '' },
    { label: 'Beginner', value: 'BEGINNER' },
    { label: 'Intermediate', value: 'INTERMEDIATE' },
    { label: 'Advanced', value: 'ADVANCED' },
  ]

  const testTypes = [
    { label: 'All Test Types', value: '' },
    { label: 'Full Mock Exams', value: 'FULL_MOCK' },
    { label: 'Comprehensive', value: 'COMPREHENSIVE' },
    { label: 'Topic Focused', value: 'TOPIC' },
    { label: 'Difficulty Track', value: 'DIFFICULTY' },
    { label: 'Practice Sessions', value: 'PRACTICE' },
  ]

  const durations = [
    { label: 'All Durations', value: '' },
    { label: 'Quick (< 20 mins)', value: 'quick' },
    { label: 'Standard (20-45 mins)', value: 'standard' },
    { label: 'Full Mock (45+ mins)', value: 'extended' },
  ]

  const statuses = [
    { label: 'All Statuses', value: '' },
    { label: 'Ready to Attempt', value: 'READY' },
    { label: 'Draft / Pool Shortfall', value: 'DRAFT' },
  ]

  return (
    <div className="mt-filters-bar">
      <div className="mt-search-box">
        <Search size={16} className="mt-search-icon" />
        <input
          type="text"
          className="mt-search-input"
          placeholder="Search mock exams by title, topic, code, or tag..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          data-testid="mock-test-search-input"
        />
      </div>

      <div className="mt-filter-groups">
        {/* Difficulty Pills */}
        <div className="mt-pill-group">
          {difficulties.map((diff) => (
            <button
              key={diff.value}
              type="button"
              className={`mt-pill-btn ${difficulty === diff.value ? 'active' : ''}`}
              onClick={() => onDifficultyChange(diff.value)}
              data-testid={`filter-diff-${diff.value || 'all'}`}
            >
              {diff.label}
            </button>
          ))}
        </div>

        {/* Test Type Select */}
        <select
          className="mt-select-input"
          value={testType}
          onChange={(e) => onTestTypeChange(e.target.value)}
          data-testid="filter-test-type"
        >
          {testTypes.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>

        {/* Topic Filter Select */}
        {availableTopics.length > 0 && onTopicChange && (
          <select
            className="mt-select-input"
            value={topic}
            onChange={(e) => onTopicChange(e.target.value)}
            data-testid="filter-topic"
          >
            <option value="">All Topics ({availableTopics.length})</option>
            {availableTopics.map((top) => (
              <option key={top.topic_id} value={top.topic_slug}>
                {top.topic_title} ({top.test_count})
              </option>
            ))}
          </select>
        )}

        {/* Duration Select */}
        {onDurationFilterChange && (
          <select
            className="mt-select-input"
            value={durationFilter}
            onChange={(e) => onDurationFilterChange(e.target.value)}
            data-testid="filter-duration"
          >
            {durations.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        )}

        {/* Status Select */}
        {onStatusFilterChange && (
          <select
            className="mt-select-input"
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            data-testid="filter-status"
          >
            {statuses.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  )
}
