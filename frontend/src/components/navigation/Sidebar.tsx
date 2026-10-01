import React from 'react'
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
  FileText,
  Lock,
} from 'lucide-react'

export const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <Shield size={20} />
        </div>
        <div className="brand-text">
          <h1>NexoraNet</h1>
          <p>Cybersecurity Lab</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-title">Overview</div>
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard />
          <span>Dashboard</span>
        </NavLink>

        <div className="nav-section-title">Core Curriculum</div>
        <NavLink
          to="/learning"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <BookOpen />
          <span>Networking Track</span>
        </NavLink>
        <NavLink
          to="/labs"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Terminal />
          <span>Hands-on Labs</span>
        </NavLink>
        <NavLink
          to="/mock-tests"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <FileCheck2 />
          <span>Mock Tests</span>
        </NavLink>
        <NavLink
          to="/adaptive-test"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Compass />
          <span>Adaptive Practice</span>
        </NavLink>
        <NavLink
          to="/challenges"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Trophy />
          <span>Challenges</span>
        </NavLink>

        <div className="nav-section-title">Interactive Sandboxes</div>
        <NavLink
          to="/network-simulator"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Network />
          <span>Network Simulator</span>
        </NavLink>
        <NavLink
          to="/packet-analysis"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Binary />
          <span>Packet Analysis</span>
        </NavLink>
        <NavLink
          to="/detection"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <ShieldAlert />
          <span>Detection Engine</span>
        </NavLink>
        <NavLink
          to="/soc"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Radio />
          <span>Mini SOC</span>
        </NavLink>
        <NavLink
          to="/threat-intelligence"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Target />
          <span>Threat Intelligence</span>
        </NavLink>
        <NavLink
          to="/threat-hunting"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Crosshair />
          <span>Threat Hunting</span>
        </NavLink>
        <NavLink
          to="/siem"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Database />
          <span>SIEM Log Engine</span>
        </NavLink>
        <NavLink
          to="/endpoint-security"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Monitor />
          <span>Endpoint Security</span>
        </NavLink>
        <NavLink
          to="/soc/incidents"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Flame />
          <span>Incident Response</span>
        </NavLink>
        <NavLink
          to="/soc/mitre"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Grid3X3 />
          <span>MITRE ATT&CK</span>
        </NavLink>
        <NavLink
          to="/soc/playbooks"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <BookMarked />
          <span>IR Playbooks</span>
        </NavLink>
        <NavLink
          to="/soc/automation"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Zap />
          <span>SOAR Automation</span>
        </NavLink>
        <NavLink
          to="/soc/scenarios"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Workflow />
          <span>SOC Scenarios</span>
        </NavLink>

        <div className="nav-section-title">Student Profile</div>
        <NavLink
          to="/progress"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <BarChart3 />
          <span>Progress Matrix</span>
        </NavLink>
        <NavLink
          to="/progress/skills"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Shield />
          <span>Skill Assessment</span>
        </NavLink>
        <NavLink
          to="/progress/assessment"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <FileText />
          <span>Assessment Report</span>
        </NavLink>
        <NavLink
          to="/portfolio"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Award />
          <span>Showcase Portfolio</span>
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Settings />
          <span>Settings</span>
        </NavLink>

        <div className="nav-section-title">Administration</div>
        <NavLink
          to="/admin"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Lock />
          <span>Admin Operations</span>
        </NavLink>
      </nav>
    </aside>
  )
}
