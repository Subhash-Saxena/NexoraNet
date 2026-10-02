import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  BookOpen,
  FlaskConical,
  FileCheck2,
  Network,
  Shield,
  ArrowRight,
  Clock,
  Zap,
  Sparkles,
  ChevronRight,
  Route,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { apiService } from '../../services/api'
import { analyticsApi } from '../../services/analyticsApi'
import '../../components/dashboard/dashboard.css'

interface DashboardTelemetry {
  learningProgress: number
  lessonsCompleted: number
  totalLessons: number
  labsCompleted: number
  totalLabs: number
  mockTests: number
  mockTestsAvg: number
  networkingSkills: number
  securitySkills: number
  streakDays: number
  currentLevel: string
}

interface ActivityItem {
  id: string
  title: string
  subtitle: string
  timeAgo: string
  type: string
}

const ZERO_TELEMETRY: DashboardTelemetry = {
  learningProgress: 0,
  lessonsCompleted: 0,
  totalLessons: 38,
  labsCompleted: 0,
  totalLabs: 22,
  mockTests: 0,
  mockTestsAvg: 0,
  networkingSkills: 0,
  securitySkills: 0,
  streakDays: 0,
  currentLevel: 'Cadet Defend-I',
}

function formatTimeAgo(dateString?: string): string {
  if (!dateString) return 'Recently'
  try {
    const diffMs = Date.now() - new Date(dateString).getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours} hr${diffHours > 1 ? 's' : ''} ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  } catch {
    return 'Recently'
  }
}

export const DashboardPage: React.FC = () => {
  const { user, isAuthenticated } = useAuth()
  const [telemetry, setTelemetry] = useState<DashboardTelemetry>(ZERO_TELEMETRY)
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    let active = true

    // If not authenticated or no user, immediately reset all metrics to 0
    if (!isAuthenticated || !user) {
      setTelemetry(ZERO_TELEMETRY)
      setActivities([])
      return
    }

    // Reset to 0 immediately on new user login while fetching actual data
    setTelemetry(ZERO_TELEMETRY)
    setActivities([])

    const loadUserData = async () => {
      try {
        const [overviewRes, historyRes, skillsRes, progressRes, labsRes] = await Promise.allSettled([
          analyticsApi.getOverview(),
          apiService.getAttemptHistory(),
          analyticsApi.getSkills(),
          apiService.getLearningProgress(),
          apiService.getLabTelemetry(),
        ])

        if (!active) return

        let lessonsComp = 0
        let totalLess = 38
        let labsComp = 0
        let totalLb = 22
        let streak = 0
        let lvl = user.current_level || 'Cadet Defend-I'
        let actList: ActivityItem[] = []

        if (overviewRes.status === 'fulfilled' && overviewRes.value) {
          const ov = overviewRes.value
          lessonsComp = ov.lessons_completed || 0
          totalLess = ov.total_lessons || 38
          labsComp = ov.labs_completed || 0
          totalLb = ov.total_labs || 22
          streak = ov.current_learning_streak || 0
          if (ov.current_level) lvl = ov.current_level

          if (ov.recent_activity && ov.recent_activity.length > 0) {
            actList = ov.recent_activity.slice(0, 5).map((a, i) => ({
              id: String(a.id || i),
              title: a.title || 'Learning Activity',
              subtitle: a.summary || a.activity_type || '',
              timeAgo: formatTimeAgo(a.occurred_at),
              type: a.activity_type || 'LESSON',
            }))
          }
        } else if (progressRes.status === 'fulfilled' && progressRes.value) {
          const pr = progressRes.value
          lessonsComp = pr.completed_lessons || 0
          totalLess = pr.total_lessons || 38
          lvl = pr.current_level || lvl
        }

        if (labsRes.status === 'fulfilled' && labsRes.value) {
          labsComp = Math.max(labsComp, labsRes.value.completed_labs || 0)
        }

        // Mock Tests count & real average score
        let testsCount = 0
        let avgScore = 0
        if (historyRes.status === 'fulfilled' && Array.isArray(historyRes.value)) {
          const completedAttempts = historyRes.value.filter(
            (a) => a.status === 'COMPLETED' || a.status === 'SUBMITTED'
          )
          testsCount = completedAttempts.length
          if (testsCount > 0) {
            const sumScores = completedAttempts.reduce((acc, a) => acc + (a.percentage || 0), 0)
            avgScore = Math.round(sumScores / testsCount)
          }
        }

        // Skill proficiencies
        let netSkillScore = 0
        let secSkillScore = 0
        if (skillsRes.status === 'fulfilled' && Array.isArray(skillsRes.value) && skillsRes.value.length > 0) {
          const netCats = ['NETWORKING', 'TCP_IP', 'DNS', 'DHCP', 'ROUTING', 'SWITCHING', 'SUBNETTING', 'TCP_UDP', 'HTTP_HTTPS']
          const secCats = [
            'NETWORK_SECURITY',
            'DEFENSE',
            'FIREWALLS',
            'IDS_IPS',
            'PACKET_ANALYSIS',
            'TRAFFIC_ANALYSIS',
            'SIEM',
            'LOG_ANALYSIS',
            'SOC_TRIAGE',
            'DETECTION_ENGINEERING',
            'THREAT_INTELLIGENCE',
            'IOC_ANALYSIS',
            'THREAT_HUNTING',
            'ENDPOINT_SECURITY',
            'INCIDENT_RESPONSE',
            'DIGITAL_FORENSICS',
            'MITRE_ATTACK',
            'SOAR',
            'SECURITY_REASONING',
          ]

          const netSkills = skillsRes.value.filter((s) => netCats.includes(s.category.toUpperCase()))
          if (netSkills.length > 0) {
            const totalProf = netSkills.reduce((acc, s) => acc + (s.accuracy || 0), 0)
            netSkillScore = Math.round(totalProf / netSkills.length)
          }

          const secSkills = skillsRes.value.filter((s) => secCats.includes(s.category.toUpperCase()))
          if (secSkills.length > 0) {
            const totalProf = secSkills.reduce((acc, s) => acc + (s.accuracy || 0), 0)
            secSkillScore = Math.round(totalProf / secSkills.length)
          }
        } else if (lessonsComp > 0 || labsComp > 0) {
          // Dynamic assessment proportional to completed items
          netSkillScore = Math.min(100, Math.round((lessonsComp / totalLess) * 100))
          secSkillScore = Math.min(100, Math.round((labsComp / totalLb) * 100))
        }

        const pct = totalLess > 0 ? Math.round((lessonsComp / totalLess) * 100) : 0

        setTelemetry({
          learningProgress: pct,
          lessonsCompleted: lessonsComp,
          totalLessons: totalLess,
          labsCompleted: labsComp,
          totalLabs: totalLb,
          mockTests: testsCount,
          mockTestsAvg: avgScore,
          networkingSkills: netSkillScore,
          securitySkills: secSkillScore,
          streakDays: streak,
          currentLevel: lvl,
        })
        setActivities(actList)
      } catch {
        if (active) {
          setTelemetry(ZERO_TELEMETRY)
          setActivities([])
        }
      }
    }

    loadUserData()

    return () => {
      active = false
    }
  }, [isAuthenticated, user?.id])

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
            <path d="M0 260 L140 180 L290 270 L500 170 L700 270 L700 320 L0 320 Z" fill="#080e1c" />

            {/* Beacon tower in distance */}
            <line x1="580" y1="100" x2="580" y2="60" stroke="#0ea5e9" strokeWidth="2" opacity="0.8" />
            <circle cx="580" cy="58" r="4" fill="#38bdf8" filter="url(#cyanGlow)" />

            {/* Neon Winding Highway (Center to bottom) */}
            <path
              d="M580 70 C 570 140, 520 200, 480 240 C 440 280, 380 300, 320 320"
              stroke="url(#roadGlow)"
              strokeWidth="4"
              strokeDasharray="6 4"
              fill="none"
              opacity="0.9"
            />
            <path
              d="M580 70 C 570 140, 520 200, 480 240 C 440 280, 380 300, 320 320"
              stroke="#06b6d4"
              strokeWidth="10"
              fill="none"
              opacity="0.25"
            />
          </svg>
        </div>

        {/* Hero Left Content */}
        <div className="dashboard-hero-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
            <span className="dashboard-tag" style={{ margin: 0 }}>
              {user ? `WELCOME BACK, ${user.display_name || user.username}` : 'WELCOME TO NEXORANET'}
            </span>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '3px 9px', borderRadius: '4px', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', fontSize: '0.74rem' }}>
              <span style={{ color: '#94a3b8' }}>Current Level</span>
              <span style={{ color: '#38bdf8', fontWeight: 700 }}>{telemetry.currentLevel}</span>
            </div>
          </div>
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
                strokeDashoffset={telemetry.streakDays > 0 ? Math.max(226 - telemetry.streakDays * 32, 20) : 226}
                strokeLinecap="round"
                fill="none"
                style={{ transition: 'stroke-dashoffset 0.6s ease' }}
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
              <span className="streak-number">{telemetry.streakDays}</span>
              <span className="streak-sub">Day Streak</span>
            </div>
          </div>

          <div className="streak-text-wrap">
            <h4>Consistency builds mastery.</h4>
            <p>
              {telemetry.streakDays > 0
                ? `${telemetry.streakDays}-day streak active! Keep going to maintain your momentum.`
                : 'Start your practice today to begin building your streak!'}
            </p>
          </div>
        </div>
      </div>

      {/* 2. 5-COLUMN KPI METRICS ROW */}
      <div className="kpi-metrics-row">
        {/* Metric 1: Learning Progress */}
        <div onClick={() => navigate('/learning')} className="kpi-card" style={{ cursor: 'pointer' }}>
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
            <div className="kpi-value">{telemetry.learningProgress}%</div>
            <div className="kpi-subtext">
              {telemetry.lessonsCompleted} / {telemetry.totalLessons} curated lessons
            </div>
            <div className="kpi-progress-track">
              <div
                className="kpi-progress-fill"
                style={{
                  width: `${telemetry.learningProgress}%`,
                  background: 'linear-gradient(90deg, #0284c7, #38bdf8)',
                }}
              />
            </div>
          </div>
        </div>

        {/* Metric 2: Labs Completed */}
        <div onClick={() => navigate('/labs')} className="kpi-card" style={{ cursor: 'pointer' }}>
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
            <div className="kpi-value">{telemetry.labsCompleted}</div>
            <div className="kpi-subtext">
              Target: {telemetry.totalLabs} interactive exercises
            </div>
            <div className="kpi-progress-track">
              <div
                className="kpi-progress-fill"
                style={{
                  width: `${telemetry.totalLabs > 0 ? Math.round((telemetry.labsCompleted / telemetry.totalLabs) * 100) : 0}%`,
                  background: 'linear-gradient(90deg, #0891b2, #06b6d4)',
                }}
              />
            </div>
          </div>
        </div>

        {/* Metric 3: Mock Tests */}
        <div onClick={() => navigate('/mock-tests')} className="kpi-card" style={{ cursor: 'pointer' }}>
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
            <div className="kpi-value">{telemetry.mockTests}</div>
            <div className="kpi-subtext">
              {telemetry.mockTests > 0
                ? `Avg Score: ${telemetry.mockTestsAvg}% (${telemetry.mockTestsAvg >= 70 ? 'Passing' : 'Practice'})`
                : 'No tests attempted yet'}
            </div>
            <div className="kpi-progress-track">
              <div
                className="kpi-progress-fill"
                style={{
                  width: `${telemetry.mockTestsAvg}%`,
                  background: 'linear-gradient(90deg, #3b82f6, #60a5fa)',
                }}
              />
            </div>
          </div>
        </div>

        {/* Metric 4: Networking Skills */}
        <div onClick={() => navigate('/progress')} className="kpi-card" style={{ cursor: 'pointer' }}>
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
            <div className="kpi-value">{telemetry.networkingSkills}%</div>
            <div className="kpi-subtext">
              {telemetry.networkingSkills > 0 ? 'Layer 2 & Layer 3 mastery' : 'Start lessons to unlock'}
            </div>
            <div className="kpi-progress-track">
              <div
                className="kpi-progress-fill"
                style={{
                  width: `${telemetry.networkingSkills}%`,
                  background: 'linear-gradient(90deg, #0d9488, #2dd4bf)',
                }}
              />
            </div>
          </div>
        </div>

        {/* Metric 5: Security Skills */}
        <div onClick={() => navigate('/progress')} className="kpi-card" style={{ cursor: 'pointer' }}>
          <div className="kpi-card-header">
            <div className="kpi-card-header-left">
              <div className="kpi-icon" style={{ color: '#a855f7' }}>
                <Shield size={16} />
              </div>
              <span className="kpi-title">Security Skills</span>
            </div>
            <ChevronRight size={14} className="kpi-chevron" />
          </div>
          <div>
            <div className="kpi-value">{telemetry.securitySkills}%</div>
            <div className="kpi-subtext">
              {telemetry.securitySkills > 0 ? 'Boundary & defence drills' : 'Complete labs to unlock'}
            </div>
            <div className="kpi-progress-track">
              <div
                className="kpi-progress-fill"
                style={{
                  width: `${telemetry.securitySkills}%`,
                  background: 'linear-gradient(90deg, #7e22ce, #a855f7)',
                }}
              />
            </div>
          </div>
        </div>
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

        {/* 6 Connected Steps with Dynamic Progress */}
        <div className="dash-path-timeline">
          {/* Step 1 */}
          <div className="dash-path-step">
            <div className={`dash-path-node ${telemetry.lessonsCompleted >= 6 ? 'active' : telemetry.lessonsCompleted > 0 ? 'active' : ''}`}>
              1
            </div>
            <div className="dash-path-step-title">Foundations</div>
            <span style={{ fontSize: '0.72rem', color: '#38bdf8', fontWeight: 600 }}>Beginner</span>
            <span className={`dash-path-status-badge ${telemetry.lessonsCompleted >= 6 ? 'in-progress' : telemetry.lessonsCompleted > 0 ? 'in-progress' : 'not-started'}`}>
              {telemetry.lessonsCompleted >= 6 ? 'Completed' : telemetry.lessonsCompleted > 0 ? 'In Progress' : 'Not Started'}
            </span>
            <p className="dash-path-step-desc">Networking, OS, protocols</p>
          </div>

          {/* Step 2 */}
          <div className="dash-path-step">
            <div className={`dash-path-node ${telemetry.lessonsCompleted >= 12 ? 'active' : ''}`}>2</div>
            <div className="dash-path-step-title">System & Linux</div>
            <span style={{ fontSize: '0.72rem', color: '#06b6d4', fontWeight: 600 }}>Intermediate</span>
            <span className={`dash-path-status-badge ${telemetry.lessonsCompleted >= 12 ? 'in-progress' : telemetry.lessonsCompleted >= 6 ? 'in-progress' : 'not-started'}`}>
              {telemetry.lessonsCompleted >= 12 ? 'Completed' : telemetry.lessonsCompleted >= 6 ? 'In Progress' : 'Not Started'}
            </span>
            <p className="dash-path-step-desc">Linux, command line, system internals</p>
          </div>

          {/* Step 3 */}
          <div className="dash-path-step">
            <div className={`dash-path-node ${telemetry.lessonsCompleted >= 18 ? 'active' : ''}`}>3</div>
            <div className="dash-path-step-title">Cybersecurity Core</div>
            <span style={{ fontSize: '0.72rem', color: '#a855f7', fontWeight: 600 }}>Advanced</span>
            <span className={`dash-path-status-badge ${telemetry.lessonsCompleted >= 18 ? 'in-progress' : telemetry.lessonsCompleted >= 12 ? 'in-progress' : 'not-started'}`}>
              {telemetry.lessonsCompleted >= 18 ? 'Completed' : telemetry.lessonsCompleted >= 12 ? 'In Progress' : 'Not Started'}
            </span>
            <p className="dash-path-step-desc">Threats, vulnerabilities, defence</p>
          </div>

          {/* Step 4 */}
          <div className="dash-path-step">
            <div className={`dash-path-node ${telemetry.labsCompleted >= 6 ? 'active' : telemetry.labsCompleted > 0 ? 'active' : ''}`}>
              4
            </div>
            <div className="dash-path-step-title">Hands-on Labs</div>
            <span style={{ fontSize: '0.72rem', color: '#2dd4bf', fontWeight: 600 }}>Practice</span>
            <span className={`dash-path-status-badge ${telemetry.labsCompleted >= 6 ? 'in-progress' : telemetry.labsCompleted > 0 ? 'in-progress' : 'not-started'}`}>
              {telemetry.labsCompleted >= 6 ? 'Completed' : telemetry.labsCompleted > 0 ? 'In Progress' : 'Not Started'}
            </span>
            <p className="dash-path-step-desc">Guided and open-ended labs</p>
          </div>

          {/* Step 5 */}
          <div className="dash-path-step">
            <div className={`dash-path-node ${telemetry.labsCompleted >= 14 ? 'active' : ''}`}>5</div>
            <div className="dash-path-step-title">SOC & Detection</div>
            <span style={{ fontSize: '0.72rem', color: '#60a5fa', fontWeight: 600 }}>Mini SOC</span>
            <span className={`dash-path-status-badge ${telemetry.labsCompleted >= 14 ? 'in-progress' : telemetry.labsCompleted >= 6 ? 'in-progress' : 'not-started'}`}>
              {telemetry.labsCompleted >= 14 ? 'Completed' : telemetry.labsCompleted >= 6 ? 'In Progress' : 'Not Started'}
            </span>
            <p className="dash-path-step-desc">SIEM, analysis, incident response</p>
          </div>

          {/* Step 6 */}
          <div className="dash-path-step">
            <div className="dash-path-node">6</div>
            <div className="dash-path-step-title">Cyber Defense</div>
            <span style={{ fontSize: '0.72rem', color: '#f59e0b', fontWeight: 600 }}>Specialization</span>
            <span className={`dash-path-status-badge ${telemetry.labsCompleted >= 14 ? 'in-progress' : 'not-started'}`}>
              {telemetry.labsCompleted >= 14 ? 'In Progress' : 'Not Started'}
            </span>
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
            {activities.length > 0 ? (
              activities.map((act) => (
                <div key={act.id} className="activity-item">
                  <div className="activity-item-left">
                    <div
                      className="activity-icon-box"
                      style={{
                        background:
                          act.type === 'TEST'
                            ? 'rgba(16, 185, 129, 0.12)'
                            : act.type === 'LAB'
                            ? 'rgba(168, 85, 247, 0.12)'
                            : 'rgba(56, 189, 248, 0.12)',
                        color:
                          act.type === 'TEST'
                            ? '#34d399'
                            : act.type === 'LAB'
                            ? '#c084fc'
                            : '#38bdf8',
                      }}
                    >
                      {act.type === 'TEST' ? (
                        <FileCheck2 size={15} />
                      ) : act.type === 'LAB' ? (
                        <FlaskConical size={15} />
                      ) : (
                        <BookOpen size={15} />
                      )}
                    </div>
                    <div>
                      <div className="activity-title">{act.title}</div>
                      <div className="activity-sub">{act.subtitle}</div>
                    </div>
                  </div>
                  <span className="activity-time">{act.timeAgo}</span>
                </div>
              ))
            ) : (
              <div style={{ padding: '36px 16px', textAlign: 'center' }}>
                <div
                  style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: '10px',
                    background: 'rgba(56, 189, 248, 0.08)',
                    color: '#38bdf8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 12px',
                  }}
                >
                  <Clock size={20} />
                </div>
                <h4 style={{ fontSize: '0.92rem', color: '#f8fafc', margin: '0 0 4px', fontWeight: 600 }}>
                  No recent activity recorded
                </h4>
                <p style={{ fontSize: '0.78rem', color: '#64748b', margin: '0 0 16px', lineHeight: 1.4 }}>
                  Start your first lesson or hands-on lab to see your live progress and telemetry.
                </p>
                <Link
                  to="/learning"
                  className="btn-hero-primary"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '7px 16px',
                    fontSize: '0.8rem',
                    textDecoration: 'none',
                  }}
                >
                  <span>Start Learning</span>
                  <ArrowRight size={13} />
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Up Next */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <div className="panel-header-left">
              <Zap size={18} style={{ color: '#38bdf8' }} />
              <h3>Up Next</h3>
            </div>
            <Link to="/learning" className="panel-header-link">
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
                <path d="M80 30 L125 55 L80 80 L35 55 Z" fill="url(#serverGrad2)" />
                <path d="M35 55 L80 80 L80 100 L35 75 Z" fill="#0369a1" />
                <path d="M80 80 L125 55 L125 75 L80 100 Z" fill="#0c4a6e" />

                <circle cx="55" cy="67" r="2.5" fill="#38bdf8" />
                <circle cx="65" cy="73" r="2.5" fill="#34d399" />
                <circle cx="95" cy="73" r="2.5" fill="#38bdf8" />

                <path d="M80 80 L125 105 L80 130 L35 105 Z" fill="url(#serverGrad1)" />
                <path d="M35 105 L80 130 L80 145 L35 120 Z" fill="#1e3a8a" />
                <path d="M80 130 L125 105 L125 120 L80 145 Z" fill="#0f172a" />

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
              <Link to="/labs" className="recommended-card">
                <div className="recommended-card-header">
                  <div className="recommended-badge">
                    <FlaskConical size={11} />
                    <span>Lab</span>
                  </div>
                  <span className="recommended-time">15m</span>
                </div>
                <div className="recommended-card-title">Port Scanning Fundamentals</div>
                <p className="recommended-card-desc">Analyze network discovery techniques with Nmap.</p>
              </Link>

              <Link to="/network-simulator" className="recommended-card">
                <div className="recommended-card-header">
                  <div className="recommended-badge">
                    <Network size={11} />
                    <span>Sandbox</span>
                  </div>
                  <span className="recommended-time">20m</span>
                </div>
                <div className="recommended-card-title">Firewall Rule Simulation</div>
                <p className="recommended-card-desc">Build packet filter policies across subnets.</p>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
