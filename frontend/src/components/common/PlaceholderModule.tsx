import React, { useEffect, useState } from 'react'
import { Badge } from './Badge'
import { CheckCircle2, Clock } from 'lucide-react'
import { apiService } from '../../services/api'

interface PlaceholderModuleProps {
  title: string
  tagline: string
  description: string
  phase: string
  apiEndpoint?: string
  practiceItems: Array<{
    title: string
    description: string
  }>
  keyObjectives: string[]
  icon: React.ReactNode
}

export const PlaceholderModule: React.FC<PlaceholderModuleProps> = ({
  title,
  tagline,
  description,
  phase,
  apiEndpoint,
  practiceItems,
  keyObjectives,
  icon,
}) => {
  const [backendMeta, setBackendMeta] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    if (apiEndpoint) {
      apiService
        .getModuleStatus(apiEndpoint)
        .then((res) => setBackendMeta(res))
        .catch(() => {
          // If backend isn't running or endpoint is unreachable, fallback cleanly
          setBackendMeta(null)
        })
    }
  }, [apiEndpoint])

  return (
    <div className="placeholder-view">
      <div className="placeholder-badge-row">
        <Badge variant="phase">{phase}</Badge>
        <Badge variant="status">Status: Coming in a later development phase</Badge>
        {backendMeta && (
          <Badge variant="ready">Backend API Route: Active</Badge>
        )}
      </div>

      <div className="placeholder-title">
        <div className="module-icon-wrap">{icon}</div>
        <span>{title}</span>
      </div>

      <div style={{ color: 'var(--cyan-primary)', fontWeight: 600, fontSize: '1.05rem', marginBottom: '8px' }}>
        &ldquo;{tagline}&rdquo;
      </div>

      <p className="placeholder-summary">{description}</p>

      {/* Development Status Notice */}
      <div className="status-callout" style={{ marginBottom: '28px' }}>
        <Clock size={24} color="#fbbf24" style={{ flexShrink: 0 }} />
        <div className="status-callout-text">
          <h5>Development Status</h5>
          <p>
            Status: Coming in a later development phase. The architectural foundation,
            backend router, and security containment policies are established in Step 1.
          </p>
        </div>
      </div>

      {/* What Students Will Practice */}
      <div className="placeholder-section-title">
        What students will eventually be able to practice
      </div>
      <div className="practice-cards-grid">
        {practiceItems.map((item, idx) => (
          <div key={idx} className="practice-card">
            <h4>{item.title}</h4>
            <p>{item.description}</p>
          </div>
        ))}
      </div>

      {/* Key Curriculum Objectives */}
      <div className="placeholder-section-title" style={{ marginTop: '20px' }}>
        Curriculum & Skill Objectives
      </div>
      <ul className="feature-list" style={{ marginTop: '12px' }}>
        {keyObjectives.map((obj, idx) => (
          <li key={idx} className="feature-item">
            <CheckCircle2 size={16} />
            <span>{obj}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
