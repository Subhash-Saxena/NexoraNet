"""Authoritative educational network simulation engine for NexoraNet.

Simulates safe virtual packet traversal, ARP resolution, Layer-2 switching (MAC learning & VLANs),
Layer-3 routing (LPM & TTL decrement), Firewalls (ACL filtering), NAT, ICMP, TCP, DNS, and DHCP.
"""

import ipaddress
import uuid
from typing import Any

from app.schemas.simulator import (
    ArpEntrySchema,
    DeviceInterfaceSchema,
    HopRecordSchema,
    MacEntrySchema,
    SimDeviceSchema,
    SimulatedPacketSchema,
    SimulatePacketRequest,
    SimulationEventSchema,
    SimulationResultResponse,
    TopologyDataSchema,
)
from app.services.simulator_network_utils import (
    are_same_subnet,
    mask_to_cidr,
)


class SimulationEngine:
    """Core educational network simulation engine."""

    def simulate(self, request: SimulatePacketRequest) -> SimulationResultResponse:
        """Run step-by-step authoritative packet simulation on given topology."""
        topology = request.topology
        node_map = {n.id: n for n in topology.nodes}
        link_map = self._build_link_map(topology)

        src_node = node_map.get(request.source_device_id)
        if not src_node:
            return SimulationResultResponse(
                success=False,
                summary="Source device not found in topology.",
                failure_reason=f"Source node ID '{request.source_device_id}' does not exist.",
            )

        events: list[SimulationEventSchema] = []
        hops: list[HopRecordSchema] = []
        packets: list[SimulatedPacketSchema] = []
        arp_updates: dict[str, list[ArpEntrySchema]] = {}
        mac_updates: dict[str, list[MacEntrySchema]] = {}

        # Handle DHCP specifically
        if request.protocol.upper() == "DHCP":
            return self._simulate_dhcp(
                src_node=src_node,
                node_map=node_map,
                link_map=link_map,
                events=events,
                hops=hops,
                packets=packets,
            )

        # Standard L3 / L4 / L7 protocols
        src_iface = self._get_active_interface(src_node)
        if not src_iface or not src_iface.ipv4_address:
            return SimulationResultResponse(
                success=False,
                summary=f"Device '{src_node.name}' has no active IPv4 interface configured.",
                failure_reason=f"Node '{src_node.name}' has no interface with an IPv4 address.",
            )

        # Resolve destination
        dst_node, dst_ip, dst_iface = self._resolve_destination(
            request=request,
            src_node=src_node,
            node_map=node_map,
        )

        if not dst_ip:
            return SimulationResultResponse(
                success=False,
                summary="Destination IP address could not be resolved.",
                failure_reason="Unable to determine destination IP for packet simulation.",
            )

        # Handle DNS Query specifically
        if request.protocol.upper() == "DNS":
            return self._simulate_dns(
                src_node=src_node,
                src_iface=src_iface,
                dns_server_ip=dst_ip,
                query_name=request.dns_query_name or "www.example.local",
                node_map=node_map,
                link_map=link_map,
                events=events,
                hops=hops,
                packets=packets,
            )

        # Handle TCP 3-Way Handshake
        if request.protocol.upper() == "TCP":
            return self._simulate_tcp_handshake(
                src_node=src_node,
                src_iface=src_iface,
                dst_node=dst_node,
                dst_ip=dst_ip,
                dst_iface=dst_iface,
                port=request.port or 80,
                node_map=node_map,
                link_map=link_map,
                events=events,
                hops=hops,
                packets=packets,
                arp_updates=arp_updates,
                mac_updates=mac_updates,
            )

        # Default: ICMP Echo / Ping
        return self._simulate_icmp_ping(
            src_node=src_node,
            src_iface=src_iface,
            dst_node=dst_node,
            dst_ip=dst_ip,
            dst_iface=dst_iface,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            packets=packets,
            arp_updates=arp_updates,
            mac_updates=mac_updates,
        )

    # -----------------------------------------------------------------------
    # Protocol Handlers
    # -----------------------------------------------------------------------

    def _simulate_icmp_ping(
        self,
        src_node: SimDeviceSchema,
        src_iface: DeviceInterfaceSchema,
        dst_node: SimDeviceSchema | None,
        dst_ip: str,
        dst_iface: DeviceInterfaceSchema | None,
        node_map: dict[str, SimDeviceSchema],
        link_map: dict[str, list[dict[str, Any]]],
        events: list[SimulationEventSchema],
        hops: list[HopRecordSchema],
        packets: list[SimulatedPacketSchema],
        arp_updates: dict[str, list[ArpEntrySchema]],
        mac_updates: dict[str, list[MacEntrySchema]],
    ) -> SimulationResultResponse:
        """Simulate ARP resolution followed by ICMP Echo Request and Echo Reply."""
        pkt_id = f"PKT-ICMP-{uuid.uuid4().hex[:6].upper()}"
        timestamp = 0

        # Step 1: Subnet & Gateway Check
        same_subnet = are_same_subnet(
            src_iface.ipv4_address,
            src_iface.subnet_mask or "255.255.255.0",
            dst_ip,
            dst_iface.subnet_mask if dst_iface else src_iface.subnet_mask,
        )

        next_hop_ip = dst_ip if same_subnet else src_iface.default_gateway
        if not same_subnet and not next_hop_ip:
            reason = f"Destination '{dst_ip}' is on a remote subnet, but '{src_node.name}' has no default gateway configured."
            events.append(
                SimulationEventSchema(
                    id=str(uuid.uuid4())[:8],
                    timestamp_ms=timestamp,
                    type="ROUTE_FAILURE",
                    device_id=src_node.id,
                    device_name=src_node.name,
                    packet_id=pkt_id,
                    message=f"Routing failure on {src_node.name}: Missing default gateway.",
                    explanation=reason,
                    why_reason="End devices must use a default gateway (router interface) to reach IP addresses outside their local subnet.",
                    cyber_relevance="Misconfigured default gateways cause complete communication blackouts and are a common IT troubleshooting ticket.",
                    severity="ERROR",
                )
            )
            return SimulationResultResponse(
                success=False,
                summary=f"Ping to {dst_ip} failed: No default gateway configured.",
                failure_reason=reason,
                events=events,
            )

        # Step 2: ARP Resolution if not in cache
        arp_resolved_mac = self._resolve_arp(
            src_node=src_node,
            src_iface=src_iface,
            target_ip=next_hop_ip,
            node_map=node_map,
            link_map=link_map,
            events=events,
            arp_updates=arp_updates,
            mac_updates=mac_updates,
            timestamp=timestamp,
        )

        if not arp_resolved_mac:
            reason = f"ARP resolution failed: No device responded for next-hop IP {next_hop_ip}."
            events.append(
                SimulationEventSchema(
                    id=str(uuid.uuid4())[:8],
                    timestamp_ms=timestamp + 100,
                    type="PACKET_DROPPED",
                    device_id=src_node.id,
                    device_name=src_node.name,
                    packet_id=pkt_id,
                    message=f"ARP Request for {next_hop_ip} timed out.",
                    explanation=reason,
                    why_reason="Devices broadcast ARP requests to learn MAC addresses. If no active link or interface matches the target IP, the request goes unanswered.",
                    cyber_relevance="ARP timeouts reveal disconnected hosts, firewall blocks, or IP misconfigurations.",
                    severity="ERROR",
                )
            )
            return SimulationResultResponse(
                success=False,
                summary=f"Ping failed: Destination/Gateway {next_hop_ip} is unreachable (ARP timeout).",
                failure_reason=reason,
                events=events,
                arp_table_updates=arp_updates,
                mac_table_updates=mac_updates,
            )

        # Step 3: Forward ICMP Echo Request
        req_packet = SimulatedPacketSchema(
            id=pkt_id,
            protocol="ICMP",
            source_device_id=src_node.id,
            destination_device_id=dst_node.id if dst_node else "UNKNOWN",
            source_ip=src_iface.ipv4_address,
            destination_ip=dst_ip,
            source_mac=src_iface.mac_address,
            destination_mac=arp_resolved_mac,
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={"type": "ECHO_REQUEST", "seq": 1, "code": 0},
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3],
        )
        packets.append(req_packet)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 150,
                type="ICMP_REQUEST",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id=pkt_id,
                message=f"{src_node.name} transmitted ICMP Echo Request to {dst_ip}.",
                explanation=f"{src_node.name} encapsulated an ICMP Echo Request into an IPv4 packet (TTL=64) and an Ethernet frame addressed to MAC {arp_resolved_mac}.",
                why_reason="Ping utilizes ICMP Type 8 (Echo Request) to test end-to-end network reachability.",
                cyber_relevance="ICMP ping sweeps are commonly used in network reconnaissance to map live hosts.",
                severity="INFO",
            )
        )

        # Forward request packet through topology
        traversal_res = self._traverse_path(
            packet=req_packet,
            curr_node=src_node,
            ingress_iface=None,
            dst_ip=dst_ip,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates=mac_updates,
            start_hop=1,
            timestamp=timestamp + 200,
        )

        if not traversal_res["delivered"]:
            req_packet.status = "DROPPED"
            req_packet.drop_reason = traversal_res["reason"]
            return SimulationResultResponse(
                success=False,
                summary=f"Ping to {dst_ip} failed: {traversal_res['reason']}",
                failure_reason=traversal_res["reason"],
                packets=packets,
                events=events,
                hops=hops,
                arp_table_updates=arp_updates,
                mac_table_updates=mac_updates,
            )

        req_packet.status = "DELIVERED"
        end_node = traversal_res["delivered_to"]

        # Step 4: Generate ICMP Echo Reply from destination back to source
        reply_pkt_id = f"PKT-REPLY-{uuid.uuid4().hex[:6].upper()}"
        reply_packet = SimulatedPacketSchema(
            id=reply_pkt_id,
            protocol="ICMP",
            source_device_id=end_node.id,
            destination_device_id=src_node.id,
            source_ip=dst_ip,
            destination_ip=src_iface.ipv4_address,
            source_mac=traversal_res["delivered_iface"].mac_address if traversal_res["delivered_iface"] else "02:00:FF:FF:FF:01",
            destination_mac=src_iface.mac_address,
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={"type": "ECHO_REPLY", "seq": 1, "code": 0},
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3],
        )
        packets.append(reply_packet)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 500,
                type="ICMP_REPLY",
                device_id=end_node.id,
                device_name=end_node.name,
                packet_id=reply_pkt_id,
                message=f"{end_node.name} received Echo Request and generated ICMP Echo Reply.",
                explanation=f"{end_node.name} successfully processed the ICMP Echo Request and formulated an ICMP Echo Reply (Type 0) returning to {src_iface.ipv4_address}.",
                why_reason="The destination host acknowledges receipt by inverting the IP source/destination and changing the ICMP type to Echo Reply.",
                cyber_relevance="Firewalls often permit outbound ping requests but can selectively block inbound ICMP Echo Replies to evade host discovery.",
                severity="SUCCESS",
            )
        )

        reply_traversal = self._traverse_path(
            packet=reply_packet,
            curr_node=end_node,
            ingress_iface=None,
            dst_ip=src_iface.ipv4_address,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates=mac_updates,
            start_hop=len(hops) + 1,
            timestamp=timestamp + 600,
        )

        if not reply_traversal["delivered"]:
            reply_packet.status = "DROPPED"
            reply_packet.drop_reason = reply_traversal["reason"]
            return SimulationResultResponse(
                success=False,
                summary=f"Ping reply dropped: {reply_traversal['reason']}",
                failure_reason=reply_traversal["reason"],
                packets=packets,
                events=events,
                hops=hops,
                arp_table_updates=arp_updates,
                mac_table_updates=mac_updates,
            )

        reply_packet.status = "DELIVERED"
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 900,
                type="ICMP_REPLY",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id=reply_pkt_id,
                message=f"{src_node.name} received ICMP Echo Reply from {dst_ip}! Ping successful.",
                explanation=f"Round-trip communication completed successfully between {src_node.name} ({src_iface.ipv4_address}) and {end_node.name} ({dst_ip}).",
                why_reason="Successful round-trip ping confirms Physical, Data Link, Network layers, and IP routing operate correctly in both directions.",
                cyber_relevance="A verified bi-directional channel confirms the destination is live, responding, and uninhibited by packet filters.",
                severity="SUCCESS",
            )
        )

        return SimulationResultResponse(
            success=True,
            summary=f"Ping from {src_node.name} ({src_iface.ipv4_address}) to {dst_ip} succeeded with 0% packet loss.",
            packets=packets,
            events=events,
            hops=hops,
            arp_table_updates=arp_updates,
            mac_table_updates=mac_updates,
        )

    def _simulate_tcp_handshake(
        self,
        src_node: SimDeviceSchema,
        src_iface: DeviceInterfaceSchema,
        dst_node: SimDeviceSchema | None,
        dst_ip: str,
        dst_iface: DeviceInterfaceSchema | None,
        port: int,
        node_map: dict[str, SimDeviceSchema],
        link_map: dict[str, list[dict[str, Any]]],
        events: list[SimulationEventSchema],
        hops: list[HopRecordSchema],
        packets: list[SimulatedPacketSchema],
        arp_updates: dict[str, list[ArpEntrySchema]],
        mac_updates: dict[str, list[MacEntrySchema]],
    ) -> SimulationResultResponse:
        """Simulate TCP 3-Way Handshake (SYN -> SYN-ACK -> ACK)."""
        src_port = 49152
        seq_init = 1000
        server_seq = 5000

        # Step 1: SYN
        syn_pkt = SimulatedPacketSchema(
            id=f"PKT-TCP-SYN-{uuid.uuid4().hex[:6].upper()}",
            protocol="TCP",
            source_device_id=src_node.id,
            destination_device_id=dst_node.id if dst_node else "UNKNOWN",
            source_ip=src_iface.ipv4_address,
            destination_ip=dst_ip,
            source_mac=src_iface.mac_address,
            destination_mac="02:00:FF:FF:FF:01",
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={
                "src_port": src_port,
                "dst_port": port,
                "seq": seq_init,
                "ack": 0,
                "flags": ["SYN"],
            },
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3, 4],
        )
        packets.append(syn_pkt)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=100,
                type="TCP_SYN",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id=syn_pkt.id,
                message=f"{src_node.name} sent TCP SYN to {dst_ip}:{port} (Seq={seq_init}).",
                explanation=f"{src_node.name} initiates connection to port {port} using an ephemeral client port {src_port} with the SYN flag enabled.",
                why_reason="The TCP 3-way handshake begins with SYN (Synchronize) to establish sequence numbers for reliable transmission.",
                cyber_relevance="SYN floods attempt to exhaust server connection queues (TCB backlogs) by sending half-open SYN packets without completing the handshake.",
                severity="INFO",
            )
        )

        res1 = self._traverse_path(
            packet=syn_pkt,
            curr_node=src_node,
            ingress_iface=None,
            dst_ip=dst_ip,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates=mac_updates,
            start_hop=1,
            timestamp=200,
        )

        if not res1["delivered"]:
            syn_pkt.status = "DROPPED"
            syn_pkt.drop_reason = res1["reason"]
            return SimulationResultResponse(
                success=False,
                summary=f"TCP handshake failed at SYN stage: {res1['reason']}",
                failure_reason=res1["reason"],
                packets=packets,
                events=events,
                hops=hops,
            )

        syn_pkt.status = "DELIVERED"
        server_node = res1["delivered_to"]

        # Step 2: SYN-ACK
        syn_ack_pkt = SimulatedPacketSchema(
            id=f"PKT-TCP-SYNACK-{uuid.uuid4().hex[:6].upper()}",
            protocol="TCP",
            source_device_id=server_node.id,
            destination_device_id=src_node.id,
            source_ip=dst_ip,
            destination_ip=src_iface.ipv4_address,
            source_mac=res1["delivered_iface"].mac_address if res1["delivered_iface"] else "02:00:FF:FF:FF:02",
            destination_mac=src_iface.mac_address,
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={
                "src_port": port,
                "dst_port": src_port,
                "seq": server_seq,
                "ack": seq_init + 1,
                "flags": ["SYN", "ACK"],
            },
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3, 4],
        )
        packets.append(syn_ack_pkt)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=400,
                type="TCP_SYN_ACK",
                device_id=server_node.id,
                device_name=server_node.name,
                packet_id=syn_ack_pkt.id,
                message=f"{server_node.name} replied with TCP SYN-ACK (Seq={server_seq}, Ack={seq_init + 1}).",
                explanation=f"{server_node.name} agreed to establish the connection, acknowledges client sequence {seq_init}, and provides its own initial sequence number {server_seq}.",
                why_reason="The server confirms readiness to receive data and synchronizes its own transmission parameters.",
                cyber_relevance="Observing SYN-ACK in packet captures confirms the destination port is open and listening for connections.",
                severity="SUCCESS",
            )
        )

        res2 = self._traverse_path(
            packet=syn_ack_pkt,
            curr_node=server_node,
            ingress_iface=None,
            dst_ip=src_iface.ipv4_address,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates=mac_updates,
            start_hop=len(hops) + 1,
            timestamp=500,
        )

        if not res2["delivered"]:
            syn_ack_pkt.status = "DROPPED"
            syn_ack_pkt.drop_reason = res2["reason"]
            return SimulationResultResponse(
                success=False,
                summary=f"TCP handshake failed at SYN-ACK stage: {res2['reason']}",
                failure_reason=res2["reason"],
                packets=packets,
                events=events,
                hops=hops,
            )

        syn_ack_pkt.status = "DELIVERED"

        # Step 3: ACK
        ack_pkt = SimulatedPacketSchema(
            id=f"PKT-TCP-ACK-{uuid.uuid4().hex[:6].upper()}",
            protocol="TCP",
            source_device_id=src_node.id,
            destination_device_id=server_node.id,
            source_ip=src_iface.ipv4_address,
            destination_ip=dst_ip,
            source_mac=src_iface.mac_address,
            destination_mac=syn_ack_pkt.source_mac,
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={
                "src_port": src_port,
                "dst_port": port,
                "seq": seq_init + 1,
                "ack": server_seq + 1,
                "flags": ["ACK"],
            },
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3, 4],
        )
        packets.append(ack_pkt)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=700,
                type="TCP_ACK",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id=ack_pkt.id,
                message=f"{src_node.name} sent final TCP ACK (Ack={server_seq + 1}). Connection ESTABLISHED.",
                explanation=f"{src_node.name} sends the final acknowledgement to {server_node.name}. Both sides transition to ESTABLISHED state.",
                why_reason="The 3-way handshake concludes with an ACK from the initiator, allowing reliable application layer byte streaming (e.g. HTTP, SSH, TLS).",
                cyber_relevance="Full TCP connections require this handshake; port scanners distinguish full-connect scans from stealth SYN scans based on whether this ACK is transmitted.",
                severity="SUCCESS",
            )
        )

        res3 = self._traverse_path(
            packet=ack_pkt,
            curr_node=src_node,
            ingress_iface=None,
            dst_ip=dst_ip,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates=mac_updates,
            start_hop=len(hops) + 1,
            timestamp=800,
        )

        ack_pkt.status = "DELIVERED" if res3["delivered"] else "DROPPED"

        return SimulationResultResponse(
            success=True,
            summary=f"TCP 3-Way Handshake with {dst_ip}:{port} completed successfully. Connection ESTABLISHED.",
            packets=packets,
            events=events,
            hops=hops,
            arp_table_updates=arp_updates,
            mac_table_updates=mac_updates,
        )

    def _simulate_dns(
        self,
        src_node: SimDeviceSchema,
        src_iface: DeviceInterfaceSchema,
        dns_server_ip: str,
        query_name: str,
        node_map: dict[str, SimDeviceSchema],
        link_map: dict[str, list[dict[str, Any]]],
        events: list[SimulationEventSchema],
        hops: list[HopRecordSchema],
        packets: list[SimulatedPacketSchema],
    ) -> SimulationResultResponse:
        """Simulate DNS Query (UDP 53) and DNS Response."""
        # 1. Query
        q_pkt = SimulatedPacketSchema(
            id=f"PKT-DNS-Q-{uuid.uuid4().hex[:6].upper()}",
            protocol="DNS",
            source_device_id=src_node.id,
            destination_device_id="DNS_SERVER",
            source_ip=src_iface.ipv4_address,
            destination_ip=dns_server_ip,
            source_mac=src_iface.mac_address,
            destination_mac="02:00:FF:FF:FF:53",
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={
                "type": "QUERY",
                "query_name": query_name,
                "record_type": "A",
                "src_port": 53000,
                "dst_port": 53,
            },
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3, 4, 7],
        )
        packets.append(q_pkt)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=100,
                type="DNS_QUERY",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id=q_pkt.id,
                message=f"{src_node.name} issued DNS Query for '{query_name}' to {dns_server_ip}:53.",
                explanation=f"{src_node.name} sends a UDP datagram to DNS server {dns_server_ip} on port 53 requesting the IPv4 Address ('A' record) for '{query_name}'.",
                why_reason="Applications use DNS to translate human-friendly domain names into routable numerical IP addresses.",
                cyber_relevance="DNS queries reveal user browsing activity to network monitors; DNS sinkholing or poisoning can redirect traffic to malicious servers.",
                severity="INFO",
            )
        )

        res1 = self._traverse_path(
            packet=q_pkt,
            curr_node=src_node,
            ingress_iface=None,
            dst_ip=dns_server_ip,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates={},
            start_hop=1,
            timestamp=200,
        )

        if not res1["delivered"]:
            q_pkt.status = "DROPPED"
            q_pkt.drop_reason = res1["reason"]
            return SimulationResultResponse(
                success=False,
                summary=f"DNS Query failed to reach DNS server: {res1['reason']}",
                failure_reason=res1["reason"],
                packets=packets,
                events=events,
                hops=hops,
            )

        q_pkt.status = "DELIVERED"
        dns_node = res1["delivered_to"]

        # Server lookup
        resolved_ip = dns_node.configuration.dns_records.get(query_name, "192.168.10.20")

        # 2. Response
        r_pkt = SimulatedPacketSchema(
            id=f"PKT-DNS-R-{uuid.uuid4().hex[:6].upper()}",
            protocol="DNS",
            source_device_id=dns_node.id,
            destination_device_id=src_node.id,
            source_ip=dns_server_ip,
            destination_ip=src_iface.ipv4_address,
            source_mac=res1["delivered_iface"].mac_address if res1["delivered_iface"] else "02:00:FF:FF:FF:53",
            destination_mac=src_iface.mac_address,
            ttl=64,
            ethernet_type="0x0800",
            l3_payload={
                "type": "RESPONSE",
                "query_name": query_name,
                "record_type": "A",
                "resolved_ip": resolved_ip,
                "src_port": 53,
                "dst_port": 53000,
            },
            status="IN_TRANSIT",
            osi_layers=[1, 2, 3, 4, 7],
        )
        packets.append(r_pkt)

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=400,
                type="DNS_RESPONSE",
                device_id=dns_node.id,
                device_name=dns_node.name,
                packet_id=r_pkt.id,
                message=f"{dns_node.name} resolved '{query_name}' -> {resolved_ip}.",
                explanation=f"{dns_node.name} located the authoritative A record mapping '{query_name}' to IP {resolved_ip} and returned a DNS Response.",
                why_reason="The server provides the IP mapping so the client can subsequent establish TCP/UDP sessions directly with the target host.",
                cyber_relevance="DNS resolution logs provide essential evidence during incident response to track malware command-and-control beaconing.",
                severity="SUCCESS",
            )
        )

        res2 = self._traverse_path(
            packet=r_pkt,
            curr_node=dns_node,
            ingress_iface=None,
            dst_ip=src_iface.ipv4_address,
            node_map=node_map,
            link_map=link_map,
            events=events,
            hops=hops,
            mac_updates={},
            start_hop=len(hops) + 1,
            timestamp=500,
        )

        r_pkt.status = "DELIVERED" if res2["delivered"] else "DROPPED"

        return SimulationResultResponse(
            success=True,
            summary=f"DNS resolution succeeded: '{query_name}' resolved to {resolved_ip}.",
            packets=packets,
            events=events,
            hops=hops,
        )

    def _simulate_dhcp(
        self,
        src_node: SimDeviceSchema,
        node_map: dict[str, SimDeviceSchema],
        link_map: dict[str, list[dict[str, Any]]],
        events: list[SimulationEventSchema],
        hops: list[HopRecordSchema],
        packets: list[SimulatedPacketSchema],
    ) -> SimulationResultResponse:
        """Simulate DHCP 4-Step Exchange: DORA (Discover -> Offer -> Request -> ACK)."""
        src_iface = src_node.interfaces[0] if src_node.interfaces else None
        if not src_iface:
            return SimulationResultResponse(
                success=False,
                summary="Device has no interface to perform DHCP.",
                failure_reason="No interface available on client.",
            )

        # Find DHCP server in topology
        dhcp_server = None
        for n in node_map.values():
            if n.type in ("DHCP_SERVER", "SERVER") and ("DHCP" in n.configuration.services or n.type == "DHCP_SERVER"):
                dhcp_server = n
                break

        if not dhcp_server:
            # Check for router with DHCP
            for n in node_map.values():
                if n.type == "ROUTER" and "DHCP" in n.configuration.services:
                    dhcp_server = n
                    break

        offered_ip = "192.168.1.150"
        offered_mask = "255.255.255.0"
        offered_gw = "192.168.1.1"
        offered_dns = "192.168.1.1"

        if dhcp_server and dhcp_server.configuration.dhcp_pool:
            pool = dhcp_server.configuration.dhcp_pool
            offered_ip = pool.get("start", offered_ip)
            offered_gw = pool.get("gateway", offered_gw)
            offered_dns = pool.get("dns", offered_dns)

        server_name = dhcp_server.name if dhcp_server else "DHCPServer1"

        # 1. DISCOVER
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=100,
                type="DHCP_DISCOVER",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id="PKT-DHCP-DISC",
                message=f"{src_node.name} broadcast DHCP Discover (0.0.0.0 -> 255.255.255.255).",
                explanation=f"{src_node.name} has no IP address. It broadcasts a DHCP Discover frame across the local broadcast domain asking any available DHCP server for a lease.",
                why_reason="DHCP Discover is broadcast at Layer 2 (FF:FF:FF:FF:FF:FF) and Layer 3 (255.255.255.255) so any local DHCP server can hear it.",
                cyber_relevance="Rogue DHCP servers can reply to Discovers to conduct man-in-the-middle attacks by supplying themselves as the default gateway.",
                severity="INFO",
            )
        )

        # 2. OFFER
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=300,
                type="DHCP_OFFER",
                device_id=dhcp_server.id if dhcp_server else "dhcp-server",
                device_name=server_name,
                packet_id="PKT-DHCP-OFFER",
                message=f"{server_name} replied with DHCP Offer: IP {offered_ip}.",
                explanation=f"{server_name} inspected its address pool and offered IP {offered_ip}, Subnet Mask {offered_mask}, Gateway {offered_gw}, and DNS {offered_dns}.",
                why_reason="The server reserves the offered address temporarily so other clients do not claim the same IP.",
                cyber_relevance="DHCP starvation attacks exhaust pools with fake MAC addresses to force network outage.",
                severity="SUCCESS",
            )
        )

        # 3. REQUEST
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=500,
                type="DHCP_REQUEST",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id="PKT-DHCP-REQ",
                message=f"{src_node.name} sent DHCP Request formally accepting {offered_ip}.",
                explanation=f"{src_node.name} broadcasts a DHCP Request stating it accepts the offer from {server_name}.",
                why_reason="The request is broadcast so other DHCP servers know their offers were declined and can release reserved IPs back to their pools.",
                cyber_relevance="DHCP snooping on managed switches validates requests against trusted server ports to prevent spoofing.",
                severity="INFO",
            )
        )

        # 4. ACK
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=700,
                type="DHCP_ACK",
                device_id=dhcp_server.id if dhcp_server else "dhcp-server",
                device_name=server_name,
                packet_id="PKT-DHCP-ACK",
                message=f"{server_name} confirmed lease with DHCP ACK. Interface configured!",
                explanation=f"{server_name} commits the lease. {src_node.name} applies IP {offered_ip}/24, Gateway {offered_gw}, and DNS {offered_dns} to {src_iface.name}.",
                why_reason="DHCP ACK finalizes the DORA process, binding the MAC address to the IP address in the server's lease database.",
                cyber_relevance="DHCP lease history in network logs helps incident responders attribute malicious activity to physical devices.",
                severity="SUCCESS",
            )
        )

        # Update interface in memory for return
        src_iface.ipv4_address = offered_ip
        src_iface.subnet_mask = offered_mask
        src_iface.default_gateway = offered_gw

        return SimulationResultResponse(
            success=True,
            summary=f"DHCP DORA completed: {src_node.name} successfully leased {offered_ip} from {server_name}.",
            events=events,
            hops=hops,
        )

    # -----------------------------------------------------------------------
    # Path Traversal & Device Forwarding Logic
    # -----------------------------------------------------------------------

    def _traverse_path(
        self,
        packet: SimulatedPacketSchema,
        curr_node: SimDeviceSchema,
        ingress_iface: DeviceInterfaceSchema | None,
        dst_ip: str,
        node_map: dict[str, SimDeviceSchema],
        link_map: dict[str, list[dict[str, Any]]],
        events: list[SimulationEventSchema],
        hops: list[HopRecordSchema],
        mac_updates: dict[str, list[MacEntrySchema]],
        start_hop: int,
        timestamp: int,
    ) -> dict[str, Any]:
        """Traverse packet hop-by-hop through connected links, switches, routers, and firewalls."""
        visited: set[str] = set()
        active_node = curr_node
        in_iface = ingress_iface
        hop_num = start_hop

        while hop_num < 25:  # Maximum hops safeguard
            visited.add(active_node.id)

            # Record Hop
            snap = packet.model_copy(deep=True)
            hops.append(
                HopRecordSchema(
                    hop_number=hop_num,
                    device_id=active_node.id,
                    device_name=active_node.name,
                    device_type=active_node.type,
                    ingress_interface=in_iface.name if in_iface else None,
                    egress_interface=None,
                    action="PROCESSING",
                    packet_snapshot=snap,
                    layer_operations={"L2": f"Frame MAC: {packet.source_mac} -> {packet.destination_mac}", "L3": f"Packet IP: {packet.source_ip} -> {packet.destination_ip} (TTL={packet.ttl})"},
                    explanation=f"{active_node.name} received packet from ingress {in_iface.name if in_iface else 'Local'}.",
                    why_reason="Each intermediate node decapsulates and evaluates the frame according to its network layer.",
                    cyber_relevance="Hops represent network telemetry collection points (NetFlow, mirror ports, firewall logs).",
                )
            )

            # Destination check: Is this the destination?
            for iface in active_node.interfaces:
                if iface.ipv4_address == dst_ip:
                    hops[-1].action = "DELIVERED"
                    return {
                        "delivered": True,
                        "delivered_to": active_node,
                        "delivered_iface": iface,
                    }

            # Device-Specific Forwarding Behavior
            node_type = active_node.type.upper()

            if node_type == "SWITCH":
                fwd_res = self._process_switch(
                    switch_node=active_node,
                    in_iface=in_iface,
                    packet=packet,
                    link_map=link_map,
                    node_map=node_map,
                    events=events,
                    mac_updates=mac_updates,
                    timestamp=timestamp,
                )
                if not fwd_res["success"]:
                    return {"delivered": False, "reason": fwd_res["reason"]}
                active_node = fwd_res["next_node"]
                in_iface = fwd_res["next_iface"]
                hops[-1].egress_interface = fwd_res["egress_iface_name"]

            elif node_type in ("ROUTER", "FIREWALL"):
                # TTL Decrement
                packet.ttl -= 1
                if packet.ttl <= 0:
                    events.append(
                        SimulationEventSchema(
                            id=str(uuid.uuid4())[:8],
                            timestamp_ms=timestamp,
                            type="PACKET_DROPPED",
                            device_id=active_node.id,
                            device_name=active_node.name,
                            packet_id=packet.id,
                            message=f"TTL expired on {active_node.name} (TTL=0). Packet dropped.",
                            explanation=f"{active_node.name} decremented the IPv4 Time-To-Live to 0, triggering an ICMP Time Exceeded drop.",
                            why_reason="The TTL field prevents packets from circulating indefinitely during routing loops.",
                            cyber_relevance="Traceroute deliberately utilizes incrementing TTLs to map network paths.",
                            severity="ERROR",
                        )
                    )
                    return {"delivered": False, "reason": "TTL expired in transit (possible routing loop)."}

                # Firewall Inspection if FIREWALL
                if node_type == "FIREWALL" or active_node.configuration.firewall_rules:
                    fw_res = self._evaluate_firewall(active_node, packet, events, timestamp)
                    if not fw_res["allow"]:
                        return {"delivered": False, "reason": fw_res["reason"]}

                # Routing Table Lookup (LPM)
                route_res = self._process_router(
                    router_node=active_node,
                    packet=packet,
                    dst_ip=dst_ip,
                    link_map=link_map,
                    node_map=node_map,
                    events=events,
                    timestamp=timestamp,
                )
                if not route_res["success"]:
                    return {"delivered": False, "reason": route_res["reason"]}

                active_node = route_res["next_node"]
                in_iface = route_res["next_iface"]
                hops[-1].egress_interface = route_res["egress_iface_name"]

            elif node_type in ("PC", "LAPTOP", "SERVER"):
                # End host forwarding (gateway forwarding)
                egress = self._get_egress_link_for_host(active_node, link_map, node_map)
                if not egress:
                    return {"delivered": False, "reason": f"Device '{active_node.name}' has no active link connected."}
                active_node = egress["next_node"]
                in_iface = egress["next_iface"]
                hops[-1].egress_interface = egress["egress_iface_name"]

            else:
                return {"delivered": False, "reason": f"Unknown device type '{node_type}'."}

            hop_num += 1
            timestamp += 100

        return {"delivered": False, "reason": "Hop limit exceeded (25 hops). Check topology for loops."}

    def _process_switch(
        self,
        switch_node: SimDeviceSchema,
        in_iface: DeviceInterfaceSchema | None,
        packet: SimulatedPacketSchema,
        link_map: dict[str, list[dict[str, Any]]],
        node_map: dict[str, SimDeviceSchema],
        events: list[SimulationEventSchema],
        mac_updates: dict[str, list[MacEntrySchema]],
        timestamp: int,
    ) -> dict[str, Any]:
        """Learn source MAC address and forward frame out matching VLAN port or flood."""
        in_name = in_iface.name if in_iface else "Port 1"

        # 1. Learn Source MAC
        mac_tbl = switch_node.configuration.mac_table
        found = False
        for entry in mac_tbl:
            if entry.mac_address == packet.source_mac:
                entry.port = in_name
                found = True
                break
        if not found:
            mac_tbl.append(
                MacEntrySchema(
                    mac_address=packet.source_mac,
                    port=in_name,
                    vlan_id=in_iface.vlan_id if in_iface else 1,
                    age=0,
                )
            )
        mac_updates[switch_node.id] = mac_tbl

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp,
                type="FRAME_RECEIVED",
                device_id=switch_node.id,
                device_name=switch_node.name,
                packet_id=packet.id,
                message=f"{switch_node.name} learned MAC {packet.source_mac} on {in_name}.",
                explanation=f"{switch_node.name} inspects the source MAC header and updates its CAM (Content Addressable Memory) table.",
                why_reason="Switches dynamically populate their forwarding database by inspecting incoming source MACs.",
                cyber_relevance="MAC flooding attacks flood random source MACs to overflow the CAM table and force the switch into hub-like fail-open mode.",
                severity="INFO",
            )
        )

        # 2. Lookup Destination MAC
        links = link_map.get(switch_node.id, [])
        if not links:
            return {"success": False, "reason": f"Switch '{switch_node.name}' has no active links connected."}

        # Filter out ingress link
        possible_egress = [
            l for l in links if not (in_iface and l["local_interface_id"] == in_iface.id)
        ]

        if not possible_egress:
            return {"success": False, "reason": f"Switch '{switch_node.name}' has no other ports to forward the frame."}

        # VLAN Check: Filter by VLAN
        current_vlan = in_iface.vlan_id if in_iface else 1
        vlan_compatible = []
        for l in possible_egress:
            local_iface = self._find_iface_by_id(switch_node, l["local_interface_id"])
            if local_iface and (local_iface.vlan_id == current_vlan or local_iface.vlan_id == 1):
                vlan_compatible.append((l, local_iface))

        if not vlan_compatible:
            events.append(
                SimulationEventSchema(
                    id=str(uuid.uuid4())[:8],
                    timestamp_ms=timestamp + 50,
                    type="PACKET_DROPPED",
                    device_id=switch_node.id,
                    device_name=switch_node.name,
                    packet_id=packet.id,
                    message=f"{switch_node.name} dropped frame: Isolated by VLAN {current_vlan}.",
                    explanation=f"No other ports on {switch_node.name} belong to VLAN {current_vlan}. Traffic cannot bridge between distinct VLANs without a Layer 3 router.",
                    why_reason="VLANs logically segment a physical switch into isolated Layer-2 broadcast domains.",
                    cyber_relevance="VLAN segmentation prevents lateral movement by attackers between sensitive network tiers.",
                    severity="WARNING",
                )
            )
            return {"success": False, "reason": f"VLAN isolation: No matching ports in VLAN {current_vlan}."}

        # Select egress port
        target_link, target_local_iface = vlan_compatible[0]
        for l, ifc in vlan_compatible:
            remote_node = node_map.get(l["remote_node_id"])
            # Prefer path toward destination
            if remote_node and (remote_node.type in ("ROUTER", "FIREWALL") or any(i.ipv4_address == packet.destination_ip for i in remote_node.interfaces)):
                target_link = l
                target_local_iface = ifc
                break

        remote_node = node_map.get(target_link["remote_node_id"])
        remote_iface = self._find_iface_by_id(remote_node, target_link["remote_interface_id"])

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 80,
                type="FRAME_FORWARDED",
                device_id=switch_node.id,
                device_name=switch_node.name,
                packet_id=packet.id,
                message=f"{switch_node.name} forwarded frame via {target_local_iface.name} to {remote_node.name}.",
                explanation=f"{switch_node.name} switched the Ethernet frame out {target_local_iface.name} based on its destination MAC / VLAN table.",
                why_reason="Layer 2 switching operates at wire-speed without rewriting IP headers or MAC addresses.",
                cyber_relevance="Port security features on switches restrict authorized MAC addresses per port to prevent rogue device attachment.",
                severity="INFO",
            )
        )

        return {
            "success": True,
            "next_node": remote_node,
            "next_iface": remote_iface,
            "egress_iface_name": target_local_iface.name,
        }

    def _process_router(
        self,
        router_node: SimDeviceSchema,
        packet: SimulatedPacketSchema,
        dst_ip: str,
        link_map: dict[str, list[dict[str, Any]]],
        node_map: dict[str, SimDeviceSchema],
        events: list[SimulationEventSchema],
        timestamp: int,
    ) -> dict[str, Any]:
        """Perform Longest Prefix Match (LPM) route lookup and Layer 2 header rewrite."""
        routes = router_node.configuration.routing_table

        # Built-in direct routes for all active interfaces
        best_route = None
        longest_prefix = -1

        dest_addr = ipaddress.IPv4Address(dst_ip)

        # 1. Evaluate configured static routes
        for r in routes:
            try:
                dest_str = "0.0.0.0" if r.destination in ("0.0.0.0", "default") else r.destination
                prefix = mask_to_cidr(r.netmask)
                net = ipaddress.IPv4Network(f"{dest_str}/{prefix}", strict=False)
                if dest_addr in net and prefix > longest_prefix:
                    best_route = r
                    longest_prefix = prefix
            except (ValueError, ipaddress.AddressValueError):
                continue

        # 2. Check directly connected interface subnets
        direct_iface = None
        for iface in router_node.interfaces:
            if iface.ipv4_address and iface.subnet_mask:
                try:
                    p = mask_to_cidr(iface.subnet_mask)
                    net = ipaddress.IPv4Network(f"{iface.ipv4_address}/{p}", strict=False)
                    if dest_addr in net and p > longest_prefix:
                        best_route = None
                        longest_prefix = p
                        direct_iface = iface
                except (ValueError, ipaddress.AddressValueError):
                    continue

        if longest_prefix == -1:
            events.append(
                SimulationEventSchema(
                    id=str(uuid.uuid4())[:8],
                    timestamp_ms=timestamp,
                    type="ROUTE_FAILURE",
                    device_id=router_node.id,
                    device_name=router_node.name,
                    packet_id=packet.id,
                    message=f"No route to destination {dst_ip} on {router_node.name}. Packet dropped.",
                    explanation=f"{router_node.name} evaluated its routing table but found no matching static route, direct subnet, or default gateway (0.0.0.0/0).",
                    why_reason="Routers drop unroutable packets and optionally return ICMP Type 3 Code 0 (Destination Network Unreachable).",
                    cyber_relevance="Missing routes create 'black holes' where traffic vanishes silently without reaching its destination.",
                    severity="ERROR",
                )
            )
            return {"success": False, "reason": f"Router '{router_node.name}' has no route to network {dst_ip}."}

        # Identify egress interface
        egress_iface = direct_iface
        if not egress_iface and best_route:
            for ifc in router_node.interfaces:
                if ifc.name == best_route.interface:
                    egress_iface = ifc
                    break

        if not egress_iface and router_node.interfaces:
            egress_iface = router_node.interfaces[-1]

        # Find connected remote node on this interface
        links = link_map.get(router_node.id, [])
        egress_link = None
        for l in links:
            if egress_iface and l["local_interface_id"] == egress_iface.id:
                egress_link = l
                break

        if not egress_link and links:
            egress_link = links[0]

        if not egress_link:
            return {"success": False, "reason": f"Router '{router_node.name}' egress interface '{egress_iface.name if egress_iface else 'eth1'}' is disconnected."}

        remote_node = node_map.get(egress_link["remote_node_id"])
        remote_iface = self._find_iface_by_id(remote_node, egress_link["remote_interface_id"])

        # Layer 2 MAC address rewrite by router
        packet.source_mac = egress_iface.mac_address if egress_iface else "02:00:05:01:00:01"
        packet.destination_mac = remote_iface.mac_address if remote_iface else "02:00:FF:FF:FF:01"

        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 50,
                type="ROUTE_MATCH",
                device_id=router_node.id,
                device_name=router_node.name,
                packet_id=packet.id,
                message=f"{router_node.name} routed packet via {egress_iface.name if egress_iface else 'eth1'} (Prefix length: /{longest_prefix}).",
                explanation=f"{router_node.name} selected the longest matching prefix (/{longest_prefix}), decremented TTL to {packet.ttl}, and rewrote the Layer 2 Ethernet source MAC to its own egress interface.",
                why_reason="Routers operate at Layer 3: they strip incoming L2 headers and encapsulate the packet in fresh L2 headers for the next hop.",
                cyber_relevance="Observing MAC address rewrites in packet forensics distinguishes local intranet traffic from routed WAN traffic.",
                severity="INFO",
            )
        )

        return {
            "success": True,
            "next_node": remote_node,
            "next_iface": remote_iface,
            "egress_iface_name": egress_iface.name if egress_iface else "eth1",
        }

    def _evaluate_firewall(
        self,
        fw_node: SimDeviceSchema,
        packet: SimulatedPacketSchema,
        events: list[SimulationEventSchema],
        timestamp: int,
    ) -> dict[str, Any]:
        """Evaluate stateless firewall rules in sequential order."""
        rules = fw_node.configuration.firewall_rules
        if not rules:
            return {"allow": True}

        for rule in rules:
            # Check protocol
            if rule.protocol != "ANY" and rule.protocol.upper() != packet.protocol.upper():
                continue

            # Check port (if applicable)
            if rule.port != "ANY" and rule.port is not None:
                packet_port = packet.l3_payload.get("dst_port") or packet.l3_payload.get("port")
                if packet_port and str(packet_port) != str(rule.port):
                    continue

            action = rule.action.upper()
            if action == "DENY":
                events.append(
                    SimulationEventSchema(
                        id=str(uuid.uuid4())[:8],
                        timestamp_ms=timestamp,
                        type="FIREWALL_DENY",
                        device_id=fw_node.id,
                        device_name=fw_node.name,
                        packet_id=packet.id,
                        message=f"{fw_node.name} blocked packet matching rule '{rule.id or 'DENY'}'.",
                        explanation=f"Traffic matching protocol {packet.protocol} was denied by policy rule: '{rule.description or rule.action}'.",
                        why_reason="Firewalls enforce organizational security policy by filtering traffic according to defined Access Control Lists (ACLs).",
                        cyber_relevance="Firewall deny logs alert SOC teams to unauthorized network traversal attempts and port scans.",
                        severity="ERROR",
                    )
                )
                return {"allow": False, "reason": f"Blocked by firewall '{fw_node.name}' rule: {rule.action} {rule.protocol}."}
            else:
                events.append(
                    SimulationEventSchema(
                        id=str(uuid.uuid4())[:8],
                        timestamp_ms=timestamp,
                        type="FIREWALL_ALLOW",
                        device_id=fw_node.id,
                        device_name=fw_node.name,
                        packet_id=packet.id,
                        message=f"{fw_node.name} permitted packet matching rule '{rule.id or 'ALLOW'}'.",
                        explanation=f"Traffic passed firewall inspection according to rule '{rule.description or 'ALLOW'}'.",
                        why_reason="Traffic matching permit rules is forwarded without modification.",
                        cyber_relevance="Firewall rules follow the principle of least privilege: deny all by default, explicitly allow required business protocols.",
                        severity="INFO",
                    )
                )
                return {"allow": True}

        return {"allow": True}

    def _resolve_arp(
        self,
        src_node: SimDeviceSchema,
        src_iface: DeviceInterfaceSchema,
        target_ip: str,
        node_map: dict[str, SimDeviceSchema],
        link_map: dict[str, list[dict[str, Any]]],
        events: list[SimulationEventSchema],
        arp_updates: dict[str, list[ArpEntrySchema]],
        mac_updates: dict[str, list[MacEntrySchema]],
        timestamp: int,
    ) -> str | None:
        """Simulate ARP resolution: Check local cache, then broadcast Request and receive Reply."""
        # 1. Check local ARP cache
        for entry in src_node.configuration.arp_table:
            if entry.ip_address == target_ip:
                return entry.mac_address

        # 2. Locate target device in topology
        target_node = None
        target_iface = None
        for n in node_map.values():
            for ifc in n.interfaces:
                if ifc.ipv4_address == target_ip:
                    target_node = n
                    target_iface = ifc
                    break
            if target_node:
                break

        if not target_node or not target_iface:
            return None

        # 3. Simulate ARP broadcast event
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 10,
                type="ARP_REQUEST",
                device_id=src_node.id,
                device_name=src_node.name,
                packet_id=f"ARP-REQ-{uuid.uuid4().hex[:4].upper()}",
                message=f"{src_node.name} broadcast ARP Request: Who has {target_ip}? Tell {src_iface.ipv4_address}.",
                explanation=f"{src_node.name} has an IP packet ready to send but does not know the Layer 2 hardware address for {target_ip}. It broadcasts an ARP Request (FF:FF:FF:FF:FF:FF).",
                why_reason="IP packets cannot traverse physical Ethernet links without the destination MAC address.",
                cyber_relevance="ARP has no authentication. Threat actors exploit this via ARP Poisoning/Spoofing to intercept network traffic.",
                severity="INFO",
            )
        )

        # 4. Simulate ARP unicast reply event
        events.append(
            SimulationEventSchema(
                id=str(uuid.uuid4())[:8],
                timestamp_ms=timestamp + 50,
                type="ARP_REPLY",
                device_id=target_node.id,
                device_name=target_node.name,
                packet_id=f"ARP-REP-{uuid.uuid4().hex[:4].upper()}",
                message=f"{target_node.name} unicast ARP Reply: {target_ip} is at {target_iface.mac_address}.",
                explanation=f"{target_node.name} recognizes its own IP in the ARP Request, updates its own ARP table with {src_node.name}'s mapping, and returns a unicast ARP Reply.",
                why_reason="Only the device owning the requested IP address formulates the ARP Reply.",
                cyber_relevance="Dynamic ARP Inspection (DAI) on switches drops invalid ARP replies that do not match DHCP bindings.",
                severity="SUCCESS",
            )
        )

        # 5. Populate ARP caches
        src_node.configuration.arp_table.append(
            ArpEntrySchema(ip_address=target_ip, mac_address=target_iface.mac_address, interface=src_iface.name)
        )
        arp_updates[src_node.id] = src_node.configuration.arp_table

        return target_iface.mac_address

    # -----------------------------------------------------------------------
    # Topology Helpers
    # -----------------------------------------------------------------------

    def _build_link_map(self, topology: TopologyDataSchema) -> dict[str, list[dict[str, Any]]]:
        """Build bidirectional link adjacency map for fast graph traversal."""
        adj: dict[str, list[dict[str, Any]]] = {}
        for l in topology.links:
            if l.status.lower() != "up":
                continue
            # Source -> Target
            adj.setdefault(l.source_node_id, []).append({
                "local_interface_id": l.source_interface_id,
                "remote_node_id": l.target_node_id,
                "remote_interface_id": l.target_interface_id,
            })
            # Target -> Source
            adj.setdefault(l.target_node_id, []).append({
                "local_interface_id": l.target_interface_id,
                "remote_node_id": l.source_node_id,
                "remote_interface_id": l.source_interface_id,
            })
        return adj

    def _get_active_interface(self, node: SimDeviceSchema) -> DeviceInterfaceSchema | None:
        """Get first operational interface with an IPv4 address."""
        for ifc in node.interfaces:
            if ifc.status.lower() == "up" and ifc.ipv4_address:
                return ifc
        return node.interfaces[0] if node.interfaces else None

    def _find_iface_by_id(self, node: SimDeviceSchema | None, iface_id: str) -> DeviceInterfaceSchema | None:
        """Find an interface on a node by its unique ID."""
        if not node:
            return None
        for ifc in node.interfaces:
            if ifc.id == iface_id:
                return ifc
        return None

    def _get_egress_link_for_host(
        self,
        host_node: SimDeviceSchema,
        link_map: dict[str, list[dict[str, Any]]],
        node_map: dict[str, SimDeviceSchema],
    ) -> dict[str, Any] | None:
        """Get connected remote node and interface for a single-homed host."""
        links = link_map.get(host_node.id, [])
        if not links:
            return None
        l = links[0]
        remote = node_map.get(l["remote_node_id"])
        if not remote:
            return None
        local_iface = self._find_iface_by_id(host_node, l["local_interface_id"])
        remote_iface = self._find_iface_by_id(remote, l["remote_interface_id"])
        return {
            "next_node": remote,
            "next_iface": remote_iface,
            "egress_iface_name": local_iface.name if local_iface else "eth0",
        }

    def _resolve_destination(
        self,
        request: SimulatePacketRequest,
        src_node: SimDeviceSchema,
        node_map: dict[str, SimDeviceSchema],
    ) -> tuple[SimDeviceSchema | None, str | None, DeviceInterfaceSchema | None]:
        """Resolve destination node and IP from simulation request."""
        # 1. Direct device ID lookup
        if request.destination_device_id and request.destination_device_id in node_map:
            dst_node = node_map[request.destination_device_id]
            dst_iface = self._get_active_interface(dst_node)
            dst_ip = dst_iface.ipv4_address if dst_iface else None
            return dst_node, dst_ip, dst_iface

        # 2. Destination IP lookup
        if request.destination_ip:
            dst_ip = request.destination_ip.strip()
            for n in node_map.values():
                for ifc in n.interfaces:
                    if ifc.ipv4_address == dst_ip:
                        return n, dst_ip, ifc
            return None, dst_ip, None

        return None, None, None


simulation_engine = SimulationEngine()
