"""Endpoint Security cross-platform integration service.

Pivots from synthetic endpoint telemetry into:
- Step 13 Threat Intelligence (IOC extraction, enrichment, and reputation lookup)
- Step 14 Threat Hunting (Campaign launch with host and entity seeds)
- Step 12 SOC Case Management (Investigation escalation)
- Step 15 SIEM Log Normalization (Cross-layer correlation)
- Step 10 PCAP Engine (Packet trace linkage)
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.endpoint_security import EndpointEvent, EndpointHost
from app.models.enums import (
    HuntConfidence,
    HuntEvidenceRelevance,
    HuntEvidenceType,
    HuntHypothesisStatus,
)
from app.models.pcap import ParsedPacket
from app.models.siem import SecurityEvent
from app.models.soc import (
    Investigation,
    InvestigationHypothesis,
    InvestigationNote,
)
from app.models.threat_hunting import (
    ThreatHunt,
    ThreatHuntEvidence,
    ThreatHuntHypothesis,
)
from app.models.threat_intel import Indicator
from app.services.threat_hunting.hunt_service import ThreatHuntService


class EndpointIntegrationService:
    """Provides pivots and contextual correlation between endpoints and other security engines."""

    @classmethod
    def pivot_to_threat_intel(
        cls, db: Session, event: EndpointEvent, user_id: int | None = None
    ) -> dict[str, Any]:
        """Extract observables (hash, IP, domain) from event and enrich with Threat Intel."""
        observables: list[dict[str, Any]] = []

        # 1. File Hash
        if event.file_hash:
            ioc = db.execute(
                select(Indicator).where(Indicator.normalized_value == event.file_hash.lower())
            ).scalars().first()
            observables.append(
                {
                    "type": "FILE_HASH",
                    "value": event.file_hash,
                    "found_in_threat_intel": ioc is not None,
                    "indicator_id": ioc.indicator_id if ioc else None,
                    "classification": ioc.classification if ioc else "SUSPICIOUS",
                    "confidence": ioc.confidence if ioc else "MEDIUM",
                    "reputation_score": ioc.reputation_score if ioc else 75,
                }
            )

        # 2. Remote IP
        remote_ip = event.destination_ip or event.source_ip
        if remote_ip and not remote_ip.startswith("127."):
            ioc = db.execute(
                select(Indicator).where(Indicator.normalized_value == remote_ip)
            ).scalars().first()
            observables.append(
                {
                    "type": "IP_ADDRESS",
                    "value": remote_ip,
                    "found_in_threat_intel": ioc is not None,
                    "indicator_id": ioc.indicator_id if ioc else None,
                    "classification": ioc.classification if ioc else "UNKNOWN",
                    "confidence": ioc.confidence if ioc else "LOW",
                    "reputation_score": ioc.reputation_score if ioc else 50,
                }
            )

        # 3. Domain
        if event.domain:
            ioc = db.execute(
                select(Indicator).where(Indicator.normalized_value == event.domain.lower())
            ).scalars().first()
            observables.append(
                {
                    "type": "DOMAIN",
                    "value": event.domain,
                    "found_in_threat_intel": ioc is not None,
                    "indicator_id": ioc.indicator_id if ioc else None,
                    "classification": ioc.classification if ioc else "SUSPICIOUS",
                    "confidence": ioc.confidence if ioc else "MEDIUM",
                    "reputation_score": ioc.reputation_score if ioc else 70,
                }
            )

        return {
            "event_id": event.event_id,
            "host_id": event.host_id,
            "observables": observables,
            "analyst_guidance": (
                "An Indicator of Compromise (IOC) is evidence, not automatically proof of compromise. "
                "Verify host telemetry context, process parentage, and network behavior."
            ),
        }

    @classmethod
    def start_threat_hunt(
        cls, db: Session, event: EndpointEvent, user_id: int
    ) -> ThreatHunt:
        """Launch a Step 14 Threat Hunting campaign initialized with endpoint event context."""
        host = db.get(EndpointHost, event.host_id)
        host_name = host.hostname if host else f"Host-{event.host_id}"

        # Choose primary pivot
        pivot_type = "HOST"
        pivot_val = host_name
        if event.file_hash:
            pivot_type = "FILE_HASH"
            pivot_val = event.file_hash
        elif event.domain:
            pivot_type = "DOMAIN"
            pivot_val = event.domain
        elif event.destination_ip:
            pivot_type = "IP_ADDRESS"
            pivot_val = event.destination_ip
        elif event.process_name:
            pivot_type = "PROCESS"
            pivot_val = event.process_name

        hunt_code = ThreatHuntService.generate_hunt_id(db)

        title = f"Endpoint Hunt: {pivot_type} {pivot_val} on {host_name}"
        desc = (
            f"Proactive threat hunt initiated from endpoint event {event.event_id} ({event.event_type}).\n"
            f"Host: {host_name} | User: {event.username or 'SYSTEM'} | Process: {event.process_name or 'N/A'}"
        )
        obj = f"Determine the scope and impact of {pivot_type} {pivot_val} across endpoint telemetry."

        hunt = ThreatHunt(
            hunt_id=hunt_code,
            title=title[:255],
            description=desc,
            objective=obj,
            status="IN_PROGRESS",
            difficulty="INTERMEDIATE",
            user_id=user_id,
            initial_pivot_type=pivot_type,
            initial_pivot_value=pivot_val,
            started_at=datetime.now(timezone.utc),
        )
        db.add(hunt)
        db.flush()

        # Seed working hypothesis
        hyp = ThreatHuntHypothesis(
            hunt_id=hunt.id,
            title=f"Activity related to {pivot_val} may indicate adversarial presence",
            description=(
                f"Observable {pivot_val} was flagged on host {host_name}. "
                "Investigating whether other processes or hosts interacted with this entity."
            ),
            status=HuntHypothesisStatus.OPEN.value,
            confidence=HuntConfidence.MEDIUM.value,
            analyst_reasoning="Triggered via 1-click pivot from endpoint security investigation.",
        )
        db.add(hyp)
        db.flush()

        # Seed initial evidence
        ev = ThreatHuntEvidence(
            hunt_id=hunt.id,
            hypothesis_id=hyp.id,
            source_id=event.event_id,
            description=f"Action: {event.action or event.event_type} | Result: {event.result or 'UNKNOWN'}",
            evidence_type=HuntEvidenceType.EVENT.value,
            relevance=HuntEvidenceRelevance.SUPPORTING.value,
            data_snapshot=json.dumps(
                {
                    "event_id": event.event_id,
                    "host": host_name,
                    "process": event.process_name,
                    "command": event.command_summary,
                    "file_hash": event.file_hash,
                    "dest_ip": event.destination_ip,
                }
            ),
        )
        db.add(ev)
        db.commit()
        db.refresh(hunt)
        return hunt

    @classmethod
    def investigate_in_soc(
        cls, db: Session, event: EndpointEvent, user_id: int
    ) -> Investigation:
        """Escalate an endpoint alert into a Step 12 SOC Investigation."""
        host = db.get(EndpointHost, event.host_id)
        host_name = host.hostname if host else f"Host-{event.host_id}"

        title = f"Endpoint Alert: {event.event_type} on {host_name}"
        desc = (
            f"Escalated from endpoint event {event.event_id}.\n"
            f"Category: {event.event_category} | Severity: {event.severity}\n"
            f"Process: {event.process_name or 'N/A'} (PID {event.process_id or 'N/A'})\n"
            f"Summary: {event.command_summary or event.raw_event_reference or 'N/A'}"
        )
        priority = "P1" if event.severity == "CRITICAL" else ("P2" if event.severity == "HIGH" else "P3")

        year = datetime.now(timezone.utc).year
        inv_code = f"INV-{year}-{uuid.uuid4().hex[:6].upper()}"

        inv = Investigation(
            investigation_id=inv_code,
            title=title[:255],
            description=desc,
            status="OPEN",
            priority=priority,
            classification="UNREVIEWED",
            created_by_id=user_id,
            started_at=datetime.now(timezone.utc),
        )
        db.add(inv)
        db.flush()

        # Add initial note
        note = InvestigationNote(
            investigation_id=inv.id,
            user_id=user_id,
            note=f"Escalated from Endpoint Security Workbench:\n{desc}",
        )
        db.add(note)

        # Add hypothesis
        hyp = InvestigationHypothesis(
            investigation_id=inv.id,
            hypothesis_text=f"The endpoint alert on {host_name} represents actionable malicious behavior requiring containment.",
            status="OPEN",
        )
        db.add(hyp)

        db.commit()
        db.refresh(inv)
        return inv

    @classmethod
    def correlate_with_siem(
        cls, db: Session, event: EndpointEvent
    ) -> list[dict[str, Any]]:
        """Find matching SIEM security events within the temporal window."""
        host = db.get(EndpointHost, event.host_id)
        host_name = host.hostname if host else ""

        window_start = event.timestamp - timedelta(minutes=15)
        window_end = event.timestamp + timedelta(minutes=15)

        stmt = select(SecurityEvent).where(
            SecurityEvent.timestamp >= window_start,
            SecurityEvent.timestamp <= window_end,
            or_(
                SecurityEvent.host.ilike(f"%{host_name}%"),
                SecurityEvent.source_ip == event.source_ip,
                SecurityEvent.destination_ip == event.destination_ip,
                SecurityEvent.username == event.username,
            ),
        ).limit(10)

        siem_events = list(db.scalars(stmt).all())
        return [
            {
                "id": s.id,
                "event_id": s.event_id,
                "timestamp": s.timestamp.isoformat() if s.timestamp else None,
                "event_category": s.event_category,
                "action": s.action,
                "host": s.host,
                "username": s.username,
                "source_ip": s.source_ip,
                "destination_ip": s.destination_ip,
                "severity": s.severity,
                "message": s.message,
            }
            for s in siem_events
        ]

    @classmethod
    def correlate_with_pcap(
        cls, db: Session, event: EndpointEvent
    ) -> list[dict[str, Any]]:
        """If network connection has IP and port, find matching packets in offline PCAPs."""
        if not event.destination_ip or not event.destination_port:
            return []

        stmt = select(ParsedPacket).where(
            or_(
                ParsedPacket.destination_ip == event.destination_ip,
                ParsedPacket.source_ip == event.destination_ip,
            ),
            or_(
                ParsedPacket.destination_port == event.destination_port,
                ParsedPacket.source_port == event.destination_port,
            ),
        ).limit(5)

        packets = list(db.scalars(stmt).all())
        return [
            {
                "id": p.id,
                "capture_id": p.capture_id,
                "packet_number": p.packet_number,
                "protocol": p.protocol,
                "source_ip": p.source_ip,
                "destination_ip": p.destination_ip,
                "length": p.length,
                "summary": p.summary,
            }
            for p in packets
        ]
