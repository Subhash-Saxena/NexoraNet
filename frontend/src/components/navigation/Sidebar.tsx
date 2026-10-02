import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  Shield,
  LayoutDashboard,
  BookOpen,
  Terminal,
  FileCheck2,
  Compass,
  Trophy,
  Network,
  Binary,
  Radio,
  ShieldAlert,
  Target,
  Crosshair,
  BarChart3,
  Settings,
  Database,
  Monitor,
  Flame,
  Grid3X3,
  BookMarked,
  Zap,
  Workflow,
  Award,
  Lock,
  LogIn,
  ChevronsLeft,
  ChevronsRight,
  X,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

interface SidebarProps {
  mobileOpen?: boolean
  onCloseMobile?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen = false, onCloseMobile }) => {
  const { user, isAuthenticated } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  const handleNavClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('a') && onCloseMobile) {
      onCloseMobile()
    }
  }

  return (
    <aside
      className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}
      style={{
        width: collapsed ? '72px' : '260px',
        transition: 'width 0.2s ease, transform 0.28s ease',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Brand Header */}
      <div
        className="sidebar-header"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: collapsed ? '16px 12px' : '20px 20px',
          borderBottom: '1px solid #14223d',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="brand-icon" style={{ flexShrink: 0 }}>
            <Shield size={20} />
          </div>
          {!collapsed && (
            <div className="brand-text">
              <h1 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>NexoraNet</h1>
              <p style={{ fontSize: '0.68rem', color: '#38bdf8', letterSpacing: '0.08em', margin: 0, textTransform: 'uppercase', fontWeight: 600 }}>Cybersecurity Lab</p>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="sidebar-collapse-desktop-btn"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#64748b',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '4px',
            }}
          >
            {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
          </button>
          <button
            onClick={onCloseMobile}
            className="sidebar-mobile-close-btn"
            title="Close sidebar"
            aria-label="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav
        className="sidebar-nav"
        onClick={handleNavClick}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: collapsed ? '12px 6px' : '14px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '2px',
        }}
      >
        {/* OVERVIEW */}
        <div className="nav-section-title" style={{ padding: collapsed ? '8px 4px 4px' : '10px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
          {!collapsed && 'Overview'}
        </div>
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Dashboard"
        >
          <LayoutDashboard size={18} />
          {!collapsed && <span>Dashboard</span>}
        </NavLink>

        {/* CORE CURRICULUM */}
        <div className="nav-section-title" style={{ padding: collapsed ? '12px 4px 4px' : '14px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
          {!collapsed && 'Core Curriculum'}
        </div>
        <NavLink
          to="/learning"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Networking Track"
        >
          <BookOpen size={18} />
          {!collapsed && <span>Networking Track</span>}
        </NavLink>
        <NavLink
          to="/labs"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Hands-on Labs"
        >
          <Terminal size={18} />
          {!collapsed && <span>Hands-on Labs</span>}
        </NavLink>
        <NavLink
          to="/mock-tests"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Mock Tests"
        >
          <FileCheck2 size={18} />
          {!collapsed && <span>Mock Tests</span>}
        </NavLink>
        <NavLink
          to="/adaptive-test"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Adaptive Practice"
        >
          <Compass size={18} />
          {!collapsed && <span>Adaptive Practice</span>}
        </NavLink>
        <NavLink
          to="/challenges"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Challenges"
        >
          <Trophy size={18} />
          {!collapsed && <span>Challenges</span>}
        </NavLink>

        {/* INTERACTIVE SANDBOXES */}
        <div className="nav-section-title" style={{ padding: collapsed ? '12px 4px 4px' : '14px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
          {!collapsed && 'Interactive Sandboxes'}
        </div>
        <NavLink
          to="/network-simulator"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Network Simulator"
        >
          <Network size={18} />
          {!collapsed && <span>Network Simulator</span>}
        </NavLink>
        <NavLink
          to="/packet-analysis"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Packet Analysis"
        >
          <Binary size={18} />
          {!collapsed && <span>Packet Analysis</span>}
        </NavLink>
        <NavLink
          to="/detection"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Detection Engine"
        >
          <ShieldAlert size={18} />
          {!collapsed && <span>Detection Engine</span>}
        </NavLink>
        <NavLink
          to="/soc"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Mini SOC"
        >
          <Radio size={18} />
          {!collapsed && <span>Mini SOC</span>}
        </NavLink>
        <NavLink
          to="/threat-intelligence"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Threat Intelligence"
        >
          <Target size={18} />
          {!collapsed && <span>Threat Intelligence</span>}
        </NavLink>
        <NavLink
          to="/threat-hunting"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Threat Hunting"
        >
          <Crosshair size={18} />
          {!collapsed && <span>Threat Hunting</span>}
        </NavLink>
        <NavLink
          to="/siem"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="SIEM Log Engine"
        >
          <Database size={18} />
          {!collapsed && <span>SIEM Log Engine</span>}
        </NavLink>
        <NavLink
          to="/endpoint-security"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Endpoint Security"
        >
          <Monitor size={18} />
          {!collapsed && <span>Endpoint Security</span>}
        </NavLink>

        {/* SOC OPERATIONS */}
        <div className="nav-section-title" style={{ padding: collapsed ? '12px 4px 4px' : '14px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
          {!collapsed && 'SOC Operations'}
        </div>
        <NavLink
          to="/soc/incidents"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Incident Response"
        >
          <Flame size={18} />
          {!collapsed && <span>Incident Response</span>}
        </NavLink>
        <NavLink
          to="/soc/mitre"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="MITRE ATT&CK"
        >
          <Grid3X3 size={18} />
          {!collapsed && <span>MITRE ATT&CK</span>}
        </NavLink>
        <NavLink
          to="/soc/playbooks"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="IR Playbooks"
        >
          <BookMarked size={18} />
          {!collapsed && <span>IR Playbooks</span>}
        </NavLink>
        <NavLink
          to="/soc/automation"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="SOAR Automation"
        >
          <Zap size={18} />
          {!collapsed && <span>SOAR Automation</span>}
        </NavLink>
        <NavLink
          to="/soc/scenarios"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="SOC Scenarios"
        >
          <Workflow size={18} />
          {!collapsed && <span>SOC Scenarios</span>}
        </NavLink>

        {/* STUDENT PROFILE */}
        <div className="nav-section-title" style={{ padding: collapsed ? '12px 4px 4px' : '14px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
          {!collapsed && 'Profile & Settings'}
        </div>
        <NavLink
          to="/progress"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Progress Matrix"
        >
          <BarChart3 size={18} />
          {!collapsed && <span>Progress Matrix</span>}
        </NavLink>
        <NavLink
          to="/portfolio"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Showcase Portfolio"
        >
          <Award size={18} />
          {!collapsed && <span>Showcase Portfolio</span>}
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          title="Settings"
        >
          <Settings size={18} />
          {!collapsed && <span>Settings</span>}
        </NavLink>

        {/* ADMINISTRATION (Admins Only) */}
        {isAuthenticated && user?.role === 'ADMIN' && (
          <>
            <div className="nav-section-title" style={{ padding: collapsed ? '12px 4px 4px' : '14px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
              {!collapsed && 'Administration'}
            </div>
            <NavLink
              to="/admin"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              title="Admin Operations"
            >
              <Lock size={18} />
              {!collapsed && <span>Admin Operations</span>}
            </NavLink>
          </>
        )}

        {/* ACCOUNT */}
        <div className="nav-section-title" style={{ padding: collapsed ? '12px 4px 4px' : '14px 12px 4px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', fontWeight: 700 }}>
          {!collapsed && 'Account'}
        </div>
        {isAuthenticated && user ? (
          <NavLink
            to="/portfolio"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            title="Account Profile"
          >
            <Shield size={18} />
            {!collapsed && <span>{user.display_name || user.username} ({user.role})</span>}
          </NavLink>
        ) : (
          <NavLink
            to="/login"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            style={{ color: '#60a5fa' }}
            title="Sign In / Register"
          >
            <LogIn size={18} />
            {!collapsed && <span>Sign In / Register</span>}
          </NavLink>
        )}
      </nav>
    </aside>
  )
}
