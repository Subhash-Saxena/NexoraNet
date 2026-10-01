"""Incident Management Service for Step 17.

Handles lifecycle transitions, creation from alerts/cases, IDOR protection,
and analyst assignment.
"""

import random
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.detection import DetectionAlert
from app.models.enums import (
    IncidentClassification,
    IncidentPhase,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
)
from app.models.incident import (
    Incident,
    IncidentAlert,
    IncidentEvidence,
    IncidentNote,
    IncidentTimelineEvent,
)


class IncidentService:
    """Core service for incident lifecycle and case coordination."""

    @classmethod
    def list_incidents(
        cls,
        db: Session,
        status: str | None = None,
        severity: str | None = None,
        classification: str | None = None,
        incident_type: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Incident], int]:
        query = select(Incident).options(
            selectinload(Incident.playbook),
            selectinload(Incident.alerts),
            selectinload(Incident.evidence),
            selectinload(Incident.response_actions),
            selectinload(Incident.technique_mappings),
        )

        if status:
            query = query.where(Incident.status == status)
        if severity:
            query = query.where(Incident.severity == severity)
        if classification:
            query = query.where(Incident.classification == classification)
        if incident_type:
            query = query.where(Incident.incident_type == incident_type)
        if search:
            search_fmt = f"%{search}%"
            query = query.where(
                or_(
                    Incident.incident_id.ilike(search_fmt),
                    Incident.title.ilike(search_fmt),
                    Incident.description.ilike(search_fmt),
                    Incident.lead_analyst.ilike(search_fmt),
                )
            )

        # Count query
        count_query = select(func.count(Incident.id))
        if status:
            count_query = count_query.where(Incident.status == status)
        if severity:
            count_query = count_query.where(Incident.severity == severity)
        if classification:
            count_query = count_query.where(Incident.classification == classification)
        if incident_type:
            count_query = count_query.where(Incident.incident_type == incident_type)
        if search:
            search_fmt = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Incident.incident_id.ilike(search_fmt),
                    Incident.title.ilike(search_fmt),
                    Incident.description.ilike(search_fmt),
                    Incident.lead_analyst.ilike(search_fmt),
                )
            )

        total = db.scalar(count_query) or 0
        incidents = db.execute(
            query.order_by(Incident.detected_at.desc()).offset(skip).limit(limit)
        ).scalars().all()

        return list(incidents), total

    @classmethod
    def get_incident(cls, db: Session, incident_id_or_int: str | int) -> Incident | None:
        query = select(Incident).options(
            selectinload(Incident.playbook),
            selectinload(Incident.alerts).selectinload(IncidentAlert.alert),
            selectinload(Incident.evidence).selectinload(IncidentEvidence.audit_logs),
            selectinload(Incident.timeline_events),
            selectinload(Incident.hypotheses),
            selectinload(Incident.findings),
            selectinload(Incident.response_actions),
            selectinload(Incident.technique_mappings),
            selectinload(Incident.notes),
            selectinload(Incident.case),
        )

        if isinstance(incident_id_or_int, int) or str(incident_id_or_int).isdigit():
            query = query.where(
                or_(
                    Incident.id == int(incident_id_or_int),
                    Incident.incident_id == str(incident_id_or_int),
                )
            )
        else:
            query = query.where(Incident.incident_id == str(incident_id_or_int))

        return db.execute(query).scalar_one_or_none()

    @classmethod
    def create_incident(
        cls,
        db: Session,
        title: str,
        description: str,
        incident_type: str = IncidentType.NETWORK_INTRUSION,
        severity: str = IncidentSeverity.MEDIUM,
        priority: str = "P2",
        playbook_id: int | None = None,
        case_id: int | None = None,
        created_by_id: int | None = None,
        lead_analyst: str | None = None,
        detected_at: datetime | None = None,
    ) -> Incident:
        # Generate next stable ID: INC-YYYY-XXXX
        year = datetime.now(timezone.utc).year
        rand_num = random.randint(1000, 9999)
        candidate_id = f"INC-{year}-{rand_num}"
        while db.scalar(select(Incident).where(Incident.incident_id == candidate_id)):
            rand_num = random.randint(1000, 9999)
            candidate_id = f"INC-{year}-{rand_num}"

        incident = Incident(
            incident_id=candidate_id,
            title=title,
            description=description,
            incident_type=incident_type,
            severity=severity,
            priority=priority,
            status=IncidentStatus.NEW,
            phase=IncidentPhase.DETECTION_ANALYSIS,
            classification=IncidentClassification.UNDETERMINED,
            playbook_id=playbook_id,
            case_id=case_id,
            created_by_id=created_by_id,
            lead_analyst=lead_analyst,
            detected_at=detected_at or datetime.now(timezone.utc),
            simulation_mode=True,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        # Automatically add initial timeline milestone
        timeline_event = IncidentTimelineEvent(
            incident_id=incident.id,
            timestamp=incident.detected_at,
            title="Incident Ticket Created",
            description=f"Incident {incident.incident_id} created in system with severity {severity}.",
            event_category="TRIAGE",
            source="ANALYST",
            is_milestone=True,
            created_by_id=created_by_id,
        )
        db.add(timeline_event)
        db.commit()

        return incident

    @classmethod
    def update_incident(
        cls,
        db: Session,
        incident_id_or_int: str | int,
        updates: dict[str, Any],
        user_id: int | None = None,
    ) -> Incident | None:
        incident = cls.get_incident(db, incident_id_or_int)
        if not incident:
            return None

        now = datetime.now(timezone.utc)
        prev_status = incident.status

        for key, val in updates.items():
            if hasattr(incident, key) and key not in ("id", "incident_id", "simulation_mode"):
                setattr(incident, key, val)

        # Auto-update phase/milestone timestamps based on status progression
        if "status" in updates and updates["status"] != prev_status:
            new_status = updates["status"]
            if new_status == IncidentStatus.CONTAINMENT and not incident.contained_at:
                incident.contained_at = now
                incident.phase = IncidentPhase.CONTAINMENT_ERADICATION_RECOVERY
            elif new_status == IncidentStatus.ERADICATION and not incident.eradicated_at:
                incident.eradicated_at = now
            elif new_status == IncidentStatus.RECOVERY and not incident.recovered_at:
                incident.recovered_at = now
            elif new_status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED, IncidentStatus.FALSE_POSITIVE) and not incident.closed_at:
                incident.closed_at = now
                incident.phase = IncidentPhase.POST_INCIDENT_ACTIVITY

            # Add timeline audit entry
            db.add(IncidentTimelineEvent(
                incident_id=incident.id,
                timestamp=now,
                title=f"Status Transitioned: {prev_status} -> {new_status}",
                description=f"Incident status changed to {new_status} by analyst.",
                event_category="TRIAGE",
                source="ACTION",
                is_milestone=True,
                created_by_id=user_id,
            ))

        db.commit()
        db.refresh(incident)
        return incident

    @classmethod
    def escalate_alert_to_incident(
        cls,
        db: Session,
        alert_id: int,
        title: str | None = None,
        severity: str | None = None,
        playbook_id: int | None = None,
        user_id: int | None = None,
    ) -> Incident:
        alert = db.get(DetectionAlert, alert_id)
        if not alert:
            raise ValueError(f"Alert ID {alert_id} not found")

        rule_title = alert.title if getattr(alert, "title", None) else (alert.rule.name if getattr(alert, "rule", None) else f"Rule {alert.rule_id}")
        inc_title = title or f"Escalated Alert: {rule_title}"
        inc_severity = severity or alert.severity
        alert_time = getattr(alert, "created_at", None) or datetime.now(timezone.utc)
        context_text = getattr(alert, "explanation", "") or getattr(alert, "description", "") or "No raw payload"
        inc_desc = f"Escalated from Detection Alert #{alert.id} ({rule_title}). Observed on {alert_time}. Context: {context_text}"

        incident = cls.create_incident(
            db=db,
            title=inc_title,
            description=inc_desc,
            incident_type=IncidentType.NETWORK_INTRUSION,
            severity=inc_severity,
            priority="P2",
            playbook_id=playbook_id,
            created_by_id=user_id,
            detected_at=alert_time,
        )

        # Link alert
        inc_alert = IncidentAlert(
            incident_id=incident.id,
            alert_id=alert.id,
            role="PRIMARY",
        )
        db.add(inc_alert)

        # Create primary evidence from alert
        rand_suf = random.randint(1000, 9999)
        evidence = IncidentEvidence(
            evidence_id=f"EVD-ALT-{alert.id}-{rand_suf}",
            incident_id=incident.id,
            title=f"Detection Alert: {rule_title}",
            description=f"Initial detection alert that triggered the incident. Severity: {alert.severity}",
            evidence_type="ALERT",
            source_engine="DETECTION_ENGINE",
            source_id=str(alert.id),
            relevance="SUPPORTING",
            is_contained=False,
            collected_by_id=user_id,
            data_payload=str(getattr(alert, "explanation", "") or ""),
        )
        db.add(evidence)

        # Add timeline entry
        timeline_event = IncidentTimelineEvent(
            incident_id=incident.id,
            timestamp=alert_time,
            title=f"Alert Triggered: {rule_title}",
            description=f"Rule ID {alert.rule_id} triggered on source {alert.source_ip}:{alert.source_port} -> {alert.destination_ip}:{alert.destination_port}",
            event_category="DETECTION",
            source="DETECTION_ENGINE",
            source_id=str(alert.id),
            is_milestone=True,
            created_by_id=user_id,
        )
        db.add(timeline_event)

        db.commit()
        db.refresh(incident)
        return incident

    @classmethod
    def add_note(cls, db: Session, incident_id_or_int: str | int, note_text: str, user_id: int | None = None) -> IncidentNote:
        incident = cls.get_incident(db, incident_id_or_int)
        if not incident:
            raise ValueError(f"Incident {incident_id_or_int} not found")

        note = IncidentNote(
            incident_id=incident.id,
            user_id=user_id,
            note=note_text,
            created_at=datetime.now(timezone.utc),
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @classmethod
    def get_metrics(cls, db: Session) -> dict[str, Any]:
        """Calculates educational incident metrics and triage distribution."""
        total = db.scalar(select(func.count(Incident.id))) or 0

        # Status distribution
        status_counts = {}
        for status_val, count in db.execute(
            select(Incident.status, func.count(Incident.id)).group_by(Incident.status)
        ).all():
            status_counts[status_val] = count

        # Severity distribution
        severity_counts = {}
        for sev_val, count in db.execute(
            select(Incident.severity, func.count(Incident.id)).group_by(Incident.severity)
        ).all():
            severity_counts[sev_val] = count

        # Type distribution
        type_counts = {}
        for type_val, count in db.execute(
            select(Incident.incident_type, func.count(Incident.id)).group_by(Incident.incident_type)
        ).all():
            type_counts[type_val] = count

        # Active vs Closed
        active_statuses = [
            IncidentStatus.NEW,
            IncidentStatus.TRIAGED,
            IncidentStatus.INVESTIGATING,
            IncidentStatus.CONTAINMENT,
            IncidentStatus.ERADICATION,
            IncidentStatus.RECOVERY,
            IncidentStatus.MONITORING,
        ]
        active_count = db.scalar(
            select(func.count(Incident.id)).where(Incident.status.in_(active_statuses))
        ) or 0

        closed_count = total - active_count

        return {
            "total_incidents": total,
            "active_incidents": active_count,
            "closed_incidents": closed_count,
            "by_status": status_counts,
            "by_severity": severity_counts,
            "by_type": type_counts,
        }
