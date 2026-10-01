import React from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, ArrowLeft } from 'lucide-react'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="state-container" style={{ minHeight: '50vh', border: 'none' }}>
      <AlertCircle size={48} color="var(--rose-danger)" />
      <div className="state-title" style={{ fontSize: '1.4rem', marginTop: '12px' }}>
        404 - Page Not Found
      </div>
      <div className="state-desc">
        The requested routing node does not exist in the NexoraNet topology.
      </div>
      <Link
        to="/dashboard"
        className="btn-retry"
        style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}
      >
        <ArrowLeft size={16} /> Return to Dashboard
      </Link>
    </div>
  )
}
