"""SIEM Cross-Platform Integration Service for NexoraNet Step 15.

Connects SIEM logs and CorrelationAlerts with:
- Step 11 Detection & Step 12 SOC Investigation
- Step 13 Threat Intelligence (IOC extraction & observation)
- Step 14 Threat Hunting (Campaign launch & pivot initialization)
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    HuntConfidence,
    HuntEvidenceRelevance,
    HuntEvidenceType,
    HuntHypothesisStatus,
)
from app.models.siem import CorrelationAlert, SecurityEvent
from app.models.soc import (
    Investigation,
    InvestigationEvidence,
    InvestigationHypothesis,
    InvestigationNote,
)
from app.models.threat_hunting import (
    ThreatHunt,
    ThreatHuntEvidence,
    ThreatHuntHypothesis,
)
from app.models.threat_intel import Indicator, IndicatorObservation, ThreatIntelSource
from app.services.threat_hunting.hunt_service import ThreatHuntService


class SiemIntegrationService:
    """Coordinates investigations across SOC, Threat Intel, and Threat Hunting."""

    @classmethod
    def investigate_in_soc(
        cls,
        db: Session,
        event_id: str | None = None,
        correlation_alert_id: int | None = None,
        user_id: int | None = None,
    ) -> Investigation:
        """Promote a SIEM security event or correlation alert into a SOC Investigation."""
        title = "SIEM Log Investigation"
        description = "Automated escalation from SIEM security log telemetry."
        priority = "P3"
        evidence_summary = ""

        alert_obj: CorrelationAlert | None = None
        event_obj: SecurityEvent | None = None

        if correlation_alert_id:
            alert_obj = db.execute(
                select(CorrelationAlert).where(CorrelationAlert.id == correlation_alert_id)
            ).scalar_one_or_none()
            if alert_obj:
                title = f"SOC Triage: {alert_obj.title}"
                description = f"Escalated from SIEM Correlation Alert {alert_obj.alert_id}.\n{alert_obj.evidence_summary}"
                priority = "P2" if alert_obj.severity in ("HIGH", "CRITICAL") else "P3"
                evidence_summary = alert_obj.evidence_summary

        elif event_id:
            event_obj = db.execute(
                select(SecurityEvent).where(SecurityEvent.event_id == event_id)
            ).scalar_one_or_none()
            if event_obj:
                title = f"SIEM Log Triage: {event_obj.event_type} on {event_obj.host or event_obj.source_ip}"
                description = f"Investigation initiated from security event {event_obj.event_id}.\nAction: {event_obj.action}\nMessage: {event_obj.message}"
                priority = "P2" if event_obj.severity in ("HIGH", "CRITICAL") else "P3"
                evidence_summary = f"Event: {event_obj.event_type}, Host: {event_obj.host}, User: {event_obj.username}, Src: {event_obj.source_ip}"

        # Generate sequential SOC investigation ID e.g. INV-2026-0001
        year = datetime.now(timezone.utc).year
        inv_code = f"INV-{year}-{uuid.uuid4().hex[:6].upper()}"

        investigation = Investigation(
            investigation_id=inv_code,
            title=title[:255],
            description=description,
            status="OPEN",
            priority=priority,
            classification="UNREVIEWED",
            created_by_id=user_id,
            started_at=datetime.now(timezone.utc),
        )
        db.add(investigation)
        db.flush()

        # Add initial evidence note
        note = InvestigationNote(
            investigation_id=investigation.id,
            user_id=user_id,
            note=f"Initial evidence context:\n{evidence_summary or description}",
        )
        db.add(note)

        # Add preliminary hypothesis
        hypo = InvestigationHypothesis(
            investigation_id=investigation.id,
            hypothesis_text=f"Telemetry indicates potential security anomaly requiring validation: {title}",
            status="UNTESTED",
            created_by_id=user_id,
        )
        db.add(hypo)

        # Add raw event evidence reference
        ev_item = InvestigationEvidence(
            investigation_id=investigation.id,
            evidence_type="LOG_EVENT",
            reference_id=event_id or (alert_obj.alert_id if alert_obj else None),
            description=evidence_summary[:500] if evidence_summary else title,
            evidence_data=json.dumps({"event_id": event_id, "correlation_alert_id": correlation_alert_id}),
        )
        db.add(ev_item)

        if alert_obj:
            alert_obj.soc_alert_id = investigation.id

        db.commit()
        db.refresh(investigation)
        return investigation

    @classmethod
    def start_threat_hunt(
        cls,
        db: Session,
        event_id: str | None = None,
        correlation_alert_id: int | None = None,
        user_id: int = 1,
        hypothesis_statement: str | None = None,
    ) -> ThreatHunt:
        """Launch a proactive Threat Hunt initialized from SIEM observables."""
        event_obj: SecurityEvent | None = None
        alert_obj: CorrelationAlert | None = None

        pivot_type = "IP"
        pivot_val = "192.0.2.1"
        hunt_title = "Threat Hunt: Suspicious SIEM Log Pattern"
        hunt_desc = "Initiated from SIEM security log analysis."

        if event_id:
            event_obj = db.execute(
                select(SecurityEvent).where(SecurityEvent.event_id == event_id)
            ).scalar_one_or_none()
            if event_obj:
                if event_obj.source_ip:
                    pivot_type = "IP"
                    pivot_val = event_obj.source_ip
                elif event_obj.domain:
                    pivot_type = "DOMAIN"
                    pivot_val = event_obj.domain
                elif event_obj.destination_ip:
                    pivot_type = "IP"
                    pivot_val = event_obj.destination_ip
                elif event_obj.destination_port:
                    pivot_type = "PORT"
                    pivot_val = str(event_obj.destination_port)

                hunt_title = f"Hunt: Activity around {pivot_val} ({event_obj.event_type})"
                hunt_desc = f"Originating SIEM Event: {event_obj.event_id}\nHost: {event_obj.host}\nUser: {event_obj.username}\nMessage: {event_obj.message}"

        elif correlation_alert_id:
            alert_obj = db.execute(
                select(CorrelationAlert).where(CorrelationAlert.id == correlation_alert_id)
            ).scalar_one_or_none()
            if alert_obj:
                hunt_title = f"Hunt: {alert_obj.title}"
                hunt_desc = f"Originating Correlation Alert: {alert_obj.alert_id}\n{alert_obj.evidence_summary}"
                try:
                    ctx = json.loads(alert_obj.source_context or "{}")
                    if "source_ip" in ctx:
                        pivot_type = "IP"
                        pivot_val = ctx["source_ip"]
                    elif "host" in ctx:
                        pivot_type = "IP"
                        pivot_val = ctx["host"]
                except (json.JSONDecodeError, TypeError):
                    pass

        objective = f"Interrogate telemetry surrounding pivot {pivot_type}:{pivot_val} to identify scope and lateral spread."
        hunt = ThreatHuntService.create_hunt(
            db=db,
            user_id=user_id,
            title=hunt_title,
            description=hunt_desc,
            objective=objective,
            dataset_id=None,
            difficulty="INTERMEDIATE",
            initial_pivot_type=pivot_type,
            initial_pivot_value=pivot_val,
        )

        # Seed initial hypothesis
        statement = hypothesis_statement or f"Host or identity associated with {pivot_val} exhibits anomalous behavior."
        hypo = ThreatHuntHypothesis(
            hunt_id=hunt.id,
            title=f"Anomaly investigation: {pivot_type} {pivot_val}",
            description=statement,
            status=HuntHypothesisStatus.OPEN.value,
            confidence=HuntConfidence.MEDIUM.value,
            analyst_reasoning=f"Query all connections, DNS queries, and authentication events matching {pivot_val}.",
        )
        db.add(hypo)
        db.flush()

        # Bind initial evidence
        ev = ThreatHuntEvidence(
            hunt_id=hunt.id,
            hypothesis_id=hypo.id,
            evidence_type=HuntEvidenceType.EVENT.value,
            source_id=f"SIEM-{event_obj.event_id if event_obj else (alert_obj.alert_id if alert_obj else 'OBSERVABLE')}",
            description=hunt_desc[:500],
            relevance=HuntEvidenceRelevance.CONTEXT.value,
            analyst_note="Imported as starting context directly from SIEM workspace.",
        )
        db.add(ev)
        db.commit()
        db.refresh(hunt)
        return hunt

    @classmethod
    def extract_and_investigate_ioc(
        cls, db: Session, event_id: str
    ) -> list[dict[str, Any]]:
        """Extract candidate IOCs from a SecurityEvent and link to Step 13 Threat Intel."""
        event_obj = db.execute(
            select(SecurityEvent).where(SecurityEvent.event_id == event_id)
        ).scalar_one_or_none()
        if not event_obj:
            raise ValueError(f"Event with ID {event_id} not found.")

        # Candidate IOCs
        candidates: list[tuple[str, str]] = []  # (ioc_type, value)
        if event_obj.source_ip:
            candidates.append(("IP_ADDRESS", event_obj.source_ip))
        if event_obj.destination_ip:
            candidates.append(("IP_ADDRESS", event_obj.destination_ip))
        if event_obj.domain:
            candidates.append(("DOMAIN", event_obj.domain.lower()))
        if event_obj.url:
            candidates.append(("URL", event_obj.url))
        if event_obj.file_hash:
            candidates.append(("FILE_HASH", event_obj.file_hash.lower()))

        # Get default synthetic source
        source = db.execute(
            select(ThreatIntelSource).where(ThreatIntelSource.name.ilike("%Synthetic%"))
        ).scalars().first()
        source_id = source.id if source else None

        results = []
        for ioc_type, val in candidates:
            # Query existing indicator
            ind = db.execute(
                select(Indicator).where(Indicator.normalized_value == val)
            ).scalar_one_or_none()

            if not ind:
                # Create as benign or suspicious observation
                code = f"IOC-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"
                ind = Indicator(
                    indicator_id=code,
                    indicator_type=ioc_type,
                    value=val,
                    normalized_value=val,
                    display_value=val,
                    source_id=source_id,
                    source_name="SIEM Telemetry Observation",
                    classification="UNKNOWN",
                    confidence="MEDIUM",
                    severity="INFO",
                    status="ACTIVE",
                )
                db.add(ind)
                db.flush()

            # Record observation from this event
            obs = IndicatorObservation(
                indicator_id=ind.id,
                observation_type="SIEM_LOG",
                observed_at=event_obj.timestamp,
                context_data=json.dumps({
                    "event_id": event_obj.event_id,
                    "dataset_id": event_obj.dataset_id,
                    "host": event_obj.host,
                    "message": event_obj.message,
                }),
            )
            db.add(obs)
            results.append({
                "indicator_id": ind.indicator_id,
                "type": ind.indicator_type,
                "value": ind.display_value,
                "classification": ind.classification,
                "confidence": ind.confidence,
                "severity": ind.severity,
            })

        db.commit()
        return results
