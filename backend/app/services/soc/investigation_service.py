"""Investigation Management and Forensic Reporting Service."""

import json
from datetime import datetime, timezone
from typing import Any

from app.models.detection import DetectionAlert
from app.models.enums import (
    FindingConfidence,
    HypothesisStatus,
    InvestigationAlertRelationship,
    InvestigationStatus,
    TrainingPriority,
    TriageClassification,
)
from app.models.soc import (
    Investigation,
    InvestigationAlert,
    InvestigationEvidence,
    InvestigationFinding,
    InvestigationHypothesis,
    InvestigationNote,
)
from app.models.user import User
from app.services.soc.audit_service import soc_audit_service
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class InvestigationService:
    """Manages the full lifecycle of SOC investigations."""

    @classmethod
    def generate_investigation_id(cls, db: Session) -> str:
        """Generate human-readable sequential identifier e.g. INV-2026-0001."""
        year = datetime.now(timezone.utc).year
        count = db.query(Investigation).count() + 1
        return f"INV-{year}-{count:04d}"

    @classmethod
    def create_investigation(
        cls,
        db: Session,
        creator: User,
        title: str,
        description: str,
        priority: TrainingPriority = TrainingPriority.P3,
        alert_ids: list[int] | None = None,
        case_id: int | None = None,
    ) -> Investigation:
        """Create a new investigation and bind initial alerts."""
        inv_id_str = cls.generate_investigation_id(db)

        inv = Investigation(
            investigation_id=inv_id_str,
            title=title.strip(),
            description=description.strip(),
            status=InvestigationStatus.OPEN.value,
            priority=priority.value if hasattr(priority, "value") else str(priority),
            classification=TriageClassification.UNREVIEWED.value,
            created_by_id=creator.id,
            assigned_to_id=creator.id,
            started_at=datetime.now(timezone.utc),
        )
        db.add(inv)
        db.flush()

        # Link initial alerts
        if alert_ids:
            for aid in alert_ids:
                alert = db.query(DetectionAlert).filter(DetectionAlert.id == aid).first()
                if alert:
                    inv_alert = InvestigationAlert(
                        investigation_id=inv.id,
                        alert_id=alert.id,
                        relationship_type=InvestigationAlertRelationship.PRIMARY.value,
                        added_at=datetime.now(timezone.utc),
                    )
                    db.add(inv_alert)
                    # Automatically update alert status to INVESTIGATING if still NEW
                    if alert.status == "NEW":
                        alert.status = "INVESTIGATING"

        # Link case if specified
        if case_id:
            from app.models.soc import Case, CaseInvestigation
            case = db.query(Case).filter(Case.id == case_id).first()
            if case:
                case_inv = CaseInvestigation(
                    case_id=case.id,
                    investigation_id=inv.id,
                    added_at=datetime.now(timezone.utc),
                )
                db.add(case_inv)

        db.commit()
        db.refresh(inv)

        soc_audit_service.log_action(
            db,
            actor=creator,
            action="CREATE_INVESTIGATION",
            object_type="INVESTIGATION",
            object_id=inv.investigation_id,
            details={"title": inv.title, "priority": inv.priority},
        )

        return inv

    @classmethod
    def get_investigation(cls, db: Session, investigation_id: int) -> Investigation:
        """Fetch investigation by ID with 404 validation."""
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation with ID {investigation_id} not found.",
            )
        return inv

    @classmethod
    def update_investigation(
        cls,
        db: Session,
        actor: User,
        investigation_id: int,
        title: str | None = None,
        description: str | None = None,
        status_val: InvestigationStatus | None = None,
        priority: TrainingPriority | None = None,
        classification: TriageClassification | None = None,
        conclusion: str | None = None,
        recommendations: str | None = None,
        assigned_to_id: int | None = None,
    ) -> Investigation:
        """Update investigation details and audit transition."""
        inv = cls.get_investigation(db, investigation_id)

        changes: dict[str, Any] = {}
        if title is not None:
            inv.title = title.strip()
            changes["title"] = inv.title
        if description is not None:
            inv.description = description.strip()
            changes["description"] = inv.description
        if status_val is not None:
            old_status = inv.status
            inv.status = status_val.value if hasattr(status_val, "value") else str(status_val)
            changes["status"] = {"old": old_status, "new": inv.status}
            if inv.status in (InvestigationStatus.CLOSED.value, InvestigationStatus.RESOLVED.value):
                inv.closed_at = datetime.now(timezone.utc)
        if priority is not None:
            inv.priority = priority.value if hasattr(priority, "value") else str(priority)
            changes["priority"] = inv.priority
        if classification is not None:
            inv.classification = classification.value if hasattr(classification, "value") else str(classification)
            changes["classification"] = inv.classification
        if conclusion is not None:
            inv.conclusion = conclusion.strip()
            changes["conclusion"] = inv.conclusion
        if recommendations is not None:
            inv.recommendations = recommendations.strip()
            changes["recommendations"] = inv.recommendations
        if assigned_to_id is not None:
            inv.assigned_to_id = assigned_to_id
            changes["assigned_to_id"] = assigned_to_id

        db.commit()
        db.refresh(inv)

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="UPDATE_INVESTIGATION",
            object_type="INVESTIGATION",
            object_id=inv.investigation_id,
            details=changes,
        )

        return inv

    @classmethod
    def add_alert(
        cls,
        db: Session,
        actor: User,
        investigation_id: int,
        alert_id: int,
        relationship_type: InvestigationAlertRelationship = InvestigationAlertRelationship.RELATED,
    ) -> InvestigationAlert:
        """Associate an alert with an investigation."""
        inv = cls.get_investigation(db, investigation_id)
        alert = db.query(DetectionAlert).filter(DetectionAlert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

        # Check existing
        existing = (
            db.query(InvestigationAlert)
            .filter(
                InvestigationAlert.investigation_id == inv.id,
                InvestigationAlert.alert_id == alert.id,
            )
            .first()
        )
        if existing:
            return existing

        inv_alert = InvestigationAlert(
            investigation_id=inv.id,
            alert_id=alert.id,
            relationship_type=relationship_type.value if hasattr(relationship_type, "value") else str(relationship_type),
            added_at=datetime.now(timezone.utc),
        )
        db.add(inv_alert)
        db.commit()
        db.refresh(inv_alert)

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="ADD_ALERT_TO_INVESTIGATION",
            object_type="INVESTIGATION",
            object_id=inv.investigation_id,
            details={"alert_id": alert.id, "alert_title": alert.title},
        )
        return inv_alert

    @classmethod
    def add_evidence(
        cls,
        db: Session,
        actor: User,
        investigation_id: int,
        evidence_type: str,
        description: str,
        reference_id: str | None = None,
        capture_id: int | None = None,
        packet_number: int | None = None,
        evidence_data: dict[str, Any] | None = None,
    ) -> InvestigationEvidence:
        """Attach evidence reference to investigation."""
        inv = cls.get_investigation(db, investigation_id)

        ev = InvestigationEvidence(
            investigation_id=inv.id,
            evidence_type=evidence_type,
            reference_id=reference_id,
            capture_id=capture_id,
            packet_number=packet_number,
            description=description.strip(),
            evidence_data=json.dumps(evidence_data) if evidence_data else None,
            created_at=datetime.now(timezone.utc),
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev

    @classmethod
    def create_hypothesis(
        cls,
        db: Session,
        actor: User,
        investigation_id: int,
        hypothesis_text: str,
        status_val: HypothesisStatus = HypothesisStatus.UNTESTED,
        reasoning: str | None = None,
        supporting_evidence_ids: list[str] | None = None,
    ) -> InvestigationHypothesis:
        """Formulate an analytical hypothesis."""
        inv = cls.get_investigation(db, investigation_id)

        hyp = InvestigationHypothesis(
            investigation_id=inv.id,
            hypothesis_text=hypothesis_text.strip(),
            status=status_val.value if hasattr(status_val, "value") else str(status_val),
            reasoning=reasoning.strip() if reasoning else None,
            supporting_evidence_ids=json.dumps(supporting_evidence_ids or []),
            created_by_id=actor.id,
        )
        db.add(hyp)
        db.commit()
        db.refresh(hyp)
        return hyp

    @classmethod
    def update_hypothesis(
        cls,
        db: Session,
        actor: User,
        hypothesis_id: int,
        status_val: HypothesisStatus | None = None,
        reasoning: str | None = None,
        supporting_evidence_ids: list[str] | None = None,
    ) -> InvestigationHypothesis:
        """Update hypothesis status, reasoning, and evidence binding."""
        hyp = db.query(InvestigationHypothesis).filter(InvestigationHypothesis.id == hypothesis_id).first()
        if not hyp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hypothesis not found.")

        if status_val is not None:
            hyp.status = status_val.value if hasattr(status_val, "value") else str(status_val)
        if reasoning is not None:
            hyp.reasoning = reasoning.strip()
        if supporting_evidence_ids is not None:
            hyp.supporting_evidence_ids = json.dumps(supporting_evidence_ids)

        db.commit()
        db.refresh(hyp)
        return hyp

    @classmethod
    def create_finding(
        cls,
        db: Session,
        actor: User,
        investigation_id: int,
        title: str,
        description: str,
        evidence_summary: str | None = None,
        confidence: FindingConfidence = FindingConfidence.MEDIUM,
    ) -> InvestigationFinding:
        """Log a substantiated investigative finding."""
        inv = cls.get_investigation(db, investigation_id)

        finding = InvestigationFinding(
            investigation_id=inv.id,
            title=title.strip(),
            description=description.strip(),
            evidence_summary=evidence_summary.strip() if evidence_summary else None,
            confidence=confidence.value if hasattr(confidence, "value") else str(confidence),
            created_by_id=actor.id,
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return finding

    @classmethod
    def add_note(
        cls,
        db: Session,
        actor: User,
        investigation_id: int,
        note_text: str,
    ) -> InvestigationNote:
        """Append an analyst note to an ongoing investigation."""
        inv = cls.get_investigation(db, investigation_id)

        note = InvestigationNote(
            investigation_id=inv.id,
            user_id=actor.id,
            note=note_text.strip(),
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @classmethod
    def generate_report(cls, db: Session, investigation_id: int) -> dict[str, Any]:
        """Compile a comprehensive JSON forensic investigation report."""
        inv = cls.get_investigation(db, investigation_id)

        alerts_data = []
        for ia in inv.alerts:
            a = ia.alert
            if a:
                alerts_data.append({
                    "id": a.id,
                    "title": a.title,
                    "severity": a.severity,
                    "confidence": a.confidence,
                    "rule": a.rule.name if a.rule else a.title,
                    "source": f"{a.source_ip}:{a.source_port}" if a.source_ip else None,
                    "destination": f"{a.destination_ip}:{a.destination_port}" if a.destination_ip else None,
                    "relationship_role": ia.relationship_type,
                })

        evidence_data = []
        for e in inv.evidence:
            evidence_data.append({
                "id": e.id,
                "type": e.evidence_type,
                "reference_id": e.reference_id,
                "packet_number": e.packet_number,
                "description": e.description,
                "payload": json.loads(e.evidence_data) if e.evidence_data else None,
            })

        hypotheses_data = []
        for h in inv.hypotheses:
            hypotheses_data.append({
                "id": h.id,
                "hypothesis": h.hypothesis_text,
                "status": h.status,
                "reasoning": h.reasoning,
                "supporting_evidence": json.loads(h.supporting_evidence_ids) if h.supporting_evidence_ids else [],
            })

        findings_data = []
        for f in inv.findings:
            findings_data.append({
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "evidence_summary": f.evidence_summary,
                "confidence": f.confidence,
            })

        notes_data = []
        for n in inv.notes:
            notes_data.append({
                "id": n.id,
                "author": n.user.display_name if n.user else "Analyst",
                "note": n.note,
                "created_at": n.created_at.isoformat(),
            })

        return {
            "platform": "NexoraNet SOC Forensic Lab",
            "report_type": "SOC_INVESTIGATION_REPORT",
            "environment": "Offline Defensive Training Environment",
            "investigation_id": inv.investigation_id,
            "title": inv.title,
            "description": inv.description,
            "status": inv.status,
            "priority": inv.priority,
            "classification": inv.classification,
            "created_by": inv.created_by.display_name if inv.created_by else "SOC Analyst",
            "assigned_to": inv.assigned_to.display_name if inv.assigned_to else "Unassigned",
            "started_at": inv.started_at.isoformat(),
            "closed_at": inv.closed_at.isoformat() if inv.closed_at else None,
            "conclusion": inv.conclusion,
            "recommendations": inv.recommendations,
            "summary_metrics": {
                "total_alerts": len(alerts_data),
                "total_evidence_items": len(evidence_data),
                "total_hypotheses": len(hypotheses_data),
                "total_findings": len(findings_data),
                "total_notes": len(notes_data),
            },
            "alerts": alerts_data,
            "evidence": evidence_data,
            "hypotheses": hypotheses_data,
            "findings": findings_data,
            "notes": notes_data,
        }


investigation_service = InvestigationService()
