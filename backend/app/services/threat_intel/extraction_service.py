"""IOC Extraction Service.

Safely extracts observable Indicators of Compromise and Interest from:
- PCAP parsed packet telemetry
- Detection alerts and alert evidence payloads
- SOC investigations and cases
- Free-form text and analyst notes

All extraction operates strictly on metadata without executing or evaluating payloads.
"""

import json
import re
from typing import Any

from app.models.detection import DetectionAlert
from app.models.enums import IndicatorType
from app.models.pcap import ParsedPacket
from app.models.soc import Investigation
from app.services.threat_intel.normalization_service import normalization_service
from sqlalchemy.orm import Session


class IOCExtractionService:
    """Extracts and normalizes indicators from structured telemetry and passive text."""

    # Regex patterns for passive text scanning
    IP_REGEX = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\[\.\]|\.)){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )
    DOMAIN_REGEX = re.compile(
        r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\[\.\]|\.))+"
        r"[a-zA-Z]{2,}\b"
    )
    URL_REGEX = re.compile(
        r"(?:hxxps?|https?|ftp)://[^\s<>\"']+",
        re.IGNORECASE,
    )
    HASH_MD5_REGEX = re.compile(r"\b[a-fA-F0-9]{32}\b")
    HASH_SHA1_REGEX = re.compile(r"\b[a-fA-F0-9]{40}\b")
    HASH_SHA256_REGEX = re.compile(r"\b[a-fA-F0-9]{64}\b")
    EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+(?:@|\[at\])[A-Za-z0-9.\-_\[\]]+", re.IGNORECASE)

    @classmethod
    def extract_from_packet(cls, packet: ParsedPacket) -> list[dict[str, Any]]:
        """Extract indicators from a single parsed packet record."""
        extracted: list[dict[str, Any]] = []

        # 1. Source and Destination IP
        for ip, role in [(packet.source_ip, "Source IP"), (packet.destination_ip, "Destination IP")]:
            if ip:
                try:
                    norm = normalization_service.normalize(ip, IndicatorType.IP_ADDRESS)
                    extracted.append({
                        **norm,
                        "context": f"{role} observed in packet #{packet.packet_number or 0}",
                        "packet_number": packet.packet_number,
                        "capture_id": packet.capture_id,
                        "timestamp": packet.timestamp,
                    })
                except ValueError:
                    pass

        # 2. Layer 7 details
        if packet.summary_data:
            try:
                layer_data = json.loads(packet.summary_data)
                # DNS Query / Response
                if "dns" in layer_data:
                    dns = layer_data["dns"]
                    query_name = dns.get("query_name")
                    if query_name:
                        try:
                            norm = normalization_service.normalize(query_name, IndicatorType.DOMAIN)
                            extracted.append({
                                **norm,
                                "context": f"DNS query name in packet #{packet.packet_number or 0}",
                                "packet_number": packet.packet_number,
                                "capture_id": packet.capture_id,
                                "timestamp": packet.timestamp,
                            })
                        except ValueError:
                            pass

                    # DNS Answers
                    answers = dns.get("answers") or []
                    for ans in answers:
                        if isinstance(ans, dict) and ans.get("data"):
                            ans_val = str(ans["data"])
                            try:
                                norm = normalization_service.normalize(ans_val)
                                extracted.append({
                                    **norm,
                                    "context": f"DNS resolution record in packet #{packet.packet_number or 0}",
                                    "packet_number": packet.packet_number,
                                    "capture_id": packet.capture_id,
                                    "timestamp": packet.timestamp,
                                })
                            except ValueError:
                                pass

                # HTTP Host and URI
                if "http" in layer_data:
                    http = layer_data["http"]
                    host = http.get("host")
                    if host:
                        try:
                            norm = normalization_service.normalize(host, IndicatorType.DOMAIN)
                            extracted.append({
                                **norm,
                                "context": f"HTTP Host header in packet #{packet.packet_number or 0}",
                                "packet_number": packet.packet_number,
                                "capture_id": packet.capture_id,
                                "timestamp": packet.timestamp,
                            })
                        except ValueError:
                            pass

                    uri = http.get("uri")
                    if uri and host:
                        full_url = f"http://{host}{uri if uri.startswith('/') else '/' + uri}"
                        try:
                            norm = normalization_service.normalize(full_url, IndicatorType.URL)
                            extracted.append({
                                **norm,
                                "context": f"HTTP Request URL in packet #{packet.packet_number or 0}",
                                "packet_number": packet.packet_number,
                                "capture_id": packet.capture_id,
                                "timestamp": packet.timestamp,
                            })
                        except ValueError:
                            pass

                # TLS SNI
                if "tls" in layer_data:
                    tls = layer_data["tls"]
                    sni = tls.get("sni")
                    if sni:
                        try:
                            norm = normalization_service.normalize(sni, IndicatorType.DOMAIN)
                            extracted.append({
                                **norm,
                                "context": f"TLS Server Name Indication (SNI) in packet #{packet.packet_number or 0}",
                                "packet_number": packet.packet_number,
                                "capture_id": packet.capture_id,
                                "timestamp": packet.timestamp,
                            })
                        except ValueError:
                            pass

            except (ValueError, TypeError):
                pass

        # Deduplicate by normalized_value within this packet
        seen = set()
        deduped = []
        for item in extracted:
            if item["normalized_value"] not in seen:
                seen.add(item["normalized_value"])
                deduped.append(item)
        return deduped

    @classmethod
    def extract_from_alert(cls, alert: DetectionAlert) -> list[dict[str, Any]]:
        """Extract indicators from an alert's endpoints and evidence records."""
        extracted: list[dict[str, Any]] = []

        # Source & Destination IPs
        if alert.source_ip:
            try:
                norm = normalization_service.normalize(alert.source_ip, IndicatorType.IP_ADDRESS)
                extracted.append({
                    **norm,
                    "context": f"Alert #{alert.id} source IP ({alert.title})",
                    "alert_id": alert.id,
                    "capture_id": alert.capture_id,
                })
            except ValueError:
                pass

        if alert.destination_ip:
            try:
                norm = normalization_service.normalize(alert.destination_ip, IndicatorType.IP_ADDRESS)
                extracted.append({
                    **norm,
                    "context": f"Alert #{alert.id} destination IP ({alert.title})",
                    "alert_id": alert.id,
                    "capture_id": alert.capture_id,
                })
            except ValueError:
                pass

        # Evidence payloads
        for ev in alert.evidence:
            if ev.evidence_data:
                try:
                    payload = json.loads(ev.evidence_data)
                    # Check for domain / host / query in evidence
                    for key in ["domain", "query", "host", "target_domain", "server_name"]:
                        if key in payload and isinstance(payload[key], str):
                            try:
                                norm = normalization_service.normalize(payload[key], IndicatorType.DOMAIN)
                                extracted.append({
                                    **norm,
                                    "context": f"Alert #{alert.id} evidence payload ({key})",
                                    "alert_id": alert.id,
                                    "capture_id": alert.capture_id,
                                    "packet_number": ev.packet_number,
                                })
                            except ValueError:
                                pass

                    # Check for hashes in evidence
                    for key in ["hash", "md5", "sha1", "sha256", "file_hash"]:
                        if key in payload and isinstance(payload[key], str):
                            try:
                                norm = normalization_service.normalize(payload[key], IndicatorType.FILE_HASH)
                                extracted.append({
                                    **norm,
                                    "context": f"Alert #{alert.id} evidence hash ({key})",
                                    "alert_id": alert.id,
                                    "capture_id": alert.capture_id,
                                })
                            except ValueError:
                                pass
                except (ValueError, TypeError):
                    pass

        # Deduplicate
        seen = set()
        deduped = []
        for item in extracted:
            if item["normalized_value"] not in seen:
                seen.add(item["normalized_value"])
                deduped.append(item)
        return deduped

    @classmethod
    def extract_from_investigation(cls, db: Session, investigation: Investigation) -> list[dict[str, Any]]:
        """Extract indicators associated with an active investigation."""
        extracted: list[dict[str, Any]] = []

        # From linked alerts
        for ia in investigation.alerts:
            if ia.alert:
                alert_iocs = cls.extract_from_alert(ia.alert)
                for item in alert_iocs:
                    extracted.append({
                        **item,
                        "investigation_id": investigation.id,
                    })

        # From free-text description and findings
        text_corpus = f"{investigation.title} {investigation.description} {investigation.conclusion or ''}"
        for f in investigation.findings:
            text_corpus += f" {f.title} {f.description}"

        free_text_iocs = cls.extract_from_text(text_corpus)
        for item in free_text_iocs:
            extracted.append({
                **item,
                "investigation_id": investigation.id,
                "context": f"Extracted from investigation '{investigation.investigation_id}' narrative",
            })

        # Deduplicate
        seen = set()
        deduped = []
        for item in extracted:
            if item["normalized_value"] not in seen:
                seen.add(item["normalized_value"])
                deduped.append(item)
        return deduped

    @classmethod
    def extract_from_text(cls, text: str) -> list[dict[str, Any]]:
        """Extract indicators from free-form text without visiting or executing strings."""
        if not text:
            return []

        extracted: list[dict[str, Any]] = []

        # 1. URLs
        for m in cls.URL_REGEX.finditer(text):
            try:
                norm = normalization_service.normalize(m.group(0), IndicatorType.URL)
                extracted.append({**norm, "context": "Extracted from text"})
            except ValueError:
                pass

        # 2. Emails
        for m in cls.EMAIL_REGEX.finditer(text):
            try:
                norm = normalization_service.normalize(m.group(0), IndicatorType.EMAIL_ADDRESS)
                extracted.append({**norm, "context": "Extracted from text"})
            except ValueError:
                pass

        # 3. IPs
        for m in cls.IP_REGEX.finditer(text):
            try:
                norm = normalization_service.normalize(m.group(0), IndicatorType.IP_ADDRESS)
                extracted.append({**norm, "context": "Extracted from text"})
            except ValueError:
                pass

        # 4. Hashes (SHA256, SHA1, MD5)
        for m in cls.HASH_SHA256_REGEX.finditer(text):
            try:
                norm = normalization_service.normalize(m.group(0), IndicatorType.FILE_HASH)
                extracted.append({**norm, "context": "Extracted SHA-256 hash"})
            except ValueError:
                pass

        for m in cls.HASH_MD5_REGEX.finditer(text):
            try:
                norm = normalization_service.normalize(m.group(0), IndicatorType.FILE_HASH)
                extracted.append({**norm, "context": "Extracted MD5 hash"})
            except ValueError:
                pass

        # 5. Domains
        for m in cls.DOMAIN_REGEX.finditer(text):
            val = m.group(0)
            # Avoid re-matching IP fragments as domains
            if re.fullmatch(r"[0-9.]+", val):
                continue
            try:
                norm = normalization_service.normalize(val, IndicatorType.DOMAIN)
                extracted.append({**norm, "context": "Extracted domain"})
            except ValueError:
                pass

        # Deduplicate
        seen = set()
        deduped = []
        for item in extracted:
            if item["normalized_value"] not in seen:
                seen.add(item["normalized_value"])
                deduped.append(item)
        return deduped


ioc_extraction_service = IOCExtractionService()
extraction_service = ioc_extraction_service
