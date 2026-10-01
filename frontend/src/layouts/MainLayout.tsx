import React from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from '../components/navigation/Sidebar'
import { Navbar } from '../components/navigation/Navbar'

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
  '/progress': { title: 'Skill Progression & Analytics', subtitle: 'Competency matrix and personalized study guidance' },
  '/settings': { title: 'Platform Settings & Boundaries', subtitle: 'Configuration defaults and safe lab execution parameters' },
}

export const MainLayout: React.FC = () => {
  const location = useLocation()
  let currentInfo = routeTitles[location.pathname]
  if (!currentInfo) {
    if (location.pathname.startsWith('/packet-analysis')) {
      currentInfo = routeTitles['/packet-analysis']
    } else if (location.pathname.startsWith('/network-simulator')) {
      currentInfo = routeTitles['/network-simulator']
    } else {
      currentInfo = {
        title: 'NexoraNet Platform',
        subtitle: 'Learn. Simulate. Analyze. Defend.',
      }
    }
  }

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content-wrapper">
        <Navbar title={currentInfo.title} subtitle={currentInfo.subtitle} />
        <main className="page-body">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
