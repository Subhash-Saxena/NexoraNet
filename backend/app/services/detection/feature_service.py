"""Feature extraction and telemetry normalization service for the Step 11 Detection Engine.

Normalizes raw packet streams from PCAPs or simulator event histories into
uniform telemetry structures, flow aggregations, and host profile metrics.
"""

import json
import math
from dataclasses import dataclass, field
from typing import Any

from app.models.pcap import ParsedPacket


@dataclass
class NormalizedEvent:
    """Standardized event abstraction across PCAP packets and simulator timeline items."""

    packet_id: int | None = None
    packet_number: int = 0
    timestamp: float = 0.0
    relative_time: float = 0.0
    protocol: str = "OTHER"
    transport_protocol: str | None = None
    application_protocol: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    source_port: int | None = None
    destination_port: int | None = None
    source_mac: str | None = None
    destination_mac: str | None = None
    tcp_flags: list[str] = field(default_factory=list)
    dns_qname: str | None = None
    dns_rcode: int | None = None
    dns_qr: str | None = None  # "Query" or "Response"
    dns_qtype: str | None = None
    http_status_code: int | None = None
    http_method: str | None = None
    http_uri: str | None = None
    icmp_type: int | None = None
    icmp_code: int | None = None
    length: int = 0
    info: str = ""
    raw_details: dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowAggregation:
    """Aggregated unidirectional or session flow metrics."""

    flow_key: tuple[str | None, str | None, int | None, str]
    source_ip: str | None
    destination_ip: str | None
    destination_port: int | None
    protocol: str
    events: list[NormalizedEvent] = field(default_factory=list)
    packet_count: int = 0
    byte_count: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    syn_count: int = 0
    syn_ack_count: int = 0
    ack_count: int = 0
    rst_count: int = 0
    handshake_complete: bool = False
    inter_arrival_times: list[float] = field(default_factory=list)
    mean_inter_arrival: float = 0.0
    std_inter_arrival: float = 0.0
    relative_std_dev: float = 1.0


@dataclass
class HostProfile:
    """Host-centric aggregations for anomalous endpoint detection."""

    ip: str
    events: list[NormalizedEvent] = field(default_factory=list)
    distinct_destinations: set[str] = field(default_factory=set)
    distinct_destination_ports: set[int] = field(default_factory=set)
    arp_macs: set[str] = field(default_factory=set)
    dns_queries: list[NormalizedEvent] = field(default_factory=list)
    dns_nxdomains: list[NormalizedEvent] = field(default_factory=list)
    subdomains_by_base_domain: dict[str, set[str]] = field(default_factory=dict)
    icmp_requests: list[NormalizedEvent] = field(default_factory=list)
    http_errors: list[NormalizedEvent] = field(default_factory=list)
    syn_count: int = 0
    handshake_completed_count: int = 0


class FeatureExtractionService:
    """Extracts analytical features, flows, and host metrics from normalized packets."""

    def normalize_parsed_packet(self, pkt: ParsedPacket) -> NormalizedEvent:
        """Convert a ParsedPacket DB model instance into a NormalizedEvent."""
        flags: list[str] = []
        if pkt.tcp_flags:
            try:
                parsed_flags = json.loads(pkt.tcp_flags)
                if isinstance(parsed_flags, list):
                    flags = [str(f).upper() for f in parsed_flags]
            except (json.JSONDecodeError, TypeError, ValueError):
                flags = []

        layer_details: dict[str, Any] = {}
        if pkt.layer_details:
            try:
                layer_details = json.loads(pkt.layer_details)
            except (json.JSONDecodeError, TypeError, ValueError):
                layer_details = {}

        dns_qname = None
        dns_rcode = None
        dns_qr = None
        dns_qtype = None
        if "DNS" in layer_details:
            dns_info = layer_details["DNS"]
            dns_qname = dns_info.get("qname")
            dns_rcode = dns_info.get("rcode")
            dns_qr = dns_info.get("qr")
            dns_qtype = dns_info.get("qtype")

        http_status_code = None
        http_method = None
        http_uri = None
        if "HTTP" in layer_details:
            http_info = layer_details["HTTP"]
            http_status_code = http_info.get("status_code")
            http_method = http_info.get("method")
            http_uri = http_info.get("uri")

        icmp_type = None
        icmp_code = None
        if "ICMP" in layer_details:
            icmp_info = layer_details["ICMP"]
            icmp_type = icmp_info.get("type")
            icmp_code = icmp_info.get("code")

        # ARP information
        if "ARP" in layer_details:
            arp_info = layer_details["ARP"]
            if not pkt.source_ip and arp_info.get("sender_ip"):
                pkt_src_ip = arp_info.get("sender_ip")
            else:
                pkt_src_ip = pkt.source_ip
            if not pkt.source_mac and arp_info.get("sender_mac"):
                pkt_src_mac = arp_info.get("sender_mac")
            else:
                pkt_src_mac = pkt.source_mac
        else:
            pkt_src_ip = pkt.source_ip
            pkt_src_mac = pkt.source_mac

        return NormalizedEvent(
            packet_id=pkt.id,
            packet_number=pkt.packet_number,
            timestamp=pkt.timestamp,
            relative_time=pkt.relative_time,
            protocol=pkt.protocol,
            transport_protocol=pkt.transport_protocol,
            application_protocol=pkt.application_protocol,
            source_ip=pkt_src_ip,
            destination_ip=pkt.destination_ip,
            source_port=pkt.source_port,
            destination_port=pkt.destination_port,
            source_mac=pkt_src_mac,
            destination_mac=pkt.destination_mac,
            tcp_flags=flags,
            dns_qname=dns_qname,
            dns_rcode=dns_rcode,
            dns_qr=dns_qr,
            dns_qtype=dns_qtype,
            http_status_code=http_status_code,
            http_method=http_method,
            http_uri=http_uri,
            icmp_type=icmp_type,
            icmp_code=icmp_code,
            length=pkt.captured_length or 0,
            info=pkt.info or "",
            raw_details=layer_details,
        )

    def extract_features(
        self, packets: list[ParsedPacket]
    ) -> tuple[list[NormalizedEvent], dict[Any, FlowAggregation], dict[str, HostProfile]]:
        """Normalize all packets and compute flow aggregations and host profiles."""
        events: list[NormalizedEvent] = [self.normalize_parsed_packet(p) for p in packets]
        events.sort(key=lambda e: e.timestamp)

        flows: dict[Any, FlowAggregation] = {}
        hosts: dict[str, HostProfile] = {}

        # First pass: group by flows and hosts
        for evt in events:
            # 1. Host profile
            if evt.source_ip:
                if evt.source_ip not in hosts:
                    hosts[evt.source_ip] = HostProfile(ip=evt.source_ip)
                hp = hosts[evt.source_ip]
                hp.events.append(evt)
                if evt.destination_ip:
                    hp.distinct_destinations.add(evt.destination_ip)
                if evt.destination_port is not None:
                    hp.distinct_destination_ports.add(evt.destination_port)
                if evt.source_mac:
                    hp.arp_macs.add(evt.source_mac)

                # DNS metrics
                if evt.protocol == "DNS" or evt.application_protocol == "DNS":
                    if evt.dns_qr == "Query" or evt.dns_qname:
                        hp.dns_queries.append(evt)
                        if evt.dns_qname:
                            base_dom, sub = self._split_domain(evt.dns_qname)
                            if base_dom:
                                if base_dom not in hp.subdomains_by_base_domain:
                                    hp.subdomains_by_base_domain[base_dom] = set()
                                hp.subdomains_by_base_domain[base_dom].add(sub)
                    if evt.dns_rcode == 3:  # NXDOMAIN
                        hp.dns_nxdomains.append(evt)

                # ICMP Echo Requests (Type 8)
                if evt.protocol == "ICMP" and (evt.icmp_type == 8 or "Echo Request" in evt.info):
                    hp.icmp_requests.append(evt)

                # HTTP Errors (4xx, 5xx)
                if evt.http_status_code and evt.http_status_code >= 400:
                    hp.http_errors.append(evt)

                # TCP SYN tracking
                if "SYN" in evt.tcp_flags and "ACK" not in evt.tcp_flags:
                    hp.syn_count += 1

            # Check if destination received an NXDOMAIN response (attribute to client who requested it)
            if (
                evt.destination_ip
                and (evt.protocol == "DNS" or evt.application_protocol == "DNS")
                and evt.dns_rcode == 3
            ):
                if evt.destination_ip not in hosts:
                    hosts[evt.destination_ip] = HostProfile(ip=evt.destination_ip)
                hosts[evt.destination_ip].dns_nxdomains.append(evt)

            # 2. Flow key: (source_ip, destination_ip, destination_port, protocol)
            proto_key = evt.transport_protocol or evt.protocol or "OTHER"
            flow_key = (evt.source_ip, evt.destination_ip, evt.destination_port, proto_key)
            if flow_key not in flows:
                flows[flow_key] = FlowAggregation(
                    flow_key=flow_key,
                    source_ip=evt.source_ip,
                    destination_ip=evt.destination_ip,
                    destination_port=evt.destination_port,
                    protocol=proto_key,
                    start_time=evt.timestamp,
                    end_time=evt.timestamp,
                )

            fl = flows[flow_key]
            fl.events.append(evt)
            fl.packet_count += 1
            fl.byte_count += evt.length
            fl.end_time = evt.timestamp

            if "SYN" in evt.tcp_flags and "ACK" not in evt.tcp_flags:
                fl.syn_count += 1
            if "SYN" in evt.tcp_flags and "ACK" in evt.tcp_flags:
                fl.syn_ack_count += 1
            if "ACK" in evt.tcp_flags and "SYN" not in evt.tcp_flags:
                fl.ack_count += 1
            if "RST" in evt.tcp_flags:
                fl.rst_count += 1

        # Second pass: Compute intervals and statistics for each flow
        for fl in flows.values():
            fl.duration = max(0.0, fl.end_time - fl.start_time)
            # Handshake complete if SYN and subsequent ACK
            fl.handshake_complete = fl.syn_count > 0 and fl.ack_count > 0

            # Inter-arrival times
            if len(fl.events) >= 2:
                intervals: list[float] = []
                for i in range(1, len(fl.events)):
                    dt = max(0.0, fl.events[i].timestamp - fl.events[i - 1].timestamp)
                    intervals.append(dt)
                fl.inter_arrival_times = intervals
                mean = sum(intervals) / len(intervals)
                fl.mean_inter_arrival = mean
                if len(intervals) > 1 and mean > 0.0001:
                    variance = sum((x - mean) ** 2 for x in intervals) / (len(intervals) - 1)
                    std_dev = math.sqrt(variance)
                    fl.std_inter_arrival = std_dev
                    fl.relative_std_dev = std_dev / mean
                else:
                    fl.relative_std_dev = 0.0

        # Also count completed handshakes on hosts
        for fl in flows.values():
            if fl.handshake_complete and fl.source_ip and fl.source_ip in hosts:
                hosts[fl.source_ip].handshake_completed_count += 1

        return events, flows, hosts

    def _split_domain(self, fqdn: str) -> tuple[str, str]:
        """Split a domain like 'sub1.sub2.example.com' into base 'example.com' and subdomain 'sub1.sub2'."""
        cleaned = fqdn.strip(".").lower()
        parts = cleaned.split(".")
        if len(parts) <= 2:
            return cleaned, ""
        # Base domain is the last two parts (e.g. example.com)
        base = ".".join(parts[-2:])
        sub = ".".join(parts[:-2])
        return base, sub
