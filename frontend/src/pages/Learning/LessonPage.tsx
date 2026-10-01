import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Clock,
  CheckCircle2,
  Bookmark,
  BookmarkCheck,
  Layers,
} from 'lucide-react'
import { apiService } from '../../services/api'
import { MarkdownContent } from '../../components/learning/MarkdownContent'
import { LessonNavigation } from '../../components/learning/LessonNavigation'
import { UpNextCard } from '../../components/learning/UpNextCard'
import { DiagramContainer } from '../../components/learning/diagrams/DiagramContainer'
import type { LessonDetailExtended } from '../../types'
import '../../components/learning/learning.css'

export const LessonPage: React.FC = () => {
  const { lessonSlug } = useParams<{ lessonSlug: string }>()
  const [lesson, setLesson] = useState<LessonDetailExtended | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCompleting, setIsCompleting] = useState(false)
  const [showDiagramExplorer, setShowDiagramExplorer] = useState(false)

  useEffect(() => {
    if (!lessonSlug) return
    let active = true
    window.scrollTo({ top: 0, behavior: 'smooth' })

    apiService
      .getLesson(lessonSlug)
      .then((data) => {
        if (!active) return
        setLesson(data)
        setLoading(false)

        // If lesson was NOT_STARTED, mark it started
        if (data.status === 'NOT_STARTED') {
          apiService.startLesson(data.id).catch(() => {})
        }
      })
      .catch((err) => {
        if (!active) return
        setError(err.message || 'Failed to load lesson')
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [lessonSlug])

  const handleMarkComplete = async () => {
    if (!lesson || lesson.status === 'COMPLETED' || isCompleting) return
    setIsCompleting(true)
    try {
      const res = await apiService.completeLesson(lesson.id)
      setLesson({
        ...lesson,
        status: res.status,
        completed_at: res.updated_at,
      })
    } catch {
      // silently handle
    } finally {
      setIsCompleting(false)
    }
  }

  const handleToggleBookmark = async () => {
    if (!lesson) return
    try {
      if (lesson.is_bookmarked) {
        await apiService.unbookmarkLesson(lesson.id)
        setLesson({ ...lesson, is_bookmarked: false })
      } else {
        await apiService.bookmarkLesson(lesson.id)
        setLesson({ ...lesson, is_bookmarked: true })
      }
    } catch {
      // silently handle
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading lesson content and diagrams...
      </div>
    )
  }

  if (error || !lesson) {
    const isAuthError = error && (error.includes('401') || error.toLowerCase().includes('unauthorized'))
    return (
      <div style={{ padding: '60px', textAlign: 'center' }}>
        <h3 style={{ color: isAuthError ? '#38bdf8' : 'var(--rose-danger)', marginBottom: '8px' }}>
          {isAuthError ? 'Sign In Required' : 'Lesson Not Found'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px', maxWidth: '450px', margin: '0 auto 16px' }}>
          {isAuthError
            ? 'Sign in to access interactive curriculum lessons, track progress, and take hands-on lab challenges.'
            : error || 'Unable to load lesson.'}
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          {isAuthError && (
            <Link to="/login" className="diagram-btn primary">
              Sign In to Continue
            </Link>
          )}
          <Link to="/learning" className="diagram-btn secondary">
            Back to Curriculum
          </Link>
        </div>
      </div>
    )
  }

  // Detect relevant initial diagram
  const getRelevantDiagram = (): 'osi_stack' | 'tcp_handshake' | 'dns_resolution' | 'dhcp_sequence' | 'encapsulation' => {
    const slug = lesson.slug.toLowerCase()
    if (slug.includes('osi') || slug.includes('layer')) return 'osi_stack'
    if (slug.includes('tcp') || slug.includes('handshake')) return 'tcp_handshake'
    if (slug.includes('dns')) return 'dns_resolution'
    if (slug.includes('dhcp') || slug.includes('dora')) return 'dhcp_sequence'
    if (slug.includes('encapsulation') || slug.includes('frame') || slug.includes('packet')) return 'encapsulation'
    return 'osi_stack'
  }

  const isCompleted = lesson.status === 'COMPLETED'

  return (
    <div className="learning-container">
      {/* Sticky Lesson Reading Pane Header */}
      <div className="lesson-meta-bar">
        <div className="lesson-breadcrumbs">
          <Link to="/learning">Curriculum</Link>
          <span>/</span>
          <Link to={`/learning/topics/${lesson.topic_slug}`}>{lesson.topic_title}</Link>
          <span>/</span>
          <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>Lesson #{lesson.order_index}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => setShowDiagramExplorer(!showDiagramExplorer)}
            className={`diagram-btn ${showDiagramExplorer ? 'primary' : ''}`}
            title="Toggle interactive protocol diagrams"
          >
            <Layers size={15} />
            <span>{showDiagramExplorer ? 'Hide Diagrams' : 'Protocol Visualizer'}</span>
          </button>

          <button
            onClick={handleToggleBookmark}
            className="diagram-btn"
            title={lesson.is_bookmarked ? 'Remove bookmark' : 'Bookmark lesson'}
          >
            {lesson.is_bookmarked ? (
              <BookmarkCheck size={16} color="var(--emerald-success)" />
            ) : (
              <Bookmark size={16} />
            )}
            <span>{lesson.is_bookmarked ? 'Saved' : 'Save'}</span>
          </button>

          <button
            onClick={handleMarkComplete}
            disabled={isCompleted || isCompleting}
            className={`diagram-btn ${isCompleted ? '' : 'primary'}`}
            style={{
              background: isCompleted ? 'rgba(16, 185, 129, 0.15)' : undefined,
              borderColor: isCompleted ? 'var(--emerald-success)' : undefined,
              color: isCompleted ? 'var(--emerald-success)' : undefined,
            }}
          >
            <CheckCircle2 size={16} />
            <span>{isCompleted ? 'Completed' : isCompleting ? 'Saving...' : 'Mark as Completed'}</span>
          </button>
        </div>
      </div>

      {/* Main Reading Pane */}
      <div className="lesson-reading-pane">
        {/* Lesson Header Banner */}
        <div style={{ marginBottom: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span className="badge badge-ready">{lesson.difficulty}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <Clock size={13} />
              {lesson.estimated_minutes} min read
            </span>
            <span
              className={`status-tag ${
                isCompleted ? 'completed' : 'in-progress'
              }`}
            >
              {isCompleted ? 'Completed' : 'In Progress'}
            </span>
          </div>

          <h1 style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', lineHeight: 1.25, margin: '8px 0 12px' }}>
            {lesson.title}
          </h1>

          {lesson.description && (
            <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.6 }}>
              {lesson.description}
            </p>
          )}
        </div>

        {/* Optional Protocol Visualizer Flyout */}
        {showDiagramExplorer && (
          <div style={{ marginBottom: '32px' }}>
            <DiagramContainer initialDiagram={getRelevantDiagram()} allowSwitching={true} />
          </div>
        )}

        {/* Lesson Markdown & Concept Content */}
        <MarkdownContent content={lesson.content} />

        {/* Up Next Card Preview */}
        <UpNextCard nextLesson={lesson.next_lesson} currentTopicSlug={lesson.topic_slug} />

        {/* Footer Navigation Bar */}
        <LessonNavigation
          previousLesson={lesson.previous_lesson}
          nextLesson={lesson.next_lesson}
          status={lesson.status}
          isBookmarked={lesson.is_bookmarked}
          onToggleBookmark={handleToggleBookmark}
          onMarkComplete={handleMarkComplete}
          isCompleting={isCompleting}
          topicSlug={lesson.topic_slug}
        />
      </div>
    </div>
  )
}
