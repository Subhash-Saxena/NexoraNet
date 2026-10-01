import React from 'react'
import { StatusDot } from '../common/StatusDot'
import { useHealthCheck } from '../../hooks/useHealthCheck'
import { Server } from 'lucide-react'

interface NavbarProps {
  title?: string
  subtitle?: string
}

export const Navbar: React.FC<NavbarProps> = ({
  title = 'Platform Overview',
  subtitle = 'Learn. Simulate. Analyze. Defend.',
}) => {
  const { status, checkNow } = useHealthCheck(15000)

  return (
    <header className="top-navbar">
      <div className="page-title-group">
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>

      <div className="navbar-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
          <Server size={14} />
          <span>API v1.0</span>
        </div>
        <StatusDot status={status} onClick={checkNow} />
      </div>
    </header>
  )
}
