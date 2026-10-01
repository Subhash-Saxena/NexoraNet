import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  History,
  ChevronLeft,
  CheckCircle2,
  XCircle,
  Clock,
  RotateCcw,
  FileText,
  AlertCircle,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { AttemptHistoryItem } from '../../types'
import '../../components/mock_tests/mock_tests.css'

export const MockTestHistoryPage: React.FC = () => {
  const [history, setHistory] = useState<AttemptHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    setIsLoading(true)
    setError(null)

    apiService
      .getAttemptHistory()
      .then((data) => setHistory(data))
      .catch((err) => setError(err.message || 'Failed to load attempt records.'))
      .finally(() => setIsLoading(false))
  }, [])

  const formatDuration = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60)
    const secs = totalSeconds % 60
    if (mins === 0) return `${secs}s`
    return `${mins}m ${secs}s`
  }

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr)
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return isoStr
    }
  }

  const handleRetake = async (testId: number) => {
    try {
      const newSitting = await apiService.startAttempt(testId, true)
      navigate(`/mock-tests/attempt/${newSitting.attempt_id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to launch new sitting.')
    }
  }

  return (
    <div className="mt-container" data-testid="mock-test-history-page">
      <Link
        to="/mock-tests"
        className="mt-btn mt-btn-secondary"
        style={{ marginBottom: '1.5rem', display: 'inline-flex' }}
        data-testid="back-to-catalog-btn"
      >
        <ChevronLeft size={16} /> Back to Catalog
      </Link>

      <div className="mt-header">
        <h1 className="mt-header-title">
          <History size={32} style={{ color: '#38bdf8' }} />
          Examination Sitting History
        </h1>
        <p className="mt-header-desc">
          Review your previous examination attempts, verify your historical scores, and revisit answer keys for continuous learning.
        </p>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', padding: '1rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#f87171' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '4rem 1rem', color: '#94a3b8' }}>
          <div style={{ display: 'inline-block', width: '2rem', height: '2rem', border: '3px solid #334155', borderTopColor: '#38bdf8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          <p style={{ marginTop: '1rem' }}>Loading sitting history...</p>
        </div>
      ) : history.length === 0 ? (
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '0.75rem', padding: '3rem 1.5rem', textAlign: 'center' }}>
          <History size={48} style={{ color: '#64748b', margin: '0 auto 1rem' }} />
          <h3 style={{ color: '#f8fafc', fontSize: '1.125rem', marginBottom: '0.5rem' }}>No Examination Attempts Yet</h3>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Choose a mock test from the catalog to begin your first timed practice session.
          </p>
          <Link to="/mock-tests" className="mt-btn mt-btn-primary">
            Browse Examinations
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {history.map((att) => {
            const isPassed = att.passed
            return (
              <div
                key={att.attempt_id}
                style={{
                  background: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '0.75rem',
                  padding: '1.25rem 1.5rem',
                  display: 'flex',
                  flexWrap: 'wrap',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '1rem',
                }}
                data-testid={`history-item-${att.attempt_id}`}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem' }}>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                      {att.test_title}
                    </h3>
                    <span
                      className={`mt-badge ${
                        att.difficulty === 'BEGINNER'
                          ? 'mt-badge-beginner'
                          : att.difficulty === 'INTERMEDIATE'
                          ? 'mt-badge-intermediate'
                          : 'mt-badge-advanced'
                      }`}
                    >
                      {att.difficulty}
                    </span>
                    <span className="mt-badge mt-badge-type">{att.test_type}</span>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '1rem', fontSize: '0.8125rem', color: '#94a3b8' }}>
                    <span>Attempted: {formatDate(att.started_at)}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Clock size={13} /> {formatDuration(att.time_taken_seconds)}
                    </span>
                    <span>Status: <strong style={{ color: '#e2e8f0' }}>{att.status}</strong></span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div
                      style={{
                        fontSize: '1.5rem',
                        fontWeight: 700,
                        color: isPassed ? '#34d399' : '#f87171',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        justifyContent: 'flex-end',
                      }}
                    >
                      {isPassed ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
                      {Math.round(att.percentage)}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                      {att.score} / {att.total_points} Points ({isPassed ? 'PASSED' : 'FAILED'})
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Link
                      to={`/mock-tests/attempt/${att.attempt_id}/result`}
                      className="mt-btn mt-btn-secondary"
                      style={{ padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}
                    >
                      Scorecard
                    </Link>
                    <Link
                      to={`/mock-tests/attempt/${att.attempt_id}/review`}
                      className="mt-btn mt-btn-primary"
                      style={{ padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}
                    >
                      <FileText size={14} /> Review
                    </Link>
                    <button
                      type="button"
                      className="mt-btn mt-btn-secondary"
                      style={{ padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}
                      onClick={() => handleRetake(att.test_id)}
                      title="Launch a fresh retake of this exam"
                    >
                      <RotateCcw size={14} />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
