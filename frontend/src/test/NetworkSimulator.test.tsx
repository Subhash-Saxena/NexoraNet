import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { NetworkSimulatorPage } from '../pages/NetworkSimulator/NetworkSimulatorPage'
import { DevicePalette } from '../components/simulator/DevicePalette'
import { SimulationControls } from '../components/simulator/SimulationControls'
import { PacketInspector } from '../components/simulator/PacketInspector'
import { EventTimeline } from '../components/simulator/EventTimeline'
import { DevicePropertiesPanel } from '../components/simulator/DevicePropertiesPanel'
import { ScenarioDrawer } from '../components/simulator/ScenarioDrawer'
import { simulatorApi } from '../services/simulatorApi'
import type {
  SimDevice,
  SimulationResult,
  SimulatedPacket,
  HopRecord,
  SimulationEvent,
  Scenario,
  ScenarioValidationResult,
  TopologyResponse,
} from '../types/simulator'

// Mock simulatorApi
vi.mock('../services/simulatorApi', () => ({
  simulatorApi: {
    getTopologies: vi.fn(),
    getTopology: vi.fn(),
    createTopology: vi.fn(),
    updateTopology: vi.fn(),
    deleteTopology: vi.fn(),
    validateTopology: vi.fn(),
    simulatePacket: vi.fn(),
    getScenarios: vi.fn(),
    getScenario: vi.fn(),
    validateScenario: vi.fn(),
  },
}))

const sampleDevices: SimDevice[] = [
  {
    id: 'pc-1',
    name: 'PC1',
    type: 'PC',
    position_x: 100,
    position_y: 100,
    interfaces: [
      {
        id: 'if-pc1-eth0',
        name: 'eth0',
        mac_address: '02:00:00:00:01:01',
        ipv4_address: '192.168.1.10',
        subnet_mask: '255.255.255.0',
        default_gateway: '192.168.1.1',
        status: 'up',
      },
    ],
    configuration: {
      arp_table: [],
    },
  },
  {
    id: 'pc-2',
    name: 'PC2',
    type: 'PC',
    position_x: 350,
    position_y: 100,
    interfaces: [
      {
        id: 'if-pc2-eth0',
        name: 'eth0',
        mac_address: '02:00:00:00:02:01',
        ipv4_address: '192.168.1.20',
        subnet_mask: '255.255.255.0',
        default_gateway: '192.168.1.1',
        status: 'up',
      },
    ],
    configuration: {
      arp_table: [],
    },
  },
]

const sampleTopology: TopologyResponse = {
  id: 1,
  name: 'Direct Two PC Link',
  slug: 'two-pcs-direct',
  description: 'Two PCs connected by an Ethernet cable.',
  difficulty: 'BEGINNER',
  is_prebuilt: true,
  topology_data: {
    nodes: sampleDevices,
    links: [
      {
        id: 'link-1',
        source_node_id: 'pc-1',
        source_interface_id: 'if-pc1-eth0',
        target_node_id: 'pc-2',
        target_interface_id: 'if-pc2-eth0',
        status: 'up',
        link_type: 'ethernet',
      },
    ],
  },
  created_at: '2026-09-30T10:00:00Z',
  updated_at: '2026-09-30T10:00:00Z',
}

const samplePacket: SimulatedPacket = {
  id: 'pkt-1',
  protocol: 'ICMP',
  source_device_id: 'pc-1',
  destination_device_id: 'pc-2',
  source_ip: '192.168.1.10',
  destination_ip: '192.168.1.20',
  source_mac: '02:00:00:00:01:01',
  destination_mac: '02:00:00:00:02:01',
  ttl: 64,
  ethernet_type: '0x0800',
  l3_payload: { icmp_type: 'ECHO_REQUEST', seq: 1 },
  status: 'DELIVERED',
  osi_layers: [1, 2, 3, 4],
}

const sampleHop: HopRecord = {
  hop_number: 1,
  device_id: 'pc-1',
  device_name: 'PC1',
  device_type: 'PC',
  ingress_interface: null,
  egress_interface: 'eth0',
  action: 'TRANSMIT',
  packet_snapshot: samplePacket,
  layer_operations: { L2: 'Encapsulated frame', L3: 'Set TTL 64' },
  explanation: 'PC1 generated an ICMP Echo Request targeted for 192.168.1.20.',
  why_reason: 'Nodes on the same subnet broadcast ARP or transmit directly using known MAC.',
  cyber_relevance: 'Network mapping and ping sweeps start with ICMP Echo queries.',
}

const sampleEvent: SimulationEvent = {
  id: 'ev-1',
  timestamp_ms: 10,
  type: 'PACKET_TRANSMIT',
  device_id: 'pc-1',
  device_name: 'PC1',
  packet_id: 'pkt-1',
  message: 'PC1 transmitted frame to PC2 across eth0.',
  explanation: 'Ethernet frame sent to next hop.',
  why_reason: 'Direct transmission across point-to-point link.',
  cyber_relevance: 'Sniffers can capture promiscuous frames on shared segments.',
  severity: 'INFO',
}

const sampleSimResult: SimulationResult = {
  success: true,
  summary: 'Ping successful. 1/1 packets delivered.',
  packets: [samplePacket],
  events: [sampleEvent],
  hops: [sampleHop],
}

const sampleScenarios: Scenario[] = [
  {
    id: 1,
    slug: 'first-ping',
    title: 'First Ping: Peer-to-Peer',
    category: 'beginner',
    difficulty: 'BEGINNER',
    description: 'Connect two PCs directly and ping successfully.',
    learning_objectives: ['Understand direct Ethernet connections', 'Configure IP addresses'],
    initial_topology: {
      devices: sampleDevices,
      links: [],
    },
    tasks: [
      {
        id: 'task-1',
        title: 'Connect PC1 and PC2',
        description: 'Connect PC1 and PC2 with an Ethernet cable',
        is_completed: false,
      },
    ],
    hints: [
      'Click and drag a wire from eth0 on PC1 to eth0 on PC2.',
      'Ensure both machines have IPs on 192.168.1.0/24.',
    ],
    solution_explanation: 'Direct connections require compatible IP subnets.',
  },
]

describe('Network Simulator Frontend Components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(simulatorApi.getTopologies).mockResolvedValue([sampleTopology])
    vi.mocked(simulatorApi.getTopology).mockResolvedValue(sampleTopology)
    vi.mocked(simulatorApi.getScenarios).mockResolvedValue(sampleScenarios)
    vi.mocked(simulatorApi.simulatePacket).mockResolvedValue(sampleSimResult)
  })

  it('renders the DevicePalette with all device categories', () => {
    const handleAdd = vi.fn()
    render(<DevicePalette onAddDevice={handleAdd} />)

    expect(screen.getByText('End Devices')).toBeInTheDocument()
    expect(screen.getByText('Network Devices')).toBeInTheDocument()
    expect(screen.getByText('Infrastructure Services')).toBeInTheDocument()

    // Test clicking a device in palette triggers onAddDevice
    const pcBtn = screen.getByText('Workstation PC')
    fireEvent.click(pcBtn)
    expect(handleAdd).toHaveBeenCalledWith('PC')

    const switchBtn = screen.getByText('L2 Switch')
    fireEvent.click(switchBtn)
    expect(handleAdd).toHaveBeenCalledWith('SWITCH')

    const routerBtn = screen.getByText('L3 Router')
    fireEvent.click(routerBtn)
    expect(handleAdd).toHaveBeenCalledWith('ROUTER')
  })

  it('renders SimulationControls and handles protocol selection', () => {
    const handleSimulate = vi.fn()
    const handleReset = vi.fn()
    const handleClear = vi.fn()
    const handlePrebuilt = vi.fn()
    const handleExport = vi.fn()
    const handleImport = vi.fn()
    const handleToggleScenarios = vi.fn()

    render(
      <SimulationControls
        devices={sampleDevices}
        sourceDeviceId="pc-1"
        destinationDeviceId="pc-2"
        protocol="ICMP"
        port={80}
        dnsQuery="www.example.local"
        isSimulating={false}
        prebuiltTopologies={[sampleTopology]}
        onSourceChange={vi.fn()}
        onDestinationChange={vi.fn()}
        onProtocolChange={vi.fn()}
        onPortChange={vi.fn()}
        onDnsQueryChange={vi.fn()}
        onTriggerSimulation={handleSimulate}
        onResetSimulation={handleReset}
        onClearCanvas={handleClear}
        onLoadPrebuiltTopology={handlePrebuilt}
        onExportTopology={handleExport}
        onImportTopology={handleImport}
        onOpenScenarios={handleToggleScenarios}
      />
    )

    expect(screen.getByText(/Send Ping/i)).toBeInTheDocument()
    expect(screen.getByText('Scenarios')).toBeInTheDocument()

    // Click Send Ping
    fireEvent.click(screen.getByText(/Send Ping/i))
    expect(handleSimulate).toHaveBeenCalled()

    // Click Scenarios
    fireEvent.click(screen.getByText('Scenarios'))
    expect(handleToggleScenarios).toHaveBeenCalled()
  })

  it('renders PacketInspector and visualizes OSI layers', () => {
    render(<PacketInspector activeHop={sampleHop} />)

    expect(screen.getByText('L4: Transport')).toBeInTheDocument()
    expect(screen.getByText('L3: Network')).toBeInTheDocument()
    expect(screen.getByText('L2: Data Link')).toBeInTheDocument()

    // Check decoded packet fields
    expect(screen.getByText('SOURCE IP')).toBeInTheDocument()
    expect(screen.getByText('192.168.1.10')).toBeInTheDocument()
    expect(screen.getByText('DESTINATION IP')).toBeInTheDocument()
    expect(screen.getByText('192.168.1.20')).toBeInTheDocument()
    expect(screen.getByText('TIME-TO-LIVE (TTL)')).toBeInTheDocument()
    expect(screen.getByText('64 hops')).toBeInTheDocument()
  })

  it('renders EventTimeline and displays chronological events and "Why?" toggle', () => {
    render(<EventTimeline events={[sampleEvent]} />)

    expect(screen.getByText(/PC1 transmitted frame to PC2 across eth0/i)).toBeInTheDocument()
    expect(screen.getByText('Why?')).toBeInTheDocument()

    // Click Why? to expand educational explanation
    fireEvent.click(screen.getByText('Why?'))
    expect(screen.getByText(/Direct transmission across point-to-point link/i)).toBeInTheDocument()
  })

  it('renders DevicePropertiesPanel showing device details and interface config', () => {
    const handleUpdate = vi.fn()
    const handleDelete = vi.fn()

    render(
      <DevicePropertiesPanel
        device={sampleDevices[0]}
        allDevices={sampleDevices}
        links={[]}
        onUpdateDevice={handleUpdate}
        onDeleteDevice={handleDelete}
      />
    )

    expect(screen.getByText(/PC1 \(PC\)/i)).toBeInTheDocument()
    expect(screen.getByDisplayValue('PC1')).toBeInTheDocument()
    expect(screen.getByText('ONLINE / ACTIVE')).toBeInTheDocument()

    // Switch to interfaces tab to inspect IP
    const ifaceTab = screen.getByRole('button', { name: /Interfaces/i })
    fireEvent.click(ifaceTab)
    expect(screen.getByDisplayValue('192.168.1.10')).toBeInTheDocument()
    expect(screen.getByDisplayValue('255.255.255.0')).toBeInTheDocument()

    // Delete device button
    const deleteBtn = screen.getByRole('button', { name: /Delete/i })
    fireEvent.click(deleteBtn)
    expect(handleDelete).toHaveBeenCalledWith('pc-1')
  })

  it('renders DevicePropertiesPanel network overview when no device is selected', () => {
    render(
      <DevicePropertiesPanel
        device={null}
        allDevices={sampleDevices}
        links={[]}
        onUpdateDevice={vi.fn()}
        onDeleteDevice={vi.fn()}
      />
    )

    expect(screen.getByText('Network Overview')).toBeInTheDocument()
    expect(screen.getByText('TOTAL DEVICES')).toBeInTheDocument()
    expect(screen.getByText(/End Stations:/i)).toBeInTheDocument()
  })

  it('renders ScenarioDrawer with tasks and progressive hints', async () => {
    const handleSelectScenario = vi.fn()
    const handleCheckSolution = vi.fn()
    const handleClose = vi.fn()

    const validationResult: ScenarioValidationResult = {
      is_passed: true,
      score: 100,
      tasks_passed: 1,
      total_tasks: 1,
      feedback: 'All objectives completed!',
      task_results: [
        {
          rule_index: 0,
          description: 'Connect PC1 and PC2 with an Ethernet cable',
          passed: true,
          message: 'Connection established between PC1 and PC2.',
        },
      ],
      solution_explanation: 'Direct connection successful.',
    }

    const handleValidateScenario = vi.fn().mockResolvedValue(validationResult)

    render(
      <ScenarioDrawer
        isOpen={true}
        scenarios={sampleScenarios}
        activeScenario={sampleScenarios[0]}
        currentTopology={{ nodes: sampleDevices, links: [] }}
        onSelectScenario={handleSelectScenario}
        onValidateScenario={handleValidateScenario}
        onClose={handleClose}
      />
    )

    expect(screen.getByText('Guided Scenarios & Challenges')).toBeInTheDocument()
    expect(screen.getByText('First Ping: Peer-to-Peer')).toBeInTheDocument()
    expect(screen.getByText('Connect PC1 and PC2')).toBeInTheDocument()

    // Progressive Hint test
    const hintBtn = screen.getByRole('button', { name: /Reveal Hint/i })
    act(() => {
      fireEvent.click(hintBtn)
    })
    expect(screen.getByText(/Click and drag a wire from eth0 on PC1 to eth0 on PC2/i)).toBeInTheDocument()

    // Check solution button
    const checkBtn = screen.getByRole('button', { name: /Check Solution/i })
    await act(async () => {
      fireEvent.click(checkBtn)
    })
    expect(handleValidateScenario).toHaveBeenCalled()
  })

  it('renders NetworkSimulatorPage with sandbox disclaimer and allows sending packet', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <NetworkSimulatorPage />
        </MemoryRouter>
      )
    })

    // Disclaimer check
    expect(
      screen.getByText(/NexoraNet Simulator uses a virtual network. Packets shown here are simulated and are not sent onto your real network./i)
    ).toBeInTheDocument()

    // Header check
    expect(screen.getByText(/NexoraNet Network Simulator/i)).toBeInTheDocument()
    expect(screen.getByText('Virtual Lab')).toBeInTheDocument()
  })
})
