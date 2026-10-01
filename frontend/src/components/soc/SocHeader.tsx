import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import './soc.css'

interface SocHeaderProps {
  title?: string
  subtitle?: string
  actionButton?: React.ReactNode
}

export const SocHeader: React.FC<SocHeaderProps> = ({
  title = 'Security Operations Center',
  subtitle = 'Defensive Triage, Alert Prioritization & Incident Investigation Lab',
  actionButton,
}) => {
  const location = useLocation()
  const currentPath = location.pathname

  const navItems = [
    { label: 'SOC Overview', path: '/soc' },
    { label: 'Alert Queue', path: '/soc/alerts' },
    { label: 'Analyst Queue', path: '/soc/queue' },
    { label: 'Investigations', path: '/soc/investigations' },
    { label: 'Cases', path: '/soc/cases' },
    { label: 'Detection Coverage', path: '/soc/detection-coverage' },
    { label: 'SOC Challenges', path: '/soc/challenges' },
  ]

  const isActive = (path: string) => {
    if (path === '/soc') {
      return currentPath === '/soc'
    }
    return currentPath.startsWith(path)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
      {/* Offline Training Banner */}
      <div className="soc-banner">
        <div className="soc-banner-content">
          <span className="soc-banner-icon">🛡️</span>
          <div>
            <div className="soc-banner-title">NexoraNet Defensive SOC — Offline Training Environment</div>
            <div className="soc-banner-sub">
              Deterministic & explainable educational simulation. Zero live packet capture, zero active blocking, zero network interception.
              Remember: <strong>ALERT ≠ INCIDENT</strong> and <strong>OBSERVATION ≠ PROOF</strong>.
            </div>
          </div>
        </div>
      </div>

      {/* Title & Actions Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: 'var(--soc-text-primary)' }}>{title}</h1>
          <p style={{ margin: '0.25rem 0 0 0', color: 'var(--soc-text-secondary)', fontSize: '0.9rem' }}>{subtitle}</p>
        </div>
        {actionButton && <div>{actionButton}</div>}
      </div>

      {/* Navigation Tabs */}
      <nav className="soc-nav-tabs" aria-label="SOC Navigation">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`soc-nav-tab ${isActive(item.path) ? 'active' : ''}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  )
}
