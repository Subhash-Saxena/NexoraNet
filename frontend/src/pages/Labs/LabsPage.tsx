import React, { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Terminal, History, BookOpen, Layers } from 'lucide-react'
import { apiService } from '../../services/api'
import { LabCard } from '../../components/labs/LabCard'
import { LabFilters } from '../../components/labs/LabFilters'
import type { LabBrief, LabTelemetry } from '../../types'
import '../../components/labs/labs.css'

export const LabsPage: React.FC = () => {
  const [labs, setLabs] = useState<LabBrief[]>([])
  const [telemetry, setTelemetry] = useState<LabTelemetry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDifficulty, setSelectedDifficulty] = useState('ALL')
  const [selectedEnvironment, setSelectedEnvironment] = useState('ALL')
  const [selectedStatus, setSelectedStatus] = useState('ALL')

  useEffect(() => {
    let isMounted = true

    const fetchData = async () => {
      try {
        setLoading(true)
        const [labsData, telemetryData] = await Promise.all([
          apiService.getLabs(),
          apiService.getLabTelemetry().catch(() => null),
        ])
        if (isMounted) {
          setLabs(labsData)
          setTelemetry(telemetryData)
          setError(null)
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load labs catalog.')
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    fetchData()
    return () => {
      isMounted = false
    }
  }, [])

  // Filtered labs
  const filteredLabs = useMemo(() => {
    return labs.filter((lab) => {
      // Difficulty filter
      if (selectedDifficulty !== 'ALL' && lab.difficulty.toUpperCase() !== selectedDifficulty) {
        return false
      }

      // Environment filter
      if (selectedEnvironment !== 'ALL' && lab.environment_type.toUpperCase() !== selectedEnvironment) {
        return false
      }

      // Status filter
      if (selectedStatus !== 'ALL') {
        if (lab.user_status !== selectedStatus) return false
      }

      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const matchTitle = lab.title.toLowerCase().includes(q)
        const matchDesc = lab.description ? lab.description.toLowerCase().includes(q) : false
        const matchTopic = lab.topic_title ? lab.topic_title.toLowerCase().includes(q) : false
        if (!matchTitle && !matchDesc && !matchTopic) return false
      }

      return true
    })
  }, [labs, selectedDifficulty, selectedEnvironment, selectedStatus, searchQuery])

  const handleClearFilters = () => {
    setSearchQuery('')
    setSelectedDifficulty('ALL')
    setSelectedEnvironment('ALL')
    setSelectedStatus('ALL')
  }

  return (
    <div className="labs-container">
      {/* Hero Banner */}
      <section className="labs-hero">
        <div className="labs-hero-content">
          <div className="labs-hero-header">
            <div>
              <div className="labs-hero-tagline">
                <Terminal size={16} /> Hands-on Laboratory Engine
              </div>
              <h1 className="labs-hero-title">Interactive Networking Labs</h1>
              <p className="labs-hero-description">
                Put theory into muscle memory. Execute safe terminal commands on your local system,
                explore interactive conceptual drills, inspect network parameters, and validate your
                networking observations.
              </p>
            </div>

            <div className="labs-hero-actions">
              <Link to="/labs/history" className="btn-lab-action btn-lab-secondary">
                <History size={16} /> My Lab History
              </Link>
              <Link to="/learning" className="btn-lab-action btn-lab-secondary">
                <BookOpen size={16} /> Curriculum
              </Link>
            </div>
          </div>

          {/* Telemetry Bar */}
          {telemetry && (
            <div className="labs-telemetry-bar">
              <div className="labs-telemetry-stat">
                <span className="labs-telemetry-label">Available Labs</span>
                <span className="labs-telemetry-val" style={{ color: 'var(--cyan-primary)' }}>
                  {telemetry.total_labs}
                </span>
              </div>

              <div className="labs-telemetry-divider" />

              <div className="labs-telemetry-stat">
                <span className="labs-telemetry-label">Completed</span>
                <span className="labs-telemetry-val" style={{ color: 'var(--emerald-success)' }}>
                  {telemetry.completed_labs}
                </span>
              </div>

              <div className="labs-telemetry-divider" />

              <div className="labs-telemetry-stat">
                <span className="labs-telemetry-label">In Progress</span>
                <span className="labs-telemetry-val" style={{ color: 'var(--amber-warning)' }}>
                  {telemetry.in_progress_labs}
                </span>
              </div>

              <div className="labs-telemetry-divider" />

              <div className="labs-telemetry-stat">
                <span className="labs-telemetry-label">Average Score</span>
                <span className="labs-telemetry-val" style={{ color: 'var(--purple-soc)' }}>
                  {telemetry.average_score}%
                </span>
              </div>

              <div className="labs-telemetry-divider" />

              <div className="labs-telemetry-stat">
                <span className="labs-telemetry-label">Beginner Tier</span>
                <span className="labs-telemetry-val" style={{ fontSize: '1.1rem' }}>
                  {telemetry.beginner_completed} / {telemetry.beginner_total}
                </span>
              </div>

              <div className="labs-telemetry-divider" />

              <div className="labs-telemetry-stat">
                <span className="labs-telemetry-label">Intermediate Tier</span>
                <span className="labs-telemetry-val" style={{ fontSize: '1.1rem' }}>
                  {telemetry.intermediate_completed} / {telemetry.intermediate_total}
                </span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Filters & Search Card */}
      <LabFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedDifficulty={selectedDifficulty}
        onDifficultyChange={setSelectedDifficulty}
        selectedEnvironment={selectedEnvironment}
        onEnvironmentChange={setSelectedEnvironment}
        selectedStatus={selectedStatus}
        onStatusChange={setSelectedStatus}
        onClearAll={handleClearFilters}
        totalResults={filteredLabs.length}
      />

      {/* Error state */}
      {error && (
        <div className="lab-feedback-alert incorrect">
          <div className="lab-feedback-head">Error Loading Labs</div>
          <div className="lab-feedback-msg">{error}</div>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '1.2rem', marginBottom: 8 }}>Loading networking labs...</div>
          <div>Configuring validation engines and step blueprints</div>
        </div>
      ) : filteredLabs.length === 0 ? (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: 48,
            textAlign: 'center',
          }}
        >
          <Layers size={40} color="var(--text-muted)" style={{ margin: '0 auto 16px auto' }} />
          <h3 style={{ fontSize: '1.25rem', marginBottom: 8 }}>No labs match your filter</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
            Try adjusting your search query, difficulty tier, or environment filter.
          </p>
          <button
            type="button"
            className="btn-lab-action btn-lab-secondary"
            onClick={handleClearFilters}
          >
            Reset Filters
          </button>
        </div>
      ) : (
        /* Lab Cards Grid */
        <div className="labs-grid">
          {filteredLabs.map((lab) => (
            <LabCard key={lab.id} lab={lab} />
          ))}
        </div>
      )}
    </div>
  )
}
