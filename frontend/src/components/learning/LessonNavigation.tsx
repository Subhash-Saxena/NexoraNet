import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, CheckCircle2, Bookmark, BookmarkCheck } from 'lucide-react'
import type { LessonBrief, ProgressStatus } from '../../types'

export interface LessonNavigationProps {
  previousLesson?: LessonBrief | null
  nextLesson?: LessonBrief | null
  status: ProgressStatus
  isBookmarked: boolean
  onToggleBookmark: () => void
  onMarkComplete: () => void
  isCompleting?: boolean
  topicSlug: string
}

export const LessonNavigation: React.FC<LessonNavigationProps> = ({
  previousLesson,
  nextLesson,
  status,
  isBookmarked,
  onToggleBookmark,
  onMarkComplete,
  isCompleting = false,
  topicSlug,
}) => {
  return (
    <div className="lesson-navigation-bar">
      <div>
        {previousLesson ? (
          <Link
            to={`/learning/lessons/${previousLesson.slug}`}
            className="nav-direction-btn"
          >
            <ChevronLeft size={18} />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Previous Lesson</div>
              <div style={{ fontSize: '0.86rem', maxWidth: '220px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {previousLesson.title}
              </div>
            </div>
          </Link>
        ) : (
          <Link to={`/learning/topics/${topicSlug}`} className="nav-direction-btn">
            <ChevronLeft size={18} />
            <span>Back to Topic</span>
          </Link>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={onToggleBookmark}
          className="diagram-btn"
          style={{ padding: '10px 14px' }}
          title={isBookmarked ? 'Remove bookmark' : 'Bookmark this lesson'}
        >
          {isBookmarked ? (
            <>
              <BookmarkCheck size={16} color="var(--emerald-success)" />
              <span style={{ color: 'var(--emerald-success)' }}>Saved</span>
            </>
          ) : (
            <>
              <Bookmark size={16} />
              <span>Save Lesson</span>
            </>
          )}
        </button>

        <button
          onClick={onMarkComplete}
          disabled={status === 'COMPLETED' || isCompleting}
          className={`diagram-btn ${status === 'COMPLETED' ? '' : 'primary'}`}
          style={{
            padding: '10px 20px',
            background: status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : undefined,
            borderColor: status === 'COMPLETED' ? 'var(--emerald-success)' : undefined,
            color: status === 'COMPLETED' ? 'var(--emerald-success)' : undefined,
          }}
        >
          <CheckCircle2 size={16} />
          <span>
            {status === 'COMPLETED'
              ? 'Completed'
              : isCompleting
              ? 'Saving...'
              : 'Mark as Completed'}
          </span>
        </button>
      </div>

      <div>
        {nextLesson ? (
          <Link
            to={`/learning/lessons/${nextLesson.slug}`}
            className="nav-direction-btn"
          >
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Next Lesson</div>
              <div style={{ fontSize: '0.86rem', maxWidth: '220px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {nextLesson.title}
              </div>
            </div>
            <ChevronRight size={18} />
          </Link>
        ) : (
          <Link
            to={`/learning/topics/${topicSlug}`}
            className="nav-direction-btn"
            style={{ borderColor: 'var(--emerald-success)' }}
          >
            <CheckCircle2 size={18} color="var(--emerald-success)" />
            <span>Complete Topic</span>
          </Link>
        )}
      </div>
    </div>
  )
}
