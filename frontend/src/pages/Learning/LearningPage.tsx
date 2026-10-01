import React, { useEffect, useState, useTransition } from 'react'
import { Link } from 'react-router-dom'
import {
  BookOpen,
  Search,
  CheckCircle2,
  ArrowRight,
  Bookmark,
  ChevronDown,
  ChevronRight,
  Layers,
} from 'lucide-react'
import { apiService } from '../../services/api'
import { LearningRoadmap } from '../../components/learning/LearningRoadmap'
import { DiagramContainer } from '../../components/learning/diagrams/DiagramContainer'
import type {
  CourseDetail,
  LearningProgressResponse,
  LearningSearchResponse,
} from '../../types'
import '../../components/learning/learning.css'

export const LearningPage: React.FC = () => {
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [progress, setProgress] = useState<LearningProgressResponse | null>(null)
  const [activeTab, setActiveTab] = useState<'curriculum' | 'diagrams'>('curriculum')
  const [expandedModuleId, setExpandedModuleId] = useState<number | null>(1)
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL')

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<LearningSearchResponse | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [, startTransition] = useTransition()

  useEffect(() => {
    // Fetch live course details & progress telemetry
    apiService
      .getCourse('networking-cybersecurity')
      .then((data) => setCourse(data))
      .catch(() => setCourse(null))

    apiService
      .getLearningProgress()
      .then((data) => setProgress(data))
      .catch(() => setProgress(null))
  }, [])

  const handleSearchChange = (val: string) => {
    setSearchQuery(val)
    if (!val.trim() || val.length < 2) {
      setSearchResults(null)
      setIsSearching(false)
    }
  }

  // Live search handler
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      return
    }

    const timer = setTimeout(() => {
      setIsSearching(true)
      apiService
        .searchCurriculum({ q: searchQuery })
        .then((res) => {
          startTransition(() => {
            setSearchResults(res)
            setIsSearching(false)
          })
        })
        .catch(() => {
          setIsSearching(false)
        })
    }, 250)

    return () => clearTimeout(timer)
  }, [searchQuery])

  const filteredModules = course?.modules
    ? selectedDifficulty === 'ALL'
      ? course.modules
      : course.modules.filter((m) => m.difficulty === selectedDifficulty)
    : []

  return (
    <div className="learning-container">
      {/* 1. Learning Hero Banner */}
      <div className="learning-hero">
        <div className="learning-hero-content">
          <div className="learning-hero-header">
            <div>
              <div className="learning-hero-tagline">NexoraNet Academy &bull; Step 3 Active</div>
              <h1 className="learning-hero-title">Structured Networking Curriculum</h1>
              <p className="learning-hero-description">
                From foundational physical bits and encapsulation to enterprise routing, packet forensics, and intrusion detection.
                Every topic connects directly to realistic protocols, offensive exploit vectors, and blue-team cyber defense.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <Link
                to="/learning/bookmarks"
                className="diagram-btn"
                style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-main)', textDecoration: 'none' }}
              >
                <Bookmark size={15} color="var(--cyan-primary)" />
                <span>Saved Bookmarks</span>
              </Link>
            </div>
          </div>

          {/* Progress Telemetry */}
          {progress && (
            <div className="progress-telemetry-bar">
              <div className="telemetry-stat">
                <span className="telemetry-label">Current Level</span>
                <span className="telemetry-value" style={{ color: 'var(--cyan-primary)' }}>
                  {progress.current_level}
                </span>
              </div>

              <div className="telemetry-stat">
                <span className="telemetry-label">Completed Lessons</span>
                <span className="telemetry-value" style={{ color: 'var(--emerald-success)' }}>
                  {progress.completed_lessons} / {progress.total_lessons}
                </span>
              </div>

              <div className="telemetry-stat">
                <span className="telemetry-label">Remaining</span>
                <span className="telemetry-value" style={{ color: '#cbd5e1' }}>
                  {progress.remaining_lessons}
                </span>
              </div>

              <div className="telemetry-progress-track">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.74rem' }}>
                  <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>OVERALL COMPLETION</span>
                  <span style={{ color: 'var(--emerald-success)', fontWeight: 700 }}>
                    {progress.overall_percentage}%
                  </span>
                </div>
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill" style={{ width: `${progress.overall_percentage}%` }} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Continue Learning Resolver */}
      {progress?.continue_learning && (
        <div className="continue-card">
          <div className="continue-card-info">
            <div className="continue-icon-box">
              <BookOpen size={24} />
            </div>
            <div>
              <span className="badge badge-ready" style={{ fontSize: '0.7rem' }}>
                Continue Learning &bull; {progress.continue_learning.module_title}
              </span>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
                {progress.continue_learning.lesson_title}
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                Topic: <strong>{progress.continue_learning.topic_title}</strong> &bull; Lesson {progress.continue_learning.lesson_index} of {progress.continue_learning.total_topic_lessons} ({progress.continue_learning.estimated_minutes} min)
              </p>
            </div>
          </div>

          <Link
            to={`/learning/lessons/${progress.continue_learning.lesson_slug}`}
            className="diagram-btn primary"
            style={{ padding: '12px 24px', textDecoration: 'none', flexShrink: 0 }}
          >
            <span>Resume Lesson</span>
            <ArrowRight size={16} />
          </Link>
        </div>
      )}

      {/* 3. Search & Discovery Bar */}
      <div className="search-container">
        <div className="search-input-box">
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search lessons, topics, protocols (e.g. TCP Handshake, OSPF, Subnetting, ARP, DNSSEC)..."
            value={searchQuery}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
          {isSearching && <span style={{ fontSize: '0.78rem', color: 'var(--cyan-primary)' }}>Searching...</span>}
        </div>

        {/* Search Results Dropdown */}
        {searchResults && (
          <div className="search-dropdown">
            <div style={{ padding: '8px 16px', fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
              Found {searchResults.total_results} matching curriculum resources
            </div>
            {searchResults.results.length === 0 ? (
              <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.86rem' }}>
                No curriculum items found matching "{searchQuery}"
              </div>
            ) : (
              searchResults.results.map((res, idx) => (
                <Link
                  key={idx}
                  to={res.url}
                  className="search-result-row"
                  onClick={() => setSearchQuery('')}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="badge badge-ready" style={{ fontSize: '0.65rem' }}>
                        {res.type.toUpperCase()}
                      </span>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-main)' }}>
                        {res.title}
                      </span>
                    </div>
                    {res.parent_title && (
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        In: {res.parent_title}
                      </div>
                    )}
                  </div>
                  <span className="badge badge-phase" style={{ fontSize: '0.68rem' }}>
                    {res.difficulty}
                  </span>
                </Link>
              ))
            )}
          </div>
        )}
      </div>

      {/* 4. Three Level Pillars (Beginner, Intermediate, Advanced) */}
      <div className="level-cards-grid">
        {/* Beginner Card */}
        <div className="level-card beginner">
          <div>
            <div className="level-card-header">
              <span className="badge badge-ready" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--emerald-success)' }}>
                LEVEL 1
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {progress?.beginner_progress.completed_lessons || 0} / {progress?.beginner_progress.total_lessons || 16} lessons
              </span>
            </div>
            <h3 className="level-card-title">Beginner Track</h3>
            <p className="level-card-tagline">
              "Build your networking foundation." Master physical frames, OSI layer models, IPv4 addressing, and core transport handshakes.
            </p>
          </div>
          <div className="level-card-progress">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Foundations Progress</span>
              <span style={{ color: 'var(--emerald-success)', fontWeight: 700 }}>
                {progress?.beginner_progress.percentage || 0}%
              </span>
            </div>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress?.beginner_progress.percentage || 0}%`, background: 'var(--emerald-success)' }}
              />
            </div>
          </div>
        </div>

        {/* Intermediate Card */}
        <div className="level-card intermediate">
          <div>
            <div className="level-card-header">
              <span className="badge badge-ready" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--cyan-primary)' }}>
                LEVEL 2
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {progress?.intermediate_progress.completed_lessons || 0} / {progress?.intermediate_progress.total_lessons || 12} lessons
              </span>
            </div>
            <h3 className="level-card-title">Intermediate Track</h3>
            <p className="level-card-tagline">
              "Understand how networks communicate and troubleshoot real traffic." Subnetting, dynamic routing protocols, DNS/DHCP, and TLS 1.3.
            </p>
          </div>
          <div className="level-card-progress">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Systems Progress</span>
              <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>
                {progress?.intermediate_progress.percentage || 0}%
              </span>
            </div>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress?.intermediate_progress.percentage || 0}%`, background: 'var(--cyan-primary)' }}
              />
            </div>
          </div>
        </div>

        {/* Advanced Card */}
        <div className="level-card advanced">
          <div>
            <div className="level-card-header">
              <span className="badge badge-ready" style={{ background: 'rgba(139, 92, 246, 0.15)', color: 'var(--purple-soc)' }}>
                LEVEL 3
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {progress?.advanced_progress.completed_lessons || 0} / {progress?.advanced_progress.total_lessons || 8} lessons
              </span>
            </div>
            <h3 className="level-card-title">Advanced Defense</h3>
            <p className="level-card-tagline">
              "Analyze network behavior and apply security concepts." Deep packet analysis, IDS rule engineering, flow telemetries, and SOC triage.
            </p>
          </div>
          <div className="level-card-progress">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Security Progress</span>
              <span style={{ color: 'var(--purple-soc)', fontWeight: 700 }}>
                {progress?.advanced_progress.percentage || 0}%
              </span>
            </div>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress?.advanced_progress.percentage || 0}%`, background: 'var(--purple-soc)' }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* 5. Interactive Learning Roadmap */}
      <LearningRoadmap />

      {/* 6. Tabs: Curriculum Browser vs Interactive Diagrams */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
        <button
          onClick={() => setActiveTab('curriculum')}
          className={`diagram-btn ${activeTab === 'curriculum' ? 'primary' : ''}`}
          style={{ padding: '10px 20px', borderRadius: 'var(--radius-sm)' }}
        >
          <BookOpen size={16} />
          <span>Curriculum Modules & Lessons ({course?.modules.length || 19})</span>
        </button>

        <button
          onClick={() => setActiveTab('diagrams')}
          className={`diagram-btn ${activeTab === 'diagrams' ? 'primary' : ''}`}
          style={{ padding: '10px 20px', borderRadius: 'var(--radius-sm)' }}
        >
          <Layers size={16} />
          <span>Interactive Visual Protocol Diagrams</span>
        </button>
      </div>

      {activeTab === 'diagrams' ? (
        <div style={{ marginTop: '12px' }}>
          <DiagramContainer allowSwitching={true} />
        </div>
      ) : (
        /* Curriculum Browser */
        <div style={{ marginTop: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Comprehensive Syllabus Explorer
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
                Select any module to inspect structured topics, objectives, and begin reading lessons.
              </p>
            </div>

            {/* Filter buttons */}
            <div style={{ display: 'flex', gap: '6px' }}>
              {['ALL', 'BEGINNER', 'INTERMEDIATE', 'ADVANCED'].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setSelectedDifficulty(lvl)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    border: '1px solid',
                    cursor: 'pointer',
                    background: selectedDifficulty === lvl ? 'var(--cyan-primary)' : 'rgba(255, 255, 255, 0.04)',
                    color: selectedDifficulty === lvl ? '#020617' : 'var(--text-secondary)',
                    borderColor: selectedDifficulty === lvl ? 'var(--cyan-primary)' : 'var(--border-color)',
                  }}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Module Accordions */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {filteredModules.map((mod) => {
              const isExpanded = expandedModuleId === mod.id
              const topics = mod.topics || []

              return (
                <div
                  key={mod.id}
                  style={{
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-card)',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    onClick={() => setExpandedModuleId(isExpanded ? null : mod.id)}
                    style={{
                      padding: '16px 20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      background: isExpanded ? 'rgba(6, 182, 212, 0.05)' : 'transparent',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      {isExpanded ? <ChevronDown size={18} color="var(--cyan-primary)" /> : <ChevronRight size={18} />}
                      <span style={{ fontWeight: 700, fontSize: '0.94rem', color: 'var(--text-main)' }}>
                        Module {mod.order_index}: {mod.title}
                      </span>
                      <span
                        className="badge"
                        style={{
                          fontSize: '0.68rem',
                          background:
                            mod.difficulty === 'BEGINNER'
                              ? 'rgba(16, 185, 129, 0.15)'
                              : mod.difficulty === 'INTERMEDIATE'
                              ? 'rgba(6, 182, 212, 0.15)'
                              : 'rgba(139, 92, 246, 0.15)',
                          color:
                            mod.difficulty === 'BEGINNER'
                              ? 'var(--emerald-success)'
                              : mod.difficulty === 'INTERMEDIATE'
                              ? 'var(--cyan-primary)'
                              : 'var(--purple-soc)',
                        }}
                      >
                        {mod.difficulty}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {topics.length} topics
                      </span>
                    </div>
                  </div>

                  {isExpanded && (
                    <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(0, 0, 0, 0.15)' }}>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
                        {mod.description}
                      </p>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                        {topics.map((t) => (
                          <Link
                            key={t.id}
                            to={`/learning/topics/${t.slug}`}
                            style={{
                              padding: '12px 16px',
                              borderRadius: 'var(--radius-sm)',
                              background: 'rgba(255, 255, 255, 0.02)',
                              border: '1px solid var(--border-color)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              textDecoration: 'none',
                              transition: 'all 0.15s ease',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <CheckCircle2 size={16} color="var(--cyan-primary)" style={{ flexShrink: 0 }} />
                              <div>
                                <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)' }}>
                                  {t.title}
                                </div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                  Topic #{t.order_index}
                                </div>
                              </div>
                            </div>
                            <ChevronRight size={16} color="var(--text-muted)" />
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
