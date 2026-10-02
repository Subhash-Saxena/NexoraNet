import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useHealthCheck } from '../../hooks/useHealthCheck'
import {
  Home,
  Search,
  Bell,
  LogIn,
  LogOut,
  User,
  ExternalLink,
  Menu,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

interface NavbarProps {
  title?: string
  subtitle?: string
  onToggleMobileMenu?: () => void
}

export const Navbar: React.FC<NavbarProps> = ({
  title = 'Dashboard',
  subtitle = 'Overview of your learning journey',
  onToggleMobileMenu,
}) => {
  const { status, checkNow } = useHealthCheck(15000)
  const { user, isAuthenticated, logout } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const navigate = useNavigate()

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    navigate(`/learning?search=${encodeURIComponent(searchQuery.trim())}`)
  }

  return (
    <header className="top-navbar">
      {/* Page Title & Breadcrumb & Mobile Hamburger */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
        <button
          type="button"
          className="mobile-hamburger-btn"
          onClick={onToggleMobileMenu}
          title="Toggle Navigation Menu"
          aria-label="Toggle Navigation Menu"
        >
          <Menu size={20} />
        </button>

        <div className="navbar-home-icon" style={{ color: '#94a3b8', display: 'flex', alignItems: 'center' }}>
          <Home size={18} />
        </div>
        <div className="page-title-group" style={{ minWidth: 0 }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            {title}
          </h2>
          <p style={{ fontSize: '0.74rem', color: '#64748b', margin: 0 }}>
            {subtitle}
          </p>
        </div>
      </div>

      {/* Global Search Bar with Ctrl K shortcut */}
      <form
        className="navbar-search-bar"
        onSubmit={handleSearchSubmit}
        style={{
          flex: '1',
          maxWidth: '460px',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <Search
          size={16}
          style={{
            position: 'absolute',
            left: '12px',
            color: '#64748b',
            pointerEvents: 'none',
          }}
        />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search labs, topics, or tools..."
          style={{
            width: '100%',
            padding: '7px 70px 7px 36px',
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            color: '#f8fafc',
            fontSize: '0.82rem',
            outline: 'none',
            transition: 'all 0.2s ease',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = '#0ea5e9'
            e.currentTarget.style.boxShadow = '0 0 10px rgba(14, 165, 233, 0.2)'
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = '#1e293b'
            e.currentTarget.style.boxShadow = 'none'
          }}
        />
        <div
          className="navbar-search-shortcut"
          style={{
            position: 'absolute',
            right: '8px',
            padding: '2px 6px',
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid #334155',
            borderRadius: '4px',
            color: '#64748b',
            fontSize: '0.68rem',
            fontFamily: 'monospace',
            pointerEvents: 'none',
          }}
        >
          Ctrl K
        </div>
      </form>

      {/* Right Controls: Backend Connected badge, Notifications, User Avatar */}
      <div className="navbar-right-controls" style={{ display: 'flex', alignItems: 'center', gap: '14px', flexShrink: 0 }}>
        {/* Backend Connected Status Pill */}
        <div
          className="status-pill-btn"
          onClick={checkNow}
          title="Click to re-verify backend telemetry connection"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '5px 12px',
            background: status === 'connected' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${status === 'connected' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            borderRadius: '9999px',
            fontSize: '0.74rem',
            fontWeight: 600,
            color: status === 'connected' ? '#34d399' : '#f87171',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
        >
          <span
            style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: status === 'connected' ? '#10b981' : '#ef4444',
              boxShadow: status === 'connected' ? '0 0 8px #10b981' : 'none',
              flexShrink: 0,
            }}
          />
          <span className="status-pill-text">{status === 'connected' ? 'Backend connected' : 'Connecting...'}</span>
        </div>

        {/* Notification Bell with Badge */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            title="Notifications"
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid #1e293b',
              color: '#94a3b8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              transition: 'all 0.2s',
            }}
          >
            <Bell size={16} />
            <span
              style={{
                position: 'absolute',
                top: '7px',
                right: '7px',
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#ef4444',
                boxShadow: '0 0 6px #ef4444',
              }}
            />
          </button>

          {showNotifications && (
            <div
              style={{
                position: 'absolute',
                right: 0,
                top: '42px',
                width: '280px',
                background: '#0d172c',
                border: '1px solid #1e293b',
                borderRadius: '10px',
                padding: '12px',
                boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                zIndex: 100,
              }}
            >
              <div style={{ fontWeight: 700, fontSize: '0.82rem', color: '#f8fafc', marginBottom: '8px' }}>
                Notifications
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', padding: '8px', background: 'rgba(15,23,42,0.5)', borderRadius: '6px' }}>
                🛡️ All simulation engines and virtual networks are operational.
              </div>
            </div>
          )}
        </div>

        {/* User Account / Avatar */}
        {isAuthenticated && user ? (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '3px',
                borderRadius: '50%',
                background: 'none',
                border: '2px solid rgba(56, 189, 248, 0.4)',
                cursor: 'pointer',
              }}
              title={user.display_name || user.username}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #0284c7 0%, #1e40af 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                }}
              >
                {(user.display_name || user.username).charAt(0).toUpperCase()}
              </div>
            </button>

            {showUserMenu && (
              <div
                style={{
                  position: 'absolute',
                  right: 0,
                  top: '44px',
                  width: '210px',
                  background: '#0d172c',
                  border: '1px solid #1e293b',
                  borderRadius: '10px',
                  padding: '12px',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                  zIndex: 100,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                }}
              >
                <div style={{ borderBottom: '1px solid #1e293b', paddingBottom: '8px', marginBottom: '4px' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f8fafc' }}>
                    {user.display_name || user.username}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#38bdf8' }}>
                    {user.role} • {user.current_level}
                  </div>
                </div>

                <Link
                  to="/portfolio"
                  onClick={() => setShowUserMenu(false)}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', fontSize: '0.78rem', color: '#cbd5e1' }}
                >
                  <User size={14} />
                  <span>My Portfolio</span>
                </Link>
                <Link
                  to="/settings"
                  onClick={() => setShowUserMenu(false)}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', fontSize: '0.78rem', color: '#cbd5e1' }}
                >
                  <ExternalLink size={14} />
                  <span>Settings</span>
                </Link>
                <button
                  onClick={() => { setShowUserMenu(false); logout() }}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', fontSize: '0.78rem', color: '#f87171', width: '100%' }}
                >
                  <LogOut size={14} />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link
            to="/login"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#ffffff',
              borderRadius: '8px',
              fontSize: '0.8rem',
              fontWeight: 600,
              textDecoration: 'none',
              boxShadow: '0 2px 8px rgba(2, 132, 199, 0.3)',
            }}
          >
            <LogIn size={14} />
            <span>Sign In</span>
          </Link>
        )}
      </div>
    </header>
  )
}
