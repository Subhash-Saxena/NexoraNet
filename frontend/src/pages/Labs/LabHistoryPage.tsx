import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  History,
  ArrowLeft,
  RotateCcw,
  Eye,
  X,
  BookOpen,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { LabAttemptBrief, LabAttemptDetail } from '../../types'
import '../../components/labs/labs.css'

export const LabHistoryPage: React.FC = () => {
  const [attempts, setAttempts] = useState<LabAttemptBrief[]>([])
  const [selectedAttempt, setSelectedAttempt] = useState<LabAttemptDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    const fetchAttempts = async () => {
      try {
        setLoading(true)
        const data = await apiService.getLabAttempts()
        if (isMounted) {
          setAttempts(data)
          setError(null)
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load attempt history.')
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    fetchAttempts()
    return () => {
      isMounted = false
    }
  }, [])

  const handleViewAttemptDetail = async (attemptId: number) => {
    try {
      setLoadingDetail(true)
      const detail = await apiService.getLabAttemptDetail(attemptId)
      setSelectedAttempt(detail)
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to load attempt details.')
    } finally {
      setLoadingDetail(false)
    }
  }

  const formatTime = (seconds?: number | null) => {
    if (!seconds) return '—'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString)
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return isoString
    }
  }

  return (
    <div className="labs-container">
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Link to="/labs" className="lab-card-topic" style={{ marginBottom: 6 }}>
            <ArrowLeft size={14} /> Back to Labs Catalog
          </Link>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-main)' }}>
            Lab Attempt History
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
            Review your past networking lab executions, submissions, and feedback.
          </p>
        </div>
      </div>

      {error && (
        <div className="lab-feedback-alert incorrect">
          <div className="lab-feedback-head">Error Loading History</div>
          <div className="lab-feedback-msg">{error}</div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          <History size={36} color="var(--cyan-primary)" style={{ margin: '0 auto 12px auto' }} />
          <div>Retrieving past lab attempts...</div>
        </div>
      ) : attempts.length === 0 ? (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: 48,
            textAlign: 'center',
          }}
        >
          <History size={40} color="var(--text-muted)" style={{ margin: '0 auto 16px auto' }} />
          <h3 style={{ fontSize: '1.25rem', marginBottom: 8 }}>No lab attempts recorded yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
            Start your first hands-on networking lab to build muscle memory and track your progress.
          </p>
          <Link to="/labs" className="btn-lab-action btn-lab-primary">
            Explore Labs Catalog
          </Link>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="lab-history-table">
            <thead>
              <tr>
                <th>Lab Title</th>
                <th>Difficulty</th>
                <th>Attempt #</th>
                <th>Status</th>
                <th>Score</th>
                <th>Time</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {attempts.map((attempt) => {
                const isCompleted = attempt.status === 'COMPLETED'
                return (
                  <tr key={attempt.id}>
                    <td>
                      <strong>{attempt.lab_title}</strong>
                    </td>
                    <td>
                      <span className="lab-badge lab-badge-env">
                        {attempt.lab_difficulty}
                      </span>
                    </td>
                    <td>#{attempt.attempt_number}</td>
                    <td>
                      <span
                        className={`lab-badge ${
                          isCompleted ? 'lab-badge-status-completed' : 'lab-badge-status-in-progress'
                        }`}
                      >
                        {attempt.status}
                      </span>
                    </td>
                    <td>
                      <strong style={{ color: isCompleted ? 'var(--emerald-success)' : 'inherit' }}>
                        {attempt.score} / {attempt.total_points} ({Math.round(attempt.percentage)}%)
                      </strong>
                    </td>
                    <td>{formatTime(attempt.time_taken_seconds)}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                      {formatDate(attempt.started_at)}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          type="button"
                          className="btn-lab-action btn-lab-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                          onClick={() => handleViewAttemptDetail(attempt.id)}
                          disabled={loadingDetail}
                        >
                          <Eye size={12} /> {loadingDetail ? 'Loading...' : 'Review'}
                        </button>
                        <Link
                          to={`/labs/${attempt.lab_slug}`}
                          className="btn-lab-action btn-lab-primary"
                          style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                        >
                          <RotateCcw size={12} /> Open Lab
                        </Link>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Review Modal / Drawer */}
      {selectedAttempt && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(2, 6, 23, 0.8)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: 20,
          }}
          onClick={() => setSelectedAttempt(null)}
        >
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-lg)',
              maxWidth: 720,
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: 28,
              display: 'flex',
              flexDirection: 'column',
              gap: 20,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span className="lab-badge lab-badge-env" style={{ marginBottom: 6 }}>
                  Attempt #{selectedAttempt.attempt_number} • {selectedAttempt.lab_difficulty}
                </span>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  {selectedAttempt.lab_title}
                </h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                  Total Score: <strong>{selectedAttempt.score} / {selectedAttempt.total_points}</strong> ({Math.round(selectedAttempt.percentage)}%)
                </div>
              </div>

              <button
                type="button"
                className="lab-hint-toggle"
                style={{ width: 'auto', padding: 8 }}
                onClick={() => setSelectedAttempt(null)}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Submitted Step Responses
              </h4>

              {selectedAttempt.submissions?.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  No submissions were recorded for this attempt.
                </div>
              ) : (
                selectedAttempt.submissions?.map((sub) => (
                  <div
                    key={sub.step_id}
                    style={{
                      background: 'var(--bg-input)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: 16,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 8,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong>
                        Step {sub.step_number}: {sub.step_title}
                      </strong>
                      <span
                        className={`lab-badge ${
                          sub.is_correct ? 'lab-badge-status-completed' : 'lab-badge-env'
                        }`}
                      >
                        {sub.is_correct ? 'Correct' : 'Incorrect'} ({sub.points_earned} / {sub.max_points} pts)
                      </span>
                    </div>

                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      Submitted Answer: <code style={{ color: 'var(--cyan-primary)' }}>{sub.submitted_answer}</code>
                    </div>

                    {sub.feedback && (
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>
                        {sub.feedback}
                      </div>
                    )}

                    {sub.explanation && (
                      <div
                        style={{
                          marginTop: 4,
                          paddingTop: 8,
                          borderTop: '1px solid var(--border-subtle)',
                          fontSize: '0.82rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        <BookOpen size={12} style={{ display: 'inline', marginRight: 4 }} />
                        {sub.explanation}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 10 }}>
              <button
                type="button"
                className="btn-lab-action btn-lab-secondary"
                onClick={() => setSelectedAttempt(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
