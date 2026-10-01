"""Rule-based pattern observation service for educational traffic analysis and SOC investigation.

Generates neutral, evidence-backed observations without prematurely declaring confirmed attacks.
"""

import json
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.enums import ObservationSeverity, ObservationType
from app.models.pcap import ParsedPacket
from app.schemas.pcap import ObservationResponse


class PacketObservationService:
    """Analyzes normalized packet streams for noteworthy patterns and investigation evidence."""

    def analyze_observations(self, db: Session, capture_id: int) -> list[ObservationResponse]:
        """Evaluate deterministic observation rules against captured packets."""
        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture_id)
            .order_by(ParsedPacket.packet_number.asc())
            .all()
        )

        observations: list[ObservationResponse] = []
        if not packets:
            return observations

        # 1. Evaluate SYN connection pattern
        syn_packets_by_src: dict[str, list[int]] = defaultdict(list)
        rst_packets: list[int] = []
        nxdomain_packets: list[int] = []
        dns_total = 0
        ip_mac_history: dict[str, set[str]] = defaultdict(set)
        unusual_port_packets: list[int] = []
        connection_attempts: dict[tuple[str, str, int], list[int]] = defaultdict(list)

        for pkt in packets:
            flags: list[str] = []
            if pkt.tcp_flags:
                try:
                    flags = json.loads(pkt.tcp_flags)
                except (json.JSONDecodeError, TypeError):
                    flags = []

            # SYN tracking
            if "SYN" in flags and "ACK" not in flags and pkt.source_ip:
                syn_packets_by_src[pkt.source_ip].append(pkt.packet_number)
                if pkt.destination_ip and pkt.destination_port:
                    connection_attempts[(pkt.source_ip, pkt.destination_ip, pkt.destination_port)].append(pkt.packet_number)

            # RST tracking
            if "RST" in flags:
                rst_packets.append(pkt.packet_number)

            # DNS NXDOMAIN tracking
            if pkt.protocol == "DNS":
                dns_total += 1
                if "rcode=3" in pkt.info.lower() or "nxdomain" in pkt.info.lower():
                    nxdomain_packets.append(pkt.packet_number)

            # ARP mapping tracking
            if pkt.protocol == "ARP" and pkt.source_ip and pkt.source_mac:
                ip_mac_history[pkt.source_ip].add(pkt.source_mac)

            # Unusual port usage (e.g. classical backdoor/test ports)
            if pkt.destination_port in {1337, 31337, 4444, 5555, 6667, 9001, 8888}:
                unusual_port_packets.append(pkt.packet_number)

        # Rule 1: High SYN Rate / Connection Pattern
        for src_ip, pnums in syn_packets_by_src.items():
            if len(pnums) >= 5:
                observations.append(
                    ObservationResponse(
                        id=f"obs-syn-{src_ip}",
                        type=ObservationType.HIGH_SYN_RATE,
                        severity=ObservationSeverity.LOW,
                        title=f"Noteworthy TCP Connection Pattern from {src_ip}",
                        description=(
                            f"Host {src_ip} initiated {len(pnums)} TCP SYN requests across the capture. "
                            "Multiple connection attempts without completed sessions were observed."
                        ),
                        why_it_matters=(
                            "In SOC investigations, frequent one-way SYN packets can indicate network discovery, "
                            "port scanning, connection timeouts, or service unreachability."
                        ),
                        cyber_relevance=(
                            "Port scanners and SYN flood attempts often generate high volumes of SYN requests without "
                            "completing the 3-way handshake."
                        ),
                        evidence_packets=pnums[:20],
                    )
                )

        # Rule 2: Many TCP Resets
        if len(rst_packets) >= 3:
            observations.append(
                ObservationResponse(
                    id="obs-rst-spike",
                    type=ObservationType.MANY_TCP_RESETS,
                    severity=ObservationSeverity.LOW,
                    title="Multiple TCP Reset (RST) Events Observed",
                    description=(
                        f"A total of {len(rst_packets)} TCP RST packets were observed in the capture. "
                        "Target ports rejected incoming connection attempts."
                    ),
                    why_it_matters=(
                        "TCP RST indicates that a destination endpoint closed or rejected a connection. "
                        "The capture alone records the rejection, though server configuration or firewall filters may be responsible."
                    ),
                    cyber_relevance=(
                        "Reconnaissance sweeps often trigger bursts of RST responses when probing closed ports."
                    ),
                    evidence_packets=rst_packets[:20],
                )
            )

        # Rule 3: DNS NXDOMAIN Spike
        if len(nxdomain_packets) >= 2:
            observations.append(
                ObservationResponse(
                    id="obs-dns-nxdomain",
                    type=ObservationType.DNS_NXDOMAIN_SPIKE,
                    severity=ObservationSeverity.LOW,
                    title="Repeated DNS Non-Existent Domain (NXDOMAIN) Responses",
                    description=(
                        f"Observed {len(nxdomain_packets)} NXDOMAIN responses out of {dns_total} DNS queries. "
                        "Clients queried hostnames that could not be resolved."
                    ),
                    why_it_matters=(
                        "Unsuccessful DNS queries can be caused by typos, decommissioned servers, or "
                        "automated algorithmic domain generation."
                    ),
                    cyber_relevance=(
                        "Malware using Domain Generation Algorithms (DGA) frequently produces high NXDOMAIN rates "
                        "when searching for active Command and Control (C2) servers."
                    ),
                    evidence_packets=nxdomain_packets[:20],
                )
            )

        # Rule 4: ARP Mapping Change
        for ip_addr, mac_set in ip_mac_history.items():
            if len(mac_set) > 1:
                arp_evidence = [p.packet_number for p in packets if p.protocol == "ARP" and p.source_ip == ip_addr]
                observations.append(
                    ObservationResponse(
                        id=f"obs-arp-{ip_addr}",
                        type=ObservationType.ARP_MAPPING_CHANGE,
                        severity=ObservationSeverity.MEDIUM,
                        title=f"Noteworthy ARP Mapping Change for {ip_addr}",
                        description=(
                            f"IP address {ip_addr} was claimed by multiple distinct MAC addresses: "
                            f"{', '.join(mac_set)}."
                        ),
                        why_it_matters=(
                            "An IP-to-MAC association changed during the capture. This warrants investigation to determine "
                            "if network renumbering, hardware replacement, or unauthorized ARP responses occurred."
                        ),
                        cyber_relevance=(
                            "Gratuitous ARP spoofing or Man-in-the-Middle (MITM) attacks cause sudden ARP cache poisoning "
                            "where an attacker MAC redirects victim gateway traffic."
                        ),
                        evidence_packets=arp_evidence[:20],
                    )
                )

        # Rule 5: Unusual Port Usage
        if unusual_port_packets:
            observations.append(
                ObservationResponse(
                    id="obs-unusual-port",
                    type=ObservationType.UNUSUAL_PORT_USAGE,
                    severity=ObservationSeverity.LOW,
                    title="Traffic Observed on Non-Standard Application Ports",
                    description=(
                        f"Detected {len(unusual_port_packets)} packets targeting uncommon transport ports "
                        "outside standard IANA web and infrastructure ranges."
                    ),
                    why_it_matters=(
                        "Traffic on non-standard ports may represent custom development services, peer-to-peer "
                        "transfers, or unapproved network communications."
                    ),
                    cyber_relevance=(
                        "Adversaries frequently bind reverse shells or secondary listeners to arbitrary high ports."
                    ),
                    evidence_packets=unusual_port_packets[:20],
                )
            )

        # Rule 6: Repeated Connection Attempts to Same Target
        for (src, dst, dport), pnums in connection_attempts.items():
            if len(pnums) >= 4:
                observations.append(
                    ObservationResponse(
                        id=f"obs-reconnect-{src}-{dst}-{dport}",
                        type=ObservationType.REPEATED_CONNECTION_ATTEMPTS,
                        severity=ObservationSeverity.INFO,
                        title=f"Repeated Connection Attempts from {src} to {dst}:{dport}",
                        description=(
                            f"Host {src} sent {len(pnums)} consecutive connection attempts to {dst} on port {dport}."
                        ),
                        why_it_matters=(
                            "Repeated attempts can indicate application retry loops or persistent communication attempts."
                        ),
                        cyber_relevance=(
                            "Automated brute-force tools and beaconing agents periodically retry target connections."
                        ),
                        evidence_packets=pnums[:20],
                    )
                )

        return observations


packet_observation_service = PacketObservationService()
