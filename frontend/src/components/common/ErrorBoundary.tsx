import React from 'react'

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  /** Optional fallback UI to render on error. Receives error details. */
  fallback?: (props: { error: Error; reset: () => void }) => React.ReactNode
  /** Page/section label shown in the default error UI */
  label?: string
}

/**
 * Global React Error Boundary for NexoraNet.
 *
 * Catches JavaScript runtime errors in any child component tree and renders
 * a styled cybersecurity-themed error card instead of a blank black screen.
 *
 * Usage:
 *   <ErrorBoundary label="Endpoint Security">
 *     <EndpointDashboardPage />
 *   </ErrorBoundary>
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    this.setState({ errorInfo: info })
    // Log to console so the developer can investigate
    console.error('[NexoraNet ErrorBoundary]', error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback({ error: this.state.error, reset: this.handleReset })
      }

      const { error } = this.state
      const label = this.props.label || 'Page'

      return (
        <div
          style={{
            minHeight: '60vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
          }}
        >
          <div
            style={{
              background: '#0b1325',
              border: '1px solid rgba(244, 63, 94, 0.35)',
              borderRadius: '12px',
              padding: '2.5rem',
              maxWidth: '600px',
              width: '100%',
              boxShadow: '0 0 40px rgba(244, 63, 94, 0.08)',
            }}
          >
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  background: 'rgba(244, 63, 94, 0.12)',
                  border: '1px solid rgba(244, 63, 94, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.3rem',
                  flexShrink: 0,
                }}
              >
                ⚠️
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#f8fafc' }}>
                  {label} Failed to Render
                </div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '2px' }}>
                  NexoraNet caught a JavaScript runtime error
                </div>
              </div>
            </div>

            {/* Error message */}
            <div
              style={{
                background: '#090d16',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                padding: '1rem',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.8rem',
                color: '#f87171',
                marginBottom: '1.5rem',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                maxHeight: '180px',
                overflowY: 'auto',
              }}
            >
              {error.message || String(error)}
            </div>

            <div style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem', lineHeight: 1.6 }}>
              This is an isolated error in the <strong style={{ color: '#94a3b8' }}>{label}</strong> section.
              The rest of the platform continues to work. You can retry loading this page or navigate elsewhere.
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                onClick={this.handleReset}
                style={{
                  padding: '0.55rem 1.25rem',
                  background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                🔄 Retry
              </button>
              <button
                onClick={() => (window.location.href = '/dashboard')}
                style={{
                  padding: '0.55rem 1.25rem',
                  background: 'transparent',
                  color: '#94a3b8',
                  border: '1px solid #1e293b',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Lightweight HOC that wraps a page component in an ErrorBoundary automatically.
 * Usage: const SafePage = withErrorBoundary(MyPage, 'My Page')
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  label?: string
): React.FC<P> {
  const Wrapped: React.FC<P> = (props) => (
    <ErrorBoundary label={label ?? Component.displayName ?? Component.name ?? 'Page'}>
      <Component {...props} />
    </ErrorBoundary>
  )
  Wrapped.displayName = `WithErrorBoundary(${Component.displayName ?? Component.name ?? 'Component'})`
  return Wrapped
}
