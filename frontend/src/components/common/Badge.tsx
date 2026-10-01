import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'phase' | 'status' | 'ready' | 'neutral'
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'status' }) => {
  return <span className={`badge badge-${variant}`}>{children}</span>
}
