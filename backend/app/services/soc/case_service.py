"""Lightweight SOC Case Management Service."""

from datetime import datetime, timezone
from typing import Any

from app.models.detection import DetectionAlert
from app.models.enums import CaseStatus, TrainingPriority
from app.models.soc import Case, CaseAlert, CaseInvestigation, CaseNote, Investigation
from app.models.user import User
from app.services.soc.audit_service import soc_audit_service
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class CaseService:
    """Manages cases grouping investigations, alerts, and executive notes."""

    @classmethod
    def generate_case_id(cls, db: Session) -> str:
        """Generate human-readable sequential identifier e.g. CASE-2026-0001."""
        year = datetime.now(timezone.utc).year
        count = db.query(Case).count() + 1
        return f"CASE-{year}-{count:04d}"

    @classmethod
    def create_case(
        cls,
        db: Session,
        creator: User,
        title: str,
        description: str,
        priority: TrainingPriority = TrainingPriority.P3,
        alert_ids: list[int] | None = None,
        investigation_ids: list[int] | None = None,
    ) -> Case:
        """Create a new case."""
        case_id_str = cls.generate_case_id(db)

        case = Case(
            case_id=case_id_str,
            title=title.strip(),
            description=description.strip(),
            status=CaseStatus.OPEN.value,
            priority=priority.value if hasattr(priority, "value") else str(priority),
            created_by_id=creator.id,
            assigned_to_id=creator.id,
        )
        db.add(case)
        db.flush()

        # Link alerts
        if alert_ids:
            for aid in alert_ids:
                alert = db.query(DetectionAlert).filter(DetectionAlert.id == aid).first()
                if alert:
                    db.add(CaseAlert(case_id=case.id, alert_id=alert.id))

        # Link investigations
        if investigation_ids:
            for iid in investigation_ids:
                inv = db.query(Investigation).filter(Investigation.id == iid).first()
                if inv:
                    db.add(CaseInvestigation(case_id=case.id, investigation_id=inv.id))

        db.commit()
        db.refresh(case)

        soc_audit_service.log_action(
            db,
            actor=creator,
            action="CREATE_CASE",
            object_type="CASE",
            object_id=case.case_id,
            details={"title": case.title, "priority": case.priority},
        )

        return case

    @classmethod
    def get_case(cls, db: Session, case_id: int) -> Case:
        """Fetch case by ID with 404 validation."""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found.",
            )
        return case

    @classmethod
    def update_case(
        cls,
        db: Session,
        actor: User,
        case_id: int,
        title: str | None = None,
        description: str | None = None,
        status_val: CaseStatus | None = None,
        priority: TrainingPriority | None = None,
        summary: str | None = None,
        assigned_to_id: int | None = None,
    ) -> Case:
        """Update case details."""
        case = cls.get_case(db, case_id)

        changes: dict[str, Any] = {}
        if title is not None:
            case.title = title.strip()
            changes["title"] = case.title
        if description is not None:
            case.description = description.strip()
            changes["description"] = case.description
        if status_val is not None:
            old_s = case.status
            case.status = status_val.value if hasattr(status_val, "value") else str(status_val)
            changes["status"] = {"old": old_s, "new": case.status}
            if case.status in (CaseStatus.CLOSED.value, CaseStatus.RESOLVED.value):
                case.closed_at = datetime.now(timezone.utc)
        if priority is not None:
            case.priority = priority.value if hasattr(priority, "value") else str(priority)
            changes["priority"] = case.priority
        if summary is not None:
            case.summary = summary.strip()
            changes["summary"] = case.summary
        if assigned_to_id is not None:
            case.assigned_to_id = assigned_to_id
            changes["assigned_to_id"] = assigned_to_id

        db.commit()
        db.refresh(case)

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="UPDATE_CASE",
            object_type="CASE",
            object_id=case.case_id,
            details=changes,
        )

        return case

    @classmethod
    def add_alert(cls, db: Session, actor: User, case_id: int, alert_id: int) -> CaseAlert:
        """Link an alert to a case."""
        case = cls.get_case(db, case_id)
        alert = db.query(DetectionAlert).filter(DetectionAlert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

        existing = db.query(CaseAlert).filter(CaseAlert.case_id == case.id, CaseAlert.alert_id == alert.id).first()
        if existing:
            return existing

        ca = CaseAlert(case_id=case.id, alert_id=alert.id)
        db.add(ca)
        db.commit()
        db.refresh(ca)

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="ADD_ALERT_TO_CASE",
            object_type="CASE",
            object_id=case.case_id,
            details={"alert_id": alert.id},
        )
        return ca

    @classmethod
    def add_investigation(cls, db: Session, actor: User, case_id: int, investigation_id: int) -> CaseInvestigation:
        """Link an investigation to a case."""
        case = cls.get_case(db, case_id)
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found.")

        existing = db.query(CaseInvestigation).filter(
            CaseInvestigation.case_id == case.id,
            CaseInvestigation.investigation_id == inv.id,
        ).first()
        if existing:
            return existing

        ci = CaseInvestigation(case_id=case.id, investigation_id=inv.id)
        db.add(ci)
        db.commit()
        db.refresh(ci)

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="ADD_INVESTIGATION_TO_CASE",
            object_type="CASE",
            object_id=case.case_id,
            details={"investigation_id": inv.investigation_id},
        )
        return ci

    @classmethod
    def add_note(cls, db: Session, actor: User, case_id: int, note_text: str) -> CaseNote:
        """Add executive note to a case."""
        case = cls.get_case(db, case_id)
        note = CaseNote(case_id=case.id, user_id=actor.id, note=note_text.strip())
        db.add(note)
        db.commit()
        db.refresh(note)
        return note


case_service = CaseService()
