import React, { useState } from 'react'
import { AlertTriangle, Search, ShieldCheck, ChevronRight } from 'lucide-react'

export interface ScenarioStep {
  label: string
  detail: string
}

export interface ScenarioCardProps {
  title: string
  context: string
  symptoms: string[]
  investigationSteps?: ScenarioStep[]
  resolution?: string
  defensiveTakeaway?: string
}

export const ScenarioCard: React.FC<ScenarioCardProps> = ({
  title,
  context,
  symptoms,
  investigationSteps,
  resolution,
  defensiveTakeaway,
}) => {
  const [showResolution, setShowResolution] = useState(false)

  return (
    <div className="scenario-box">
      <div className="scenario-title">
        <AlertTriangle size={18} />
        <span>Real-World Scenario: {title}</span>
      </div>

      <p style={{ color: '#cbd5e1', fontSize: '0.9rem', marginBottom: '14px', lineHeight: 1.6 }}>
        {context}
      </p>

      {symptoms && symptoms.length > 0 && (
        <div style={{ marginBottom: '14px' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '6px' }}>
            Reported Symptoms & Indicators
          </div>
          <ul style={{ margin: '0 0 0 18px', color: '#e2e8f0', fontSize: '0.88rem' }}>
            {symptoms.map((s, idx) => (
              <li key={idx} style={{ marginBottom: '4px' }}>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {investigationSteps && investigationSteps.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Search size={14} color="var(--purple-soc)" />
            <span>Investigation Workflow</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {investigationSteps.map((step, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(0, 0, 0, 0.25)',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: '3px solid var(--purple-soc)',
                  fontSize: '0.86rem',
                }}
              >
                <span style={{ fontWeight: 600, color: 'var(--text-main)', marginRight: '6px' }}>
                  Step {idx + 1}: {step.label}
                </span>
                <p style={{ color: 'var(--text-secondary)', marginTop: '2px', fontSize: '0.82rem' }}>
                  {step.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(139, 92, 246, 0.2)' }}>
        {!showResolution ? (
          <button
            onClick={() => setShowResolution(true)}
            className="diagram-btn"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            <span>Reveal Incident Analysis & Defensive Resolution</span>
            <ChevronRight size={14} />
          </button>
        ) : (
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-sm)', padding: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--emerald-success)', fontWeight: 700, fontSize: '0.88rem', marginBottom: '6px' }}>
              <ShieldCheck size={16} />
              <span>Root Cause & Defensive Remediation</span>
            </div>
            {resolution && (
              <p style={{ color: '#cbd5e1', fontSize: '0.86rem', lineHeight: 1.5, marginBottom: '8px' }}>
                {resolution}
              </p>
            )}
            {defensiveTakeaway && (
              <div style={{ fontSize: '0.82rem', color: 'var(--cyan-primary)', fontWeight: 600 }}>
                &bull; Security Rule: {defensiveTakeaway}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
