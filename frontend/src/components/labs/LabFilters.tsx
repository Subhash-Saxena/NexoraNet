import React from 'react'
import { Search, X } from 'lucide-react'

interface LabFiltersProps {
  searchQuery: string
  onSearchChange: (q: string) => void
  selectedDifficulty: string
  onDifficultyChange: (diff: string) => void
  selectedEnvironment: string
  onEnvironmentChange: (env: string) => void
  selectedStatus: string
  onStatusChange: (status: string) => void
  onClearAll: () => void
  totalResults: number
}

export const LabFilters: React.FC<LabFiltersProps> = ({
  searchQuery,
  onSearchChange,
  selectedDifficulty,
  onDifficultyChange,
  selectedEnvironment,
  onEnvironmentChange,
  selectedStatus,
  onStatusChange,
  onClearAll,
  totalResults,
}) => {
  const difficulties = [
    { label: 'All Levels', value: 'ALL' },
    { label: 'Beginner', value: 'BEGINNER' },
    { label: 'Intermediate', value: 'INTERMEDIATE' },
    { label: 'Advanced', value: 'ADVANCED' },
  ]

  const environments = [
    { label: 'All Environments', value: 'ALL' },
    { label: 'Local Terminal', value: 'LOCAL_SYSTEM' },
    { label: 'Interactive Theory', value: 'CONCEPTUAL' },
  ]

  const statuses = [
    { label: 'All Statuses', value: 'ALL' },
    { label: 'Completed', value: 'COMPLETED' },
    { label: 'In Progress', value: 'IN_PROGRESS' },
    { label: 'Not Started', value: 'NOT_STARTED' },
  ]

  const hasActiveFilters =
    searchQuery.trim() !== '' ||
    selectedDifficulty !== 'ALL' ||
    selectedEnvironment !== 'ALL' ||
    selectedStatus !== 'ALL'

  return (
    <div className="labs-controls-card">
      <div className="labs-search-row">
        <div className="labs-search-wrapper">
          <Search size={18} className="labs-search-icon" />
          <input
            type="text"
            className="labs-search-input"
            placeholder="Search labs by command, skill, or protocol (e.g. ping, subnet, arp, dns)..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        {hasActiveFilters && (
          <button
            type="button"
            className="btn-lab-action btn-lab-secondary"
            onClick={onClearAll}
            title="Clear all filters"
          >
            <X size={14} /> Clear Filters
          </button>
        )}
      </div>

      <div className="labs-filter-row">
        <div className="labs-filter-group">
          <span className="labs-filter-label">Difficulty:</span>
          <div className="labs-filter-pills">
            {difficulties.map((d) => (
              <button
                key={d.value}
                type="button"
                className={`labs-filter-pill ${selectedDifficulty === d.value ? 'active' : ''}`}
                onClick={() => onDifficultyChange(d.value)}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>

        <div className="labs-filter-group">
          <span className="labs-filter-label">Environment:</span>
          <select
            className="labs-select"
            value={selectedEnvironment}
            onChange={(e) => onEnvironmentChange(e.target.value)}
          >
            {environments.map((e) => (
              <option key={e.value} value={e.value}>
                {e.label}
              </option>
            ))}
          </select>
        </div>

        <div className="labs-filter-group">
          <span className="labs-filter-label">Status:</span>
          <select
            className="labs-select"
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
          >
            {statuses.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Showing <strong>{totalResults}</strong> labs
        </div>
      </div>
    </div>
  )
}
