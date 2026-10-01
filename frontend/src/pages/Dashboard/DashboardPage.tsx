import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  GraduationCap,
  Terminal,
  FileCheck,
  Network,
  ShieldAlert,
  Award,
  ArrowRight,
  ShieldCheck,
  Binary,
  Radio,
  Sliders,
} from 'lucide-react'
import { MetricCard } from '../../components/common/MetricCard'
import { LearningPathFlow } from './LearningPathFlow'
import { apiService } from '../../services/api'
import type { LearningProgressResponse, StudentDashboardMetrics, LabTelemetry } from '../../types'

const DEFAULT_METRICS: StudentDashboardMetrics = {
  learningProgress: 0,
  labsCompleted: 0,
  mockTests: 2,
  networkingSkills: 35,
  securitySkills: 20,
  currentLevel: 'Cadet Defend-I',
}

export const DashboardPage: React.FC = () => {
  const [progress, setProgress] = useState<LearningProgressResponse | null>(null)
  const [labTelemetry, setLabTelemetry] = useState<LabTelemetry | null>(null)

  useEffect(() => {
    let active = true
    apiService
      .getLearningProgress()
      .then((data) => {
        if (active) setProgress(data)
      })
      .catch(() => {})

    apiService
      .getLabTelemetry()
      .then((data) => {
        if (active) setLabTelemetry(data)
      })
      .catch(() => {})

    return () => {
      active = false
    }
  }, [])

  const metrics = {
    ...DEFAULT_METRICS,
    learningProgress: progress ? progress.overall_percentage : DEFAULT_METRICS.learningProgress,
    labsCompleted: labTelemetry ? labTelemetry.completed_labs : DEFAULT_METRICS.labsCompleted,
    currentLevel: progress ? progress.current_level : DEFAULT_METRICS.currentLevel,
  }

  return (
    <div>
      {/* Platform Welcome Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)',
          border: '1px solid rgba(6, 182, 212, 0.2)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px 28px',
          marginBottom: '28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
            Welcome to NexoraNet
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Interactive Computer Networking & Cybersecurity Platform &bull;{' '}
            <strong style={{ color: 'var(--cyan-primary)' }}>Learn. Simulate. Analyze. Defend.</strong>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link
            to="/learning"
            style={{
              background: 'var(--cyan-primary)',
              color: '#020617',
              fontWeight: 600,
              padding: '8px 18px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            Start Learning <ArrowRight size={14} />
          </Link>
          <Link
            to="/labs"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-main)',
              fontWeight: 500,
              padding: '8px 18px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem',
            }}
          >
            Explore Labs
          </Link>
        </div>
      </div>

      {/* Required Placeholder KPI Metric Cards */}
      <div className="metrics-grid">
        <MetricCard
          label="Learning Progress"
          value={`${metrics.learningProgress}%`}
          hint={progress ? `${progress.completed_lessons} of ${progress.total_lessons} lessons completed` : '38 curated curriculum lessons'}
          icon={<GraduationCap size={18} />}
        />
        <MetricCard
          label="Labs Completed"
          value={metrics.labsCompleted}
          hint={labTelemetry ? `${labTelemetry.completed_labs} of ${labTelemetry.total_labs} labs completed` : 'Target: 22 interactive exercises'}
          icon={<Terminal size={18} />}
        />
        <MetricCard
          label="Mock Tests"
          value={metrics.mockTests}
          hint="Avg Score: 85% (Passing)"
          icon={<FileCheck size={18} />}
        />
        <MetricCard
          label="Networking Skills"
          value={`${metrics.networkingSkills}%`}
          hint="Layer 2 & Layer 3 mastery"
          icon={<Network size={18} />}
        />
        <MetricCard
          label="Security Skills"
          value={`${metrics.securitySkills}%`}
          hint="Boundary & defense drills"
          icon={<ShieldAlert size={18} />}
        />
        <MetricCard
          label="Current Level"
          value={metrics.currentLevel}
          hint="Tier 1 Foundation Candidate"
          icon={<Award size={18} />}
        />
      </div>

      {/* Required Learning Path Section: Beginner -> Intermediate -> Advanced -> Cyber Defense -> Mini SOC */}
      <LearningPathFlow />

      {/* Platform Exploration Grid */}
      <div style={{ marginTop: '36px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-main)' }}>
            NexoraNet Platform Modules
          </h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Step 1 Architecture Foundation Active
          </span>
        </div>

        <div className="modules-grid">
          {/* Networking Curriculum */}
          <div className="module-card">
            <div>
              <div className="module-card-header">
                <div className="module-icon-wrap">
                  <Network size={20} />
                </div>
                <span className="badge badge-phase">Phase 2</span>
              </div>
              <div className="module-title">Structured Curriculum</div>
              <p className="module-desc">
                Interactive breakdowns of OSI, TCP/IP, IP subnetting, routing protocols (OSPF/BGP), and transport layer semantics.
              </p>
            </div>
            <Link to="/learning" className="nav-link" style={{ padding: '8px 0', color: 'var(--cyan-primary)' }}>
              Inspect Curriculum <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Link>
          </div>

          {/* Hands-on Labs */}
          <div className="module-card">
            <div>
              <div className="module-card-header">
                <div className="module-icon-wrap">
                  <Terminal size={20} />
                </div>
                <span className="badge badge-phase">Phase 3</span>
              </div>
              <div className="module-title">Hands-on Labs</div>
              <p className="module-desc">
                Container-isolated virtual networking topologies with strict localhost and lab subnet target containment.
              </p>
            </div>
            <Link to="/labs" className="nav-link" style={{ padding: '8px 0', color: 'var(--cyan-primary)' }}>
              Inspect Labs <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Link>
          </div>

          {/* Network Simulator */}
          <div className="module-card">
            <div>
              <div className="module-card-header">
                <div className="module-icon-wrap">
                  <Sliders size={20} />
                </div>
                <span className="badge badge-phase">Phase 3</span>
              </div>
              <div className="module-title">Network Simulator</div>
              <p className="module-desc">
                Interactive canvas for building topologies, configuring IP interfaces, and watching packet frames traverse routers.
              </p>
            </div>
            <Link to="/network-simulator" className="nav-link" style={{ padding: '8px 0', color: 'var(--cyan-primary)' }}>
              Inspect Simulator <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Link>
          </div>

          {/* PCAP Packet Analysis */}
          <div className="module-card">
            <div>
              <div className="module-card-header">
                <div className="module-icon-wrap">
                  <Binary size={20} />
                </div>
                <span className="badge badge-phase">Phase 4</span>
              </div>
              <div className="module-title">Packet Analysis</div>
              <p className="module-desc">
                Wireshark-grade browser packet dissector for inspecting TCP handshakes, DNS exfiltration, and attack signatures.
              </p>
            </div>
            <Link to="/packet-analysis" className="nav-link" style={{ padding: '8px 0', color: 'var(--cyan-primary)' }}>
              Inspect Analyzer <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Link>
          </div>

          {/* Mini SOC */}
          <div className="module-card">
            <div>
              <div className="module-card-header">
                <div className="module-icon-wrap">
                  <Radio size={20} />
                </div>
                <span className="badge badge-phase">Phase 5</span>
              </div>
              <div className="module-title">Mini SOC Center</div>
              <p className="module-desc">
                Realistic security operations center with simulated SIEM alert queues, triage workflows, and incident reports.
              </p>
            </div>
            <Link to="/soc" className="nav-link" style={{ padding: '8px 0', color: 'var(--cyan-primary)' }}>
              Inspect SOC <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Link>
          </div>

          {/* Security Safeguards */}
          <div className="module-card" style={{ background: 'rgba(16, 185, 129, 0.04)', borderColor: 'rgba(16, 185, 129, 0.2)' }}>
            <div>
              <div className="module-card-header">
                <div className="module-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--emerald-success)' }}>
                  <ShieldCheck size={20} />
                </div>
                <span className="badge badge-ready">Enforced</span>
              </div>
              <div className="module-title">Lab Isolation Boundary</div>
              <p className="module-desc">
                All platform commands and simulator tools are strictly restricted to localhost (127.0.0.1) and safe virtual lab CIDR (10.99.0.0/16).
              </p>
            </div>
            <Link to="/settings" className="nav-link" style={{ padding: '8px 0', color: 'var(--emerald-success)' }}>
              View Security Rules <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
