"""Alert triage, lifecycle management, and SOC telemetry service for the Step 11 Detection Engine."""


from app.models.detection import (
    AlertNote,
    AlertStatusHistory,
    DetectionAlert,
    DetectionRule,
    DetectionRun,
)
from app.models.enums import AlertStatus
from app.schemas.detection import DetectionStatsResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload


class AlertService:
    """Service for managing alerts, investigation notes, and status transitions."""

    def get_alerts(
        self,
        db: Session,
        status: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        capture_id: int | None = None,
        run_id: int | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[DetectionAlert], int]:
        """Fetch filtered alerts with total matching count."""
        query = db.query(DetectionAlert).options(joinedload(DetectionAlert.rule))

        if status:
            query = query.filter(DetectionAlert.status == status)
        if severity:
            query = query.filter(DetectionAlert.severity == severity)
        if category:
            query = query.filter(DetectionAlert.category == category)
        if capture_id:
            query = query.filter(DetectionAlert.capture_id == capture_id)
        if run_id:
            query = query.filter(DetectionAlert.run_id == run_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (DetectionAlert.title.ilike(search_pattern))
                | (DetectionAlert.source_ip.ilike(search_pattern))
                | (DetectionAlert.destination_ip.ilike(search_pattern))
            )

        total = query.count()
        alerts = (
            query.order_by(desc(DetectionAlert.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return alerts, total

    def get_alert_by_id(self, db: Session, alert_id: int) -> DetectionAlert | None:
        """Fetch alert by ID with evidence, notes, and audit history preloaded."""
        return (
            db.query(DetectionAlert)
            .options(
                joinedload(DetectionAlert.rule),
                joinedload(DetectionAlert.evidence),
                joinedload(DetectionAlert.notes),
                joinedload(DetectionAlert.status_history),
            )
            .filter(DetectionAlert.id == alert_id)
            .first()
        )

    def update_alert_status(
        self,
        db: Session,
        alert: DetectionAlert,
        new_status: str,
        reason: str | None = None,
        user_id: int | None = None,
    ) -> DetectionAlert:
        """Transition an alert workflow state and append to status audit history."""
        old_status = alert.status
        alert.status = new_status

        history = AlertStatusHistory(
            alert_id=alert.id,
            user_id=user_id,
            previous_status=old_status,
            new_status=new_status,
            reason=reason,
        )
        db.add(history)
        db.commit()
        db.refresh(alert)
        return alert

    def add_alert_note(
        self,
        db: Session,
        alert: DetectionAlert,
        note_text: str,
        user_id: int | None = None,
    ) -> AlertNote:
        """Add an analyst note to an alert."""
        note = AlertNote(
            alert_id=alert.id,
            user_id=user_id,
            note=note_text.strip(),
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    def get_detection_statistics(self, db: Session) -> DetectionStatsResponse:
        """Compute aggregate statistics for the detection dashboard."""
        total_runs = db.query(func.count(DetectionRun.id)).scalar() or 0
        total_alerts = db.query(func.count(DetectionAlert.id)).scalar() or 0
        active_alerts = (
            db.query(func.count(DetectionAlert.id))
            .filter(DetectionAlert.status.in_([AlertStatus.NEW, AlertStatus.INVESTIGATING]))
            .scalar()
            or 0
        )

        # By severity
        sev_counts = (
            db.query(DetectionAlert.severity, func.count(DetectionAlert.id))
            .group_by(DetectionAlert.severity)
            .all()
        )
        alerts_by_severity = {sev: count for sev, count in sev_counts}

        # By category
        cat_counts = (
            db.query(DetectionAlert.category, func.count(DetectionAlert.id))
            .group_by(DetectionAlert.category)
            .all()
        )
        alerts_by_category = {cat: count for cat, count in cat_counts}

        # By status
        status_counts = (
            db.query(DetectionAlert.status, func.count(DetectionAlert.id))
            .group_by(DetectionAlert.status)
            .all()
        )
        alerts_by_status = {st: count for st, count in status_counts}

        # Top matching rules
        top_rules_raw = (
            db.query(
                DetectionRule.rule_id,
                DetectionRule.name,
                DetectionRule.severity,
                func.count(DetectionAlert.id).label("count"),
            )
            .join(DetectionAlert, DetectionAlert.rule_id == DetectionRule.id)
            .group_by(DetectionRule.id, DetectionRule.rule_id, DetectionRule.name, DetectionRule.severity)
            .order_by(desc("count"))
            .limit(5)
            .all()
        )
        top_matching_rules = [
            {"rule_id": r[0], "name": r[1], "severity": r[2], "count": r[3]}
            for r in top_rules_raw
        ]

        # Recent alerts
        recent_alerts = (
            db.query(DetectionAlert)
            .options(joinedload(DetectionAlert.rule))
            .order_by(desc(DetectionAlert.created_at))
            .limit(8)
            .all()
        )

        from app.schemas.detection import DetectionAlertListItem

        formatted_recent = [
            DetectionAlertListItem(
                id=a.id,
                run_id=a.run_id,
                rule_id=a.rule_id,
                rule_code=a.rule.rule_id if a.rule else None,
                title=a.title,
                category=a.category,
                severity=a.severity,
                confidence=a.confidence,
                status=a.status,
                source_ip=a.source_ip,
                source_port=a.source_port,
                destination_ip=a.destination_ip,
                destination_port=a.destination_port,
                protocol=a.protocol,
                first_seen_timestamp=a.first_seen_timestamp,
                last_seen_timestamp=a.last_seen_timestamp,
                packet_count=a.packet_count,
                created_at=a.created_at,
            )
            for a in recent_alerts
        ]

        return DetectionStatsResponse(
            total_runs=total_runs,
            total_alerts=total_alerts,
            active_alerts=active_alerts,
            alerts_by_severity=alerts_by_severity,
            alerts_by_category=alerts_by_category,
            alerts_by_status=alerts_by_status,
            top_matching_rules=top_matching_rules,
            recent_alerts=formatted_recent,
        )
