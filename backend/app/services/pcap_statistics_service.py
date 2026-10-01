"""Aggregation and telemetry statistics service for PCAP captures."""

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.models.pcap import Capture, ParsedPacket
from app.schemas.pcap import (
    CaptureStatisticsResponse,
    EndpointItem,
    PortItem,
    TimelineBucketItem,
)

# Common port service hints for educational clarity
PORT_HINTS: dict[int, str] = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    80: "HTTP",
    110: "POP3",
    123: "NTP",
    143: "IMAP",
    443: "HTTPS / TLS",
    445: "SMB",
    3389: "RDP",
    8080: "HTTP Alt",
}


class PcapStatisticsService:
    """Calculates capture metrics, top talkers, endpoint distributions, and timeline slices."""

    def get_statistics(self, db: Session, capture: Capture) -> CaptureStatisticsResponse:
        """Compute summary traffic telemetry."""
        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture.id)
            .order_by(ParsedPacket.packet_number.asc())
            .all()
        )

        total_packets = len(packets)
        total_bytes = 0
        protocol_counts: dict[str, int] = defaultdict(int)
        ip_packets: dict[str, int] = defaultdict(int)
        ip_bytes: dict[str, int] = defaultdict(int)
        ip_destinations: dict[str, set[str]] = defaultdict(set)
        unique_ips: set[str] = set()
        unique_macs: set[str] = set()
        unique_ports: set[int] = set()

        for p in packets:
            p_bytes = p.original_length or p.captured_length or 0
            total_bytes += p_bytes

            proto = p.protocol
            protocol_counts[proto] += 1

            if p.source_ip:
                unique_ips.add(p.source_ip)
                ip_packets[p.source_ip] += 1
                ip_bytes[p.source_ip] += p_bytes
                if p.destination_ip:
                    ip_destinations[p.source_ip].add(p.destination_ip)

            if p.destination_ip:
                unique_ips.add(p.destination_ip)

            if p.source_mac:
                unique_macs.add(p.source_mac)
            if p.destination_mac:
                unique_macs.add(p.destination_mac)

            if p.source_port:
                unique_ports.add(p.source_port)
            if p.destination_port:
                unique_ports.add(p.destination_port)

        duration = max(capture.duration, 0.001)
        pps = round(total_packets / duration, 2)
        bps = round(total_bytes / duration, 2)

        top_protocols = [
            {"protocol": k, "count": v, "percentage": round((v / max(total_packets, 1)) * 100, 1)}
            for k, v in sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        top_talkers = [
            {
                "ip": ip,
                "packet_count": ip_packets[ip],
                "byte_count": ip_bytes[ip],
                "destinations": list(ip_destinations[ip])[:10],
            }
            for ip in sorted(ip_bytes.keys(), key=lambda x: ip_bytes[x], reverse=True)[:10]
        ]

        return CaptureStatisticsResponse(
            capture_id=capture.id,
            total_packets=total_packets,
            total_bytes=total_bytes,
            duration_seconds=capture.duration,
            packets_per_second=pps,
            bytes_per_second=bps,
            unique_ips=len(unique_ips),
            unique_macs=len(unique_macs),
            unique_ports=len(unique_ports),
            protocol_distribution=dict(protocol_counts),
            top_protocols=top_protocols,
            top_talkers=top_talkers,
        )

    def get_endpoints(self, db: Session, capture_id: int) -> list[EndpointItem]:
        """Aggregate traffic metrics by IP endpoint."""
        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture_id)
            .order_by(ParsedPacket.packet_number.asc())
            .all()
        )

        endpoints: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "mac": None,
                "sent_pkts": 0,
                "rcvd_pkts": 0,
                "sent_bytes": 0,
                "rcvd_bytes": 0,
                "protocols": set(),
                "first_seen": None,
                "last_seen": None,
            }
        )

        for p in packets:
            p_bytes = p.original_length or p.captured_length or 0
            if p.source_ip:
                e = endpoints[p.source_ip]
                e["mac"] = e["mac"] or p.source_mac
                e["sent_pkts"] += 1
                e["sent_bytes"] += p_bytes
                e["protocols"].add(p.protocol)
                if e["first_seen"] is None:
                    e["first_seen"] = p.relative_time
                e["last_seen"] = p.relative_time

            if p.destination_ip:
                e = endpoints[p.destination_ip]
                e["mac"] = e["mac"] or p.destination_mac
                e["rcvd_pkts"] += 1
                e["rcvd_bytes"] += p_bytes
                e["protocols"].add(p.protocol)
                if e["first_seen"] is None:
                    e["first_seen"] = p.relative_time
                e["last_seen"] = p.relative_time

        items: list[EndpointItem] = []
        for ip, d in endpoints.items():
            tot_pkts = d["sent_pkts"] + d["rcvd_pkts"]
            tot_bytes = d["sent_bytes"] + d["rcvd_bytes"]
            items.append(
                EndpointItem(
                    ip=ip,
                    mac=d["mac"],
                    packets_sent=d["sent_pkts"],
                    packets_received=d["rcvd_pkts"],
                    total_packets=tot_pkts,
                    bytes_sent=d["sent_bytes"],
                    bytes_received=d["rcvd_bytes"],
                    total_bytes=tot_bytes,
                    protocols=sorted(d["protocols"]),
                    first_seen=d["first_seen"] or 0.0,
                    last_seen=d["last_seen"] or 0.0,
                )
            )

        items.sort(key=lambda x: x.total_bytes, reverse=True)
        return items

    def get_ports(self, db: Session, capture_id: int) -> list[PortItem]:
        """Aggregate transport port usage and frequencies."""
        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture_id)
            .filter(ParsedPacket.destination_port.isnot(None))
            .all()
        )

        port_stats: dict[tuple[int, str], dict[str, Any]] = defaultdict(
            lambda: {"pkts": 0, "bytes": 0, "clients": set(), "servers": set()}
        )

        for p in packets:
            port = p.destination_port
            if not port:
                continue
            proto = p.transport_protocol or "TCP"
            key = (port, proto)
            p_bytes = p.original_length or p.captured_length or 0

            port_stats[key]["pkts"] += 1
            port_stats[key]["bytes"] += p_bytes
            if p.source_ip:
                port_stats[key]["clients"].add(p.source_ip)
            if p.destination_ip:
                port_stats[key]["servers"].add(p.destination_ip)

        items: list[PortItem] = []
        for (port, proto), d in port_stats.items():
            hint = PORT_HINTS.get(port, "Unknown / Dynamic")
            items.append(
                PortItem(
                    port=port,
                    protocol=proto,
                    service_hint=hint,
                    packet_count=d["pkts"],
                    byte_count=d["bytes"],
                    client_count=len(d["clients"]),
                    server_count=len(d["servers"]),
                )
            )

        items.sort(key=lambda x: x.packet_count, reverse=True)
        return items

    def get_timeline(self, db: Session, capture: Capture, bucket_count: int = 30) -> list[TimelineBucketItem]:
        """Partition packet distribution into discrete temporal time slices for burst visualizer."""
        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture.id)
            .order_by(ParsedPacket.packet_number.asc())
            .all()
        )

        duration = max(capture.duration, 1.0)
        slice_duration = duration / bucket_count

        buckets: list[dict[str, Any]] = [
            {
                "bucket_index": i,
                "start": round(i * slice_duration, 3),
                "end": round((i + 1) * slice_duration, 3),
                "packets": 0,
                "bytes": 0,
                "protocols": defaultdict(int),
            }
            for i in range(bucket_count)
        ]

        for p in packets:
            rel = p.relative_time
            idx = min(int(rel / slice_duration), bucket_count - 1)
            b = buckets[idx]
            b["packets"] += 1
            b["bytes"] += p.original_length or p.captured_length or 0
            b["protocols"][p.protocol] += 1

        return [
            TimelineBucketItem(
                bucket_index=b["bucket_index"],
                start_offset_seconds=b["start"],
                end_offset_seconds=b["end"],
                packet_count=b["packets"],
                byte_count=b["bytes"],
                protocols=dict(b["protocols"]),
            )
            for b in buckets
        ]


pcap_statistics_service = PcapStatisticsService()
