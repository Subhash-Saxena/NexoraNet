import React, { useState } from 'react'
import {
  HelpCircle,
  Cpu,
  ShieldAlert,
  GraduationCap,
  Copy,
  Check,
} from 'lucide-react'

export type CalloutType = 'bca_simple' | 'technical' | 'security' | 'interview'

export interface CalloutCardProps {
  type?: CalloutType
  title?: string
  children?: React.ReactNode
  content?: string
  // If tabs are provided, renders multi-perspective tab switcher
  perspectives?: {
    type: CalloutType
    title: string
    content: string
  }[]
}

const TYPE_CONFIG = {
  bca_simple: {
    label: 'BCA Simple Concept',
    icon: HelpCircle,
    className: 'bca-simple',
  },
  technical: {
    label: 'Technical Deep-Dive',
    icon: Cpu,
    className: 'technical',
  },
  security: {
    label: 'Security & Attack Relevance',
    icon: ShieldAlert,
    className: 'security',
  },
  interview: {
    label: 'Exam & Interview Note',
    icon: GraduationCap,
    className: 'interview',
  },
}

export const CalloutCard: React.FC<CalloutCardProps> = ({
  type = 'bca_simple',
  title,
  children,
  content,
  perspectives,
}) => {
  const [activeTab, setActiveTab] = useState<number>(0)
  const [copied, setCopied] = useState(false)

  // Multi-tab perspective mode
  if (perspectives && perspectives.length > 0) {
    const current = perspectives[activeTab] || perspectives[0]
    const config = TYPE_CONFIG[current.type] || TYPE_CONFIG.bca_simple
    const Icon = config.icon

    const handleCopy = () => {
      navigator.clipboard.writeText(current.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }

    return (
      <div className={`callout-box ${config.className}`}>
        <div className="callout-tabs">
          {perspectives.map((p, idx) => {
            const TabIcon = TYPE_CONFIG[p.type]?.icon || HelpCircle
            return (
              <button
                key={idx}
                className={`callout-tab-btn ${activeTab === idx ? 'active' : ''}`}
                onClick={() => setActiveTab(idx)}
              >
                <TabIcon size={14} />
                <span>{p.title || TYPE_CONFIG[p.type]?.label}</span>
              </button>
            )
          })}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div className="callout-header">
            <Icon size={18} />
            <span>{current.title || config.label}</span>
          </div>
          <button
            onClick={handleCopy}
            title="Copy explanation"
            style={{
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px',
            }}
          >
            {copied ? <Check size={14} color="var(--emerald-success)" /> : <Copy size={14} />}
          </button>
        </div>

        <div className="callout-content" style={{ whiteSpace: 'pre-line' }}>
          {current.content}
        </div>
      </div>
    )
  }

  // Single callout mode
  const config = TYPE_CONFIG[type] || TYPE_CONFIG.bca_simple
  const Icon = config.icon

  const handleCopy = () => {
    if (content) {
      navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className={`callout-box ${config.className}`}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div className="callout-header">
          <Icon size={18} />
          <span>{title || config.label}</span>
        </div>
        {content && (
          <button
            onClick={handleCopy}
            title="Copy explanation"
            style={{
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px',
            }}
          >
            {copied ? <Check size={14} color="var(--emerald-success)" /> : <Copy size={14} />}
          </button>
        )}
      </div>

      <div className="callout-content">
        {content ? <div style={{ whiteSpace: 'pre-line' }}>{content}</div> : children}
      </div>
    </div>
  )
}
