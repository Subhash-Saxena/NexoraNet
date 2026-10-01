import React from 'react'
import {
  Play,
  RotateCcw,
  Download,
  Upload,
  BookOpen,
  Send,
  Trash2,
} from 'lucide-react'
import type { SimDevice, SimProtocol, TopologyResponse } from '../../types/simulator'

interface SimulationControlsProps {
  devices: SimDevice[]
  sourceDeviceId: string
  destinationDeviceId: string
  protocol: SimProtocol
  port: number
  dnsQuery: string
  isSimulating: boolean
  prebuiltTopologies?: TopologyResponse[]
  onSourceChange: (deviceId: string) => void
  onDestinationChange: (deviceId: string) => void
  onProtocolChange: (protocol: SimProtocol) => void
  onPortChange: (port: number) => void
  onDnsQueryChange: (query: string) => void
  onTriggerSimulation: () => void
  onResetSimulation: () => void
  onClearCanvas: () => void
  onLoadPrebuiltTopology: (topo: TopologyResponse) => void
  onExportTopology: () => void
  onImportTopology: (jsonText: string) => void
  onOpenScenarios: () => void
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  devices,
  sourceDeviceId,
  destinationDeviceId,
  protocol,
  port,
  dnsQuery,
  isSimulating,
  prebuiltTopologies = [],
  onSourceChange,
  onDestinationChange,
  onProtocolChange,
  onPortChange,
  onDnsQueryChange,
  onTriggerSimulation,
  onResetSimulation,
  onClearCanvas,
  onLoadPrebuiltTopology,
  onExportTopology,
  onImportTopology,
  onOpenScenarios,
}) => {
  const fileInputRef = React.useRef<HTMLInputElement | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result as string
      if (content) {
        onImportTopology(content)
      }
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  return (
    <div className="simulation-dock" aria-label="Simulation Controls">
      <div className="simulation-dock-left">
        {/* Source Device */}
        <div className="sim-input-group">
          <label className="sim-input-label">Source:</label>
          <select
            className="sim-select"
            value={sourceDeviceId}
            onChange={(e) => onSourceChange(e.target.value)}
          >
            <option value="">-- Select Source --</option>
            {devices.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.interfaces[0]?.ipv4_address || 'No IP'})
              </option>
            ))}
          </select>
        </div>

        {/* Protocol Selector */}
        <div className="sim-input-group">
          <label className="sim-input-label">Protocol:</label>
          <select
            className="sim-select"
            value={protocol}
            onChange={(e) => onProtocolChange(e.target.value as SimProtocol)}
          >
            <option value="ICMP">ICMP (Ping)</option>
            <option value="TCP">TCP (3-Way Handshake)</option>
            <option value="DNS">DNS Query (Port 53)</option>
            <option value="DHCP">DHCP (DORA)</option>
          </select>
        </div>

        {/* Destination Device (for ICMP / TCP) */}
        {protocol !== 'DHCP' && (
          <div className="sim-input-group">
            <label className="sim-input-label">Target:</label>
            <select
              className="sim-select"
              value={destinationDeviceId}
              onChange={(e) => onDestinationChange(e.target.value)}
            >
              <option value="">-- Select Destination --</option>
              {devices
                .filter((d) => d.id !== sourceDeviceId)
                .map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.interfaces[0]?.ipv4_address || 'No IP'})
                  </option>
                ))}
            </select>
          </div>
        )}

        {/* Port Input for TCP */}
        {protocol === 'TCP' && (
          <div className="sim-input-group">
            <label className="sim-input-label">Port:</label>
            <input
              type="number"
              className="sim-select"
              style={{ width: '70px' }}
              value={port}
              onChange={(e) => onPortChange(parseInt(e.target.value, 10) || 80)}
            />
          </div>
        )}

        {/* DNS Query Name */}
        {protocol === 'DNS' && (
          <div className="sim-input-group">
            <label className="sim-input-label">Hostname:</label>
            <input
              type="text"
              className="sim-select"
              style={{ width: '140px' }}
              value={dnsQuery}
              onChange={(e) => onDnsQueryChange(e.target.value)}
            />
          </div>
        )}

        {/* Action Trigger */}
        <button
          className="sim-btn sim-btn-primary"
          onClick={onTriggerSimulation}
          disabled={isSimulating || (!sourceDeviceId && protocol !== 'DHCP')}
        >
          {protocol === 'ICMP' ? (
            <>
              <Send size={14} /> Send Ping
            </>
          ) : (
            <>
              <Play size={14} /> Simulate
            </>
          )}
        </button>

        <button
          className="sim-btn sim-btn-secondary"
          onClick={onResetSimulation}
          title="Reset Active Packet Animation & State"
        >
          <RotateCcw size={14} /> Reset
        </button>
      </div>

      <div className="simulator-topbar-actions">
        {/* Prebuilt Topologies Dropdown */}
        <select
          className="sim-select"
          onChange={(e) => {
            const found = prebuiltTopologies.find((t) => t.slug === e.target.value)
            if (found) onLoadPrebuiltTopology(found)
            e.target.value = ''
          }}
          defaultValue=""
        >
          <option value="" disabled>
            📂 Load Sample Topology...
          </option>
          {prebuiltTopologies.map((t) => (
            <option key={t.slug || t.id} value={t.slug || t.id}>
              {t.name}
            </option>
          ))}
        </select>

        {/* Scenarios Mode Button */}
        <button className="sim-btn sim-btn-accent" onClick={onOpenScenarios}>
          <BookOpen size={14} /> Scenarios
        </button>

        {/* Export / Import JSON */}
        <button
          className="sim-btn sim-btn-secondary"
          onClick={onExportTopology}
          title="Export topology as JSON file"
        >
          <Download size={14} /> Export
        </button>
        <button
          className="sim-btn sim-btn-secondary"
          onClick={() => fileInputRef.current?.click()}
          title="Import topology JSON"
        >
          <Upload size={14} /> Import
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        <button
          className="sim-btn sim-btn-danger"
          onClick={onClearCanvas}
          title="Clear all devices and links from canvas"
        >
          <Trash2 size={14} /> Clear
        </button>
      </div>
    </div>
  )
}
