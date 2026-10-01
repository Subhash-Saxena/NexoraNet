"""Pydantic schemas for Network Simulator topology, simulation engine, and scenarios."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Device & Interface Schemas
# ---------------------------------------------------------------------------


class DeviceInterfaceSchema(BaseModel):
    """Network interface model for a simulated device."""

    id: str
    name: str = Field(..., description="Interface name (e.g. eth0, fa0/1)")
    mac_address: str = Field(..., description="Deterministic virtual MAC address")
    ipv4_address: str | None = Field(default=None, description="Assigned IPv4 address")
    subnet_mask: str | None = Field(default="255.255.255.0", description="IPv4 subnet mask")
    ipv6_address: str | None = Field(default=None, description="Assigned IPv6 address")
    ipv6_prefix: int | None = Field(default=None, description="IPv6 prefix length")
    default_gateway: str | None = Field(default=None, description="Default gateway IPv4")
    vlan_id: int | None = Field(default=1, description="VLAN assignment")
    status: str = Field(default="up", description="Port operational status (up/down)")


class RouteEntrySchema(BaseModel):
    """Routing table entry on a router."""

    destination: str = Field(..., description="Network destination (e.g. 192.168.2.0 or 0.0.0.0)")
    netmask: str = Field(default="255.255.255.0", description="Destination subnet mask")
    next_hop: str = Field(..., description="Next hop IP or 'DIRECT'")
    interface: str = Field(..., description="Outbound interface name")
    metric: int = Field(default=1, description="Route cost/metric")


class MacEntrySchema(BaseModel):
    """Layer 2 MAC forwarding table entry on a switch."""

    mac_address: str
    port: str
    vlan_id: int = 1
    age: int = 0


class ArpEntrySchema(BaseModel):
    """ARP cache table entry on a host or router."""

    ip_address: str
    mac_address: str
    interface: str = "eth0"


class FirewallRuleSchema(BaseModel):
    """Stateless firewall rule."""

    id: str
    action: str = Field(default="ALLOW", description="ALLOW or DENY")
    protocol: str = Field(default="ANY", description="ANY, TCP, UDP, ICMP")
    source_ip: str = Field(default="ANY", description="Source IP or CIDR or ANY")
    destination_ip: str = Field(default="ANY", description="Destination IP or CIDR or ANY")
    port: str | int = Field(default="ANY", description="Destination port or ANY")
    description: str | None = None


class NatRuleSchema(BaseModel):
    """Network address translation static or overload rule."""

    inside_interface: str = "eth0"
    outside_interface: str = "eth1"
    public_ip: str = "203.0.113.1"


class NatEntrySchema(BaseModel):
    """Active NAT state table mapping."""

    inside_local: str
    inside_global: str
    outside_local: str
    outside_global: str
    protocol: str = "TCP"


class DeviceConfigurationSchema(BaseModel):
    """Device internal forwarding state, routing tables, and services."""

    routing_table: list[RouteEntrySchema] = Field(default_factory=list)
    mac_table: list[MacEntrySchema] = Field(default_factory=list)
    arp_table: list[ArpEntrySchema] = Field(default_factory=list)
    firewall_rules: list[FirewallRuleSchema] = Field(default_factory=list)
    nat_rules: list[NatRuleSchema] = Field(default_factory=list)
    nat_table: list[NatEntrySchema] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list, description="Enabled services e.g. DNS, DHCP, HTTP")
    dns_records: dict[str, str] = Field(default_factory=dict, description="Hostname to IP mappings")
    dhcp_pool: dict[str, Any] | None = Field(default=None, description="DHCP server configuration pool")


class SimDeviceSchema(BaseModel):
    """Simulated network device node."""

    id: str
    name: str
    type: str = Field(..., description="PC, LAPTOP, SERVER, SWITCH, ROUTER, FIREWALL, INTERNET, DNS_SERVER, DHCP_SERVER")
    position_x: float = 0.0
    position_y: float = 0.0
    interfaces: list[DeviceInterfaceSchema] = Field(default_factory=list)
    configuration: DeviceConfigurationSchema = Field(default_factory=DeviceConfigurationSchema)
    status: str = Field(default="active", description="active or offline")


class TopologyLinkSchema(BaseModel):
    """Link connecting two device interfaces."""

    id: str
    source_node_id: str
    source_interface_id: str
    target_node_id: str
    target_interface_id: str
    status: str = Field(default="up", description="up or down")
    link_type: str = Field(default="ethernet", description="ethernet, fiber, serial")


class TopologyDataSchema(BaseModel):
    """Complete graph state of devices and links."""

    nodes: list[SimDeviceSchema] = Field(default_factory=list)
    links: list[TopologyLinkSchema] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Topology API CRUD Schemas
# ---------------------------------------------------------------------------


class TopologyCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    difficulty: str = "BEGINNER"
    topology_data: TopologyDataSchema


class TopologyUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    difficulty: str | None = None
    topology_data: TopologyDataSchema | None = None


class TopologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    difficulty: str
    is_prebuilt: bool
    topology_data: TopologyDataSchema
    created_at: datetime
    updated_at: datetime


class TopologyValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    subnets_detected: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Simulation Engine Execution Schemas
# ---------------------------------------------------------------------------


class SimulatePacketRequest(BaseModel):
    topology: TopologyDataSchema
    source_device_id: str
    destination_device_id: str | None = None
    destination_ip: str | None = None
    protocol: str = Field(default="ICMP", description="ICMP, TCP, UDP, DNS, DHCP, HTTP")
    tcp_flags: list[str] | None = Field(default=None, description="SYN, SYN_ACK, ACK")
    dns_query_name: str | None = None
    port: int | None = None


class SimulationEventSchema(BaseModel):
    id: str
    timestamp_ms: int
    type: str
    device_id: str
    device_name: str
    packet_id: str
    message: str
    explanation: str
    why_reason: str
    cyber_relevance: str
    severity: str = "INFO"  # INFO, WARNING, ERROR, SUCCESS


class SimulatedPacketSchema(BaseModel):
    id: str
    protocol: str
    source_device_id: str
    destination_device_id: str
    source_ip: str
    destination_ip: str
    source_mac: str
    destination_mac: str
    ttl: int = 64
    ethernet_type: str = "0x0800"
    l3_payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "DELIVERED"  # IN_TRANSIT, DELIVERED, DROPPED
    drop_reason: str | None = None
    osi_layers: list[int] = Field(default_factory=lambda: [1, 2, 3])


class HopRecordSchema(BaseModel):
    hop_number: int
    device_id: str
    device_name: str
    device_type: str
    ingress_interface: str | None = None
    egress_interface: str | None = None
    action: str
    packet_snapshot: SimulatedPacketSchema
    layer_operations: dict[str, str] = Field(default_factory=dict)
    explanation: str
    why_reason: str
    cyber_relevance: str


class SimulationResultResponse(BaseModel):
    success: bool
    summary: str
    failure_reason: str | None = None
    packets: list[SimulatedPacketSchema] = Field(default_factory=list)
    events: list[SimulationEventSchema] = Field(default_factory=list)
    hops: list[HopRecordSchema] = Field(default_factory=list)
    arp_table_updates: dict[str, list[ArpEntrySchema]] = Field(default_factory=dict)
    mac_table_updates: dict[str, list[MacEntrySchema]] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scenario & Challenge Schemas
# ---------------------------------------------------------------------------


class ScenarioTaskSchema(BaseModel):
    id: str
    title: str
    description: str
    is_completed: bool = False


class ScenarioValidationRuleSchema(BaseModel):
    rule_type: str  # DEVICE_EXISTS, IP_MATCH, SUBNET_MATCH, GATEWAY_MATCH, ROUTE_EXISTS, PING_SUCCESS, etc.
    target_device: str | None = None
    target_interface: str | None = None
    expected_value: Any = None
    description: str


class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    difficulty: str
    category: str
    description: str
    learning_objectives: list[str] = Field(default_factory=list)
    initial_topology: TopologyDataSchema
    tasks: list[ScenarioTaskSchema] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    solution_explanation: str


class ScenarioValidationRequest(BaseModel):
    topology: TopologyDataSchema
    simulation_result: SimulationResultResponse | None = None
    hints_used: int = 0


class ScenarioValidationResultResponse(BaseModel):
    is_passed: bool
    score: int
    tasks_passed: int
    total_tasks: int
    task_results: list[dict[str, Any]] = Field(default_factory=list)
    feedback: str
    solution_explanation: str | None = None
