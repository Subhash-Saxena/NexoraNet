"""Authoritative offline PCAP parser and packet normalization service.

Parses .pcap and .pcapng files into normalized relational packet records
and layer trees without executing any binary payloads or transmitting network frames.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Suppress scapy runtime warnings about missing live capture providers
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import PcapReader
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.dns import DNS, DNSRR
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import ARP, Ether
from scapy.packet import Packet as ScapyPacket
from sqlalchemy.orm import Session

from app.core.pcap_config import pcap_settings
from app.models.enums import CaptureStatus
from app.models.pcap import Capture, ParsedPacket

logger = logging.getLogger(__name__)


class PcapParserService:
    """Offline defensive packet capture parsing engine."""

    def parse_and_index_capture(self, db: Session, capture: Capture) -> Capture:
        """Parse raw PCAP file from disk and populate normalized ParsedPacket rows."""
        file_path = Path(capture.storage_path)
        if not file_path.exists():
            capture.status = CaptureStatus.FAILED
            capture.error_message = f"File not found on storage: {file_path.name}"
            db.commit()
            return capture

        capture.status = CaptureStatus.PARSING
        db.commit()

        try:
            parsed_packets_data: list[dict[str, Any]] = []
            protocol_counts: dict[str, int] = {}
            unique_ips: set[str] = set()
            unique_macs: set[str] = set()
            unique_ports: set[int] = set()

            first_timestamp: float | None = None
            last_timestamp: float | None = None
            total_bytes: int = 0
            packet_idx = 0

            # Use explicit open() context to guarantee file closure on Windows
            with open(file_path, "rb") as fdesc, PcapReader(fdesc) as reader:
                for pkt in reader:
                    packet_idx += 1
                    if packet_idx > pcap_settings.MAX_PACKETS_TO_STORE:
                        logger.warning(
                            "Capture %s exceeded max stored packet limit (%s). Stopping parse.",
                            capture.id,
                            pcap_settings.MAX_PACKETS_TO_STORE,
                        )
                        break

                    pkt_time = float(getattr(pkt, "time", 0.0))
                    if first_timestamp is None:
                        first_timestamp = pkt_time
                    last_timestamp = pkt_time

                    relative_time = round(pkt_time - first_timestamp, 6)
                    captured_len = len(pkt)
                    orig_len = int(getattr(pkt, "wirelen", captured_len))
                    total_bytes += orig_len

                    parsed_record = self._normalize_packet(
                        pkt, packet_idx, pkt_time, relative_time, captured_len, orig_len
                    )
                    parsed_packets_data.append(parsed_record)

                    # Update statistics sets
                    proto = parsed_record["protocol"]
                    protocol_counts[proto] = protocol_counts.get(proto, 0) + 1
                    if parsed_record["source_ip"]:
                        unique_ips.add(parsed_record["source_ip"])
                    if parsed_record["destination_ip"]:
                        unique_ips.add(parsed_record["destination_ip"])
                    if parsed_record["source_mac"]:
                        unique_macs.add(parsed_record["source_mac"])
                    if parsed_record["destination_mac"]:
                        unique_macs.add(parsed_record["destination_mac"])
                    if parsed_record["source_port"]:
                        unique_ports.add(parsed_record["source_port"])
                    if parsed_record["destination_port"]:
                        unique_ports.add(parsed_record["destination_port"])

            # Bulk insert parsed packets for high database performance
            db.query(ParsedPacket).filter(ParsedPacket.capture_id == capture.id).delete()

            # Insert in chunks of 500
            chunk_size = 500
            for i in range(0, len(parsed_packets_data), chunk_size):
                chunk = parsed_packets_data[i : i + chunk_size]
                db.bulk_insert_mappings(
                    ParsedPacket,
                    [{"capture_id": capture.id, **data} for data in chunk],
                )

            # Update capture metadata
            duration = round(last_timestamp - first_timestamp, 3) if first_timestamp and last_timestamp else 0.0
            capture.packet_count = packet_idx
            capture.file_size = file_path.stat().st_size
            capture.duration = duration
            if first_timestamp:
                capture.start_time = datetime.fromtimestamp(first_timestamp, tz=timezone.utc)
            if last_timestamp:
                capture.end_time = datetime.fromtimestamp(last_timestamp, tz=timezone.utc)

            summary = {
                "total_bytes": total_bytes,
                "protocol_distribution": protocol_counts,
                "unique_ips_count": len(unique_ips),
                "unique_macs_count": len(unique_macs),
                "unique_ports_count": len(unique_ports),
            }
            capture.summary_metadata = json.dumps(summary)
            capture.status = CaptureStatus.READY
            capture.error_message = None

            db.commit()
            db.refresh(capture)
            return capture

        except Exception:
            logger.exception("Error parsing PCAP capture %s", capture.id)
            capture.status = CaptureStatus.FAILED
            capture.error_message = "Invalid or corrupted packet capture."
            db.commit()
            return capture

    def _normalize_packet(
        self,
        pkt: ScapyPacket,
        packet_idx: int,
        timestamp: float,
        relative_time: float,
        captured_length: int,
        original_length: int,
    ) -> dict[str, Any]:
        """Normalize Scapy packet into relational fields and protocol layer trees."""
        layers: list[str] = ["Frame"]
        layer_details: dict[str, Any] = {
            "Frame": {
                "number": packet_idx,
                "timestamp": timestamp,
                "relative_time": relative_time,
                "captured_length": captured_length,
                "original_length": original_length,
            }
        }

        source_mac: str | None = None
        destination_mac: str | None = None
        source_ip: str | None = None
        destination_ip: str | None = None
        source_port: int | None = None
        destination_port: int | None = None
        transport_protocol: str | None = None
        application_protocol: str | None = None
        protocol: str = "Ethernet"
        info: str = ""
        tcp_flags: list[str] = []
        tcp_seq: int | None = None
        tcp_ack: int | None = None

        # Layer 2: Ethernet
        if Ether in pkt:
            eth = pkt[Ether]
            source_mac = eth.src
            destination_mac = eth.dst
            layers.append("Ethernet")
            layer_details["Ethernet"] = {
                "src": eth.src,
                "dst": eth.dst,
                "type": hex(eth.type),
            }
            protocol = "Ethernet"
            info = f"Ethernet II, Src: {eth.src}, Dst: {eth.dst}"

        # Layer 2/3: ARP
        if ARP in pkt:
            arp = pkt[ARP]
            layers.append("ARP")
            op_name = "who-has" if arp.op == 1 else "is-at" if arp.op == 2 else f"op {arp.op}"
            layer_details["ARP"] = {
                "opcode": arp.op,
                "opcode_name": op_name,
                "sender_mac": arp.hwsrc,
                "sender_ip": arp.psrc,
                "target_mac": arp.hwdst,
                "target_ip": arp.pdst,
            }
            protocol = "ARP"
            if arp.op == 1:
                info = f"Who has {arp.pdst}? Tell {arp.psrc}"
            elif arp.op == 2:
                info = f"{arp.psrc} is at {arp.hwsrc}"
            else:
                info = f"ARP {op_name}"

        # Layer 3: IPv4
        if IP in pkt:
            ip = pkt[IP]
            source_ip = ip.src
            destination_ip = ip.dst
            layers.append("IPv4")
            layer_details["IPv4"] = {
                "version": 4,
                "ihl": ip.ihl * 4,
                "tos": ip.tos,
                "total_length": ip.len,
                "id": ip.id,
                "flags": str(ip.flags),
                "ttl": ip.ttl,
                "proto": ip.proto,
                "checksum": hex(ip.chksum or 0),
                "src": ip.src,
                "dst": ip.dst,
            }
            protocol = "IPv4"
            info = f"IPv4 {ip.src} -> {ip.dst} (TTL={ip.ttl})"

        # Layer 3: IPv6
        elif IPv6 in pkt:
            ip6 = pkt[IPv6]
            source_ip = ip6.src
            destination_ip = ip6.dst
            layers.append("IPv6")
            layer_details["IPv6"] = {
                "version": 6,
                "traffic_class": ip6.tc,
                "flow_label": ip6.fl,
                "payload_len": ip6.plen,
                "next_header": ip6.nh,
                "hop_limit": ip6.hlim,
                "src": ip6.src,
                "dst": ip6.dst,
            }
            protocol = "IPv6"
            info = f"IPv6 {ip6.src} -> {ip6.dst}"

        # Layer 4: ICMP
        if ICMP in pkt:
            icmp = pkt[ICMP]
            protocol = "ICMP"
            type_name = (
                "Echo Request"
                if icmp.type == 8
                else "Echo Reply"
                if icmp.type == 0
                else "Destination Unreachable"
                if icmp.type == 3
                else "Time Exceeded"
                if icmp.type == 11
                else f"Type {icmp.type}"
            )
            layers.append("ICMP")
            icmp_id = getattr(icmp, "id", None)
            icmp_seq = getattr(icmp, "seq", None)
            layer_details["ICMP"] = {
                "type": icmp.type,
                "type_name": type_name,
                "code": icmp.code,
                "checksum": hex(icmp.chksum or 0),
                "identifier": icmp_id,
                "sequence": icmp_seq,
            }
            info = f"{type_name} (id={icmp_id or 0}, seq={icmp_seq or 0})"

        # Layer 4: TCP
        if TCP in pkt:
            tcp = pkt[TCP]
            transport_protocol = "TCP"
            source_port = tcp.sport
            destination_port = tcp.dport
            tcp_seq = tcp.seq
            tcp_ack = tcp.ack
            protocol = "TCP"

            # Parse standard TCP flags
            flag_str = str(tcp.flags)
            flag_map = [
                ("SYN", "S"),
                ("ACK", "A"),
                ("FIN", "F"),
                ("RST", "R"),
                ("PSH", "P"),
                ("URG", "U"),
                ("ECE", "E"),
                ("CWR", "C"),
            ]
            tcp_flags = [name for name, char in flag_map if char in flag_str]

            layers.append("TCP")
            layer_details["TCP"] = {
                "sport": tcp.sport,
                "dport": tcp.dport,
                "seq": tcp.seq,
                "ack": tcp.ack,
                "header_length": tcp.dataofs * 4,
                "flags": tcp_flags,
                "raw_flags": flag_str,
                "window": tcp.window,
                "checksum": hex(tcp.chksum or 0),
            }

            flag_disp = " ".join(tcp_flags) if tcp_flags else "None"
            info = f"{tcp.sport} -> {tcp.dport} [{flag_disp}] Seq={tcp.seq} Ack={tcp.ack} Win={tcp.window}"

        # Layer 4: UDP
        elif UDP in pkt:
            udp = pkt[UDP]
            transport_protocol = "UDP"
            source_port = udp.sport
            destination_port = udp.dport
            protocol = "UDP"
            layers.append("UDP")
            layer_details["UDP"] = {
                "sport": udp.sport,
                "dport": udp.dport,
                "length": udp.len,
                "checksum": hex(udp.chksum or 0),
            }
            info = f"{udp.sport} -> {udp.dport} Len={udp.len}"

        # Layer 7: DNS
        if DNS in pkt:
            dns = pkt[DNS]
            application_protocol = "DNS"
            protocol = "DNS"
            qr = "Response" if dns.qr == 1 else "Query"
            qname = ""
            qtype = "A"

            if dns.qd:
                raw_qname = getattr(dns.qd, "qname", b"")
                qname = raw_qname.decode("utf-8", errors="ignore").rstrip(".") if isinstance(raw_qname, bytes) else str(raw_qname).rstrip(".")
                qtype_num = getattr(dns.qd, "qtype", 1)
                qtype = "A" if qtype_num == 1 else "AAAA" if qtype_num == 28 else "CNAME" if qtype_num == 5 else f"Type {qtype_num}"

            answers: list[dict[str, Any]] = []
            if dns.an:
                an = dns.an
                while an and isinstance(an, DNSRR):
                    rdata = getattr(an, "rdata", "")
                    if isinstance(rdata, bytes):
                        rdata = rdata.decode("utf-8", errors="ignore")
                    answers.append({"name": str(getattr(an, "rrname", "")), "type": getattr(an, "type", 1), "rdata": str(rdata)})
                    an = getattr(an, "payload", None)

            layers.append("DNS")
            layer_details["DNS"] = {
                "id": dns.id,
                "qr": qr,
                "opcode": dns.opcode,
                "rcode": dns.rcode,
                "qname": qname,
                "qtype": qtype,
                "answers": answers,
            }

            if qr == "Query":
                info = f"Standard query 0x{dns.id:04x} {qtype} {qname}"
            else:
                ans_summary = answers[0]["rdata"] if answers else f"rcode={dns.rcode}"
                info = f"Standard query response 0x{dns.id:04x} {qname} -> {ans_summary}"

        # Layer 7: DHCP / BOOTP
        if DHCP in pkt or BOOTP in pkt:
            application_protocol = "DHCP"
            protocol = "DHCP"
            layers.append("DHCP")

            dhcp_type = "Request"
            if DHCP in pkt:
                for opt in pkt[DHCP].options:
                    if isinstance(opt, tuple) and opt[0] == "message-type":
                        msg_id = opt[1]
                        type_map = {1: "Discover", 2: "Offer", 3: "Request", 5: "ACK", 6: "NAK"}
                        dhcp_type = type_map.get(msg_id, f"Type {msg_id}")
                        break

            layer_details["DHCP"] = {
                "message_type": dhcp_type,
            }
            info = f"DHCP {dhcp_type}"

        # Layer 7: HTTP Detection (Safely parsed as untrusted text)
        if TCP in pkt and (source_port in {80, 8080, 8000} or destination_port in {80, 8080, 8000}):
            raw_payload = bytes(pkt[TCP].payload)
            if raw_payload:
                text_prefix = raw_payload[:256].decode("utf-8", errors="ignore")
                if text_prefix.startswith(("GET ", "POST ", "PUT ", "DELETE ", "HEAD ", "OPTIONS ", "HTTP/1.")):
                    application_protocol = "HTTP"
                    protocol = "HTTP"
                    layers.append("HTTP")

                    first_line = text_prefix.split("\r\n")[0]
                    layer_details["HTTP"] = {
                        "first_line": first_line,
                        "raw_header_preview": text_prefix[:500],
                    }
                    info = first_line

        # Layer 7: TLS Metadata (Handshake / SNI without decryption)
        if TCP in pkt and (source_port == 443 or destination_port == 443):
            raw_payload = bytes(pkt[TCP].payload)
            if len(raw_payload) >= 5 and raw_payload[0] == 0x16:  # TLS Handshake ContentType
                application_protocol = "TLS"
                protocol = "TLS"
                layers.append("TLS")

                handshake_type = raw_payload[5] if len(raw_payload) > 5 else 0
                hs_name = "Client Hello" if handshake_type == 1 else "Server Hello" if handshake_type == 2 else "Handshake"

                layer_details["TLS"] = {
                    "content_type": 22,
                    "handshake_type": handshake_type,
                    "handshake_name": hs_name,
                    "notice": "Encrypted application content cannot be inspected without appropriate decryption material.",
                }
                info = f"TLSv1.2 Record Layer: Handshake Protocol: {hs_name}"

        return {
            "packet_number": packet_idx,
            "timestamp": timestamp,
            "relative_time": relative_time,
            "captured_length": captured_length,
            "original_length": original_length,
            "protocol": protocol,
            "source_mac": source_mac,
            "destination_mac": destination_mac,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "source_port": source_port,
            "destination_port": destination_port,
            "transport_protocol": transport_protocol,
            "application_protocol": application_protocol,
            "info": info or f"Packet #{packet_idx} ({protocol})",
            "tcp_flags": json.dumps(tcp_flags) if tcp_flags else None,
            "tcp_seq": tcp_seq,
            "tcp_ack": tcp_ack,
            "layers": json.dumps(layers),
            "layer_details": json.dumps(layer_details),
        }


pcap_parser_service = PcapParserService()
