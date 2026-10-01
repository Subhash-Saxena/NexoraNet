import React from 'react'

interface MetricCardProps {
  label: string
  value: string | number
  hint?: string
  icon: React.ReactNode
  accentColor?: string
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  hint,
  icon,
}) => {
  return (
    <div className="metric-card">
      <div className="metric-card-top">
        <span className="metric-card-label">{label}</span>
        <div className="metric-card-icon">{icon}</div>
      </div>
      <div>
        <div className="metric-card-value">{value}</div>
        {hint && <div className="metric-card-hint">{hint}</div>}
      </div>
    </div>
  )
}
