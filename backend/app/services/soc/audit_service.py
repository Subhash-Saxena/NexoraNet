"""Audit Logging and Notification Services for Step 12 SOC."""

import json
from datetime import datetime, timezone
from typing import Any

from app.models.soc import SocAuditLog, SocNotification
from app.models.user import User
from sqlalchemy.orm import Session


class SocAuditService:
    """Manages append-only audit trail logging for SOC analyst operations."""

    @classmethod
    def log_action(
        cls,
        db: Session,
        actor: User | None,
        action: str,
        object_type: str,
        object_id: str | int,
        details: dict[str, Any] | None = None,
    ) -> SocAuditLog:
        """Record an immutable audit event."""
        actor_name = actor.display_name or actor.username if actor else "System"
        user_id = actor.id if actor else None

        entry = SocAuditLog(
            user_id=user_id,
            actor_name=actor_name,
            action=action,
            object_type=object_type,
            object_id=str(object_id),
            details=json.dumps(details) if details else None,
            created_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def list_logs(cls, db: Session, limit: int = 50) -> list[SocAuditLog]:
        """Fetch recent audit logs in reverse chronological order."""
        return db.query(SocAuditLog).order_by(SocAuditLog.created_at.desc()).limit(limit).all()


class SocNotificationService:
    """Manages in-app SOC notifications."""

    @classmethod
    def create_notification(
        cls,
        db: Session,
        user_id: int | None,
        title: str,
        message: str,
        notification_type: str,
        reference_type: str | None = None,
        reference_id: str | int | None = None,
    ) -> SocNotification:
        """Create a notification for an analyst."""
        notif = SocNotification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            reference_type=reference_type,
            reference_id=str(reference_id) if reference_id else None,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @classmethod
    def list_notifications(
        cls,
        db: Session,
        user_id: int | None = None,
        unread_only: bool = False,
        limit: int = 30,
    ) -> list[SocNotification]:
        """List notifications for the current analyst."""
        q = db.query(SocNotification)
        if user_id:
            q = q.filter(SocNotification.user_id == user_id)
        if unread_only:
            q = q.filter(SocNotification.is_read.is_(False))
        return q.order_by(SocNotification.created_at.desc()).limit(limit).all()

    @classmethod
    def mark_as_read(cls, db: Session, notification_id: int) -> SocNotification | None:
        """Mark a notification as read."""
        notif = db.query(SocNotification).filter(SocNotification.id == notification_id).first()
        if notif:
            notif.is_read = True
            db.commit()
            db.refresh(notif)
        return notif


soc_audit_service = SocAuditService()
soc_notification_service = SocNotificationService()
