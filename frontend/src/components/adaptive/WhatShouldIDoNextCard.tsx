import React from 'react'
import { Link } from 'react-router-dom'
import { Compass, ArrowRight, Zap, Settings2 } from 'lucide-react'
import type { RecommendationItem } from '../../types'

interface WhatShouldIDoNextCardProps {
  recommendation: RecommendationItem | null
  onStartPractice: () => void
  onCustomize: () => void
  isStarting?: boolean
}

export const WhatShouldIDoNextCard: React.FC<WhatShouldIDoNextCardProps> = ({
  recommendation,
  onStartPractice,
  onCustomize,
  isStarting = false,
}) => {
  if (!recommendation) {
    return (
      <div className="ad-hero-card" data-testid="what-should-i-do-next-empty">
        <div className="ad-hero-badge">
          <Compass size={14} /> Recommended Next Step
        </div>
        <div className="ad-hero-content">
          <div className="ad-hero-text">
            <h2>Start Personalized Adaptive Practice</h2>
            <div className="ad-hero-reason">
              Take an introductory session to establish your diagnostic profile and unlock tailored guidance.
            </div>
          </div>
          <div className="ad-hero-actions">
            <button
              onClick={onStartPractice}
              disabled={isStarting}
              className="ad-btn-primary"
              data-testid="start-adaptive-btn"
            >
              <Zap size={16} />
              {isStarting ? 'Calibrating...' : 'Start Practice'}
            </button>
            <button onClick={onCustomize} className="ad-btn-secondary" title="Configure session size and topics">
              <Settings2 size={16} />
              Configure
            </button>
          </div>
        </div>
      </div>
    )
  }

  const isInternalUrl = recommendation.action_url.startsWith('/')

  return (
    <div className="ad-hero-card" data-testid="what-should-i-do-next-card">
      <div className="ad-hero-badge">
        <Compass size={14} /> Recommended Next Step • {recommendation.priority} PRIORITY
      </div>
      <div className="ad-hero-content">
        <div className="ad-hero-text">
          <h2>{recommendation.title}</h2>
          <div className="ad-hero-reason">
            <strong>Why: </strong>
            {recommendation.reason}
          </div>
        </div>
        <div className="ad-hero-actions">
          {recommendation.action_url === '/adaptive-test' ? (
            <button
              onClick={onStartPractice}
              disabled={isStarting}
              className="ad-btn-primary"
              data-testid="start-adaptive-btn"
            >
              <Zap size={16} />
              {isStarting ? 'Calibrating...' : recommendation.action_label}
            </button>
          ) : isInternalUrl ? (
            <Link to={recommendation.action_url} className="ad-btn-primary" data-testid="hero-action-link">
              <span>{recommendation.action_label}</span>
              <ArrowRight size={16} />
            </Link>
          ) : (
            <a href={recommendation.action_url} className="ad-btn-primary">
              <span>{recommendation.action_label}</span>
              <ArrowRight size={16} />
            </a>
          )}
          <button onClick={onCustomize} className="ad-btn-secondary" title="Configure adaptive session">
            <Settings2 size={16} />
            Configure
          </button>
        </div>
      </div>
    </div>
  )
}
