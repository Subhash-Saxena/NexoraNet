import React, { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  FileCheck2,
  History,
  Sparkles,
  AlertCircle,
  CheckCircle,
  HelpCircle,
  Clock,
  Layers,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type {
  CatalogCategoryItem,
  CatalogStatisticsResponse,
  CatalogTopicItem,
  MockTestBrief,
  TestBlueprintResponse,
} from '../../types'
import { MockTestCard } from '../../components/mock_tests/MockTestCard'
import { MockTestCategoryTabs } from '../../components/mock_tests/MockTestCategoryTabs'
import { MockTestFilters } from '../../components/mock_tests/MockTestFilters'
import '../../components/mock_tests/mock_tests.css'

export const MockTestsPage: React.FC = () => {
  const [mockTests, setMockTests] = useState<MockTestBrief[]>([])
  const [categories, setCategories] = useState<CatalogCategoryItem[]>([])
  const [topics, setTopics] = useState<CatalogTopicItem[]>([])
  const [statistics, setStatistics] = useState<CatalogStatisticsResponse | null>(null)
  const [blueprints, setBlueprints] = useState<TestBlueprintResponse[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Filters state
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [difficulty, setDifficulty] = useState<string>('')
  const [testType, setTestType] = useState<string>('')
  const [selectedTopic, setSelectedTopic] = useState<string>('')
  const [durationFilter, setDurationFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const loadData = () => {
    setIsLoading(true)
    setError(null)

    Promise.all([
      apiService.getMockTests(),
      apiService.getCatalogCategories ? apiService.getCatalogCategories().catch(() => []) : Promise.resolve([]),
      apiService.getCatalogTopics ? apiService.getCatalogTopics().catch(() => []) : Promise.resolve([]),
      apiService.getCatalogStatistics ? apiService.getCatalogStatistics().catch(() => null) : Promise.resolve(null),
      apiService.getTestBlueprints ? apiService.getTestBlueprints().catch(() => []) : Promise.resolve([]),
    ])
      .then(([tests, cats, tops, stats, bps]) => {
        setMockTests(tests)
        setCategories(cats)
        setTopics(tops)
        setStatistics(stats)
        setBlueprints(bps)
      })
      .catch((err) => {
        setError(err.message || 'Failed to load examinations catalog.')
      })
      .finally(() => {
        setIsLoading(false)
      })
  }

  useEffect(() => {
    loadData()
  }, [])

  // In-memory multi-attribute filtering
  const filteredTests = useMemo(() => {
    return mockTests.filter((test) => {
      // 1. Category Filter
      if (activeCategory !== 'all') {
        if (activeCategory === 'recommended') {
          // Curated non-adaptive practice: Beginner or unattempted ready tests
          if (
            test.status !== 'PUBLISHED' ||
            (test.difficulty !== 'BEGINNER' && test.difficulty !== 'MIXED')
          ) {
            return false
          }
        } else if (activeCategory === 'beginner') {
          if (test.difficulty !== 'BEGINNER') return false
        } else if (activeCategory === 'intermediate') {
          if (test.difficulty !== 'INTERMEDIATE') return false
        } else if (activeCategory === 'advanced') {
          if (test.difficulty !== 'ADVANCED') return false
        } else if (activeCategory === 'comprehensive') {
          if (test.test_type !== 'COMPREHENSIVE' && test.test_type !== 'MIXED') return false
        } else if (activeCategory === 'full_mocks') {
          if (test.test_type !== 'FULL_MOCK') return false
        }
      }

      // 2. Difficulty Filter
      if (difficulty && test.difficulty.toUpperCase() !== difficulty.toUpperCase()) {
        return false
      }

      // 3. Test Type Filter
      if (testType && test.test_type !== testType) {
        return false
      }

      // 4. Topic Filter
      if (selectedTopic) {
        const topicNorm = selectedTopic.toLowerCase()
        const hasTopic = test.topics_covered?.some(
          (t) =>
            t.toLowerCase().replace(/[^a-z0-9]/g, '-') === topicNorm ||
            t.toLowerCase().includes(topicNorm)
        )
        if (!hasTopic) return false
      }

      // 5. Duration Filter
      if (durationFilter === 'quick' && test.duration_minutes > 20) return false
      if (
        durationFilter === 'standard' &&
        (test.duration_minutes <= 20 || test.duration_minutes > 45)
      )
        return false
      if (durationFilter === 'extended' && test.duration_minutes <= 45) return false

      // 6. Status Filter
      if (statusFilter === 'READY') {
        if (test.status !== 'PUBLISHED' || test.is_ready === false) return false
      } else if (statusFilter === 'DRAFT') {
        if (test.status === 'PUBLISHED' && test.is_ready !== false) return false
      }

      // 7. Search Query Filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase()
        const matchTitle = test.title.toLowerCase().includes(query)
        const matchDesc = test.description?.toLowerCase().includes(query) ?? false
        const matchCode = test.code?.toLowerCase().includes(query) ?? false
        const matchTopic =
          test.topics_covered?.some((t) => t.toLowerCase().includes(query)) ?? false
        const matchTag = test.tags?.some((t) => t.toLowerCase().includes(query)) ?? false

        if (!matchTitle && !matchDesc && !matchCode && !matchTopic && !matchTag) {
          return false
        }
      }

      return true
    })
  }, [
    mockTests,
    activeCategory,
    difficulty,
    testType,
    selectedTopic,
    durationFilter,
    statusFilter,
    searchQuery,
  ])

  return (
    <div className="mt-container" data-testid="mock-tests-page">
      {/* Header */}
      <div className="mt-header">
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
          }}
        >
          <div>
            <h1 className="mt-header-title">
              <FileCheck2 size={32} style={{ color: '#38bdf8' }} />
              Mock Test Library & Examination Catalog
            </h1>
            <p className="mt-header-desc">
              Browse 46 structured networking and cybersecurity assessments. From beginner OSI
              mechanics to advanced packet analysis and full 60-minute certification simulations.
            </p>
          </div>

          <Link
            to="/mock-tests/history"
            className="mt-btn mt-btn-secondary"
            data-testid="view-history-btn"
          >
            <History size={16} />
            My Attempt History
          </Link>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="mt-stat-grid" data-testid="catalog-statistics">
          <div className="mt-stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} style={{ color: '#38bdf8' }} />
              <span className="mt-stat-val">{statistics.total_tests}</span>
            </div>
            <span className="mt-stat-label">Total Examinations</span>
          </div>

          <div className="mt-stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle size={18} style={{ color: '#34d399' }} />
              <span className="mt-stat-val" style={{ color: '#34d399' }}>
                {statistics.ready_tests}
              </span>
            </div>
            <span className="mt-stat-label">Ready to Attempt</span>
          </div>

          <div className="mt-stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={18} style={{ color: '#a855f7' }} />
              <span className="mt-stat-val">{statistics.full_mock_tests}</span>
            </div>
            <span className="mt-stat-label">Full Mock Exams</span>
          </div>

          <div className="mt-stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <HelpCircle size={18} style={{ color: '#fbbf24' }} />
              <span className="mt-stat-val">{statistics.total_questions_represented}</span>
            </div>
            <span className="mt-stat-label">Questions Represented</span>
          </div>
        </div>
      )}

      {/* Category Tabs */}
      {categories.length > 0 && (
        <MockTestCategoryTabs
          categories={categories}
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
        />
      )}

      {/* Filter and Search Bar */}
      <MockTestFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        difficulty={difficulty}
        onDifficultyChange={setDifficulty}
        testType={testType}
        onTestTypeChange={setTestType}
        topic={selectedTopic}
        onTopicChange={setSelectedTopic}
        availableTopics={topics}
        durationFilter={durationFilter}
        onDurationFilterChange={setDurationFilter}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
      />

      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid #ef4444',
            borderRadius: '0.5rem',
            padding: '1rem',
            marginBottom: '2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#f87171',
          }}
        >
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Recommended Track banner on recommended category */}
      {activeCategory === 'recommended' && (
        <div
          style={{
            marginBottom: '1.5rem',
            background: 'rgba(56, 189, 248, 0.08)',
            border: '1px solid rgba(56, 189, 248, 0.25)',
            borderRadius: '0.75rem',
            padding: '1rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <Sparkles size={20} style={{ color: '#38bdf8' }} />
          <div>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Recommended Foundational Track
            </h3>
            <p style={{ fontSize: '0.8125rem', color: '#94a3b8', margin: '0.25rem 0 0' }}>
              Hand-picked practice assessments to build mastery across OSI layers, IPv4 addressing, and standard protocols.
            </p>
          </div>
        </div>
      )}

      {/* Catalog Grid Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1rem',
        }}
      >
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
          {activeCategory === 'all'
            ? 'All Catalog Tests'
            : categories.find((c) => c.key === activeCategory)?.title || 'Tests'}{' '}
          <span style={{ fontSize: '0.875rem', color: '#94a3b8', fontWeight: 400 }}>
            ({filteredTests.length} available)
          </span>
        </h2>
      </div>

      {/* Loading & Grid */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '4rem 1rem', color: '#94a3b8' }}>
          <div
            style={{
              display: 'inline-block',
              width: '2rem',
              height: '2rem',
              border: '3px solid #334155',
              borderTopColor: '#38bdf8',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          />
          <p style={{ marginTop: '1rem' }}>Loading examination catalog...</p>
        </div>
      ) : filteredTests.length === 0 ? (
        <div
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '0.75rem',
            padding: '3rem 1.5rem',
            textAlign: 'center',
          }}
        >
          <FileCheck2 size={48} style={{ color: '#64748b', margin: '0 auto 1rem' }} />
          <h3 style={{ color: '#f8fafc', fontSize: '1.125rem', marginBottom: '0.5rem' }}>
            No examinations matched your filters
          </h3>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Try broadening your search term or clearing the difficulty/type/duration filters.
          </p>
          <button
            type="button"
            className="mt-btn mt-btn-secondary"
            onClick={() => {
              setActiveCategory('all')
              setSearchQuery('')
              setDifficulty('')
              setTestType('')
              setSelectedTopic('')
              setDurationFilter('')
              setStatusFilter('')
            }}
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="mt-grid" data-testid="mock-tests-grid">
          {filteredTests.map((test) => (
            <MockTestCard key={test.id} test={test} />
          ))}
        </div>
      )}

      {/* Blueprint Architecture Banner */}
      {blueprints.length > 0 && (
        <div
          style={{
            marginTop: '3rem',
            background:
              'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)',
            border: '1px solid #334155',
            borderRadius: '0.75rem',
            padding: '1.5rem 2rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              marginBottom: '0.5rem',
            }}
          >
            <Sparkles size={20} style={{ color: '#38bdf8' }} />
            <h3
              style={{
                color: '#f8fafc',
                fontSize: '1.125rem',
                fontWeight: 600,
                margin: 0,
              }}
            >
              Algorithmic Blueprint Test Generation Engine
            </h3>
          </div>
          <p
            style={{
              color: '#94a3b8',
              fontSize: '0.875rem',
              maxWidth: '48rem',
              margin: '0 0 1rem 0',
              lineHeight: 1.5,
            }}
          >
            NexoraNet links modular test blueprints directly to our 531-question bank.
            Every test sitting guarantees strict topic distribution, cognitive balance, and
            uncompromised exam integrity.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
            {blueprints.slice(0, 10).map((bp) => (
              <span
                key={bp.id}
                style={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '0.375rem',
                  padding: '0.35rem 0.75rem',
                  fontSize: '0.8125rem',
                  color: '#cbd5e1',
                }}
              >
                {bp.title} ({bp.total_questions} Qs, {bp.duration_minutes}m)
              </span>
            ))}
            {blueprints.length > 10 && (
              <span
                style={{
                  background: 'transparent',
                  padding: '0.35rem 0.5rem',
                  fontSize: '0.8125rem',
                  color: '#64748b',
                }}
              >
                +{blueprints.length - 10} more blueprints
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
