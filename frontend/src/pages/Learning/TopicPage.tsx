import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  BookOpen,
  Clock,
  CheckCircle2,
  Lock,
  Unlock,
  ShieldAlert,
  Terminal,
  FileCheck2,
  ChevronLeft,
  ChevronRight,
  Bookmark,
  BookmarkCheck,
  Target,
  ArrowRight,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { TopicDetailExtended, LessonBriefWithProgress } from '../../types'
import '../../components/learning/learning.css'

export const TopicPage: React.FC = () => {
  const { topicSlug } = useParams<{ topicSlug: string }>()
  const [topic, setTopic] = useState<TopicDetailExtended | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!topicSlug) return
    let active = true

    apiService
      .getTopicDetail(topicSlug)
      .then((data) => {
        if (!active) return
        setTopic(data)
        setLoading(false)
      })
      .catch((err) => {
        if (!active) return
        setError(err.message || 'Failed to load topic details')
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [topicSlug])

  const handleToggleBookmark = async (lesson: LessonBriefWithProgress) => {
    if (!topic) return
    try {
      if (lesson.is_bookmarked) {
        await apiService.unbookmarkLesson(lesson.id)
      } else {
        await apiService.bookmarkLesson(lesson.id)
      }
      // Update local state
      setTopic({
        ...topic,
        lessons: topic.lessons.map((l) =>
          l.id === lesson.id ? { ...l, is_bookmarked: !l.is_bookmarked } : l
        ),
      })
    } catch {
      // error handled silently
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading syllabus topic...
      </div>
    )
  }

  if (error || !topic) {
    return (
      <div style={{ padding: '48px', textAlign: 'center' }}>
        <h3 style={{ color: 'var(--rose-danger)', marginBottom: '8px' }}>Topic Not Found</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
          {error || 'Unable to load topic content.'}
        </p>
        <Link to="/learning" className="diagram-btn primary">
          Return to Curriculum
        </Link>
      </div>
    )
  }

  const allPrereqsMet = topic.prerequisites.every((p) => p.is_completed)

  return (
    <div className="learning-container">
      {/* Breadcrumb Navigation */}
      <div className="lesson-breadcrumbs">
        <Link to="/learning">Curriculum</Link>
        <span>/</span>
        <span>Module {topic.module_id}: {topic.module_title}</span>
        <span>/</span>
        <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{topic.title}</span>
      </div>

      {/* Topic Header Card */}
      <div className="topic-header-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-ready">{topic.difficulty}</span>
              <span className="badge badge-phase">Topic #{topic.order_index}</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                <Clock size={13} />
                {topic.estimated_minutes} min estimated
              </span>
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', marginBottom: '8px' }}>
              {topic.title}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.94rem', maxWidth: '780px', lineHeight: 1.6 }}>
              {topic.description}
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--cyan-primary)' }}>
              {topic.completed_lessons_count} / {topic.lessons_count}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Lessons Completed ({topic.completion_percentage}%)
            </div>
            <div className="progress-bar-bg" style={{ width: '140px', marginTop: '6px' }}>
              <div className="progress-bar-fill" style={{ width: `${topic.completion_percentage}%` }} />
            </div>
          </div>
        </div>

        {/* Prerequisites Section */}
        {topic.prerequisites.length > 0 && (
          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.76rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
              {allPrereqsMet ? <Unlock size={14} color="var(--emerald-success)" /> : <Lock size={14} color="var(--amber-warning)" />}
              <span>Curriculum Prerequisites</span>
            </div>
            <div className="prerequisites-badge-list">
              {topic.prerequisites.map((p) => (
                <Link
                  key={p.id}
                  to={`/learning/topics/${p.slug}`}
                  className={`prerequisite-badge ${p.is_completed ? 'completed' : 'locked'}`}
                  style={{ textDecoration: 'none' }}
                >
                  {p.is_completed ? <CheckCircle2 size={12} /> : <Lock size={12} />}
                  <span>{p.title}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', alignItems: 'start' }}>
        {/* Left Column: Lesson Syllabus & Learning Objectives */}
        <div>
          {/* Learning Objectives */}
          {topic.learning_objectives && topic.learning_objectives.length > 0 && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--cyan-primary)', fontWeight: 700, fontSize: '0.94rem', marginBottom: '12px' }}>
                <Target size={18} />
                <span>Learning Objectives</span>
              </div>
              <ul style={{ margin: '0 0 0 18px', color: '#cbd5e1', fontSize: '0.88rem' }}>
                {topic.learning_objectives.map((obj, idx) => (
                  <li key={idx} style={{ marginBottom: '6px', lineHeight: 1.5 }}>
                    {obj}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Lessons List */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={18} color="var(--cyan-primary)" />
                <span>Topic Lessons ({topic.lessons.length})</span>
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Step-by-step reading modules
              </span>
            </div>

            {topic.lessons.length === 0 ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                Lessons for this topic will be available soon.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {topic.lessons.map((lesson) => {
                  const isCompleted = lesson.status === 'COMPLETED'
                  const isInProgress = lesson.status === 'IN_PROGRESS'

                  return (
                    <div key={lesson.id} className="lesson-list-item">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <span
                          style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            background: isCompleted ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                            color: isCompleted ? 'var(--emerald-success)' : 'var(--text-muted)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.8rem',
                            fontWeight: 700,
                          }}
                        >
                          {isCompleted ? <CheckCircle2 size={16} /> : lesson.order_index}
                        </span>

                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                            {lesson.title}
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                              <Clock size={11} />
                              {lesson.estimated_minutes} min
                            </span>
                            <span>&bull;</span>
                            <span
                              className={`status-tag ${
                                isCompleted ? 'completed' : isInProgress ? 'in-progress' : 'not-started'
                              }`}
                            >
                              {isCompleted ? 'Completed' : isInProgress ? 'In Progress' : 'Not Started'}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <button
                          onClick={() => handleToggleBookmark(lesson)}
                          style={{ color: lesson.is_bookmarked ? 'var(--emerald-success)' : 'var(--text-muted)', padding: '6px', cursor: 'pointer' }}
                          title={lesson.is_bookmarked ? 'Bookmarked' : 'Save bookmark'}
                        >
                          {lesson.is_bookmarked ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
                        </button>

                        <Link
                          to={`/learning/lessons/${lesson.slug}`}
                          className="diagram-btn primary"
                          style={{ padding: '6px 14px', textDecoration: 'none' }}
                        >
                          <span>{isCompleted ? 'Review' : isInProgress ? 'Continue' : 'Start'}</span>
                          <ArrowRight size={14} />
                        </Link>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Security Relevance & Future Connections */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Security Relevance Card */}
          {topic.security_relevance && (
            <div className="card" style={{ borderColor: 'rgba(244, 63, 94, 0.3)', background: 'rgba(244, 63, 94, 0.04)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--rose-danger)', fontWeight: 700, fontSize: '0.92rem', marginBottom: '10px' }}>
                <ShieldAlert size={18} />
                <span>Cybersecurity Relevance</span>
              </div>
              <p style={{ color: '#e2e8f0', fontSize: '0.86rem', lineHeight: 1.6, margin: 0 }}>
                {topic.security_relevance}
              </p>
            </div>
          )}

          {/* Related Labs Preview (Step 4 Connection) */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--cyan-primary)', fontWeight: 700, fontSize: '0.92rem', marginBottom: '10px' }}>
              <Terminal size={18} />
              <span>Connected Hands-on Lab</span>
            </div>
            {topic.related_labs.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {topic.related_labs.map((lab) => (
                  <div key={lab.id} style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.84rem', color: 'var(--text-main)' }}>{lab.title}</span>
                      <span className="badge badge-phase" style={{ fontSize: '0.65rem' }}>Phase 4 Lab</span>
                    </div>
                    {lab.description && (
                      <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        {lab.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                Interactive terminal lab for this topic activates in Step 4.
              </p>
            )}
          </div>

          {/* Related Mock Tests Preview (Step 5 Connection) */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--emerald-success)', fontWeight: 700, fontSize: '0.92rem', marginBottom: '10px' }}>
              <FileCheck2 size={18} />
              <span>Knowledge Evaluation</span>
            </div>
            {topic.related_mock_tests.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {topic.related_mock_tests.map((test) => (
                  <div key={test.id} style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.84rem', color: 'var(--text-main)' }}>{test.title}</span>
                      <span className="badge badge-ready" style={{ fontSize: '0.65rem' }}>{test.difficulty}</span>
                    </div>
                    {test.description && (
                      <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        {test.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                Targeted practice exam questions for this topic activate in Step 5.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Previous / Next Topic Footer Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '32px', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
        {topic.previous_topic ? (
          <Link to={`/learning/topics/${topic.previous_topic.slug}`} className="nav-direction-btn">
            <ChevronLeft size={16} />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Previous Topic</div>
              <div style={{ fontSize: '0.86rem' }}>{topic.previous_topic.title}</div>
            </div>
          </Link>
        ) : (
          <Link to="/learning" className="nav-direction-btn">
            <ChevronLeft size={16} />
            <span>Curriculum Overview</span>
          </Link>
        )}

        {topic.next_topic ? (
          <Link to={`/learning/topics/${topic.next_topic.slug}`} className="nav-direction-btn">
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Next Topic</div>
              <div style={{ fontSize: '0.86rem' }}>{topic.next_topic.title}</div>
            </div>
            <ChevronRight size={16} />
          </Link>
        ) : (
          <Link to="/learning" className="nav-direction-btn">
            <span>Course Complete</span>
            <ChevronRight size={16} />
          </Link>
        )}
      </div>
    </div>
  )
}
