import React from 'react'
import { NavLink } from 'react-router-dom'
import './threat_hunting.css'

interface ThreatHuntingNavProps {
  currentHuntId?: string | number
  huntCode?: string
}

export const ThreatHuntingNav: React.FC<ThreatHuntingNavProps> = ({ currentHuntId, huntCode }) => {
  return (
    <div className="threat-hunting-nav">
      <NavLink
        to="/threat-hunting"
        end
        className={({ isActive }) => `threat-hunting-nav-tab ${isActive ? 'active' : ''}`}
      >
        <span>📊</span> Dashboard
      </NavLink>
      <NavLink
        to="/threat-hunting/scenarios"
        className={({ isActive }) => `threat-hunting-nav-tab ${isActive ? 'active' : ''}`}
      >
        <span>🎯</span> Training Scenarios
      </NavLink>
      {currentHuntId && (
        <NavLink
          to={`/threat-hunting/hunts/${currentHuntId}`}
          className={({ isActive }) => `threat-hunting-nav-tab ${isActive ? 'active' : ''}`}
        >
          <span>🔬</span> Active Workspace {huntCode ? `(${huntCode})` : ''}
        </NavLink>
      )}
    </div>
  )
}
