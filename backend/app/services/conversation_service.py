"""Conversation and flow analysis service for grouping packets into 5-tuple sessions and detecting TCP states."""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import TcpHandshakeState
from app.models.pcap import ParsedPacket
from app.schemas.pcap import ConversationItem, FlowLadderItem


class ConversationService:
    """Aggregates packets into network flows, conversation ladders, and handshake states."""

    def get_conversations(self, db: Session, capture_id: int) -> list[ConversationItem]:
        """Group all packets for a capture into bi-directional conversations."""
        packets = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture_id)
            .order_by(ParsedPacket.packet_number.asc())
            .all()
        )

        flow_map: dict[str, dict[str, Any]] = {}

        for pkt in packets:
            # Need at least layer 3 addresses
            if not pkt.source_ip or not pkt.destination_ip:
                continue

            proto = pkt.transport_protocol or pkt.protocol or "IP"
            s_ip, s_port = pkt.source_ip, pkt.source_port or 0
            d_ip, d_port = pkt.destination_ip, pkt.destination_port or 0

            # Canonical conversation key regardless of direction
            ep1 = f"{s_ip}:{s_port}" if s_port else s_ip
            ep2 = f"{d_ip}:{d_port}" if d_port else d_ip

            if (s_ip, s_port) <= (d_ip, d_port):
                conv_key = f"{proto}_{s_ip}:{s_port}_{d_ip}:{d_port}"
            else:
                conv_key = f"{proto}_{d_ip}:{d_port}_{s_ip}:{s_port}"

            flags: list[str] = []
            if pkt.tcp_flags:
                try:
                    flags = json.loads(pkt.tcp_flags)
                except (json.JSONDecodeError, TypeError):
                    flags = []

            ladder_entry = FlowLadderItem(
                step=pkt.packet_number,
                relative_time=pkt.relative_time,
                source=ep1,
                destination=ep2,
                protocol=pkt.protocol,
                info=pkt.info,
                tcp_flags=flags,
            )

            if conv_key not in flow_map:
                flow_map[conv_key] = {
                    "id": conv_key,
                    "client_endpoint": ep1,
                    "server_endpoint": ep2,
                    "protocol": proto,
                    "packet_count": 0,
                    "byte_count": 0,
                    "start_time": pkt.relative_time,
                    "last_time": pkt.relative_time,
                    "packets": [],
                    "syn_seen": False,
                    "syn_ack_seen": False,
                    "ack_seen": False,
                    "rst_seen": False,
                }

            entry = flow_map[conv_key]
            entry["packet_count"] += 1
            entry["byte_count"] += pkt.original_length or pkt.captured_length
            entry["last_time"] = pkt.relative_time
            if len(entry["packets"]) < 50:  # Cap ladder steps per conversation
                entry["packets"].append(ladder_entry)

            # Analyze TCP handshake flags
            if proto == "TCP":
                if "RST" in flags:
                    entry["rst_seen"] = True
                elif "SYN" in flags and "ACK" not in flags:
                    entry["syn_seen"] = True
                elif "SYN" in flags and "ACK" in flags:
                    entry["syn_ack_seen"] = True
                elif "ACK" in flags and entry["syn_ack_seen"] and not entry["ack_seen"]:
                    entry["ack_seen"] = True

        conversations: list[ConversationItem] = []
        for conv_key, data in flow_map.items():
            duration = round(data["last_time"] - data["start_time"], 4)

            # Determine handshake state
            if data["protocol"] == "TCP":
                if data["rst_seen"]:
                    state = TcpHandshakeState.RESET
                elif data["syn_seen"] and data["syn_ack_seen"] and data["ack_seen"]:
                    state = TcpHandshakeState.COMPLETE
                elif data["syn_seen"] and not data["syn_ack_seen"]:
                    state = TcpHandshakeState.INCOMPLETE
                else:
                    state = TcpHandshakeState.UNKNOWN
            else:
                state = TcpHandshakeState.UNKNOWN

            conversations.append(
                ConversationItem(
                    id=conv_key,
                    client_endpoint=data["client_endpoint"],
                    server_endpoint=data["server_endpoint"],
                    protocol=data["protocol"],
                    packet_count=data["packet_count"],
                    byte_count=data["byte_count"],
                    start_time=data["start_time"],
                    duration=duration,
                    handshake_state=state,
                    ladder=data["packets"],
                )
            )

        # Sort by packet count descending
        conversations.sort(key=lambda c: c.packet_count, reverse=True)
        return conversations


conversation_service = ConversationService()
