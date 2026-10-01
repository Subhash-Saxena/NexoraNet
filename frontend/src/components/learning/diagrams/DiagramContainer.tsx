import React, { useState } from 'react'
import { OSIStackDiagram } from './OSIStackDiagram'
import { TCPHandshakeDiagram } from './TCPHandshakeDiagram'
import { DNSResolutionDiagram } from './DNSResolutionDiagram'
import { DHCPSequenceDiagram } from './DHCPSequenceDiagram'
import { EncapsulationDiagram } from './EncapsulationDiagram'
import { Layers, Activity, Globe, Wifi, Binary } from 'lucide-react'

export interface DiagramContainerProps {
  initialDiagram?: 'osi_stack' | 'tcp_handshake' | 'dns_resolution' | 'dhcp_sequence' | 'encapsulation'
  allowSwitching?: boolean
}

export const DiagramContainer: React.FC<DiagramContainerProps> = ({
  initialDiagram = 'osi_stack',
  allowSwitching = true,
}) => {
  const [selectedDiagram, setSelectedDiagram] = useState<string>(initialDiagram)

  const renderActiveDiagram = () => {
    switch (selectedDiagram) {
      case 'osi_stack':
        return <OSIStackDiagram />
      case 'tcp_handshake':
        return <TCPHandshakeDiagram />
      case 'dns_resolution':
        return <DNSResolutionDiagram />
      case 'dhcp_sequence':
        return <DHCPSequenceDiagram />
      case 'encapsulation':
        return <EncapsulationDiagram />
      default:
        return <OSIStackDiagram />
    }
  }

  if (!allowSwitching) {
    return <div>{renderActiveDiagram()}</div>
  }

  const tabs = [
    { id: 'osi_stack', label: 'OSI 7 Layers', icon: Layers },
    { id: 'tcp_handshake', label: 'TCP 3-Way Handshake', icon: Activity },
    { id: 'dns_resolution', label: 'DNS Resolution', icon: Globe },
    { id: 'dhcp_sequence', label: 'DHCP DORA', icon: Wifi },
    { id: 'encapsulation', label: 'Frame Encapsulation', icon: Binary },
  ]

  return (
    <div>
      <div
        style={{
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '8px',
          marginBottom: '12px',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = selectedDiagram === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setSelectedDiagram(tab.id)}
              className={`diagram-btn ${isActive ? 'primary' : ''}`}
              style={{
                borderRadius: 'var(--radius-sm)',
                padding: '8px 14px',
              }}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {renderActiveDiagram()}
    </div>
  )
}
