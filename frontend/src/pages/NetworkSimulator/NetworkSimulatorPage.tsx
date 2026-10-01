import React, { useState, useEffect, useCallback } from 'react'
import {
  Network,
  List,
  Layers,
  ChevronUp,
  ChevronDown,
  ShieldAlert,
} from 'lucide-react'
import { DevicePalette } from '../../components/simulator/DevicePalette'
import { NetworkCanvas } from '../../components/simulator/NetworkCanvas'
import { DevicePropertiesPanel } from '../../components/simulator/DevicePropertiesPanel'
import { SimulationControls } from '../../components/simulator/SimulationControls'
import { EventTimeline } from '../../components/simulator/EventTimeline'
import { PacketInspector } from '../../components/simulator/PacketInspector'
import { ScenarioDrawer } from '../../components/simulator/ScenarioDrawer'
import { simulatorApi } from '../../services/simulatorApi'
import type {
  SimDevice,
  SimDeviceType,
  TopologyLink,
  SimProtocol,
  SimulationResult,
  TopologyResponse,
  Scenario,
  ScenarioValidationResult,
  DeviceInterface,
} from '../../types/simulator'
import '../../components/simulator/simulator.css'

export const NetworkSimulatorPage: React.FC = () => {
  // Topology state
  const [devices, setDevices] = useState<SimDevice[]>([])
  const [links, setLinks] = useState<TopologyLink[]>([])
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null)
  const [selectedLinkId, setSelectedLinkId] = useState<string | null>(null)

  // Simulation controls state
  const [sourceDeviceId, setSourceDeviceId] = useState<string>('')
  const [destinationDeviceId, setDestinationDeviceId] = useState<string>('')
  const [protocol, setProtocol] = useState<SimProtocol>('ICMP')
  const [port, setPort] = useState<number>(80)
  const [dnsQuery, setDnsQuery] = useState<string>('www.example.local')
  const [isSimulating, setIsSimulating] = useState<boolean>(false)

  // Simulation Results & Hops
  const [simResult, setSimResult] = useState<SimulationResult | null>(null)
  const [activeHopIndex, setActiveHopIndex] = useState<number>(-1)

  // Bottom drawer state
  const [activeBottomTab, setActiveBottomTab] = useState<'timeline' | 'inspector'>('timeline')
  const [isDrawerCollapsed, setIsDrawerCollapsed] = useState<boolean>(false)

  // Scenarios and prebuilts
  const [prebuiltTopologies, setPrebuiltTopologies] = useState<TopologyResponse[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null)
  const [isScenarioDrawerOpen, setIsScenarioDrawerOpen] = useState<boolean>(false)

  // Load initial prebuilt topologies & scenarios
  useEffect(() => {
    simulatorApi
      .getTopologies()
      .then((topos) => {
        setPrebuiltTopologies(topos)
        if (topos.length > 0 && devices.length === 0) {
          // Load first topology by default
          const initial = topos[0]
          const nodes = initial.topology_data?.nodes || (initial.topology_data as any)?.devices || []
          const links = initial.topology_data?.links || []
          setDevices(nodes)
          setLinks(links)
          if (nodes.length >= 2) {
            setSourceDeviceId(nodes[0].id)
            setDestinationDeviceId(nodes[2]?.id || nodes[1].id)
          }
        }
      })
      .catch((err) => console.error('Failed to fetch topologies:', err))

    simulatorApi
      .getScenarios()
      .then((scs) => setScenarios(scs))
      .catch((err) => console.error('Failed to fetch scenarios:', err))
  }, [])

  // Listen for drop event from canvas
  useEffect(() => {
    const handleAddAt = (e: any) => {
      const { type, x, y } = e.detail
      handleAddDevice(type, x, y)
    }
    window.addEventListener('add-device-at', handleAddAt)
    return () => window.removeEventListener('add-device-at', handleAddAt)
  }, [devices])

  // Helper: Generate deterministic MAC
  const generateMac = (type: string, index: number, ifaceIndex: number = 0) => {
    const typeMap: Record<string, string> = {
      PC: '01',
      LAPTOP: '02',
      SERVER: '03',
      SWITCH: '04',
      ROUTER: '05',
      FIREWALL: '06',
      INTERNET: '07',
      DNS_SERVER: '08',
      DHCP_SERVER: '09',
    }
    const tCode = typeMap[type] || '10'
    const dCode = index.toString(16).padStart(2, '0')
    const iCode = ifaceIndex.toString(16).padStart(2, '0')
    return `02:00:${tCode}:${dCode}:${iCode}:01`
  }

  // Add Device
  const handleAddDevice = useCallback(
    (type: SimDeviceType, x?: number, y?: number) => {
      const count = devices.filter((d) => d.type === type).length + 1
      const id = `${type.toLowerCase()}-${Date.now().toString().slice(-4)}`
      const name = `${type === 'SWITCH' ? 'Switch' : type === 'ROUTER' ? 'Router' : type === 'FIREWALL' ? 'Firewall' : type === 'SERVER' ? 'Server' : 'PC'}${count}`

      let interfaces: DeviceInterface[] = [
        {
          id: `if-${id}-eth0`,
          name: 'eth0',
          mac_address: generateMac(type, count, 0),
          ipv4_address: type === 'SWITCH' ? null : `192.168.1.${10 + count}`,
          subnet_mask: '255.255.255.0',
          default_gateway: type === 'ROUTER' || type === 'SWITCH' ? null : '192.168.1.1',
          status: 'up',
        },
      ]

      if (type === 'SWITCH') {
        interfaces = [
          { id: `if-${id}-p1`, name: 'Port 1', mac_address: generateMac(type, count, 1), status: 'up', vlan_id: 1 },
          { id: `if-${id}-p2`, name: 'Port 2', mac_address: generateMac(type, count, 2), status: 'up', vlan_id: 1 },
          { id: `if-${id}-p3`, name: 'Port 3', mac_address: generateMac(type, count, 3), status: 'up', vlan_id: 1 },
          { id: `if-${id}-p4`, name: 'Port 4', mac_address: generateMac(type, count, 4), status: 'up', vlan_id: 1 },
        ]
      } else if (type === 'ROUTER' || type === 'FIREWALL') {
        interfaces = [
          { id: `if-${id}-eth0`, name: 'eth0', mac_address: generateMac(type, count, 0), ipv4_address: '192.168.1.1', subnet_mask: '255.255.255.0', default_gateway: null, status: 'up' },
          { id: `if-${id}-eth1`, name: 'eth1', mac_address: generateMac(type, count, 1), ipv4_address: '192.168.2.1', subnet_mask: '255.255.255.0', default_gateway: null, status: 'up' },
        ]
      }

      const newDevice: SimDevice = {
        id,
        name,
        type,
        position_x: x ?? 100 + (devices.length % 5) * 80,
        position_y: y ?? 100 + Math.floor(devices.length / 5) * 80,
        interfaces,
        configuration: {
          routing_table:
            type === 'ROUTER' || type === 'FIREWALL'
              ? [
                  { destination: '192.168.1.0', netmask: '255.255.255.0', next_hop: 'DIRECT', interface: 'eth0' },
                  { destination: '192.168.2.0', netmask: '255.255.255.0', next_hop: 'DIRECT', interface: 'eth1' },
                ]
              : [],
          firewall_rules: [],
          services: type === 'DNS_SERVER' ? ['DNS'] : type === 'DHCP_SERVER' ? ['DHCP'] : [],
        },
        status: 'active',
      }

      setDevices((prev) => [...prev, newDevice])
      setSelectedDeviceId(newDevice.id)
    },
    [devices]
  )

  // Move Device
  const handleMoveDevice = (deviceId: string, x: number, y: number) => {
    setDevices((prev) =>
      prev.map((d) => (d.id === deviceId ? { ...d, position_x: x, position_y: y } : d))
    )
  }

  // Connect Devices
  const handleConnectDevices = (
    sourceNodeId: string,
    sourceIfaceId: string,
    targetNodeId: string,
    targetIfaceId: string
  ) => {
    // Check if link already exists between these interfaces
    const exists = links.some(
      (l) =>
        (l.source_interface_id === sourceIfaceId && l.target_interface_id === targetIfaceId) ||
        (l.source_interface_id === targetIfaceId && l.target_interface_id === sourceIfaceId)
    )
    if (exists) return

    const newLink: TopologyLink = {
      id: `link-${Date.now().toString().slice(-5)}`,
      source_node_id: sourceNodeId,
      source_interface_id: sourceIfaceId,
      target_node_id: targetNodeId,
      target_interface_id: targetIfaceId,
      status: 'up',
      link_type: 'ethernet',
    }
    setLinks((prev) => [...prev, newLink])
  }

  // Delete Link
  const handleDeleteLink = (linkId: string) => {
    setLinks((prev) => prev.filter((l) => l.id !== linkId))
    if (selectedLinkId === linkId) setSelectedLinkId(null)
  }

  // Update Device
  const handleUpdateDevice = (updated: SimDevice) => {
    setDevices((prev) => prev.map((d) => (d.id === updated.id ? updated : d)))
  }

  // Delete Device
  const handleDeleteDevice = (deviceId: string) => {
    setDevices((prev) => prev.filter((d) => d.id !== deviceId))
    setLinks((prev) =>
      prev.filter((l) => l.source_node_id !== deviceId && l.target_node_id !== deviceId)
    )
    if (selectedDeviceId === deviceId) setSelectedDeviceId(null)
    if (sourceDeviceId === deviceId) setSourceDeviceId('')
    if (destinationDeviceId === deviceId) setDestinationDeviceId('')
  }

  // Clear Canvas
  const handleClearCanvas = () => {
    setDevices([])
    setLinks([])
    setSelectedDeviceId(null)
    setSelectedLinkId(null)
    setSimResult(null)
    setActiveHopIndex(-1)
  }

  // Load Prebuilt Topology
  const handleLoadPrebuilt = (topo: TopologyResponse) => {
    const nodes = topo.topology_data?.nodes || (topo.topology_data as any)?.devices || []
    const links = topo.topology_data?.links || []
    setDevices(nodes)
    setLinks(links)
    setSelectedDeviceId(null)
    setSelectedLinkId(null)
    setSimResult(null)
    setActiveHopIndex(-1)
    if (nodes.length >= 2) {
      setSourceDeviceId(nodes[0].id)
      setDestinationDeviceId(nodes[2]?.id || nodes[1].id)
    }
  }

  // Export JSON
  const handleExportTopology = () => {
    const topoData = {
      version: 1,
      name: 'My Exported Network',
      devices,
      links,
    }
    const blob = new Blob([JSON.stringify(topoData, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `network-topology-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Import JSON with sanitization
  const handleImportTopology = (jsonText: string) => {
    try {
      const parsed = JSON.parse(jsonText)
      if (Array.isArray(parsed.devices) && Array.isArray(parsed.links)) {
        setDevices(parsed.devices)
        setLinks(parsed.links)
        setSelectedDeviceId(null)
        setSimResult(null)
      } else if (Array.isArray(parsed.nodes) && Array.isArray(parsed.links)) {
        setDevices(parsed.nodes)
        setLinks(parsed.links)
        setSelectedDeviceId(null)
        setSimResult(null)
      } else {
        alert('Invalid topology format. File must contain devices and links arrays.')
      }
    } catch (e) {
      alert('Failed to parse JSON file.')
    }
  }

  // Trigger Authoritative Simulation
  const handleTriggerSimulation = async () => {
    if (!sourceDeviceId && protocol !== 'DHCP') return

    setIsSimulating(true)
    setSimResult(null)
    setActiveHopIndex(-1)

    try {
      const res = await simulatorApi.simulatePacket({
        topology: { nodes: devices, links },
        source_device_id: sourceDeviceId,
        destination_device_id: destinationDeviceId || undefined,
        protocol,
        port,
        dns_query_name: dnsQuery,
      })

      setSimResult(res)

      // Step through hops sequentially
      if (res.hops.length > 0) {
        let currentHop = 0
        setActiveHopIndex(0)

        const interval = setInterval(() => {
          currentHop += 1
          if (currentHop < res.hops.length) {
            setActiveHopIndex(currentHop)
          } else {
            clearInterval(interval)
          }
        }, 900)
      }
    } catch (err: any) {
      alert(err.message || 'Simulation execution failed.')
    } finally {
      setIsSimulating(false)
    }
  }

  // Reset Simulation
  const handleResetSimulation = () => {
    setSimResult(null)
    setActiveHopIndex(-1)
  }

  // Scenario Validation
  const handleValidateScenario = async (hintsUsed: number): Promise<ScenarioValidationResult | null> => {
    if (!activeScenario) return null
    return simulatorApi.validateScenario(activeScenario.slug, {
      topology: { nodes: devices, links },
      hints_used: hintsUsed,
    })
  }

  // Currently selected device
  const selectedDevice = (devices || []).find((d) => d.id === selectedDeviceId) || null
  const activeHop = simResult && activeHopIndex >= 0 ? simResult.hops[activeHopIndex] : null

  return (
    <div className="simulator-container" data-testid="network-simulator-page">
      {/* Disclaimer Banner */}
      <div className="simulator-disclaimer">
        <div className="simulator-disclaimer-text">
          <ShieldAlert size={14} />
          <span>
            <strong>Educational Sandbox Notice:</strong> NexoraNet Simulator uses a virtual network. Packets shown here are simulated and are not sent onto your real network.
          </span>
        </div>
      </div>

      {/* Top Bar */}
      <header className="simulator-topbar">
        <div className="simulator-topbar-left">
          <span className="simulator-title">
            <Network size={20} color="#38bdf8" /> NexoraNet Network Simulator
          </span>
          <span className="simulator-badge">Virtual Lab</span>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="simulator-body">
        {/* Left: Device Palette */}
        <DevicePalette onAddDevice={(t) => handleAddDevice(t)} />

        {/* Center: Canvas Area */}
        <main className="simulator-canvas-area">
          <NetworkCanvas
            devices={devices}
            links={links}
            selectedDeviceId={selectedDeviceId}
            selectedLinkId={selectedLinkId}
            onSelectDevice={(id) => setSelectedDeviceId(id)}
            onSelectLink={(id) => setSelectedLinkId(id)}
            onMoveDevice={handleMoveDevice}
            onConnectDevices={handleConnectDevices}
            onDeleteLink={handleDeleteLink}
            activeHop={activeHop}
          />

          {/* Docked Simulation Controls */}
          <SimulationControls
            devices={devices}
            sourceDeviceId={sourceDeviceId}
            destinationDeviceId={destinationDeviceId}
            protocol={protocol}
            port={port}
            dnsQuery={dnsQuery}
            isSimulating={isSimulating}
            prebuiltTopologies={prebuiltTopologies}
            onSourceChange={(id) => setSourceDeviceId(id)}
            onDestinationChange={(id) => setDestinationDeviceId(id)}
            onProtocolChange={(p) => setProtocol(p)}
            onPortChange={(pt) => setPort(pt)}
            onDnsQueryChange={(q) => setDnsQuery(q)}
            onTriggerSimulation={handleTriggerSimulation}
            onResetSimulation={handleResetSimulation}
            onClearCanvas={handleClearCanvas}
            onLoadPrebuiltTopology={handleLoadPrebuilt}
            onExportTopology={handleExportTopology}
            onImportTopology={handleImportTopology}
            onOpenScenarios={() => setIsScenarioDrawerOpen(true)}
          />
        </main>

        {/* Right: Device Properties Panel */}
        <DevicePropertiesPanel
          device={selectedDevice}
          allDevices={devices}
          links={links}
          onUpdateDevice={handleUpdateDevice}
          onDeleteDevice={handleDeleteDevice}
        />
      </div>

      {/* Bottom Drawer: Event Timeline & Packet Inspector */}
      <section
        className={`simulator-bottom-drawer ${isDrawerCollapsed ? 'collapsed' : ''}`}
        aria-label="Packet Traversal and Event Inspector"
      >
        <div className="drawer-header">
          <div className="drawer-tabs">
            <button
              className={`drawer-tab ${activeBottomTab === 'timeline' ? 'active' : ''}`}
              onClick={() => {
                setActiveBottomTab('timeline')
                if (isDrawerCollapsed) setIsDrawerCollapsed(false)
              }}
            >
              <List size={14} /> Event Timeline ({simResult?.events.length || 0})
            </button>
            <button
              className={`drawer-tab ${activeBottomTab === 'inspector' ? 'active' : ''}`}
              onClick={() => {
                setActiveBottomTab('inspector')
                if (isDrawerCollapsed) setIsDrawerCollapsed(false)
              }}
            >
              <Layers size={14} /> Packet Inspector & OSI Stack
            </button>
          </div>

          <button
            className="sim-btn sim-btn-secondary"
            style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem' }}
            onClick={() => setIsDrawerCollapsed(!isDrawerCollapsed)}
            title={isDrawerCollapsed ? 'Expand panel' : 'Collapse panel'}
          >
            {isDrawerCollapsed ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>

        {!isDrawerCollapsed && (
          <div className="drawer-content">
            {activeBottomTab === 'timeline' ? (
              <EventTimeline events={simResult?.events || []} />
            ) : (
              <PacketInspector activeHop={activeHop} />
            )}
          </div>
        )}
      </section>

      {/* Scenario & Challenge Drawer */}
      <ScenarioDrawer
        isOpen={isScenarioDrawerOpen}
        onClose={() => setIsScenarioDrawerOpen(false)}
        scenarios={scenarios}
        activeScenario={activeScenario}
        onSelectScenario={(sc) => {
          setActiveScenario(sc)
          if (sc) {
            setDevices(sc.initial_topology.nodes)
            setLinks(sc.initial_topology.links)
            setSimResult(null)
          }
        }}
        currentTopology={{ nodes: devices, links }}
        onValidateScenario={handleValidateScenario}
      />
    </div>
  )
}
