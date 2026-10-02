import React from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from '../components/navigation/Sidebar'
import { Navbar } from '../components/navigation/Navbar'
import { ErrorBoundary } from '../components/common/ErrorBoundary'

const routeTitles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Security Operations & Learning Dashboard', subtitle: 'Interactive computer networking & defensive cybersecurity' },
  '/dashboard': { title: 'Security Operations & Learning Dashboard', subtitle: 'Interactive computer networking & defensive cybersecurity' },
  '/learning': { title: 'Structured Networking Curriculum', subtitle: 'Layer-by-layer progressive network fundamentals' },
  '/labs': { title: 'Hands-on Networking & Security Labs', subtitle: 'Isolated sandboxes with strict target boundary enforcement' },
  '/mock-tests': { title: 'Mock Tests & Certification Practice', subtitle: 'Exam engine for CCNA, CompTIA Network+, and Security+' },
  '/challenges': { title: 'Security Challenges & CTF Drills', subtitle: 'Real-world defensive scenarios and attack-path analysis' },
  '/network-simulator': { title: 'Interactive Network Simulator', subtitle: 'Visual topology builder and packet traversal sandbox' },
  '/packet-analysis': { title: 'PCAP & Packet Analyzer', subtitle: 'Deep packet inspection and malicious flow forensics' },
  '/soc': { title: 'Mini SOC Incident Center', subtitle: 'Simulated alert queues, triage workflows, and incident response' },
  '/threat-intelligence': { title: 'Threat Intelligence Platform', subtitle: 'IOC investigation, indicator correlation, and watchlists' },
  '/threat-hunting': { title: 'Threat Hunting Workspace', subtitle: 'Hypothesis-driven adversary hunt campaigns' },
  '/siem': { title: 'SIEM & Security Log Analysis', subtitle: 'Event correlation, rule engine, and dataset forensics' },
  '/endpoint-security': { title: 'Endpoint Security & Host Investigation', subtitle: 'Process trees, telemetry forensics, and incident response' },
  '/detection': { title: 'Detection Engineering', subtitle: 'Rule authoring, alert management, and coverage analysis' },
  '/progress': { title: 'Skill Progression & Analytics', subtitle: 'Competency matrix and personalized study guidance' },
  '/adaptive-test': { title: 'Adaptive Assessment Engine', subtitle: 'Personalized difficulty calibration and skill gap analysis' },
  '/settings': { title: 'Platform Settings & Boundaries', subtitle: 'Configuration defaults and safe lab execution parameters' },
  '/portfolio': { title: 'Analyst Portfolio', subtitle: 'Verified skill certificates and shareable achievement records' },
  '/admin': { title: 'Admin Control Plane', subtitle: 'Platform configuration, content management, and audit logs' },
  '/login': { title: 'Sign In to NexoraNet', subtitle: 'Authenticate to access personalized learning and progress tracking' },
  '/register': { title: 'Create Account', subtitle: 'Join the NexoraNet cybersecurity learning platform' },
}

function getRouteLabel(pathname: string): string {
  // Extract a human-readable section name from the path
  const parts = pathname.split('/').filter(Boolean)
  if (!parts.length) return 'Dashboard'
  const map: Record<string, string> = {
    'endpoint-security': 'Endpoint Security',
    'threat-intelligence': 'Threat Intelligence',
    'threat-hunting': 'Threat Hunting',
    'soc': 'SOC Operations',
    'siem': 'SIEM & Logs',
    'network-simulator': 'Network Simulator',
    'packet-analysis': 'Packet Analysis',
    'mock-tests': 'Mock Tests',
    'labs': 'Labs',
    'learning': 'Learning',
    'challenges': 'Challenges',
    'detection': 'Detection Engine',
    'admin': 'Admin Panel',
    'portfolio': 'Portfolio',
    'progress': 'Progress',
    'settings': 'Settings',
  }
  return map[parts[0]] ?? parts[0].replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export const MainLayout: React.FC = () => {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)

  // Automatically close mobile menu when navigating to another route
  React.useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  // Close mobile drawer on Escape key press
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [mobileMenuOpen])

  let currentInfo = routeTitles[location.pathname]
  if (!currentInfo) {
    const prefix = '/' + location.pathname.split('/')[1]
    currentInfo = routeTitles[prefix] ?? {
      title: 'NexoraNet Platform',
      subtitle: 'Learn. Simulate. Analyze. Defend.',
    }
  }

  const pageLabel = getRouteLabel(location.pathname)

  return (
    <div className="app-container">
      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="mobile-backdrop"
          onClick={() => setMobileMenuOpen(false)}
          aria-label="Close navigation menu"
        />
      )}

      <Sidebar
        mobileOpen={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      <div className="main-content-wrapper">
        <Navbar
          title={currentInfo.title}
          subtitle={currentInfo.subtitle}
          onToggleMobileMenu={() => setMobileMenuOpen((prev) => !prev)}
        />
        <main className="page-body">
          <ErrorBoundary key={location.pathname} label={pageLabel}>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
