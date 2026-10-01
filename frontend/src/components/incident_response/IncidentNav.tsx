import React from 'react'

export type WorkbenchTab =
  | 'overview'
  | 'evidence'
  | 'timeline'
  | 'hypotheses'
  | 'mitre'
  | 'response'
  | 'playbook'
  | 'report'

interface IncidentNavProps {
  activeTab: WorkbenchTab
  onSelectTab: (tab: WorkbenchTab) => void
  counts: {
    evidence: number
    timeline: number
    hypotheses: number
    mitre: number
    actions: number
  }
}

export const IncidentNav: React.FC<IncidentNavProps> = ({
  activeTab,
  onSelectTab,
  counts,
}) => {
  const tabs: Array<{ id: WorkbenchTab; label: string; icon: string; count?: number }> = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'evidence', label: 'Evidence & Custody', icon: '📦', count: counts.evidence },
    { id: 'timeline', label: 'Timeline', icon: '⏱️', count: counts.timeline },
    { id: 'hypotheses', label: 'Hypotheses & Findings', icon: '🔬', count: counts.hypotheses },
    { id: 'mitre', label: 'MITRE ATT&CK', icon: '🎯', count: counts.mitre },
    { id: 'response', label: 'Response Simulation', icon: '🛡️', count: counts.actions },
    { id: 'playbook', label: 'Playbook Guide', icon: '📖' },
    { id: 'report', label: 'Executive Report', icon: '📄' },
  ]

  return (
    <div className="ir-tabs-nav" role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          className={`ir-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onSelectTab(tab.id)}
        >
          <span>{tab.icon}</span>
          <span>{tab.label}</span>
          {tab.count !== undefined && tab.count > 0 && (
            <span
              style={{
                background: 'rgba(55, 65, 81, 0.8)',
                borderRadius: '10px',
                padding: '1px 6px',
                fontSize: '0.75rem',
                color: '#cbd5e1',
              }}
            >
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
