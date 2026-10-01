import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart3,
  ArrowRight,
  TrendingUp,
  Shield,
  FileCheck,
  Award,
} from 'lucide-react'
import { apiService } from '../../services/api'
import type { LearningProgressResponse } from '../../types'
import { PlaceholderModule } from '../../components/common/PlaceholderModule'

export const ProgressPage: React.FC = () => {
  const [progress, setProgress] = useState<LearningProgressResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    apiService
      .getLearningProgress()
      .then((data) => {
        if (!active) return
        setProgress(data)
        setLoading(false)
      })
      .catch(() => {
        if (!active) return
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Live Competency Matrix Card */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--cyan-primary)', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>
              <TrendingUp size={16} />
              <span>Live Student Competency Matrix</span>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
              Curriculum Mastery & Progress Telemetry
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '2px' }}>
              Real-time progress verified against SQLite relational store and development cadet profile.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <Link to="/progress/skills" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '0.82rem', textDecoration: 'none' }}>
              <Shield size={14} className="text-cyan-400" />
              <span>Skill Matrix</span>
            </Link>
            <Link to="/progress/assessment" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '0.82rem', textDecoration: 'none' }}>
              <FileCheck size={14} className="text-blue-400" />
              <span>Assessment Report</span>
            </Link>
            <Link to="/portfolio" className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '0.82rem', textDecoration: 'none' }}>
              <Award size={14} />
              <span>Portfolio</span>
            </Link>
            {progress && (
              <span className="badge badge-ready" style={{ padding: '6px 12px', fontSize: '0.82rem' }}>
                Rank: {progress.current_level}
              </span>
            )}
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading live telemetry...
          </div>
        ) : progress ? (
          <div>
            {/* Top Telemetry Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Overall Completion
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--cyan-primary)', marginTop: '4px' }}>
                  {progress.overall_percentage}%
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {progress.completed_lessons} of {progress.total_lessons} lessons finished
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Beginner Foundations
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--emerald-success)', marginTop: '4px' }}>
                  {progress.beginner_progress.percentage}%
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {progress.beginner_progress.completed_lessons} / {progress.beginner_progress.total_lessons} foundation lessons
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Intermediate Architecture
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
                  {progress.intermediate_progress.percentage}%
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {progress.intermediate_progress.completed_lessons} / {progress.intermediate_progress.total_lessons} routing & subnetting
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Advanced Cyber Defense
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--purple-soc)', marginTop: '4px' }}>
                  {progress.advanced_progress.percentage}%
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {progress.advanced_progress.completed_lessons} / {progress.advanced_progress.total_lessons} forensics & defense
                </div>
              </div>
            </div>

            {/* Next Recommended Activity */}
            {progress.continue_learning && (
              <div
                style={{
                  background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(16, 185, 129, 0.05) 100%)',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '16px',
                  flexWrap: 'wrap',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--cyan-primary)', fontWeight: 700, textTransform: 'uppercase' }}>
                    Next Recommended Step
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                    {progress.continue_learning.lesson_title}
                  </h4>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    In: {progress.continue_learning.module_title} &bull; {progress.continue_learning.estimated_minutes} min estimated
                  </div>
                </div>

                <Link
                  to={`/learning/lessons/${progress.continue_learning.lesson_slug}`}
                  className="diagram-btn primary"
                  style={{ textDecoration: 'none', padding: '10px 18px' }}
                >
                  <span>Resume Lesson</span>
                  <ArrowRight size={14} />
                </Link>
              </div>
            )}

            {/* Adaptive Diagnostics Entry */}
            <div
              style={{
                marginTop: '16px',
                background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(147, 51, 234, 0.08) 100%)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '16px 20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '16px',
                flexWrap: 'wrap',
              }}
            >
              <div>
                <div style={{ fontSize: '0.74rem', color: '#60a5fa', fontWeight: 700, textTransform: 'uppercase' }}>
                  Rule-Based Adaptive Engine
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                  Personalized Practice & Topic Diagnostics
                </h4>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Dynamic recency-weighted accuracy analysis and tailored curriculum next steps.
                </div>
              </div>
              <Link
                to="/adaptive-test"
                style={{
                  background: '#2563eb',
                  color: '#ffffff',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  padding: '8px 18px',
                  borderRadius: 'var(--radius-sm)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  textDecoration: 'none',
                }}
                data-testid="progress-open-adaptive-btn"
              >
                Open Adaptive Hub <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        ) : null}
      </div>

      {/* Module Overview Details */}
      <PlaceholderModule
        title="Student Skill Progression & Analytics"
        tagline="Track competency growth, identify weak concepts, and follow targeted study recommendations."
        description="The NexoraNet Progress engine monitors student performance across labs, mock tests, and interactive drills. It builds a personalized competency profile, pointing out precisely which networking protocols or defensive concepts need reinforcement before certification exams."
        phase="Phase 2: Analytics & Tracking"
        apiEndpoint="progress"
        icon={<BarChart3 size={24} />}
        practiceItems={[
          {
            title: 'Granular Domain Competency Matrix',
            description:
              'View percentage mastery across 12 core networking and cybersecurity domains including Subnetting, Routing, Transport, and Incident Response.',
          },
          {
            title: 'Algorithmic Weak-Topic Identification',
            description:
              'Automatic detection of recurring mistakes in exams and labs, paired with recommended focused refresher exercises.',
          },
          {
            title: 'Certification Readiness Scoring',
            description:
              'A real-time predictive index estimating student probability of passing CCNA, Network+, and Security+ certification tests.',
          },
          {
            title: 'Portfolio & Badge Export',
            description:
              'Generate a verifiable digital portfolio of completed hands-on networking topologies, PCAP analysis reports, and SOC incident triage runs.',
          },
        ]}
        keyObjectives={[
          'Provide actionable learning telemetry to help students study efficiently',
          'Eliminate blind spots before taking formal certification examinations',
          'Empower instructors and students to visualize concrete technical growth over time',
          'Deliver verifiable portfolio evidence of hands-on networking competency',
        ]}
      />
    </div>
  )
}
