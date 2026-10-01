import React from 'react'
import { NavLink } from 'react-router-dom'
import './endpointSecurity.css'

interface EndpointNavProps {
  currentHostId?: string
  currentInvestigationId?: string | number
}

export const EndpointNav: React.FC<EndpointNavProps> = ({ currentHostId, currentInvestigationId }) => {
  return (
    <nav className="endpoint-nav" aria-label="Endpoint Security Navigation">
      <NavLink
        to="/endpoint-security"
        end
        className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
      >
        <span>🖥️</span> Dashboard
      </NavLink>

      <NavLink
        to="/endpoint-security/hosts"
        className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
      >
        <span>💻</span> Host Inventory
      </NavLink>

      {currentHostId && (
        <NavLink
          to={`/endpoint-security/hosts/${currentHostId}`}
          className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
        >
          <span>🔍</span> Host Workbench ({currentHostId})
        </NavLink>
      )}

      <NavLink
        to="/endpoint-security/events"
        className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
      >
        <span>📋</span> Events Explorer
      </NavLink>

      <NavLink
        to="/endpoint-security/investigations"
        className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
      >
        <span>🕵️</span> Investigations
      </NavLink>

      {currentInvestigationId && (
        <NavLink
          to={`/endpoint-security/investigations/${currentInvestigationId}`}
          className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
        >
          <span>📁</span> Case #{currentInvestigationId}
        </NavLink>
      )}

      <NavLink
        to="/endpoint-security/scenarios"
        className={({ isActive }) => `endpoint-nav-link ${isActive ? 'active' : ''}`}
      >
        <span>🎯</span> Guided Scenarios
      </NavLink>
    </nav>
  )
}
