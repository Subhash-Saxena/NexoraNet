"""Catalog and synchronization service for prebuilt topologies and guided scenarios."""

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.simulator import SimulatorScenario, SimulatorTopology
from app.schemas.simulator import (
    ScenarioResponse,
    ScenarioTaskSchema,
    TopologyDataSchema,
    TopologyResponse,
)

logger = logging.getLogger("nexoranet.simulator_catalog")

# ---------------------------------------------------------------------------
# Prebuilt Topologies
# ---------------------------------------------------------------------------

PREBUILT_TOPOLOGIES: list[dict[str, Any]] = [
    {
        "name": "Simple LAN (PC to PC via Switch)",
        "slug": "simple-lan",
        "description": "Two workstation PCs connected via an unmanaged Layer 2 switch within the 192.168.1.0/24 broadcast domain.",
        "difficulty": "BEGINNER",
        "is_prebuilt": True,
        "nodes": [
            {
                "id": "pc-1",
                "name": "PC1",
                "type": "PC",
                "position_x": 120,
                "position_y": 180,
                "interfaces": [
                    {
                        "id": "if-pc1-eth0",
                        "name": "eth0",
                        "mac_address": "02:00:01:01:00:01",
                        "ipv4_address": "192.168.1.10",
                        "subnet_mask": "255.255.255.0",
                        "default_gateway": "192.168.1.1",
                    }
                ],
            },
            {
                "id": "sw-1",
                "name": "Switch1",
                "type": "SWITCH",
                "position_x": 340,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01", "vlan_id": 1},
                    {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01", "vlan_id": 1},
                ],
            },
            {
                "id": "pc-2",
                "name": "PC2",
                "type": "PC",
                "position_x": 560,
                "position_y": 180,
                "interfaces": [
                    {
                        "id": "if-pc2-eth0",
                        "name": "eth0",
                        "mac_address": "02:00:01:02:00:01",
                        "ipv4_address": "192.168.1.20",
                        "subnet_mask": "255.255.255.0",
                        "default_gateway": "192.168.1.1",
                    }
                ],
            },
        ],
        "links": [
            {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
            {"id": "link-2", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p2", "target_node_id": "pc-2", "target_interface_id": "if-pc2-eth0"},
        ],
    },
    {
        "name": "Local LAN with Department File Server",
        "slug": "lan-with-server",
        "description": "Two workstations and a department Web/File Server on a shared local Ethernet subnet.",
        "difficulty": "BEGINNER",
        "is_prebuilt": True,
        "nodes": [
            {
                "id": "pc-1",
                "name": "PC1",
                "type": "PC",
                "position_x": 100,
                "position_y": 120,
                "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
            },
            {
                "id": "pc-2",
                "name": "PC2",
                "type": "PC",
                "position_x": 100,
                "position_y": 260,
                "interfaces": [{"id": "if-pc2-eth0", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": "192.168.1.20", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
            },
            {
                "id": "sw-1",
                "name": "Switch1",
                "type": "SWITCH",
                "position_x": 320,
                "position_y": 190,
                "interfaces": [
                    {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                    {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                    {"id": "if-sw1-p3", "name": "Port 3", "mac_address": "02:00:04:01:03:01"},
                ],
            },
            {
                "id": "srv-1",
                "name": "FileServer",
                "type": "SERVER",
                "position_x": 540,
                "position_y": 190,
                "interfaces": [{"id": "if-srv-eth0", "name": "eth0", "mac_address": "02:00:03:01:00:01", "ipv4_address": "192.168.1.100", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
                "configuration": {"services": ["HTTP", "FILE"]},
            },
        ],
        "links": [
            {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
            {"id": "link-2", "source_node_id": "pc-2", "source_interface_id": "if-pc2-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p2"},
            {"id": "link-3", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p3", "target_node_id": "srv-1", "target_interface_id": "if-srv-eth0"},
        ],
    },
    {
        "name": "Two Routed Subnets with Default Gateways",
        "slug": "two-subnets-routed",
        "description": "Connecting Subnet A (192.168.1.0/24) to Subnet B (192.168.2.0/24) via a multi-interface Layer 3 router.",
        "difficulty": "INTERMEDIATE",
        "is_prebuilt": True,
        "nodes": [
            {
                "id": "pc-1",
                "name": "PC1",
                "type": "PC",
                "position_x": 80,
                "position_y": 180,
                "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
            },
            {
                "id": "sw-1",
                "name": "Switch1",
                "type": "SWITCH",
                "position_x": 220,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                    {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                ],
            },
            {
                "id": "rtr-1",
                "name": "Router1",
                "type": "ROUTER",
                "position_x": 400,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-rtr1-eth0", "name": "eth0", "mac_address": "02:00:05:01:00:01", "ipv4_address": "192.168.1.1", "subnet_mask": "255.255.255.0"},
                    {"id": "if-rtr1-eth1", "name": "eth1", "mac_address": "02:00:05:01:01:01", "ipv4_address": "192.168.2.1", "subnet_mask": "255.255.255.0"},
                ],
                "configuration": {
                    "routing_table": [
                        {"destination": "192.168.1.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth0", "metric": 0},
                        {"destination": "192.168.2.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth1", "metric": 0},
                    ]
                },
            },
            {
                "id": "sw-2",
                "name": "Switch2",
                "type": "SWITCH",
                "position_x": 580,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-sw2-p1", "name": "Port 1", "mac_address": "02:00:04:02:01:01"},
                    {"id": "if-sw2-p2", "name": "Port 2", "mac_address": "02:00:04:02:02:01"},
                ],
            },
            {
                "id": "pc-2",
                "name": "PC2",
                "type": "PC",
                "position_x": 720,
                "position_y": 180,
                "interfaces": [{"id": "if-pc2-eth0", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": "192.168.2.20", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.2.1"}],
            },
        ],
        "links": [
            {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
            {"id": "link-2", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p2", "target_node_id": "rtr-1", "target_interface_id": "if-rtr1-eth0"},
            {"id": "link-3", "source_node_id": "rtr-1", "source_interface_id": "if-rtr1-eth1", "target_node_id": "sw-2", "target_interface_id": "if-sw2-p1"},
            {"id": "link-4", "source_node_id": "sw-2", "source_interface_id": "if-sw2-p2", "target_node_id": "pc-2", "target_interface_id": "if-pc2-eth0"},
        ],
    },
    {
        "name": "Multi-Router WAN Backbone",
        "slug": "multi-router-wan",
        "description": "Two enterprise routers connected across a serial point-to-point link (10.0.0.0/30) with static routing.",
        "difficulty": "ADVANCED",
        "is_prebuilt": True,
        "nodes": [
            {
                "id": "pc-a",
                "name": "HQ-Client",
                "type": "PC",
                "position_x": 100,
                "position_y": 180,
                "interfaces": [{"id": "if-pca-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "172.16.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "172.16.1.1"}],
            },
            {
                "id": "rtr-a",
                "name": "Router-HQ",
                "type": "ROUTER",
                "position_x": 280,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-rtra-eth0", "name": "eth0", "mac_address": "02:00:05:01:00:01", "ipv4_address": "172.16.1.1", "subnet_mask": "255.255.255.0"},
                    {"id": "if-rtra-eth1", "name": "eth1", "mac_address": "02:00:05:01:01:01", "ipv4_address": "10.0.0.1", "subnet_mask": "255.255.255.252"},
                ],
                "configuration": {
                    "routing_table": [
                        {"destination": "172.16.1.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth0", "metric": 0},
                        {"destination": "10.0.0.0", "netmask": "255.255.255.252", "next_hop": "DIRECT", "interface": "eth1", "metric": 0},
                        {"destination": "172.16.2.0", "netmask": "255.255.255.0", "next_hop": "10.0.0.2", "interface": "eth1", "metric": 1},
                    ]
                },
            },
            {
                "id": "rtr-b",
                "name": "Router-Branch",
                "type": "ROUTER",
                "position_x": 500,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-rtrb-eth0", "name": "eth0", "mac_address": "02:00:05:02:00:01", "ipv4_address": "10.0.0.2", "subnet_mask": "255.255.255.252"},
                    {"id": "if-rtrb-eth1", "name": "eth1", "mac_address": "02:00:05:02:01:01", "ipv4_address": "172.16.2.1", "subnet_mask": "255.255.255.0"},
                ],
                "configuration": {
                    "routing_table": [
                        {"destination": "10.0.0.0", "netmask": "255.255.255.252", "next_hop": "DIRECT", "interface": "eth0", "metric": 0},
                        {"destination": "172.16.2.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth1", "metric": 0},
                        {"destination": "172.16.1.0", "netmask": "255.255.255.0", "next_hop": "10.0.0.1", "interface": "eth0", "metric": 1},
                    ]
                },
            },
            {
                "id": "srv-b",
                "name": "Branch-Server",
                "type": "SERVER",
                "position_x": 680,
                "position_y": 180,
                "interfaces": [{"id": "if-srvb-eth0", "name": "eth0", "mac_address": "02:00:03:02:00:01", "ipv4_address": "172.16.2.100", "subnet_mask": "255.255.255.0", "default_gateway": "172.16.2.1"}],
            },
        ],
        "links": [
            {"id": "link-1", "source_node_id": "pc-a", "source_interface_id": "if-pca-eth0", "target_node_id": "rtr-a", "target_interface_id": "if-rtra-eth0"},
            {"id": "link-2", "source_node_id": "rtr-a", "source_interface_id": "if-rtra-eth1", "target_node_id": "rtr-b", "target_interface_id": "if-rtrb-eth0"},
            {"id": "link-3", "source_node_id": "rtr-b", "source_interface_id": "if-rtrb-eth1", "target_node_id": "srv-b", "target_interface_id": "if-srvb-eth0"},
        ],
    },
    {
        "name": "Infrastructure Services: DNS & DHCP",
        "slug": "dns-dhcp-services",
        "description": "Host resolving internal domain names and leasing addresses from an infrastructure server.",
        "difficulty": "INTERMEDIATE",
        "is_prebuilt": True,
        "nodes": [
            {
                "id": "pc-1",
                "name": "Workstation1",
                "type": "PC",
                "position_x": 120,
                "position_y": 180,
                "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.10.15", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.10.1"}],
            },
            {
                "id": "sw-1",
                "name": "Switch1",
                "type": "SWITCH",
                "position_x": 340,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                    {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                ],
            },
            {
                "id": "dns-srv",
                "name": "DNS-DHCP-Server",
                "type": "DNS_SERVER",
                "position_x": 560,
                "position_y": 180,
                "interfaces": [{"id": "if-dnssrv-eth0", "name": "eth0", "mac_address": "02:00:08:01:00:01", "ipv4_address": "192.168.10.53", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.10.1"}],
                "configuration": {
                    "services": ["DNS", "DHCP"],
                    "dns_records": {
                        "www.example.local": "192.168.10.20",
                        "intranet.local": "192.168.10.100",
                        "mail.local": "192.168.10.25",
                    },
                    "dhcp_pool": {
                        "network": "192.168.10.0/24",
                        "start": "192.168.10.100",
                        "end": "192.168.10.200",
                        "gateway": "192.168.10.1",
                        "dns": "192.168.10.53",
                    },
                },
            },
        ],
        "links": [
            {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
            {"id": "link-2", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p2", "target_node_id": "dns-srv", "target_interface_id": "if-dnssrv-eth0"},
        ],
    },
    {
        "name": "Perimeter Security: Stateless Firewall & WAN",
        "slug": "firewall-perimeter",
        "description": "Internal LAN protected by a perimeter firewall controlling outbound access to an external WAN server.",
        "difficulty": "ADVANCED",
        "is_prebuilt": True,
        "nodes": [
            {
                "id": "pc-1",
                "name": "Internal-PC",
                "type": "PC",
                "position_x": 100,
                "position_y": 180,
                "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
            },
            {
                "id": "fw-1",
                "name": "Firewall1",
                "type": "FIREWALL",
                "position_x": 300,
                "position_y": 180,
                "interfaces": [
                    {"id": "if-fw1-eth0", "name": "eth0", "mac_address": "02:00:06:01:00:01", "ipv4_address": "192.168.1.1", "subnet_mask": "255.255.255.0"},
                    {"id": "if-fw1-eth1", "name": "eth1", "mac_address": "02:00:06:01:01:01", "ipv4_address": "203.0.113.1", "subnet_mask": "255.255.255.0"},
                ],
                "configuration": {
                    "firewall_rules": [
                        {"id": "FW-1", "action": "ALLOW", "protocol": "ICMP", "source_ip": "ANY", "destination_ip": "ANY", "port": "ANY", "description": "Permit ICMP echo"},
                        {"id": "FW-2", "action": "ALLOW", "protocol": "TCP", "source_ip": "ANY", "destination_ip": "ANY", "port": 443, "description": "Permit HTTPS"},
                        {"id": "FW-3", "action": "DENY", "protocol": "TCP", "source_ip": "ANY", "destination_ip": "ANY", "port": 23, "description": "Block insecure Telnet"},
                    ],
                    "routing_table": [
                        {"destination": "192.168.1.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth0"},
                        {"destination": "203.0.113.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth1"},
                    ],
                },
            },
            {
                "id": "ext-srv",
                "name": "External-Server",
                "type": "SERVER",
                "position_x": 520,
                "position_y": 180,
                "interfaces": [{"id": "if-ext-eth0", "name": "eth0", "mac_address": "02:00:03:01:00:01", "ipv4_address": "203.0.113.100", "subnet_mask": "255.255.255.0", "default_gateway": "203.0.113.1"}],
            },
        ],
        "links": [
            {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "fw-1", "target_interface_id": "if-fw1-eth0"},
            {"id": "link-2", "source_node_id": "fw-1", "source_interface_id": "if-fw1-eth1", "target_node_id": "ext-srv", "target_interface_id": "if-ext-eth0"},
        ],
    },
]


# ---------------------------------------------------------------------------
# Guided Scenarios & Challenges
# ---------------------------------------------------------------------------

GUIDED_SCENARIOS: list[dict[str, Any]] = [
    # Beginner 1
    {
        "slug": "connect-two-pcs",
        "title": "Scenario 1: Connect Two Workstations on a Local LAN",
        "difficulty": "BEGINNER",
        "category": "FUNDAMENTALS",
        "description": "Establish a local Layer 2 connection between PC1 and PC2 using an unmanaged switch. Configure both workstations with valid IPv4 addresses in the 192.168.1.0/24 subnet and test end-to-end ping reachability.",
        "learning_objectives": [
            "Understand how end devices connect to a central Layer 2 switch",
            "Assign valid static IPv4 addresses within the same subnet",
            "Observe dynamic ARP resolution and ICMP Echo transmission",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "PC1",
                    "type": "PC",
                    "position_x": 140,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0"}],
                },
                {
                    "id": "sw-1",
                    "name": "Switch1",
                    "type": "SWITCH",
                    "position_x": 340,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                        {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                    ],
                },
                {
                    "id": "pc-2",
                    "name": "PC2",
                    "type": "PC",
                    "position_x": 540,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pc2-eth0", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": None, "subnet_mask": "255.255.255.0"}],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Connect PC2 to Switch1", "description": "Cable PC2's eth0 to Switch1's Port 2."},
            {"id": "t2", "title": "Configure PC2's IP", "description": "Set PC2's IPv4 address to 192.168.1.20 with netmask 255.255.255.0."},
            {"id": "t3", "title": "Test Ping Reachability", "description": "Send an ICMP Ping from PC1 to PC2 (192.168.1.20)."},
        ],
        "validation_rules": [
            {"rule_type": "DEVICE_CONNECTED", "target_device": "PC2", "expected_value": "Switch1", "description": "PC2 must be cabled to Switch1"},
            {"rule_type": "IP_MATCH", "target_device": "PC2", "expected_value": "192.168.1.20", "description": "PC2 must have IP 192.168.1.20"},
            {"rule_type": "PING_SUCCESS", "target_device": "PC1", "expected_value": "PC2", "description": "Ping from PC1 to PC2 must succeed"},
        ],
        "hints": [
            "Select the Cable tool or click on PC2's port indicator to connect it to Switch1.",
            "Click on PC2 to open the Properties Panel, then enter 192.168.1.20 in the IPv4 field.",
            "Use the Simulation Controls bar at the bottom: select Source: PC1, Destination: PC2, Protocol: ICMP, and click 'Send Packet'.",
        ],
        "solution_explanation": "In a local Ethernet LAN, workstations connect to switch ports. Because both devices reside within 192.168.1.0/24, PC1 resolves PC2's MAC address directly via ARP broadcast without needing a router or default gateway.",
    },

    # Intermediate 1: Troubleshooting
    {
        "slug": "troubleshoot-broken-network",
        "title": "Scenario 2: Troubleshoot Gateway Misconfiguration",
        "difficulty": "INTERMEDIATE",
        "category": "TROUBLESHOOTING",
        "description": "PC1 is unable to communicate with Server1 on a remote subnet. Investigate device configurations, identify the misconfigured parameter, fix the problem, and verify connectivity.",
        "learning_objectives": [
            "Diagnose why an end host fails to communicate across subnets",
            "Inspect default gateway settings against router interface IP addresses",
            "Verify that routing tables and ARP resolution operate across intermediate hops",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "PC1",
                    "type": "PC",
                    "position_x": 100,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.254"}],  # BROKEN: .254 instead of .1
                },
                {
                    "id": "rtr-1",
                    "name": "Router1",
                    "type": "ROUTER",
                    "position_x": 340,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-rtr1-eth0", "name": "eth0", "mac_address": "02:00:05:01:00:01", "ipv4_address": "192.168.1.1", "subnet_mask": "255.255.255.0"},
                        {"id": "if-rtr1-eth1", "name": "eth1", "mac_address": "02:00:05:01:01:01", "ipv4_address": "192.168.2.1", "subnet_mask": "255.255.255.0"},
                    ],
                    "configuration": {
                        "routing_table": [
                            {"destination": "192.168.1.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth0"},
                            {"destination": "192.168.2.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth1"},
                        ]
                    },
                },
                {
                    "id": "srv-1",
                    "name": "Server1",
                    "type": "SERVER",
                    "position_x": 580,
                    "position_y": 180,
                    "interfaces": [{"id": "if-srv-eth0", "name": "eth0", "mac_address": "02:00:03:01:00:01", "ipv4_address": "192.168.2.10", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.2.1"}],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "rtr-1", "target_interface_id": "if-rtr1-eth0"},
                {"id": "link-2", "source_node_id": "rtr-1", "source_interface_id": "if-rtr1-eth1", "target_node_id": "srv-1", "target_interface_id": "if-srv-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Inspect PC1's Configuration", "description": "Review PC1's default gateway address and compare it to Router1's eth0 IP."},
            {"id": "t2", "title": "Correct the Gateway", "description": "Update PC1's default gateway to point to Router1's local interface (192.168.1.1)."},
            {"id": "t3", "title": "Verify Communication", "description": "Transmit a ping from PC1 to Server1 (192.168.2.10)."},
        ],
        "validation_rules": [
            {"rule_type": "GATEWAY_MATCH", "target_device": "PC1", "expected_value": "192.168.1.1", "description": "PC1 default gateway must be 192.168.1.1"},
            {"rule_type": "PING_SUCCESS", "target_device": "PC1", "expected_value": "Server1", "description": "Ping from PC1 to Server1 must succeed"},
        ],
        "hints": [
            "Check Router1's eth0 IP address in its properties panel.",
            "PC1 is currently trying to send packets to gateway 192.168.1.254, which does not exist.",
            "Change PC1's Default Gateway to 192.168.1.1 and send the ping again.",
        ],
        "solution_explanation": "When an end device wants to send traffic to an IP address outside its local subnet (192.168.1.10 -> 192.168.2.10), it sends an ARP request for its configured default gateway. Because 192.168.1.254 was unassigned, ARP timed out and packets were dropped. Correcting the gateway to 192.168.1.1 enabled PC1 to reach Router1, which then routed the packet to Server1.",
    },

    # Intermediate 2: VLANs
    {
        "slug": "configure-vlans",
        "title": "Scenario 3: Segment Traffic using Virtual LANs (VLANs)",
        "difficulty": "INTERMEDIATE",
        "category": "SWITCHING",
        "description": "Configure switch port VLAN assignments to isolate Engineering (VLAN 10) from Human Resources (VLAN 20). Verify that devices in the same VLAN communicate while cross-VLAN traffic is blocked.",
        "learning_objectives": [
            "Understand Layer 2 segmentation using 802.1Q VLAN IDs",
            "Assign switch access ports to specific VLANs",
            "Observe how VLAN isolation prevents unauthorized broadcast and unicast leakage",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-eng",
                    "name": "Eng-PC",
                    "type": "PC",
                    "position_x": 120,
                    "position_y": 120,
                    "interfaces": [{"id": "if-pceng-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.10.10", "subnet_mask": "255.255.255.0", "vlan_id": 10}],
                },
                {
                    "id": "pc-hr",
                    "name": "HR-PC",
                    "type": "PC",
                    "position_x": 120,
                    "position_y": 260,
                    "interfaces": [{"id": "if-pchr-eth0", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": "192.168.20.10", "subnet_mask": "255.255.255.0", "vlan_id": 20}],
                },
                {
                    "id": "sw-1",
                    "name": "Switch1",
                    "type": "SWITCH",
                    "position_x": 340,
                    "position_y": 190,
                    "interfaces": [
                        {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01", "vlan_id": 10},
                        {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01", "vlan_id": 20},
                    ],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-eng", "source_interface_id": "if-pceng-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
                {"id": "link-2", "source_node_id": "pc-hr", "source_interface_id": "if-pchr-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p2"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Verify Port 1 VLAN", "description": "Ensure Switch1 Port 1 is assigned to VLAN 10 (Engineering)."},
            {"id": "t2", "title": "Verify Port 2 VLAN", "description": "Ensure Switch1 Port 2 is assigned to VLAN 20 (HR)."},
            {"id": "t3", "title": "Observe Isolation", "description": "Send a packet from Eng-PC to HR-PC and confirm the switch drops the frame due to VLAN boundary isolation."},
        ],
        "validation_rules": [
            {"rule_type": "VLAN_MATCH", "target_device": "Switch1", "target_interface": "Port 1", "expected_value": 10, "description": "Port 1 must be in VLAN 10"},
            {"rule_type": "VLAN_MATCH", "target_device": "Switch1", "target_interface": "Port 2", "expected_value": 20, "description": "Port 2 must be in VLAN 20"},
        ],
        "hints": [
            "Click on Switch1 to inspect port VLAN configuration.",
            "Switches do not bridge traffic between different VLANs without a Layer 3 router.",
        ],
        "solution_explanation": "VLANs divide a single physical switch into isolated logical switches. When Eng-PC transmits a frame into Port 1 (VLAN 10), the switch refuses to flood or forward it out Port 2 (VLAN 20), preserving confidentiality between departments.",
    },

    # Advanced 1: Firewall ACL Defense
    {
        "slug": "firewall-rule-defense",
        "title": "Scenario 4: Implement Defensive Firewall Policies",
        "difficulty": "ADVANCED",
        "category": "SECURITY",
        "description": "Configure access control lists on Perimeter-Firewall to permit secure web browsing (HTTPS port 443) and diagnostics (ICMP), while explicitly dropping insecure cleartext administration protocols (Telnet port 23).",
        "learning_objectives": [
            "Author stateless packet filtering rules based on protocol and port",
            "Implement defense-in-depth perimeter policy",
            "Verify that authorized applications pass while unauthorized services are dropped",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "LAN-Host",
                    "type": "PC",
                    "position_x": 120,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.50", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
                },
                {
                    "id": "fw-1",
                    "name": "Perimeter-Firewall",
                    "type": "FIREWALL",
                    "position_x": 340,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-fw1-eth0", "name": "eth0", "mac_address": "02:00:06:01:00:01", "ipv4_address": "192.168.1.1", "subnet_mask": "255.255.255.0"},
                        {"id": "if-fw1-eth1", "name": "eth1", "mac_address": "02:00:06:01:01:01", "ipv4_address": "203.0.113.1", "subnet_mask": "255.255.255.0"},
                    ],
                    "configuration": {
                        "firewall_rules": [
                            {"id": "R1", "action": "ALLOW", "protocol": "ICMP", "source_ip": "ANY", "destination_ip": "ANY", "port": "ANY", "description": "Permit Ping"},
                            {"id": "R2", "action": "DENY", "protocol": "TCP", "source_ip": "ANY", "destination_ip": "ANY", "port": 23, "description": "Block Telnet"},
                        ],
                        "routing_table": [
                            {"destination": "192.168.1.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth0"},
                            {"destination": "203.0.113.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth1"},
                        ],
                    },
                },
                {
                    "id": "srv-1",
                    "name": "Cloud-Server",
                    "type": "SERVER",
                    "position_x": 560,
                    "position_y": 180,
                    "interfaces": [{"id": "if-srv-eth0", "name": "eth0", "mac_address": "02:00:03:01:00:01", "ipv4_address": "203.0.113.50", "subnet_mask": "255.255.255.0", "default_gateway": "203.0.113.1"}],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "fw-1", "target_interface_id": "if-fw1-eth0"},
                {"id": "link-2", "source_node_id": "fw-1", "source_interface_id": "if-fw1-eth1", "target_node_id": "srv-1", "target_interface_id": "if-srv-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Inspect Firewall Policy", "description": "Verify rule R1 allows ICMP and R2 denies TCP port 23."},
            {"id": "t2", "title": "Verify Diagnostic Ping", "description": "Test ping from LAN-Host to Cloud-Server (203.0.113.50) to confirm rule R1 permits traffic."},
            {"id": "t3", "title": "Add HTTPS Allow Rule", "description": "Ensure rule ALLOW TCP on port 443 exists."},
        ],
        "validation_rules": [
            {"rule_type": "FIREWALL_RULE", "target_device": "Perimeter-Firewall", "action": "ALLOW", "protocol": "ICMP", "description": "Firewall must permit ICMP traffic"},
            {"rule_type": "FIREWALL_RULE", "target_device": "Perimeter-Firewall", "action": "DENY", "protocol": "TCP", "description": "Firewall must block Telnet (TCP)"},
            {"rule_type": "PING_SUCCESS", "target_device": "LAN-Host", "expected_value": "Cloud-Server", "description": "Ping to Cloud-Server must succeed"},
        ],
        "hints": [
            "Click on Perimeter-Firewall and inspect the Firewall Rules tab.",
            "Run ping from LAN-Host to Cloud-Server using the simulation controls.",
        ],
        "solution_explanation": "Network firewalls inspect packet headers against an ordered rule list. Legitimate ICMP traffic matches the first allow rule and is forwarded. Unauthorized cleartext Telnet traffic matches the second rule and is immediately discarded at the perimeter, shielding the internal network.",
    },

    # Beginner 2: Build a LAN
    {
        "slug": "build-a-lan",
        "title": "Scenario 5: Build a Departmental Local Area Network",
        "difficulty": "BEGINNER",
        "category": "FUNDAMENTALS",
        "description": "Construct a full LAN topology connecting three workstations and a departmental File Server through a central switch in the 192.168.1.0/24 subnet.",
        "learning_objectives": [
            "Scale a star topology using a central switch",
            "Assign sequential unique IPv4 host addresses",
            "Verify all workstations can communicate with the server",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "PC1",
                    "type": "PC",
                    "position_x": 100,
                    "position_y": 100,
                    "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0"}],
                },
                {
                    "id": "pc-2",
                    "name": "PC2",
                    "type": "PC",
                    "position_x": 100,
                    "position_y": 200,
                    "interfaces": [{"id": "if-pc2-eth0", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": "192.168.1.20", "subnet_mask": "255.255.255.0"}],
                },
                {
                    "id": "sw-1",
                    "name": "Switch1",
                    "type": "SWITCH",
                    "position_x": 300,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                        {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                        {"id": "if-sw1-p3", "name": "Port 3", "mac_address": "02:00:04:01:03:01"},
                    ],
                },
                {
                    "id": "srv-1",
                    "name": "FileServer",
                    "type": "SERVER",
                    "position_x": 500,
                    "position_y": 180,
                    "interfaces": [{"id": "if-srv-eth0", "name": "eth0", "mac_address": "02:00:03:01:00:01", "ipv4_address": "192.168.1.100", "subnet_mask": "255.255.255.0"}],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
                {"id": "link-2", "source_node_id": "pc-2", "source_interface_id": "if-pc2-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p2"},
                {"id": "link-3", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p3", "target_node_id": "srv-1", "target_interface_id": "if-srv-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Verify FileServer Connectivity", "description": "Ping FileServer (192.168.1.100) from PC1."},
            {"id": "t2", "title": "Verify PC2 Connectivity", "description": "Ping FileServer (192.168.1.100) from PC2."},
        ],
        "validation_rules": [
            {"rule_type": "PING_SUCCESS", "target_device": "PC1", "expected_value": "FileServer", "description": "PC1 must ping FileServer"},
            {"rule_type": "PING_SUCCESS", "target_device": "PC2", "expected_value": "FileServer", "description": "PC2 must ping FileServer"},
        ],
        "hints": ["Verify that PC1, PC2, and FileServer share subnet 192.168.1.0/24."],
        "solution_explanation": "Ethernet star topologies centralize traffic switching. All devices within the /24 prefix communicate through direct Layer 2 frame switching.",
    },

    # Beginner 3: Default Gateway
    {
        "slug": "configure-default-gateway",
        "title": "Scenario 6: Configure Default Gateway for Remote Access",
        "difficulty": "BEGINNER",
        "category": "ROUTING",
        "description": "Configure the default gateway on Workstation PC1 so it can forward packets intended for external networks to Router1.",
        "learning_objectives": [
            "Understand why end hosts require a default gateway to exit their local subnet",
            "Set the default gateway parameter on an interface",
            "Verify reachability of the router gateway interface",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "PC1",
                    "type": "PC",
                    "position_x": 140,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0", "default_gateway": None}],
                },
                {
                    "id": "rtr-1",
                    "name": "Router1",
                    "type": "ROUTER",
                    "position_x": 380,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-rtr-eth0", "name": "eth0", "mac_address": "02:00:05:01:00:01", "ipv4_address": "192.168.1.1", "subnet_mask": "255.255.255.0"},
                        {"id": "if-rtr-eth1", "name": "eth1", "mac_address": "02:00:05:01:01:01", "ipv4_address": "10.0.0.1", "subnet_mask": "255.255.255.0"},
                    ],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "rtr-1", "target_interface_id": "if-rtr-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Configure Default Gateway", "description": "Set PC1's default gateway to 192.168.1.1."},
            {"id": "t2", "title": "Ping Gateway", "description": "Send an ICMP ping from PC1 to 192.168.1.1."},
        ],
        "validation_rules": [
            {"rule_type": "GATEWAY_MATCH", "target_device": "PC1", "expected_value": "192.168.1.1", "description": "PC1 default gateway must be 192.168.1.1"},
            {"rule_type": "PING_SUCCESS", "target_device": "PC1", "expected_value": "Router1", "description": "Ping to Router1 must succeed"},
        ],
        "hints": ["Router1's interface facing PC1 is eth0 with IP 192.168.1.1."],
        "solution_explanation": "The default gateway serves as the exit door for any packet whose destination address lies outside the local IP subnet.",
    },

    # Intermediate 3: Connect Two Subnets
    {
        "slug": "connect-two-subnets",
        "title": "Scenario 7: Inter-VLAN / Inter-Subnet Routing",
        "difficulty": "INTERMEDIATE",
        "category": "ROUTING",
        "description": "Establish routing between Subnet A (192.168.1.0/24) and Subnet B (192.168.2.0/24) through Router1. Verify that PCs in different subnets communicate through the router.",
        "learning_objectives": [
            "Configure distinct IP subnets on adjacent router interfaces",
            "Understand how routers decrement TTL and re-encapsulate frames",
            "Verify end-to-end ping across routed hops",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "PC-SubnetA",
                    "type": "PC",
                    "position_x": 100,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pca-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.50", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
                },
                {
                    "id": "rtr-1",
                    "name": "Router1",
                    "type": "ROUTER",
                    "position_x": 340,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-rtr1-eth0", "name": "eth0", "mac_address": "02:00:05:01:00:01", "ipv4_address": "192.168.1.1", "subnet_mask": "255.255.255.0"},
                        {"id": "if-rtr1-eth1", "name": "eth1", "mac_address": "02:00:05:01:01:01", "ipv4_address": "192.168.2.1", "subnet_mask": "255.255.255.0"},
                    ],
                },
                {
                    "id": "pc-2",
                    "name": "PC-SubnetB",
                    "type": "PC",
                    "position_x": 580,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pcb-eth0", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": "192.168.2.50", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.2.1"}],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pca-eth0", "target_node_id": "rtr-1", "target_interface_id": "if-rtr1-eth0"},
                {"id": "link-2", "source_node_id": "rtr-1", "source_interface_id": "if-rtr1-eth1", "target_node_id": "pc-2", "target_interface_id": "if-pcb-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Verify Subnet A Gateway", "description": "Ensure PC-SubnetA gateway points to 192.168.1.1."},
            {"id": "t2", "title": "Verify Subnet B Gateway", "description": "Ensure PC-SubnetB gateway points to 192.168.2.1."},
            {"id": "t3", "title": "Ping Across Subnets", "description": "Transmit ping from PC-SubnetA to PC-SubnetB (192.168.2.50)."},
        ],
        "validation_rules": [
            {"rule_type": "GATEWAY_MATCH", "target_device": "PC-SubnetA", "expected_value": "192.168.1.1", "description": "PC-SubnetA gateway must be 192.168.1.1"},
            {"rule_type": "GATEWAY_MATCH", "target_device": "PC-SubnetB", "expected_value": "192.168.2.1", "description": "PC-SubnetB gateway must be 192.168.2.1"},
            {"rule_type": "PING_SUCCESS", "target_device": "PC-SubnetA", "expected_value": "PC-SubnetB", "description": "Ping across subnets must succeed"},
        ],
        "hints": ["Both PCs must have valid gateways configured on their respective subnets."],
        "solution_explanation": "Routers operate at Layer 3 to bridge independent IP networks. When PC-SubnetA sends a packet to 192.168.2.50, Router1 inspects its routing table and forwards the packet out eth1 with its own source MAC address.",
    },

    # Intermediate 4: DNS Resolution
    {
        "slug": "dns-resolution-flow",
        "title": "Scenario 8: Simulate Internal DNS Resolution",
        "difficulty": "INTERMEDIATE",
        "category": "SERVICES",
        "description": "Configure client workstation to query an internal DNS server (192.168.10.53) for the hostname 'www.example.local' and inspect the resulting DNS Query and Response exchange.",
        "learning_objectives": [
            "Understand UDP port 53 DNS message exchanges",
            "Observe A record resolution from query to response",
            "Understand DNS caching and server configurations",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "Client-PC",
                    "type": "PC",
                    "position_x": 120,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pc1-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.10.15", "subnet_mask": "255.255.255.0"}],
                },
                {
                    "id": "sw-1",
                    "name": "Switch1",
                    "type": "SWITCH",
                    "position_x": 340,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                        {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                    ],
                },
                {
                    "id": "dns-1",
                    "name": "DNS-Server",
                    "type": "DNS_SERVER",
                    "position_x": 560,
                    "position_y": 180,
                    "interfaces": [{"id": "if-dns-eth0", "name": "eth0", "mac_address": "02:00:08:01:00:01", "ipv4_address": "192.168.10.53", "subnet_mask": "255.255.255.0"}],
                    "configuration": {
                        "services": ["DNS"],
                        "dns_records": {"www.example.local": "192.168.10.20"},
                    },
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-pc1-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
                {"id": "link-2", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p2", "target_node_id": "dns-1", "target_interface_id": "if-dns-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Initiate DNS Query", "description": "Select Protocol: DNS, Query: 'www.example.local', and send from Client-PC to DNS-Server."},
            {"id": "t2", "title": "Inspect DNS Response", "description": "Confirm the server returns IPv4 address 192.168.10.20."},
        ],
        "validation_rules": [
            {"rule_type": "DEVICE_CONNECTED", "target_device": "Client-PC", "expected_value": "Switch1", "description": "Client must be connected to switch"},
            {"rule_type": "DEVICE_CONNECTED", "target_device": "DNS-Server", "expected_value": "Switch1", "description": "DNS server must be connected to switch"},
        ],
        "hints": ["Select DNS in the simulation bar at the bottom and click Send Packet."],
        "solution_explanation": "DNS queries use UDP port 53. The client queries the server for the A record of www.example.local, and the server returns the mapped IPv4 address 192.168.10.20.",
    },

    # Intermediate 5: DHCP
    {
        "slug": "dhcp-auto-configuration",
        "title": "Scenario 9: Dynamic Host Configuration Protocol (DHCP DORA)",
        "difficulty": "INTERMEDIATE",
        "category": "SERVICES",
        "description": "Observe how an unconfigured workstation acquires an IP address, subnet mask, default gateway, and DNS server address through the 4-step DORA exchange (Discover, Offer, Request, ACK).",
        "learning_objectives": [
            "Trace the 4 stages of DHCP lease acquisition",
            "Understand Layer 2 and Layer 3 broadcasts during initial boot",
            "Verify automatic IP assignment to client interfaces",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-1",
                    "name": "New-Laptop",
                    "type": "LAPTOP",
                    "position_x": 120,
                    "position_y": 180,
                    "interfaces": [{"id": "if-lap-eth0", "name": "eth0", "mac_address": "02:00:02:01:00:01", "ipv4_address": None, "subnet_mask": None}],
                },
                {
                    "id": "sw-1",
                    "name": "Switch1",
                    "type": "SWITCH",
                    "position_x": 340,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-sw1-p1", "name": "Port 1", "mac_address": "02:00:04:01:01:01"},
                        {"id": "if-sw1-p2", "name": "Port 2", "mac_address": "02:00:04:01:02:01"},
                    ],
                },
                {
                    "id": "dhcp-1",
                    "name": "DHCP-Server",
                    "type": "DHCP_SERVER",
                    "position_x": 560,
                    "position_y": 180,
                    "interfaces": [{"id": "if-dhcp-eth0", "name": "eth0", "mac_address": "02:00:09:01:00:01", "ipv4_address": "192.168.1.254", "subnet_mask": "255.255.255.0"}],
                    "configuration": {
                        "services": ["DHCP"],
                        "dhcp_pool": {"network": "192.168.1.0/24", "start": "192.168.1.150", "gateway": "192.168.1.1", "dns": "192.168.1.1"},
                    },
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-1", "source_interface_id": "if-lap-eth0", "target_node_id": "sw-1", "target_interface_id": "if-sw1-p1"},
                {"id": "link-2", "source_node_id": "sw-1", "source_interface_id": "if-sw1-p2", "target_node_id": "dhcp-1", "target_interface_id": "if-dhcp-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Run DHCP Simulation", "description": "Select Protocol: DHCP and click 'Send Packet' to trigger Discover/Offer/Request/ACK."},
            {"id": "t2", "title": "Verify Leased IP", "description": "Confirm New-Laptop receives IP 192.168.1.150."},
        ],
        "validation_rules": [
            {"rule_type": "DEVICE_CONNECTED", "target_device": "New-Laptop", "expected_value": "Switch1", "description": "Laptop must be connected to switch"},
        ],
        "hints": ["Select Protocol: DHCP in the simulation bar and click Send Packet."],
        "solution_explanation": "DHCP eliminates manual IP addressing by dynamically leasing configuration parameters via UDP broadcast ports 67 (server) and 68 (client).",
    },

    # Advanced 2: Multi-Router Static Routing
    {
        "slug": "multi-router-routing",
        "title": "Scenario 10: Multi-Router Static Route Construction",
        "difficulty": "ADVANCED",
        "category": "ROUTING",
        "description": "Configure static routes across two autonomous routers (Router-HQ and Router-Branch) to bridge remote networks 172.16.1.0/24 and 172.16.2.0/24 across point-to-point link 10.0.0.0/30.",
        "learning_objectives": [
            "Configure next-hop static routes for non-adjacent subnets",
            "Understand point-to-point transit link addressing (/30)",
            "Verify bi-directional communication across multiple router hops",
        ],
        "initial_topology": {
            "nodes": [
                {
                    "id": "pc-hq",
                    "name": "HQ-PC",
                    "type": "PC",
                    "position_x": 80,
                    "position_y": 180,
                    "interfaces": [{"id": "if-pchq-eth0", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "172.16.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "172.16.1.1"}],
                },
                {
                    "id": "rtr-hq",
                    "name": "Router-HQ",
                    "type": "ROUTER",
                    "position_x": 260,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-rhq-eth0", "name": "eth0", "mac_address": "02:00:05:01:00:01", "ipv4_address": "172.16.1.1", "subnet_mask": "255.255.255.0"},
                        {"id": "if-rhq-eth1", "name": "eth1", "mac_address": "02:00:05:01:01:01", "ipv4_address": "10.0.0.1", "subnet_mask": "255.255.255.252"},
                    ],
                    "configuration": {
                        "routing_table": [
                            {"destination": "172.16.1.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth0"},
                            {"destination": "10.0.0.0", "netmask": "255.255.255.252", "next_hop": "DIRECT", "interface": "eth1"},
                            {"destination": "172.16.2.0", "netmask": "255.255.255.0", "next_hop": "10.0.0.2", "interface": "eth1"},
                        ]
                    },
                },
                {
                    "id": "rtr-br",
                    "name": "Router-Branch",
                    "type": "ROUTER",
                    "position_x": 480,
                    "position_y": 180,
                    "interfaces": [
                        {"id": "if-rbr-eth0", "name": "eth0", "mac_address": "02:00:05:02:00:01", "ipv4_address": "10.0.0.2", "subnet_mask": "255.255.255.252"},
                        {"id": "if-rbr-eth1", "name": "eth1", "mac_address": "02:00:05:02:01:01", "ipv4_address": "172.16.2.1", "subnet_mask": "255.255.255.0"},
                    ],
                    "configuration": {
                        "routing_table": [
                            {"destination": "10.0.0.0", "netmask": "255.255.255.252", "next_hop": "DIRECT", "interface": "eth0"},
                            {"destination": "172.16.2.0", "netmask": "255.255.255.0", "next_hop": "DIRECT", "interface": "eth1"},
                            {"destination": "172.16.1.0", "netmask": "255.255.255.0", "next_hop": "10.0.0.1", "interface": "eth0"},
                        ]
                    },
                },
                {
                    "id": "srv-br",
                    "name": "Branch-Server",
                    "type": "SERVER",
                    "position_x": 680,
                    "position_y": 180,
                    "interfaces": [{"id": "if-sbr-eth0", "name": "eth0", "mac_address": "02:00:03:02:00:01", "ipv4_address": "172.16.2.100", "subnet_mask": "255.255.255.0", "default_gateway": "172.16.2.1"}],
                },
            ],
            "links": [
                {"id": "link-1", "source_node_id": "pc-hq", "source_interface_id": "if-pchq-eth0", "target_node_id": "rtr-hq", "target_interface_id": "if-rhq-eth0"},
                {"id": "link-2", "source_node_id": "rtr-hq", "source_interface_id": "if-rhq-eth1", "target_node_id": "rtr-br", "target_interface_id": "if-rbr-eth0"},
                {"id": "link-3", "source_node_id": "rtr-br", "source_interface_id": "if-rbr-eth1", "target_node_id": "srv-br", "target_interface_id": "if-sbr-eth0"},
            ],
        },
        "tasks": [
            {"id": "t1", "title": "Verify Router-HQ Static Route", "description": "Ensure Router-HQ has route to 172.16.2.0/24 via 10.0.0.2."},
            {"id": "t2", "title": "Verify Router-Branch Static Route", "description": "Ensure Router-Branch has route to 172.16.1.0/24 via 10.0.0.1."},
            {"id": "t3", "title": "Ping Across WAN", "description": "Ping Branch-Server (172.16.2.100) from HQ-PC."},
        ],
        "validation_rules": [
            {"rule_type": "ROUTE_EXISTS", "target_device": "Router-HQ", "destination": "172.16.2.0", "description": "Router-HQ must route 172.16.2.0"},
            {"rule_type": "ROUTE_EXISTS", "target_device": "Router-Branch", "destination": "172.16.1.0", "description": "Router-Branch must route 172.16.1.0"},
            {"rule_type": "PING_SUCCESS", "target_device": "HQ-PC", "expected_value": "Branch-Server", "description": "Ping across WAN must succeed"},
        ],
        "hints": ["Static routes require specifying the destination network and the next-hop router's IP address."],
        "solution_explanation": "Without dynamic routing protocols (like OSPF or BGP), network administrators configure static routes so each intermediate router knows which physical interface and next-hop IP forwards traffic toward remote subnets.",
    },
]



class SimulatorCatalogService:
    """Manages prebuilt network topologies and scenarios."""

    def sync_catalog(self, db: Session) -> dict[str, int]:
        """Idempotently sync prebuilt topologies and scenarios into database."""
        topo_count = 0
        scenario_count = 0

        # 1. Sync Topologies
        for topo in PREBUILT_TOPOLOGIES:
            existing = (
                db.query(SimulatorTopology)
                .filter(SimulatorTopology.slug == topo["slug"])
                .first()
            )
            raw_data = {
                "nodes": topo.get("nodes", []),
                "links": topo.get("links", []),
            }
            json_str = json.dumps(raw_data)

            if existing:
                existing.name = topo["name"]
                existing.description = topo["description"]
                existing.difficulty = topo["difficulty"]
                existing.is_prebuilt = True
                existing.topology_data = json_str
            else:
                db.add(
                    SimulatorTopology(
                        name=topo["name"],
                        slug=topo["slug"],
                        description=topo["description"],
                        difficulty=topo["difficulty"],
                        is_prebuilt=True,
                        topology_data=json_str,
                    )
                )
            topo_count += 1

        # 2. Sync Scenarios
        for sc in GUIDED_SCENARIOS:
            existing = (
                db.query(SimulatorScenario)
                .filter(SimulatorScenario.slug == sc["slug"])
                .first()
            )
            obj_json = json.dumps(sc.get("learning_objectives", []))
            topo_json = json.dumps(sc.get("initial_topology", {}))
            tasks_json = json.dumps(sc.get("tasks", []))
            rules_json = json.dumps(sc.get("validation_rules", []))
            hints_json = json.dumps(sc.get("hints", []))

            if existing:
                existing.title = sc["title"]
                existing.difficulty = sc["difficulty"]
                existing.category = sc.get("category", "FUNDAMENTALS")
                existing.description = sc["description"]
                existing.learning_objectives = obj_json
                existing.initial_topology = topo_json
                existing.tasks = tasks_json
                existing.validation_rules = rules_json
                existing.hints = hints_json
                existing.solution_explanation = sc["solution_explanation"]
            else:
                db.add(
                    SimulatorScenario(
                        slug=sc["slug"],
                        title=sc["title"],
                        difficulty=sc["difficulty"],
                        category=sc.get("category", "FUNDAMENTALS"),
                        description=sc["description"],
                        learning_objectives=obj_json,
                        initial_topology=topo_json,
                        tasks=tasks_json,
                        validation_rules=rules_json,
                        hints=hints_json,
                        solution_explanation=sc["solution_explanation"],
                    )
                )
            scenario_count += 1

        db.commit()
        return {"topologies_synced": topo_count, "scenarios_synced": scenario_count}

    def list_topologies(self, db: Session, user_id: int | None = None) -> list[TopologyResponse]:
        """List all prebuilt topologies plus any topologies created by the user."""
        query = db.query(SimulatorTopology).filter(
            (SimulatorTopology.is_prebuilt.is_(True)) | (SimulatorTopology.user_id == user_id)
        )
        results = []
        for t in query.order_by(SimulatorTopology.id.asc()).all():
            data = json.loads(t.topology_data) if t.topology_data else {"nodes": [], "links": []}
            results.append(
                TopologyResponse(
                    id=t.id,
                    user_id=t.user_id,
                    name=t.name,
                    slug=t.slug,
                    description=t.description,
                    difficulty=t.difficulty,
                    is_prebuilt=t.is_prebuilt,
                    topology_data=TopologyDataSchema.model_validate(data),
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                )
            )
        return results

    def get_topology(self, db: Session, id_or_slug: str | int) -> TopologyResponse | None:
        """Fetch single topology by ID or slug."""
        query = db.query(SimulatorTopology)
        if isinstance(id_or_slug, int) or (isinstance(id_or_slug, str) and id_or_slug.isdigit()):
            topo = query.filter(SimulatorTopology.id == int(id_or_slug)).first()
        else:
            topo = query.filter(SimulatorTopology.slug == str(id_or_slug)).first()

        if not topo:
            return None

        data = json.loads(topo.topology_data) if topo.topology_data else {"nodes": [], "links": []}
        return TopologyResponse(
            id=topo.id,
            user_id=topo.user_id,
            name=topo.name,
            slug=topo.slug,
            description=topo.description,
            difficulty=topo.difficulty,
            is_prebuilt=topo.is_prebuilt,
            topology_data=TopologyDataSchema.model_validate(data),
            created_at=topo.created_at,
            updated_at=topo.updated_at,
        )

    def list_scenarios(self, db: Session) -> list[ScenarioResponse]:
        """List all guided scenarios."""
        scenarios = db.query(SimulatorScenario).order_by(SimulatorScenario.id.asc()).all()
        results = []
        for s in scenarios:
            results.append(self._format_scenario(s))
        return results

    def get_scenario(self, db: Session, slug: str) -> ScenarioResponse | None:
        """Fetch scenario by slug."""
        scenario = db.query(SimulatorScenario).filter(SimulatorScenario.slug == slug).first()
        if not scenario:
            return None
        return self._format_scenario(scenario)

    def _format_scenario(self, s: SimulatorScenario) -> ScenarioResponse:
        """Deserialize database scenario entity into response schema."""
        objectives = json.loads(s.learning_objectives) if s.learning_objectives else []
        initial_topo = json.loads(s.initial_topology) if s.initial_topology else {"nodes": [], "links": []}
        tasks = json.loads(s.tasks) if s.tasks else []
        hints = json.loads(s.hints) if s.hints else []

        task_objs = [ScenarioTaskSchema.model_validate(t) for t in tasks]

        return ScenarioResponse(
            id=s.id,
            slug=s.slug,
            title=s.title,
            difficulty=s.difficulty,
            category=s.category,
            description=s.description,
            learning_objectives=objectives,
            initial_topology=TopologyDataSchema.model_validate(initial_topo),
            tasks=task_objs,
            hints=hints,
            solution_explanation=s.solution_explanation,
        )


simulator_catalog_service = SimulatorCatalogService()
