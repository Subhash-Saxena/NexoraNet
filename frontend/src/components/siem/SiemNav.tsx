import React from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Search, Database, ShieldAlert, GraduationCap } from 'lucide-react'

export const SiemNav: React.FC = () => {
  return (
    <nav className="siem-nav">
      <NavLink
        to="/siem"
        end
        className={({ isActive }) => `siem-nav-link ${isActive ? 'active' : ''}`}
      >
        <LayoutDashboard size={16} />
        <span>Overview</span>
      </NavLink>

      <NavLink
        to="/siem/search"
        className={({ isActive }) => `siem-nav-link ${isActive ? 'active' : ''}`}
      >
        <Search size={16} />
        <span>Log Search & Analytics</span>
      </NavLink>

      <NavLink
        to="/siem/datasets"
        className={({ isActive }) => `siem-nav-link ${isActive ? 'active' : ''}`}
      >
        <Database size={16} />
        <span>Datasets & Ingestion</span>
      </NavLink>

      <NavLink
        to="/siem/rules"
        className={({ isActive }) => `siem-nav-link ${isActive ? 'active' : ''}`}
      >
        <ShieldAlert size={16} />
        <span>Correlation Rules & Alerts</span>
      </NavLink>

      <NavLink
        to="/siem/labs"
        className={({ isActive }) => `siem-nav-link ${isActive ? 'active' : ''}`}
      >
        <GraduationCap size={16} />
        <span>Practice Labs</span>
      </NavLink>
    </nav>
  )
}
