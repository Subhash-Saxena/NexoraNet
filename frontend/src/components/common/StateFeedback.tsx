import React from 'react'
import { AlertCircle, Inbox, Loader2 } from 'lucide-react'

export interface StateFeedbackProps {
  type: 'loading' | 'error' | 'empty'
  title?: string
  description?: string
  actionLabel?: string
  onAction?: () => void
}

export const StateFeedback: React.FC<StateFeedbackProps> = ({
  type,
  title,
  description,
  actionLabel,
  onAction,
}) => {
  if (type === 'loading') {
    return (
      <div className="state-container" role="status">
        <Loader2 className="spinner" size={28} />
        <div className="state-title">{title || 'Loading Platform Data...'}</div>
        <div className="state-desc">{description || 'Connecting to NexoraNet microservices.'}</div>
      </div>
    )
  }

  if (type === 'error') {
    return (
      <div className="state-container" role="alert">
        <AlertCircle size={36} color="var(--rose-danger)" />
        <div className="state-title">{title || 'Unable to Load Data'}</div>
        <div className="state-desc">
          {description || 'There was an issue communicating with the backend API service.'}
        </div>
        {onAction && (
          <button className="btn-retry" onClick={onAction}>
            {actionLabel || 'Retry Request'}
          </button>
        )}
      </div>
    )
  }

  return (
    <div className="state-container">
      <Inbox size={36} color="var(--text-muted)" />
      <div className="state-title">{title || 'No Records Found'}</div>
      <div className="state-desc">
        {description || 'No data is currently available for this module.'}
      </div>
      {onAction && (
        <button className="btn-retry" onClick={onAction}>
          {actionLabel || 'Refresh'}
        </button>
      )}
    </div>
  )
}
