import React from 'react'
import { NavLink } from 'react-router-dom'
import './threat_intel.css'

export const ThreatIntelNav: React.FC = () => {
  return (
    <div className="threat-intel-tabs">
      <NavLink
        to="/threat-intelligence"
        end
        className={({ isActive }) => `threat-intel-tab ${isActive ? 'active' : ''}`}
      >
        <span>📊</span> Dashboard
      </NavLink>
      <NavLink
        to="/threat-intelligence/indicators"
        className={({ isActive }) => `threat-intel-tab ${isActive ? 'active' : ''}`}
      >
        <span>🎯</span> Indicators (IOCs)
      </NavLink>
      <NavLink
        to="/threat-intelligence/search"
        className={({ isActive }) => `threat-intel-tab ${isActive ? 'active' : ''}`}
      >
        <span>🔍</span> Search & OSINT
      </NavLink>
      <NavLink
        to="/threat-intelligence/watchlist"
        className={({ isActive }) => `threat-intel-tab ${isActive ? 'active' : ''}`}
      >
        <span>👁️</span> Watchlist
      </NavLink>
      <NavLink
        to="/threat-intelligence/graph"
        className={({ isActive }) => `threat-intel-tab ${isActive ? 'active' : ''}`}
      >
        <span>🕸️</span> Correlation Graph
      </NavLink>
      <NavLink
        to="/threat-intelligence/challenges"
        className={({ isActive }) => `threat-intel-tab ${isActive ? 'active' : ''}`}
      >
        <span>🏆</span> Investigation Challenges
      </NavLink>
    </div>
  )
}
