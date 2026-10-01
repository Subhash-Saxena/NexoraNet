import React from 'react'
import { Link } from 'react-router-dom'
import { StatusDot } from '../common/StatusDot'
import { useHealthCheck } from '../../hooks/useHealthCheck'
import { Server, LogIn, LogOut } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

interface NavbarProps {
  title?: string
  subtitle?: string
}

export const Navbar: React.FC<NavbarProps> = ({
  title = 'Platform Overview',
  subtitle = 'Learn. Simulate. Analyze. Defend.',
}) => {
  const { status, checkNow } = useHealthCheck(15000)
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="top-navbar">
      <div className="page-title-group">
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>

      <div className="navbar-actions" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted, #94a3b8)', fontSize: '0.78rem' }}>
          <Server size={14} />
          <span>API v1.0</span>
        </div>
        <StatusDot status={status} onClick={checkNow} />

        {/* User Account Controls */}
        {isAuthenticated && user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '0.75rem', borderLeft: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'linear-gradient(135deg, #3b82f6, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 600, fontSize: '0.75rem' }}>
                {(user.display_name || user.username).charAt(0).toUpperCase()}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.82rem', lineHeight: 1.2 }}>
                  {user.display_name || user.username}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#38bdf8' }}>
                  {user.role} • {user.current_level}
                </span>
              </div>
            </div>

            <button
              onClick={() => logout()}
              title="Sign Out"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '0.4rem 0.65rem',
                background: 'rgba(239, 68, 68, 0.1)',
                color: '#f87171',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: '6px',
                fontSize: '0.78rem',
                cursor: 'pointer',
                fontWeight: 500,
              }}
            >
              <LogOut size={13} />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div style={{ paddingLeft: '0.75rem', borderLeft: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <Link
              to="/login"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '0.45rem 0.9rem',
                background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                color: '#ffffff',
                borderRadius: '6px',
                fontSize: '0.82rem',
                fontWeight: 600,
                textDecoration: 'none',
                boxShadow: '0 2px 8px rgba(37, 99, 235, 0.3)',
              }}
            >
              <LogIn size={14} />
              <span>Sign In</span>
            </Link>
          </div>
        )}
      </div>
    </header>
  )
}
