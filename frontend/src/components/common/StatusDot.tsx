import React from 'react'
import type { BackendHealthState } from '../../types'

interface StatusDotProps {
  status: BackendHealthState
  showLabel?: boolean
  onClick?: () => void
}

export const StatusDot: React.FC<StatusDotProps> = ({ status, showLabel = true, onClick }) => {
  const getLabel = () => {
    switch (status) {
      case 'connected':
        return 'Connected'
      case 'disconnected':
        return 'Disconnected'
      case 'checking':
        return 'Checking...'
    }
  }

  return (
    <div
      className={`status-badge ${status}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      title={onClick ? 'Click to re-verify backend connectivity' : undefined}
      role="status"
      aria-live="polite"
    >
      <span className={`dot-indicator ${status}`} aria-hidden="true" />
      {showLabel && (
        <span>
          Backend: <strong>{getLabel()}</strong>
        </span>
      )}
    </div>
  )
}
