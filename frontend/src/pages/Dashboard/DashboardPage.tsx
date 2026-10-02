import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BookOpen,
  FlaskConical,
  FileCheck2,
  Network,
  Shield,
  ArrowRight,
  Clock,
  Zap,
  Play,
  Trophy,
  ChevronRight,
  Route,
  Sparkles,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { LearningProgressResponse, LabTelemetry, StudentDashboardMetrics } from '../../types'
import '../../components/dashboard/dashboard.css'

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
      {/* 1. HERO BANNER SECTION */}
      <div className="dashboard-hero">
        {/* Background Cyber Mountain & Highway SVG Scenery */}
        <div className="dashboard-hero-bg" aria-hidden="true">
          <svg viewBox="0 0 700 320" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
            <defs>
              <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.25" />
                <stop offset="60%" stopColor="#080d1a" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#080d1a" stopOpacity="1" />
              </linearGradient>
              <linearGradient id="roadGlow" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.9" />
                <stop offset="50%" stopColor="#38bdf8" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.85" />
              </linearGradient>
              <linearGradient id="mountainGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1e293b" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#0b1329" stopOpacity="0.95" />
              </linearGradient>
              <filter id="cyanGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Stars */}
            <circle cx="120" cy="40" r="1.5" fill="#38bdf8" opacity="0.6" />
            <circle cx="280" cy="25" r="1.2" fill="#ffffff" opacity="0.8" />
            <circle cx="450" cy="60" r="1.8" fill="#38bdf8" opacity="0.7" />
            <circle cx="580" cy="35" r="1.4" fill="#ffffff" opacity="0.5" />
            <circle cx="340" cy="80" r="1.2" fill="#ffffff" opacity="0.4" />

            {/* Distant Mountain Silhouettes */}
            <path d="M100 240 L280 110 L410 210 L560 90 L700 220 L700 320 L100 320 Z" fill="url(#mountainGrad)" />
            <path d="M300 240 L450 140 L580 230 L700 130 L700 320 L300 320 Z" fill="#0f1b34" opacity="0.8" />

            {/* Futuristic Lighthouse / Citadel Tower */}
            <path d="M510 88 L525 88 L522 55 L513 55 Z" fill="#38bdf8" opacity="0.9" />
            <circle cx="517" cy="50" r="12" fill="#38bdf8" opacity="0.3" filter="url(#cyanGlow)" />
            <circle cx="517" cy="50" r="4" fill="#ffffff" />
            <line x1="517" y1="50" x2="400" y2="20" stroke="#38bdf8" strokeWidth="1.5" strokeOpacity="0.4" />
            <line x1="517" y1="50" x2="650" y2="25" stroke="#38bdf8" strokeWidth="1.5" strokeOpacity="0.4" />

            {/* Glowing Winding Cyber Highway */}
            <path
              d="M700 320 Q540 310 490 270 T480 200 T510 160 T517 90"
              fill="none"
              stroke="url(#roadGlow)"
              strokeWidth="6"
              strokeLinecap="round"
              filter="url(#cyanGlow)"
            />
            <path
              d="M700 320 Q540 310 490 270 T480 200 T510 160 T517 90"
              fill="none"
              stroke="#ffffff"
              strokeWidth="2"
              strokeDasharray="6 8"
            />
          </svg>
        </div>

        {/* Hero Left Content */}
        <div className="dashboard-hero-content">
          <span className="dashboard-tag">WELCOME TO NEXORANET</span>
          <h1 className="dashboard-hero-title">
            Learn. Simulate. Analyze. <span className="glow-cyan">Defend.</span>
          </h1>
          <p className="dashboard-hero-desc">
            An interactive cybersecurity platform to build real-world skills through guided learning, hands-on labs and realistic simulations.
          </p>
          <div className="dashboard-hero-actions">
            <Link to="/learning" className="btn-hero-primary">
              <span>Continue learning</span>
              <ArrowRight size={15} />
            </Link>
            <Link to="/labs" className="btn-hero-secondary">
              <FlaskConical size={15} />
              <span>Explore labs</span>
            </Link>
          </div>
        </div>

        {/* Hero Right: Circular Streak Gauge Card */}
        <div className="dashboard-streak-card">
          <div className="streak-circle-wrap">
            <svg viewBox="0 0 86 86">
              <circle
                cx="43"
                cy="43"
                r="36"
                stroke="#1e293b"
                strokeWidth="7"
                fill="none"
              />
              <circle
                cx="43"
                cy="43"
                r="36"
                stroke="url(#streakGradient)"
                strokeWidth="7"
                strokeDasharray="226"
                strokeDashoffset="60"
                strokeLinecap="round"
                fill="none"
              />
              <defs>
                <linearGradient id="streakGradient" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" />
                  <stop offset="100%" stopColor="#38bdf8" />
                </linearGradient>
              </defs>
            </svg>
            <div className="streak-inner-content">
              <span className="streak-fire-icon">🔥</span>
              <span className="streak-number">0</span>
              <span className="streak-sub">Day Streak</span>
            </div>
          </div>

          <div className="streak-text-wrap">
            <h4>Consistency builds mastery.</h4>
            <p>Keep learning to grow your skills and streak!</p>
          </div>
        </div>
      </div>

      {/* 2. 5-COLUMN KPI METRICS ROW */}
      <div className="kpi-metrics-row">
        {/* Metric 1 */}
        <Link to="/learning" className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-card-header-left">
              <div className="kpi-icon" style={{ color: '#38bdf8' }}>
                <BookOpen size={16} />
              </div>
              <span className="kpi-title">Learning Progress</span>
            </div>
            <ChevronRight size={14} className="kpi-chevron" />
          </div>
          <div>
            <div className="kpi-value">{metrics.learningProgress}%</div>
            <div className="kpi-subtext">38 curated curriculum lessons</div>
            <div className="kpi-progress-track">
              <div className="kpi-progress-fill" style={{ width: `${Math.max(metrics.learningProgress, 6)}%` }} />
            </div>
          </div>
        </Link>

        {/* Metric 2 */}
        <Link to="/labs" className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-card-header-left">
              <div className="kpi-icon" style={{ color: '#06b6d4' }}>
                <FlaskConical size={16} />
              </div>
              <span className="kpi-title">Labs Completed</span>
            </div>
            <ChevronRight size={14} className="kpi-chevron" />
          </div>
          <div>
            <div className="kpi-value">{metrics.labsCompleted}</div>
            <div className="kpi-subtext">Target: 22 interactive exercises</div>
            <div className="kpi-progress-track">
              <div className="kpi-progress-fill" style={{ width: `${Math.max((metrics.labsCompleted / 22) * 100, 4)}%` }} />
            </div>
          </div>
        </Link>

        {/* Metric 3 */}
        <Link to="/mock-tests" className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-card-header-left">
              <div className="kpi-icon" style={{ color: '#60a5fa' }}>
                <FileCheck2 size={16} />
              </div>
              <span className="kpi-title">Mock Tests</span>
            </div>
            <ChevronRight size={14} className="kpi-chevron" />
          </div>
          <div>
            <div className="kpi-value">{metrics.mockTests}</div>
            <div className="kpi-subtext">Avg Score: 83% (Passing)</div>
            <div className="kpi-progress-track">
              <div className="kpi-progress-fill" style={{ width: '83%' }} />
            </div>
          </div>
        </Link>

        {/* Metric 4 */}
        <Link to="/progress/skills" className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-card-header-left">
              <div className="kpi-icon" style={{ color: '#2dd4bf' }}>
                <Network size={16} />
              </div>
              <span className="kpi-title">Networking Skills</span>
            </div>
            <ChevronRight size={14} className="kpi-chevron" />
          </div>
          <div>
            <div className="kpi-value">{metrics.networkingSkills}%</div>
            <div className="kpi-subtext">Layer 2 & Layer 3 mastery</div>
            <div className="kpi-progress-track">
              <div className="kpi-progress-fill" style={{ width: `${metrics.networkingSkills}%` }} />
            </div>
          </div>
        </Link>

        {/* Metric 5 */}
        <Link to="/progress/skills" className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-card-header-left">
              <div className="kpi-icon" style={{ color: '#38bdf8' }}>
                <Shield size={16} />
              </div>
              <span className="kpi-title">Security Skills</span>
            </div>
            <ChevronRight size={14} className="kpi-chevron" />
          </div>
          <div>
            <div className="kpi-value">{metrics.securitySkills}%</div>
            <div className="kpi-subtext">Boundary & defence drills</div>
            <div className="kpi-progress-track">
              <div className="kpi-progress-fill" style={{ width: `${metrics.securitySkills}%` }} />
            </div>
          </div>
        </Link>
      </div>

      {/* 3. YOUR LEARNING PATH ROADMAP */}
      <div className="dash-path-card">
        <div className="dash-path-header">
          <div className="dash-path-header-left">
            <div className="dash-path-icon-box">
              <Route size={18} />
            </div>
            <div>
              <div className="dash-path-header-title">Your Learning Path</div>
              <p className="dash-path-header-desc">
                Step-by-step journey from fundamentals to real-world defense.
              </p>
            </div>
          </div>

          <Link to="/learning" className="btn-view-curriculum">
            <span>View Full Curriculum</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {/* 6 Connected Steps */}
        <div className="dash-path-timeline">
          {/* Step 1 */}
          <div className="dash-path-step">
            <div className="dash-path-node active">1</div>
            <div className="dash-path-step-title">Foundations</div>
            <span className="dash-path-status-badge in-progress">In Progress</span>
            <p className="dash-path-step-desc">Networking, OS, protocols</p>
          </div>

          {/* Step 2 */}
          <div className="dash-path-step">
            <div className="dash-path-node">2</div>
            <div className="dash-path-step-title">System & Linux</div>
            <span className="dash-path-status-badge not-started">Not Started</span>
            <p className="dash-path-step-desc">Linux, command line, system internals</p>
          </div>

          {/* Step 3 */}
          <div className="dash-path-step">
            <div className="dash-path-node">3</div>
            <div className="dash-path-step-title">Cybersecurity Core</div>
            <span className="dash-path-status-badge not-started">Not Started</span>
            <p className="dash-path-step-desc">Threats, vulnerabilities, defence</p>
          </div>

          {/* Step 4 */}
          <div className="dash-path-step">
            <div className="dash-path-node">4</div>
            <div className="dash-path-step-title">Hands-on Labs</div>
            <span className="dash-path-status-badge not-started">Not Started</span>
            <p className="dash-path-step-desc">Guided and open-ended labs</p>
          </div>

          {/* Step 5 */}
          <div className="dash-path-step">
            <div className="dash-path-node">5</div>
            <div className="dash-path-step-title">SOC & Detection</div>
            <span className="dash-path-status-badge not-started">Not Started</span>
            <p className="dash-path-step-desc">SIEM, analysis, incident response</p>
          </div>

          {/* Step 6 */}
          <div className="dash-path-step">
            <div className="dash-path-node">6</div>
            <div className="dash-path-step-title">Advanced & Specialization</div>
            <span className="dash-path-status-badge not-started">Not Started</span>
            <p className="dash-path-step-desc">Cloud, malware analysis, red/blue team</p>
          </div>
        </div>
      </div>

      {/* 4. LOWER TWO-COLUMN SECTION */}
      <div className="dashboard-lower-grid">
        {/* Left Column: Recent Activity */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <div className="panel-header-left">
              <Clock size={18} style={{ color: '#38bdf8' }} />
              <h3>Recent Activity</h3>
            </div>
            <Link to="/progress" className="panel-header-link">
              <span>View All</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="activity-list">
            {/* Activity 1 */}
            <div className="activity-item">
              <div className="activity-item-left">
                <div className="activity-icon-box" style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#34d399' }}>
                  <Play size={15} />
                </div>
                <div>
                  <div className="activity-title">Attempted Mock Test</div>
                  <div className="activity-sub">Network Fundamentals - Test 1</div>
                </div>
              </div>
              <span className="activity-time">2 hours ago</span>
            </div>

            {/* Activity 2 */}
            <div className="activity-item">
              <div className="activity-item-left">
                <div className="activity-icon-box" style={{ background: 'rgba(168, 85, 247, 0.12)', color: '#c084fc' }}>
                  <FlaskConical size={15} />
                </div>
                <div>
                  <div className="activity-title">Explored Lab</div>
                  <div className="activity-sub">Subnetting and IP Addressing</div>
                </div>
              </div>
              <span className="activity-time">5 hours ago</span>
            </div>

            {/* Activity 3 */}
            <div className="activity-item">
              <div className="activity-item-left">
                <div className="activity-icon-box" style={{ background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8' }}>
                  <BookOpen size={15} />
                </div>
                <div>
                  <div className="activity-title">Started Learning</div>
                  <div className="activity-sub">OSI Model and Network Layers</div>
                </div>
              </div>
              <span className="activity-time">1 day ago</span>
            </div>

            {/* Activity 4 */}
            <div className="activity-item">
              <div className="activity-item-left">
                <div className="activity-icon-box" style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#fbbf24' }}>
                  <Trophy size={15} />
                </div>
                <div>
                  <div className="activity-title">Viewed Challenge</div>
                  <div className="activity-sub">Packet Analysis Challenge</div>
                </div>
              </div>
              <span className="activity-time">2 days ago</span>
            </div>
          </div>
        </div>

        {/* Right Column: Up Next */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <div className="panel-header-left">
              <Zap size={18} style={{ color: '#38bdf8' }} />
              <h3>Up Next</h3>
            </div>
            <Link to="/learning/lessons/what-is-computer-networking-intro" className="panel-header-link">
              <span>Continue</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          {/* Featured Module Card */}
          <div className="featured-module-card">
            <div className="featured-module-left">
              <div className="module-type-badge">
                <BookOpen size={12} />
                <span>Learning Module</span>
              </div>
              <div className="featured-module-title">Introduction to Computer Networks</div>
              <div className="featured-module-meta">
                <span>⏱ 45 min</span>
                <span>🎯 Beginner</span>
              </div>
              <p className="featured-module-desc">
                Learn the fundamentals of networks, protocols, and how data flows across the internet.
              </p>
            </div>

            {/* Isometric 3D Cyber Server Illustration */}
            <div className="featured-graphic" aria-hidden="true">
              <svg viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="serverGrad1" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#0284c7" />
                    <stop offset="100%" stopColor="#1e3a8a" />
                  </linearGradient>
                  <linearGradient id="serverGrad2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#38bdf8" />
                    <stop offset="100%" stopColor="#0369a1" />
                  </linearGradient>
                </defs>
                {/* Isometric Server Block 1 */}
                <path d="M80 30 L125 55 L80 80 L35 55 Z" fill="url(#serverGrad2)" />
                <path d="M35 55 L80 80 L80 100 L35 75 Z" fill="#0369a1" />
                <path d="M80 80 L125 55 L125 75 L80 100 Z" fill="#0c4a6e" />

                {/* Glowing Nodes on Server */}
                <circle cx="55" cy="67" r="2.5" fill="#38bdf8" />
                <circle cx="65" cy="73" r="2.5" fill="#34d399" />
                <circle cx="95" cy="73" r="2.5" fill="#38bdf8" />

                {/* Isometric Server Block 2 */}
                <path d="M80 80 L125 105 L80 130 L35 105 Z" fill="url(#serverGrad1)" />
                <path d="M35 105 L80 130 L80 145 L35 120 Z" fill="#1e3a8a" />
                <path d="M80 130 L125 105 L125 120 L80 145 Z" fill="#0f172a" />

                {/* Hologram Light Rays */}
                <line x1="80" y1="20" x2="80" y2="30" stroke="#38bdf8" strokeWidth="2" strokeDasharray="3 3" />
                <circle cx="80" cy="18" r="4" fill="#38bdf8" opacity="0.8" />
              </svg>
            </div>
          </div>

          {/* Sub-section: Recommended for You */}
          <div>
            <div className="recommended-section-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={14} style={{ color: '#fbbf24' }} />
                <span>Recommended for You</span>
              </div>
              <Link to="/learning" style={{ fontSize: '0.78rem', color: '#38bdf8', textDecoration: 'none' }}>
                See All →
              </Link>
            </div>

            <div className="recommended-cards-row">
              {/* Rec 1 */}
              <Link to="/labs" className="recommended-card">
                <div className="recommended-card-left">
                  <div className="recommended-icon-box" style={{ background: 'rgba(14, 165, 233, 0.12)', color: '#38bdf8' }}>
                    <FlaskConical size={16} />
                  </div>
                  <div>
                    <span className="rec-type-label">Hands-on Lab</span>
                    <div className="rec-card-title">Wireshark Packet Analysis</div>
                    <div className="rec-card-sub">+ Intermediate</div>
                  </div>
                </div>
                <ChevronRight size={14} style={{ color: '#64748b' }} />
              </Link>

              {/* Rec 2 */}
              <Link to="/mock-tests" className="recommended-card">
                <div className="recommended-card-left">
                  <div className="recommended-icon-box" style={{ background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8' }}>
                    <FileCheck2 size={16} />
                  </div>
                  <div>
                    <span className="rec-type-label">Mock Test</span>
                    <div className="rec-card-title">Network Fundamentals</div>
                    <div className="rec-card-sub">20 Questions</div>
                  </div>
                </div>
                <ChevronRight size={14} style={{ color: '#64748b' }} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
