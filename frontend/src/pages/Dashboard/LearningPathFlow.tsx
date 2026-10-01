import React from 'react'
import { ChevronRight } from 'lucide-react'
import type { LearningPathStep } from '../../types'

const PATH_STEPS: LearningPathStep[] = [
  {
    id: 'beginner',
    title: 'Beginner',
    subtitle: 'OSI Model, IP Addressing, Ethernet & Subnetting',
    tag: 'Track 1',
    active: true,
  },
  {
    id: 'intermediate',
    title: 'Intermediate',
    subtitle: 'Routing Protocols, Switching, TCP Deep-Dive, DNS & DHCP',
    tag: 'Track 2',
    active: false,
  },
  {
    id: 'advanced',
    title: 'Advanced',
    subtitle: 'BGP peering, Network Architecture, VPNs & NAT traversal',
    tag: 'Track 3',
    active: false,
  },
  {
    id: 'cyber-defense',
    title: 'Cyber Defense',
    subtitle: 'Packet Forensics, Firewalls, Port Scanners, Detection Rules',
    tag: 'Track 4',
    active: false,
  },
  {
    id: 'mini-soc',
    title: 'Mini SOC',
    subtitle: 'Incident Triage, Alert Analysis, SIEM workflows & Threat Hunting',
    tag: 'Capstone',
    active: false,
  },
]

export const LearningPathFlow: React.FC = () => {
  return (
    <div className="learning-path-card">
      <div className="card-header">
        <div>
          <div className="card-title">NexoraNet Learning Progression Path</div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', marginTop: '4px' }}>
            Structured graduation curriculum: from basic packet flow to live defensive operations.
          </p>
        </div>
      </div>

      <div className="learning-path-timeline">
        {PATH_STEPS.map((step, idx) => (
          <React.Fragment key={step.id}>
            <div className="timeline-step">
              <div className={`step-node ${step.active ? 'active' : ''}`}>
                0{idx + 1}
              </div>
              <div className="step-title">{step.title}</div>
              <div className="step-subtitle">{step.subtitle}</div>
            </div>

            {idx < PATH_STEPS.length - 1 && (
              <div className="step-arrow" aria-hidden="true">
                <ChevronRight size={22} className="desktop-arrow" />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}
