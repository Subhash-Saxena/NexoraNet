"""Unit and integration tests for Step 9 Interactive Network Simulator."""

from app.schemas.simulator import (
    DeviceConfigurationSchema,
    DeviceInterfaceSchema,
    FirewallRuleSchema,
    RouteEntrySchema,
    SimDeviceSchema,
    SimulatePacketRequest,
    TopologyDataSchema,
    TopologyLinkSchema,
)
from app.services.simulation_engine import simulation_engine
from app.services.simulator_network_utils import (
    are_same_subnet,
    cidr_to_mask,
    generate_deterministic_mac,
    get_subnet_details,
    is_valid_gateway,
    is_valid_ipv4,
    mask_to_cidr,
)
from fastapi import status
from fastapi.testclient import TestClient

# ===========================================================================
# 1. Network Math & Subnet Utility Tests
# ===========================================================================


def test_ipv4_validation():
    assert is_valid_ipv4("192.168.1.1") is True
    assert is_valid_ipv4("10.0.0.254") is True
    assert is_valid_ipv4("invalid-ip") is False
    assert is_valid_ipv4("999.999.999.999") is False
    assert is_valid_ipv4("") is False


def test_cidr_and_mask_conversion():
    assert mask_to_cidr("255.255.255.0") == 24
    assert mask_to_cidr("255.255.0.0") == 16
    assert mask_to_cidr("255.255.255.252") == 30
    assert mask_to_cidr("/24") == 24
    assert mask_to_cidr("24") == 24

    assert cidr_to_mask(24) == "255.255.255.0"
    assert cidr_to_mask(16) == "255.255.0.0"
    assert cidr_to_mask(30) == "255.255.255.252"


def test_subnet_details_calculation():
    details = get_subnet_details("192.168.1.10", 24)
    assert details.network_address == "192.168.1.0"
    assert details.broadcast_address == "192.168.1.255"
    assert details.first_usable_ip == "192.168.1.1"
    assert details.last_usable_ip == "192.168.1.254"
    assert details.total_hosts == 256
    assert details.usable_hosts == 254


def test_are_same_subnet():
    assert are_same_subnet("192.168.1.10", 24, "192.168.1.20", 24) is True
    assert are_same_subnet("192.168.1.10", 24, "192.168.2.20", 24) is False
    assert are_same_subnet("10.0.0.1", 30, "10.0.0.2", 30) is True
    assert are_same_subnet("10.0.0.1", 30, "10.0.0.5", 30) is False


def test_gateway_validation():
    # Valid gateway in subnet
    valid, _ = is_valid_gateway("192.168.1.10", 24, "192.168.1.1")
    assert valid is True

    # Gateway == Host IP
    valid, msg = is_valid_gateway("192.168.1.10", 24, "192.168.1.10")
    assert valid is False
    assert "identical" in msg

    # Gateway outside subnet
    valid, msg = is_valid_gateway("192.168.1.10", 24, "192.168.2.1")
    assert valid is False
    assert "outside" in msg

    # Gateway is broadcast address
    valid, msg = is_valid_gateway("192.168.1.10", 24, "192.168.1.255")
    assert valid is False
    assert "broadcast" in msg


def test_deterministic_mac_generation():
    mac_pc = generate_deterministic_mac("PC", 1, 0)
    assert mac_pc.startswith("02:00:01:01:")
    mac_sw = generate_deterministic_mac("SWITCH", 2, 1)
    assert mac_sw.startswith("02:00:04:02:")


# ===========================================================================
# 2. Simulation Engine Protocol Tests
# ===========================================================================


def test_simulation_pc_to_pc_ping():
    """Verify Layer 2 switching and ICMP ping between 2 PCs on a switch."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="PC1",
        type="PC",
        interfaces=[
            DeviceInterfaceSchema(
                id="i1",
                name="eth0",
                mac_address="02:00:01:01:00:01",
                ipv4_address="192.168.1.10",
                subnet_mask="255.255.255.0",
            )
        ],
    )
    sw = SimDeviceSchema(
        id="sw1",
        name="Switch1",
        type="SWITCH",
        interfaces=[
            DeviceInterfaceSchema(id="p1", name="Port 1", mac_address="02:00:04:01:01:01", vlan_id=1),
            DeviceInterfaceSchema(id="p2", name="Port 2", mac_address="02:00:04:01:02:01", vlan_id=1),
        ],
    )
    pc2 = SimDeviceSchema(
        id="pc2",
        name="PC2",
        type="PC",
        interfaces=[
            DeviceInterfaceSchema(
                id="i2",
                name="eth0",
                mac_address="02:00:01:02:00:01",
                ipv4_address="192.168.1.20",
                subnet_mask="255.255.255.0",
            )
        ],
    )

    topo = TopologyDataSchema(
        nodes=[pc1, sw, pc2],
        links=[
            TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="sw1", target_interface_id="p1"),
            TopologyLinkSchema(id="l2", source_node_id="sw1", source_interface_id="p2", target_node_id="pc2", target_interface_id="i2"),
        ],
    )

    req = SimulatePacketRequest(
        topology=topo,
        source_device_id="pc1",
        destination_device_id="pc2",
        protocol="ICMP",
    )
    res = simulation_engine.simulate(req)
    assert res.success is True
    assert "succeeded" in res.summary
    assert len(res.events) >= 4
    # Verify ARP and ICMP events present
    event_types = [e.type for e in res.events]
    assert "ARP_REQUEST" in event_types
    assert "ARP_REPLY" in event_types
    assert "ICMP_REQUEST" in event_types
    assert "ICMP_REPLY" in event_types


def test_simulation_vlan_isolation():
    """Verify VLAN isolation drops frames when ports have mismatched VLAN IDs."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="PC1",
        type="PC",
        interfaces=[DeviceInterfaceSchema(id="i1", name="eth0", mac_address="02:00:01:01:00:01", ipv4_address="192.168.10.10", vlan_id=10)],
    )
    sw = SimDeviceSchema(
        id="sw1",
        name="Switch1",
        type="SWITCH",
        interfaces=[
            DeviceInterfaceSchema(id="p1", name="Port 1", mac_address="02:00:04:01:01:01", vlan_id=10),
            DeviceInterfaceSchema(id="p2", name="Port 2", mac_address="02:00:04:01:02:01", vlan_id=20),  # Different VLAN
        ],
    )
    pc2 = SimDeviceSchema(
        id="pc2",
        name="PC2",
        type="PC",
        interfaces=[DeviceInterfaceSchema(id="i2", name="eth0", mac_address="02:00:01:02:00:01", ipv4_address="192.168.10.20", vlan_id=20)],
    )

    topo = TopologyDataSchema(
        nodes=[pc1, sw, pc2],
        links=[
            TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="sw1", target_interface_id="p1"),
            TopologyLinkSchema(id="l2", source_node_id="sw1", source_interface_id="p2", target_node_id="pc2", target_interface_id="i2"),
        ],
    )

    req = SimulatePacketRequest(
        topology=topo,
        source_device_id="pc1",
        destination_device_id="pc2",
        protocol="ICMP",
    )
    res = simulation_engine.simulate(req)
    assert res.success is False
    assert "VLAN" in (res.failure_reason or "") or "ARP timeout" in (res.failure_reason or "")


def test_simulation_routed_subnets():
    """Verify Layer 3 router decrements TTL and routes between subnets."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="PC1",
        type="PC",
        interfaces=[
            DeviceInterfaceSchema(
                id="i1",
                name="eth0",
                mac_address="02:00:01:01:00:01",
                ipv4_address="192.168.1.10",
                subnet_mask="255.255.255.0",
                default_gateway="192.168.1.1",
            )
        ],
    )
    rtr = SimDeviceSchema(
        id="rtr1",
        name="Router1",
        type="ROUTER",
        interfaces=[
            DeviceInterfaceSchema(id="r0", name="eth0", mac_address="02:00:05:01:00:01", ipv4_address="192.168.1.1", subnet_mask="255.255.255.0"),
            DeviceInterfaceSchema(id="r1", name="eth1", mac_address="02:00:05:01:01:01", ipv4_address="192.168.2.1", subnet_mask="255.255.255.0"),
        ],
        configuration=DeviceConfigurationSchema(
            routing_table=[
                RouteEntrySchema(destination="192.168.1.0", netmask="255.255.255.0", next_hop="DIRECT", interface="eth0"),
                RouteEntrySchema(destination="192.168.2.0", netmask="255.255.255.0", next_hop="DIRECT", interface="eth1"),
            ]
        ),
    )
    pc2 = SimDeviceSchema(
        id="pc2",
        name="PC2",
        type="PC",
        interfaces=[
            DeviceInterfaceSchema(
                id="i2",
                name="eth0",
                mac_address="02:00:01:02:00:01",
                ipv4_address="192.168.2.20",
                subnet_mask="255.255.255.0",
                default_gateway="192.168.2.1",
            )
        ],
    )

    topo = TopologyDataSchema(
        nodes=[pc1, rtr, pc2],
        links=[
            TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="rtr1", target_interface_id="r0"),
            TopologyLinkSchema(id="l2", source_node_id="rtr1", source_interface_id="r1", target_node_id="pc2", target_interface_id="i2"),
        ],
    )

    req = SimulatePacketRequest(
        topology=topo,
        source_device_id="pc1",
        destination_device_id="pc2",
        protocol="ICMP",
    )
    res = simulation_engine.simulate(req)
    assert res.success is True
    # Verify TTL decrement recorded in hops
    assert len(res.hops) >= 3


def test_simulation_tcp_handshake():
    """Verify TCP 3-Way Handshake (SYN, SYN-ACK, ACK)."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="ClientPC",
        type="PC",
        interfaces=[DeviceInterfaceSchema(id="i1", name="eth0", mac_address="02:00:01:01:00:01", ipv4_address="192.168.1.10", subnet_mask="255.255.255.0")],
    )
    srv = SimDeviceSchema(
        id="srv1",
        name="WebServer",
        type="SERVER",
        interfaces=[DeviceInterfaceSchema(id="i2", name="eth0", mac_address="02:00:03:01:00:01", ipv4_address="192.168.1.100", subnet_mask="255.255.255.0")],
    )

    topo = TopologyDataSchema(
        nodes=[pc1, srv],
        links=[TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="srv1", target_interface_id="i2")],
    )

    req = SimulatePacketRequest(
        topology=topo,
        source_device_id="pc1",
        destination_device_id="srv1",
        protocol="TCP",
        port=80,
    )
    res = simulation_engine.simulate(req)
    assert res.success is True
    assert "ESTABLISHED" in res.summary
    event_types = [e.type for e in res.events]
    assert "TCP_SYN" in event_types
    assert "TCP_SYN_ACK" in event_types
    assert "TCP_ACK" in event_types


def test_simulation_dns_query():
    """Verify DNS resolution (query & response)."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="PC1",
        type="PC",
        interfaces=[DeviceInterfaceSchema(id="i1", name="eth0", mac_address="02:00:01:01:00:01", ipv4_address="192.168.10.15", subnet_mask="255.255.255.0")],
    )
    dns = SimDeviceSchema(
        id="dns1",
        name="DNSServer",
        type="DNS_SERVER",
        interfaces=[DeviceInterfaceSchema(id="i2", name="eth0", mac_address="02:00:08:01:00:01", ipv4_address="192.168.10.53", subnet_mask="255.255.255.0")],
        configuration=DeviceConfigurationSchema(
            dns_records={"intranet.local": "192.168.10.200"}
        ),
    )

    topo = TopologyDataSchema(
        nodes=[pc1, dns],
        links=[TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="dns1", target_interface_id="i2")],
    )

    req = SimulatePacketRequest(
        topology=topo,
        source_device_id="pc1",
        destination_ip="192.168.10.53",
        protocol="DNS",
        dns_query_name="intranet.local",
    )
    res = simulation_engine.simulate(req)
    assert res.success is True
    assert "intranet.local" in res.summary
    assert "192.168.10.200" in res.summary


def test_simulation_dhcp():
    """Verify DHCP DORA simulation."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="NewLaptop",
        type="LAPTOP",
        interfaces=[DeviceInterfaceSchema(id="i1", name="eth0", mac_address="02:00:02:01:00:01", ipv4_address=None, subnet_mask=None)],
    )
    dhcp = SimDeviceSchema(
        id="dhcp1",
        name="DHCPServer",
        type="DHCP_SERVER",
        interfaces=[DeviceInterfaceSchema(id="i2", name="eth0", mac_address="02:00:09:01:00:01", ipv4_address="192.168.1.1", subnet_mask="255.255.255.0")],
        configuration=DeviceConfigurationSchema(
            dhcp_pool={"network": "192.168.1.0/24", "start": "192.168.1.105", "gateway": "192.168.1.1"}
        ),
    )

    topo = TopologyDataSchema(
        nodes=[pc1, dhcp],
        links=[TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="dhcp1", target_interface_id="i2")],
    )

    req = SimulatePacketRequest(
        topology=topo,
        source_device_id="pc1",
        protocol="DHCP",
    )
    res = simulation_engine.simulate(req)
    assert res.success is True
    assert "DORA" in res.summary
    assert "192.168.1.105" in res.summary


def test_simulation_firewall_filtering():
    """Verify firewall permits ICMP and drops denied TCP port."""
    pc1 = SimDeviceSchema(
        id="pc1",
        name="Host",
        type="PC",
        interfaces=[DeviceInterfaceSchema(id="i1", name="eth0", mac_address="02:00:01:01:00:01", ipv4_address="192.168.1.10", subnet_mask="255.255.255.0", default_gateway="192.168.1.1")],
    )
    fw = SimDeviceSchema(
        id="fw1",
        name="Firewall",
        type="FIREWALL",
        interfaces=[
            DeviceInterfaceSchema(id="f0", name="eth0", mac_address="02:00:06:01:00:01", ipv4_address="192.168.1.1", subnet_mask="255.255.255.0"),
            DeviceInterfaceSchema(id="f1", name="eth1", mac_address="02:00:06:01:01:01", ipv4_address="10.0.0.1", subnet_mask="255.255.255.0"),
        ],
        configuration=DeviceConfigurationSchema(
            firewall_rules=[
                FirewallRuleSchema(id="FW1", action="ALLOW", protocol="ICMP"),
                FirewallRuleSchema(id="FW2", action="DENY", protocol="TCP", port=23),
            ],
            routing_table=[
                RouteEntrySchema(destination="192.168.1.0", netmask="255.255.255.0", next_hop="DIRECT", interface="eth0"),
                RouteEntrySchema(destination="10.0.0.0", netmask="255.255.255.0", next_hop="DIRECT", interface="eth1"),
            ],
        ),
    )
    srv = SimDeviceSchema(
        id="srv1",
        name="Server",
        type="SERVER",
        interfaces=[DeviceInterfaceSchema(id="i2", name="eth0", mac_address="02:00:03:01:00:01", ipv4_address="10.0.0.50", subnet_mask="255.255.255.0", default_gateway="10.0.0.1")],
    )

    topo = TopologyDataSchema(
        nodes=[pc1, fw, srv],
        links=[
            TopologyLinkSchema(id="l1", source_node_id="pc1", source_interface_id="i1", target_node_id="fw1", target_interface_id="f0"),
            TopologyLinkSchema(id="l2", source_node_id="fw1", source_interface_id="f1", target_node_id="srv1", target_interface_id="i2"),
        ],
    )

    # Test 1: ICMP Ping should succeed
    req_ping = SimulatePacketRequest(topology=topo, source_device_id="pc1", destination_device_id="srv1", protocol="ICMP")
    res_ping = simulation_engine.simulate(req_ping)
    assert res_ping.success is True

    # Test 2: TCP on port 23 (Telnet) should be DENIED
    req_telnet = SimulatePacketRequest(topology=topo, source_device_id="pc1", destination_device_id="srv1", protocol="TCP", port=23)
    res_telnet = simulation_engine.simulate(req_telnet)
    assert res_telnet.success is False
    assert "firewall" in res_telnet.failure_reason.lower()


# ===========================================================================
# 3. REST API Endpoint Tests
# ===========================================================================


def test_api_list_and_get_topologies(client: TestClient):
    response = client.get("/api/v1/simulator/topologies")
    assert response.status_code == status.HTTP_200_OK
    topos = response.json()
    assert len(topos) >= 6
    assert any(t["slug"] == "simple-lan" for t in topos)

    # Get specific topology
    res_single = client.get("/api/v1/simulator/topologies/simple-lan")
    assert res_single.status_code == status.HTTP_200_OK
    data = res_single.json()
    assert data["slug"] == "simple-lan"
    assert len(data["topology_data"]["nodes"]) >= 3


def test_api_validate_topology(client: TestClient):
    payload = {
        "nodes": [
            {
                "id": "pc1",
                "name": "PC1",
                "type": "PC",
                "interfaces": [{"id": "i1", "name": "eth0", "mac_address": "02:00:01:01:00:01", "ipv4_address": "192.168.1.10", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
            },
            {
                "id": "pc2",
                "name": "PC2",
                "type": "PC",
                "interfaces": [{"id": "i2", "name": "eth0", "mac_address": "02:00:01:02:00:01", "ipv4_address": "192.168.1.20", "subnet_mask": "255.255.255.0", "default_gateway": "192.168.1.1"}],
            },
        ],
        "links": [],
    }
    response = client.post("/api/v1/simulator/topologies/validate", json=payload)
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    assert res["is_valid"] is True
    assert len(res["subnets_detected"]) == 2


def test_api_list_and_validate_scenarios(client: TestClient):
    # List scenarios
    res_list = client.get("/api/v1/simulator/scenarios")
    assert res_list.status_code == status.HTTP_200_OK
    scenarios = res_list.json()
    assert len(scenarios) >= 10

    # Get single scenario
    res_get = client.get("/api/v1/simulator/scenarios/connect-two-pcs")
    assert res_get.status_code == status.HTTP_200_OK
    sc = res_get.json()
    assert sc["slug"] == "connect-two-pcs"
    assert len(sc["tasks"]) == 3

    # Validate passing scenario
    valid_topo = sc["initial_topology"]
    # Fix PC2 IP and link
    valid_topo["nodes"][2]["interfaces"][0]["ipv4_address"] = "192.168.1.20"
    valid_topo["links"].append({
        "id": "link-2",
        "source_node_id": "sw-1",
        "source_interface_id": "if-sw1-p2",
        "target_node_id": "pc-2",
        "target_interface_id": "if-pc2-eth0",
    })

    val_res = client.post(
        "/api/v1/simulator/scenarios/connect-two-pcs/validate",
        json={"topology": valid_topo, "hints_used": 0},
    )
    assert val_res.status_code == status.HTTP_200_OK
    val_data = val_res.json()
    assert val_data["is_passed"] is True
    assert val_data["score"] >= 80
