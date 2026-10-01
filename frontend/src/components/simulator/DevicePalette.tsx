import React from 'react'
import {
  Monitor,
  Laptop,
  Server,
  Network,
  GitBranch,
  Shield,
  Globe,
  Database,
  Radio,
} from 'lucide-react'
import type { SimDeviceType } from '../../types/simulator'

interface DevicePaletteProps {
  onAddDevice: (type: SimDeviceType) => void
}

interface PaletteItem {
  type: SimDeviceType
  name: string
  icon: React.ReactNode
}

export const DevicePalette: React.FC<DevicePaletteProps> = ({ onAddDevice }) => {
  const endDevices: PaletteItem[] = [
    { type: 'PC', name: 'Workstation PC', icon: <Monitor size={20} /> },
    { type: 'LAPTOP', name: 'Laptop', icon: <Laptop size={20} /> },
    { type: 'SERVER', name: 'Server', icon: <Server size={20} /> },
  ]

  const networkDevices: PaletteItem[] = [
    { type: 'SWITCH', name: 'L2 Switch', icon: <Network size={20} /> },
    { type: 'ROUTER', name: 'L3 Router', icon: <GitBranch size={20} /> },
    { type: 'FIREWALL', name: 'Firewall', icon: <Shield size={20} /> },
  ]

  const conceptualDevices: PaletteItem[] = [
    { type: 'INTERNET', name: 'Internet Cloud', icon: <Globe size={20} /> },
    { type: 'DNS_SERVER', name: 'DNS Server', icon: <Database size={20} /> },
    { type: 'DHCP_SERVER', name: 'DHCP Server', icon: <Radio size={20} /> },
  ]

  const handleDragStart = (e: React.DragEvent, type: SimDeviceType) => {
    e.dataTransfer.setData('application/nexoranet-device', type)
  }

  return (
    <aside className="simulator-palette" aria-label="Device Palette">
      <div className="palette-section">
        <div className="palette-section-title">End Devices</div>
        <div className="palette-grid">
          {endDevices.map((item) => (
            <div
              key={item.type}
              className="palette-item"
              draggable
              onDragStart={(e) => handleDragStart(e, item.type)}
              onClick={() => onAddDevice(item.type)}
              title={`Click or drag to place a ${item.name}`}
              data-testid={`palette-item-${item.type.toLowerCase()}`}
            >
              {item.icon}
              <span className="palette-item-name">{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="palette-section">
        <div className="palette-section-title">Network Devices</div>
        <div className="palette-grid">
          {networkDevices.map((item) => (
            <div
              key={item.type}
              className="palette-item"
              draggable
              onDragStart={(e) => handleDragStart(e, item.type)}
              onClick={() => onAddDevice(item.type)}
              title={`Click or drag to place a ${item.name}`}
              data-testid={`palette-item-${item.type.toLowerCase()}`}
            >
              {item.icon}
              <span className="palette-item-name">{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="palette-section">
        <div className="palette-section-title">Infrastructure Services</div>
        <div className="palette-grid">
          {conceptualDevices.map((item) => (
            <div
              key={item.type}
              className="palette-item"
              draggable
              onDragStart={(e) => handleDragStart(e, item.type)}
              onClick={() => onAddDevice(item.type)}
              title={`Click or drag to place a ${item.name}`}
              data-testid={`palette-item-${item.type.toLowerCase()}`}
            >
              {item.icon}
              <span className="palette-item-name">{item.name}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
