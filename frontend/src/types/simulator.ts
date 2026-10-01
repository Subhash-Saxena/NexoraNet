/**
 * TypeScript domain types for the Interactive Network Simulator.
 */

export type SimDeviceType =
  | 'PC'
  | 'LAPTOP'
  | 'SERVER'
  | 'SWITCH'
  | 'ROUTER'
  | 'FIREWALL'
  | 'INTERNET'
  | 'DNS_SERVER'
  | 'DHCP_SERVER'

export type SimProtocol = 'ICMP' | 'TCP' | 'UDP' | 'DNS' | 'DHCP' | 'ARP' | 'HTTP'

export interface DeviceInterface {
  id: string
  name: string
  mac_address: string
  ipv4_address?: string | null
  subnet_mask?: string | null
  ipv6_address?: string | null
  ipv6_prefix?: number | null
  default_gateway?: string | null
  vlan_id?: number | null
  status: 'up' | 'down'
}

export interface RouteEntry {
  destination: string
  netmask: string
  next_hop: string
  interface: string
  metric?: number
}

export interface MacEntry {
  mac_address: string
  port: string
  vlan_id: number
  age: number
}

export interface ArpEntry {
  ip_address: string
  mac_address: string
  interface: string
}

export interface FirewallRule {
  id: string
  action: 'ALLOW' | 'DENY'
  protocol: 'ANY' | 'TCP' | 'UDP' | 'ICMP'
  source_ip: string
  destination_ip: string
  port: string | number
  description?: string | null
}

export interface NatRule {
  inside_interface: string
  outside_interface: string
  public_ip: string
}

export interface DeviceConfiguration {
  routing_table?: RouteEntry[]
  mac_table?: MacEntry[]
  arp_table?: ArpEntry[]
  firewall_rules?: FirewallRule[]
  nat_rules?: NatRule[]
  services?: string[]
  dns_records?: Record<string, string>
  dhcp_pool?: {
    network?: string
    start?: string
    end?: string
    gateway?: string
    dns?: string
  } | null
}

export interface SimDevice {
  id: string
  name: string
  type: SimDeviceType
  position_x: number
  position_y: number
  interfaces: DeviceInterface[]
  configuration: DeviceConfiguration
  status: 'active' | 'offline'
}

export interface TopologyLink {
  id: string
  source_node_id: string
  source_interface_id: string
  target_node_id: string
  target_interface_id: string
  status: 'up' | 'down'
  link_type: 'ethernet' | 'fiber' | 'serial'
}

export interface TopologyData {
  nodes: SimDevice[]
  links: TopologyLink[]
}

export interface TopologyResponse {
  id: number
  user_id?: number | null
  name: string
  slug: string
  description?: string | null
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'
  is_prebuilt: boolean
  topology_data: TopologyData
  created_at: string
  updated_at: string
}

export interface SimulationEvent {
  id: string
  timestamp_ms: number
  type: string
  device_id: string
  device_name: string
  packet_id: string
  message: string
  explanation: string
  why_reason: string
  cyber_relevance: string
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS'
}

export interface SimulatedPacket {
  id: string
  protocol: SimProtocol
  source_device_id: string
  destination_device_id: string
  source_ip: string
  destination_ip: string
  source_mac: string
  destination_mac: string
  ttl: number
  ethernet_type: string
  l3_payload: Record<string, any>
  status: 'IN_TRANSIT' | 'DELIVERED' | 'DROPPED'
  drop_reason?: string | null
  osi_layers: number[]
}

export interface HopRecord {
  hop_number: number
  device_id: string
  device_name: string
  device_type: string
  ingress_interface?: string | null
  egress_interface?: string | null
  action: string
  packet_snapshot: SimulatedPacket
  layer_operations: Record<string, string>
  explanation: string
  why_reason: string
  cyber_relevance: string
}

export interface SimulationResult {
  success: boolean
  summary: string
  failure_reason?: string | null
  packets: SimulatedPacket[]
  events: SimulationEvent[]
  hops: HopRecord[]
  arp_table_updates?: Record<string, ArpEntry[]>
  mac_table_updates?: Record<string, MacEntry[]>
}

export interface ScenarioTask {
  id: string
  title: string
  description: string
  is_completed: boolean
}

export interface Scenario {
  id: number
  slug: string
  title: string
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'
  category: string
  description: string
  learning_objectives: string[]
  initial_topology: TopologyData
  tasks: ScenarioTask[]
  hints: string[]
  solution_explanation: string
}

export interface ScenarioValidationResult {
  is_passed: boolean
  score: number
  tasks_passed: number
  total_tasks: number
  task_results: Array<{
    rule_index: number
    description: string
    passed: boolean
    message: string
  }>
  feedback: string
  solution_explanation?: string | null
}
