import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  Shield,
  LayoutDashboard,
  BookOpen,
  FlaskConical,
  FileCheck2,
  Compass,
  Trophy,
  Network,
  Binary,
  ShieldAlert,
  Radio,
  Target,
  Crown,
  ArrowRight,
  ChevronsLeft,
  ChevronsRight,
  Lock,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export const Sidebar: React.FC = () => {
  const { user, isAuthenticated } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`} style={{ width: collapsed ? '72px' : '260px', transition: 'width 0.2s ease' }}>
      {/* Brand Header */}
      <div className="sidebar-header" style={{ justifyContent: 'space-between', padding: collapsed ? '16px 12px' : '20px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="brand-icon" style={{ flexShrink: 0 }}>
            <Shield size={20} />
          </div>
          {!collapsed && (
            <div className="brand-text">
              <h1>NexoraNet</h1>
              <p>Cybersecurity Lab</p>
            </div>
          )}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="sidebar-collapse-btn"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          style={{
            color: '#64748b',
            padding: '4px',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'color 0.2s',
          }}
        >
          {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        {/* OVERVIEW */}
        {!collapsed && <div className="nav-section-title">OVERVIEW</div>}
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Dashboard"
        >
          <LayoutDashboard />
          {!collapsed && <span>Dashboard</span>}
        </NavLink>

        {/* LEARNING */}
        {!collapsed && <div className="nav-section-title">LEARNING</div>}
        <NavLink
          to="/learning"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Learning Track"
        >
          <BookOpen />
          {!collapsed && <span>Learning Track</span>}
        </NavLink>
        <NavLink
          to="/labs"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Hands-on Labs"
        >
          <FlaskConical />
          {!collapsed && <span>Hands-on Labs</span>}
        </NavLink>

        {/* ASSESSMENTS */}
        {!collapsed && <div className="nav-section-title">ASSESSMENTS</div>}
        <NavLink
          to="/mock-tests"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Mock Tests"
        >
          <FileCheck2 />
          {!collapsed && <span>Mock Tests</span>}
        </NavLink>
        <NavLink
          to="/adaptive-test"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Adaptive Practice"
        >
          <Compass />
          {!collapsed && <span>Adaptive Practice</span>}
        </NavLink>
        <NavLink
          to="/challenges"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Challenges"
        >
          <Trophy />
          {!collapsed && <span>Challenges</span>}
        </NavLink>

        {/* SANDBOX & TOOLS */}
        {!collapsed && <div className="nav-section-title">SANDBOX & TOOLS</div>}
        <NavLink
          to="/network-simulator"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Network Simulator"
        >
          <Network />
          {!collapsed && <span>Network Simulator</span>}
        </NavLink>
        <NavLink
          to="/packet-analysis"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Packet Analysis"
        >
          <Binary />
          {!collapsed && <span>Packet Analysis</span>}
        </NavLink>
        <NavLink
          to="/detection"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Detection Engine"
        >
          <ShieldAlert />
          {!collapsed && <span>Detection Engine</span>}
        </NavLink>
        <NavLink
          to="/soc"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Mini SOC"
        >
          <Radio />
          {!collapsed && <span>Mini SOC</span>}
        </NavLink>
        <NavLink
          to="/threat-intelligence"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Threat Intelligence"
        >
          <Target />
          {!collapsed && <span>Threat Intelligence</span>}
        </NavLink>

        {/* Compact Admin / Settings Link if User is Admin or logged in */}
        {isAuthenticated && user?.role === 'ADMIN' && (
          <NavLink
            to="/admin"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            title="Admin Operations"
            style={{ marginTop: '8px' }}
          >
            <Lock />
            {!collapsed && <span>Admin Operations</span>}
          </NavLink>
        )}
      </nav>

      {/* Upgrade Your Skills Bottom Promo Card */}
      {!collapsed && (
        <div style={{ padding: '16px', borderTop: '1px solid #14223d' }}>
          <div
            style={{
              background: 'linear-gradient(180deg, #0e1930 0%, #0a1122 100%)',
              border: '1px solid #1b2c4e',
              borderRadius: '12px',
              padding: '16px',
              boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  background: 'rgba(245, 158, 11, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fbbf24',
                }}
              >
                <Crown size={16} />
              </div>
              <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Upgrade Your Skills
              </h4>
            </div>
            <p style={{ fontSize: '0.74rem', color: '#94a3b8', lineHeight: 1.4, margin: '0 0 12px' }}>
              Unlock advanced labs, certifications and more.
            </p>
            <NavLink
              to="/portfolio"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                width: '100%',
                padding: '7px',
                borderRadius: '6px',
                background: 'rgba(14, 165, 233, 0.1)',
                border: '1px solid rgba(14, 165, 233, 0.3)',
                color: '#38bdf8',
                fontSize: '0.8rem',
                fontWeight: 600,
                textDecoration: 'none',
                transition: 'all 0.2s',
              }}
            >
              <span>View Plans</span>
              <ArrowRight size={13} />
            </NavLink>
          </div>
        </div>
      )}
    </aside>
  )
}
