import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, Clock } from 'lucide-react'
import type { LessonBrief } from '../../types'

export interface UpNextCardProps {
  nextLesson?: LessonBrief | null
  currentTopicSlug: string
}

export const UpNextCard: React.FC<UpNextCardProps> = ({ nextLesson, currentTopicSlug }) => {
  if (!nextLesson) {
    return (
      <div className="up-next-card" style={{ borderColor: 'rgba(16, 185, 129, 0.3)' }}>
        <div>
          <span className="badge badge-ready">Topic Mastered</span>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '6px' }}>
            You've completed all lessons in this topic!
          </h4>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Ready to review your skills or jump into the next learning roadmap module?
          </p>
        </div>
        <Link
          to={`/learning/topics/${currentTopicSlug}`}
          className="diagram-btn primary"
          style={{ padding: '10px 18px', textDecoration: 'none' }}
        >
          <span>Return to Topic</span>
          <ArrowRight size={16} />
        </Link>
      </div>
    )
  }

  return (
    <div className="up-next-card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            width: '44px',
            height: '44px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(6, 182, 212, 0.15)',
            color: 'var(--cyan-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <BookOpen size={20} />
        </div>
        <div>
          <span className="badge badge-phase" style={{ fontSize: '0.72rem' }}>
            Up Next &bull; Lesson {nextLesson.order_index}
          </span>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
            {nextLesson.title}
          </h4>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} />
              {nextLesson.estimated_minutes} min read
            </span>
            <span>&bull;</span>
            <span style={{ textTransform: 'uppercase', color: 'var(--cyan-primary)', fontWeight: 600 }}>
              {nextLesson.difficulty}
            </span>
          </div>
        </div>
      </div>

      <Link
        to={`/learning/lessons/${nextLesson.slug}`}
        className="diagram-btn primary"
        style={{ padding: '10px 20px', textDecoration: 'none', flexShrink: 0 }}
      >
        <span>Continue Reading</span>
        <ArrowRight size={16} />
      </Link>
    </div>
  )
}
