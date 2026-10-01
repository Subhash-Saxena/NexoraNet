import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bookmark,
  Clock,
  Trash2,
  BookOpen,
  ArrowRight,
  ChevronLeft,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { BookmarkItem } from '../../types'
import '../../components/learning/learning.css'

export const BookmarksPage: React.FC = () => {
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    apiService
      .getBookmarks()
      .then((data) => {
        if (!active) return
        setBookmarks(data)
        setLoading(false)
      })
      .catch(() => {
        if (!active) return
        setBookmarks([])
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const handleRemoveBookmark = async (lessonId: number) => {
    try {
      await apiService.unbookmarkLesson(lessonId)
      setBookmarks((prev) => prev.filter((b) => b.lesson_id !== lessonId))
    } catch {
      // silently handle
    }
  }

  return (
    <div className="learning-container">
      {/* Breadcrumb Navigation */}
      <div className="lesson-breadcrumbs">
        <Link to="/learning">Curriculum</Link>
        <span>/</span>
        <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>Saved Bookmarks</span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Bookmark size={24} color="var(--cyan-primary)" />
            <span>Saved Learning Bookmarks</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Quick access to reference lessons, protocol analyses, and study notes you've pinned.
          </p>
        </div>

        <Link to="/learning" className="diagram-btn">
          <ChevronLeft size={16} />
          <span>Back to Curriculum</span>
        </Link>
      </div>

      {loading ? (
        <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading saved bookmarks...
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="card" style={{ padding: '48px', textAlign: 'center' }}>
          <Bookmark size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
            No Bookmarked Lessons Yet
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', maxWidth: '440px', margin: '0 auto 20px' }}>
            As you read through lessons in the curriculum, click the bookmark icon to save key topics for quick exam revision.
          </p>
          <Link to="/learning" className="diagram-btn primary" style={{ display: 'inline-flex' }}>
            <BookOpen size={16} />
            <span>Browse Lessons</span>
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {bookmarks.map((b) => (
            <div
              key={b.id}
              className="card"
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '16px 20px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge badge-ready" style={{ fontSize: '0.68rem' }}>
                    {b.difficulty}
                  </span>
                  <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    Module: {b.module_title} &bull; Topic: {b.topic_title}
                  </span>
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {b.lesson_title}
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} />
                    {b.estimated_minutes} min read
                  </span>
                  <span>&bull;</span>
                  <span>Saved on {new Date(b.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <button
                  onClick={() => handleRemoveBookmark(b.lesson_id)}
                  style={{
                    padding: '8px',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                  }}
                  title="Remove bookmark"
                >
                  <Trash2 size={16} />
                </button>

                <Link
                  to={`/learning/lessons/${b.lesson_slug}`}
                  className="diagram-btn primary"
                  style={{ padding: '8px 16px', textDecoration: 'none' }}
                >
                  <span>Read Lesson</span>
                  <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
