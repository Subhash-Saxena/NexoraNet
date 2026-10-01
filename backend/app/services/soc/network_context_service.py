"""Network Context Service.

Calculates endpoint statistics, protocol distributions, and conversation
summaries by inspecting parsed capture packets without re-parsing raw PCAP bytes.
"""

from typing import Any

from app.models.pcap import ParsedPacket
from sqlalchemy import or_
from sqlalchemy.orm import Session


class NetworkContextService:
    """Extracts endpoint and flow context from capture database telemetry."""

    @classmethod
    def get_endpoint_context(
        cls,
        db: Session,
        capture_id: int | None,
        ip_address: str | None,
    ) -> dict[str, Any] | None:
        """Calculate packet counts, byte volumes, and protocol distributions for an IP."""
        if not capture_id or not ip_address:
            return None

        packets = (
            db.query(ParsedPacket)
            .filter(
                ParsedPacket.capture_id == capture_id,
                or_(
                    ParsedPacket.source_ip == ip_address,
                    ParsedPacket.destination_ip == ip_address,
                ),
            )
            .all()
        )

        if not packets:
            return {
                "ip": ip_address,
                "packet_count": 0,
                "byte_count": 0,
                "protocols": [],
                "ports": [],
                "first_seen": None,
                "last_seen": None,
            }

        protocols = set()
        ports = set()
        total_bytes = 0
        timestamps = []

        for p in packets:
            if p.protocol:
                protocols.add(p.protocol)
            if p.source_ip == ip_address and p.source_port:
                ports.add(p.source_port)
            if p.destination_ip == ip_address and p.destination_port:
                ports.add(p.destination_port)
            total_bytes += p.captured_length or 0
            if p.timestamp is not None:
                timestamps.append(p.timestamp)

        first_seen = min(timestamps) if timestamps else None
        last_seen = max(timestamps) if timestamps else None

        return {
            "ip": ip_address,
            "packet_count": len(packets),
            "byte_count": total_bytes,
            "protocols": sorted(protocols),
            "ports": sorted(ports)[:25],  # Cap port list to avoid huge arrays
            "first_seen": first_seen,
            "last_seen": last_seen,
        }

    @classmethod
    def get_flow_context(
        cls,
        db: Session,
        capture_id: int | None,
        source_ip: str | None,
        destination_ip: str | None,
    ) -> dict[str, Any]:
        """Summarize conversation context between two endpoints."""
        source_ctx = cls.get_endpoint_context(db, capture_id, source_ip)
        dest_ctx = cls.get_endpoint_context(db, capture_id, destination_ip)

        summary = None
        if source_ip and destination_ip:
            summary = f"Telemetry observed between source {source_ip} and destination {destination_ip}."

        return {
            "source": source_ctx,
            "destination": dest_ctx,
            "conversation_summary": summary,
        }


network_context_service = NetworkContextService()
